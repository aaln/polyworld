"""Convert complete hosted evidence into reusable, scoped semantic feedback."""
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

import hosted
from hosted import ROOT, STUDY, read, write, sha

OUT = ROOT / 'docs/microplay/2026-09-20-hosted'


def aggregate(rows):
    totals = {key: sum(r[key] for r in rows) for key in [
        'ticks', 'deaths', 'alive_ticks', 'basic_hits', 'allied_deaths', 'allied_alive_ticks',
        'xp', 'decisions', 'crowded_decisions', 'eligible_original_unit_decisions',
        'picks', 'refinements', 'finish_refinements', 'assist_refinements', 'refined_attack_commands']}
    return totals | {'episodes': len(rows), 'games_with_refinements': sum(r['refinements'] > 0 for r in rows),
        'deaths_per_alive_minute': totals['deaths'] * 1440 / totals['alive_ticks'],
        'basic_hits_per_alive_minute': totals['basic_hits'] * 1440 / totals['alive_ticks'],
        'allied_deaths_per_allied_alive_minute': totals['allied_deaths'] * 1440 / totals['allied_alive_ticks'],
        'xp_per_game_minute': totals['xp'] * 1440 / totals['ticks'],
        'crowded_fraction': totals['crowded_decisions'] / totals['decisions'],
        'max_instructions': max(r['max_instructions'] for r in rows),
        'max_work': max(r['max_work'] for r in rows),
        'unique_effective_seeds': len({r['seed'] for r in rows}),
        'distinct_sampled_outcome_signatures': len({r['sampled_outcome_signature'] for r in rows}),
        'seat_counts': dict(sorted(Counter(r['slot'] for r in rows).items()))}


def main():
    plan = read(STUDY / 'plan.ir.json')
    cfg = read(hosted.CAMPAIGN / 'config.json')
    assert sha(cfg['auditor']) == cfg['auditor_sha256']
    assert subprocess.check_output(['git', '-C', str(hosted.CLEAN), 'rev-parse', 'HEAD'], text=True).strip() == plan['engine_commit']
    assert not subprocess.check_output(['git', '-C', str(hosted.CLEAN), 'status', '--porcelain', '--untracked-files=no'], text=True).strip()
    assert sha(hosted.CLEAN / 'tmp/microplay/hosted_probe.nim') == sha(Path(__file__).parent / 'hosted_probe.nim')
    rows, decisions = [], []
    requests = {}
    patterns = {}
    for arm in ['parent', 'finish', 'combined']:
        subject = plan['arms'][arm]['version']
        request = read(STUDY / arm / 'batch/created.json')['id']
        requests[arm] = {'id': request, 'url': 'https://softmax.com/observatory/v2?tab=overview&detail=experience-request:' + request}
        episodes = read(STUDY / arm / 'batch/episodes.json')
        assert len(episodes) == 40 and all(e['status'] == 'completed' for e in episodes)
        expected = Counter([subject] + [p['version'] for p in plan['other_players']])
        patterns[arm] = Counter()
        for ep in episodes:
            folder = STUDY / arm / 'artifacts' / ep['id']
            ep, result, audit, probe, validity = [read(folder / n) for n in
                ['episode.json', 'results.json', 'audit.json', 'probe.json', 'vm-validity.json']]
            assert Counter(ep['policy_version_ids']) == expected
            assert ep['coworld_id'] == plan['target']['coworld_id'] and ep['coworld_version'] == plan['game_version']
            assert {k: v for k, v in ep['game_config'].items() if k not in {'seed', 'players', 'tokens'}} == plan['config']
            assert [h['total_xp'] for h in audit['heroes']] == result['total_xp']
            assert probe['source_sha256'] == plan['arms'][arm]['source_sha256']
            assert probe['all_state_hashes_equal'] and probe['all_actions_consumed']
            assert probe['ticks'] == audit['ticks'] == result['ticks']
            assert audit['hash_mismatches'] == 0 and audit['actions_consumed'] == audit['recorded_actions']
            assert audit['binary_sha256'] == cfg['auditor_sha256']
            assert sha(folder / 'replay.bin') == probe['replay_sha256'] == audit['replay_sha256']
            roster = tuple('<subject>' if v == subject else v for v in ep['policy_version_ids'])
            patterns[arm][roster] += 1
            slot = ep['policy_version_ids'].index(subject)
            hero = audit['heroes'][slot]
            # Allies exclude the subject, so teamwork is not a relabelled self metric.
            allies = [h for h in audit['heroes'] if h['team'] == hero['team'] and h['slot'] != slot]
            signature = hashlib.sha256(json.dumps({'roster': roster, 'ticks': audit['ticks'],
                'heroes': audit['heroes'], 'events': audit['events'], 'frames': audit['frames']}, sort_keys=True).encode()).hexdigest()
            row = {'arm': arm, 'episode': ep['id'], 'request': request, 'seed': result['seed'],
                'slot': slot, 'class': hero['class'], 'team': hero['team'], 'ticks': result['ticks'],
                'deaths': hero['deaths'], 'alive_ticks': hero['alive_ticks'], 'basic_hits': hero['basic_hits'],
                'xp': hero['total_xp'], 'allied_deaths': sum(h['deaths'] for h in allies),
                'allied_alive_ticks': sum(h['alive_ticks'] for h in allies),
                'score_diagnostic_only': hero['score'], 'normalized_roster': roster,
                'sampled_outcome_signature': signature, 'vm_validity_method': validity['method'],
                'evidence_directory': str(folder.relative_to(ROOT)),
                'artifacts': {p.name: sha(p) for p in folder.iterdir() if p.is_file() and p.name != '.done'}}
            row.update({k: probe[k] for k in ['decisions', 'crowded_decisions', 'eligible_original_unit_decisions',
                'picks', 'refinements', 'finish_refinements', 'assist_refinements', 'refined_attack_commands',
                'max_instructions', 'max_work', 'commands_matched']})
            if arm == 'combined':
                row['counterfactuals'] = {other: read(folder / ('counterfactual-' + other + '.json'))
                                          for other in ['parent', 'finish']}
            rows.append(row)
            for line in gzip.decompress((folder / 'probe.jsonl.gz').read_bytes()).decode().splitlines():
                event = json.loads(line)
                if event['type'] == 'refinement':
                    decisions.append({'episode': ep['id'], 'arm': arm, 'source_sha256': probe['source_sha256']} | event)
    assert len({r['seed'] for r in rows}) == 120, 'Repeated seeds require explicit analysis'
    for arm in plan['arms']:
        assert Counter(r['slot'] for r in rows if r['arm'] == arm) == Counter({i: 4 for i in range(10)})
    roster_matched = patterns['parent'] == patterns['finish'] == patterns['combined']
    arms = {a: aggregate([r for r in rows if r['arm'] == a]) for a in plan['arms']}
    cf = {a: dict(Counter(r['counterfactuals'][a]['counterfactual'] for r in rows if r['arm'] == 'combined'))
          for a in ['parent', 'finish']}
    equivalent = all(v == {'identical_full_trajectory_with_other_players_commands': 40} for v in cf.values())
    active = arms['combined']['refinements'] > 0
    report = {'schema': 'gota-microplay-hosted-research-ir/1', 'id': plan['id'],
        'situation': {'engine_commit': plan['engine_commit'], 'game_version': plan['game_version'],
                      'target': plan['target'], 'config': plan['config'], 'other_players': plan['other_players'],
                      'policy_arms': plan['arms'], 'requests': requests},
        'goal': {'primary': 'Verify individual finishing and guarded cooperative assistance against real other players',
                 'win_optimization': False},
        'skill': {'operator': 'microplay_local_target_v4', 'parameters': {'range_percent': 60, 'object_limit': 48},
                  'causal_boundary': 'No structure/no-target macro override; target refinement feeds unchanged action controller'},
        'experiment': {'episodes': 120, 'episodes_per_arm': 40, 'all_ten_seats_per_arm': True,
            'same_normalized_roster_distribution': roster_matched, 'across_request_seeds_paired': False,
            'counterfactual_method': read(STUDY / 'counterfactual-method.ir.json'),
            'all_complete_replays_verified': True, 'all_ten_vms_valid_in_every_game': True,
            'exact_subject_vm_reconstructions': 120, 'counterfactual_reconstructions': 80},
        'observation': {'arms': arms, 'counterfactuals': cf,
            'by_class': {a: {c: aggregate([r for r in rows if r['arm'] == a and r['class'] == c])
                           for c in sorted({r['class'] for r in rows})} for a in plan['arms']}},
        'belief': {'runtime_validity': {'status': 'supported', 'claim': 'All full tapes and exact subject commands replay correctly; all ten hosted VMs complete.'},
            'natural_activation': {'status': 'supported' if active else 'not_observed',
                                  'claim': f"Combined policy changed targets {arms['combined']['refinements']} times in 40 hosted games."},
            'field_improvement': {'status': 'requires_review', 'claim': 'No causal improvement established by these independent-seed cohorts.'}},
        'update': {'decision': 'field_activation_observed_benefit_unverified' if active else 'field_improvement_not_verified_skill_inactive',
                   'promotion': False, 'preserve_local_evidence': True,
                   'next_experiment': 'If inactive, redesign opportunity/VM gating in a new IR fork and repeat the same frozen-player ablation; do not expand identical inactive batches.'},
        'limitations': ['One fixed pool of nine other players on the competition map; not general opponent coverage.',
            'Fresh seeds across cohorts do not make them paired counterfactual outcomes.',
            'Counterfactuals stop at the first different command; no outcomes beyond that point are estimated.',
            'Repeated sampled outcome signatures are reported; seeds alone are not evidence of independent behavioral diversity.',
            'Basic hit metrics include all target kinds. Allied mortality is descriptive, not attribution of protection.',
            'Crowding and conservative range gates can prevent activation; command intent is not landed damage.'],
        'episodes': rows}
    if equivalent:
        report['belief']['same_game_behavioral_equivalence'] = {
            'status': 'supported_on_this_roster',
            'claim': 'On every one of40combined-arm games, substituting either the parent or finishing-only subject produces exactly the same commands and all world states through termination. No individual or cooperative gameplay improvement occurs on these40trajectories.'}
    report['experiment']['provenance'] = {
        'clean_checkout': str(hosted.CLEAN), 'tracked_checkout_clean': True,
        'auditor_sha256': cfg['auditor_sha256'], 'probe_binary_sha256': sha(STUDY / 'hosted-probe'),
        'probe_source_sha256': sha(Path(__file__).parent / 'hosted_probe.nim'),
        'nim_sha256': sha('/Users/aaln/.local/bin/nim'),
        'compile_command': 'POLYWORLD_DEPS=/Users/aaln/experiments/softmax/gota-research-20260916/deps /Users/aaln/.local/bin/nim c -d:headless -d:release --hints:off tmp/microplay/hosted_probe.nim'}
    OUT.mkdir(parents=True, exist_ok=True)
    write(OUT / 'research.ir.json', report)
    for name in ['plan.ir.json', 'counterfactual-method.ir.json', 'allowance-change.ir.json']:
        shutil.copy2(STUDY / name, OUT / name)
    raw = ''.join(json.dumps(d, separators=(',', ':')) + '\n' for d in decisions).encode()
    (OUT / 'decisions.ir.jsonl.gz').write_bytes(gzip.compress(raw, mtime=0))
    evidence = {'artifact': str((OUT / 'research.ir.json').relative_to(ROOT)), 'sha256': sha(OUT / 'research.ir.json')}
    import ir_v4
    parity = {}
    for arm in ['finish', 'combined']:
        prior = read(STUDY / arm / 'policy.ir.json')
        updated = deepcopy(prior)
        updated['belief']['claims']['B_microplay_hosted'] = {
            'claim': f"Hosted {arm}: {arms[arm]['refinements']} target refinements in40games against nine frozen other players; full replay/VM validity established. Field benefit remains unverified.",
            'status': 'requires_review', 'evidence': [evidence]}
        updated['update']['revision'] += 1
        updated['update']['parent'] = ir_v4.compiler.digest(prior)
        updated['update']['change'] = 'Hosted microplay ablation and exact same-tape counterfactual feedback; executable unchanged.'
        updated['update']['needs_review'] = ['Natural opportunity coverage and causal field benefit remain unverified.']
        updated['update']['evidence'].append(evidence)
        source = ir_v4.compiler.compile_policy(updated)
        assert source == (STUDY / arm / 'policy.bas').read_text()
        assert ir_v4.compiler.extract(source, updated) == updated
        write(OUT / 'evaluated' / arm / 'policy.ir.json', updated)
        (OUT / 'evaluated' / arm / 'policy.bas').write_text(source)
        parity[arm] = {'semantic_digest': ir_v4.compiler.digest(updated),
                       'source_sha256': sha(OUT / 'evaluated' / arm / 'policy.bas'), 'unchanged_source': True, 'roundtrip': True}
    write(OUT / 'manifest.json', {'schema': 'gota-microplay-hosted-bundle/1', 'research': evidence,
        'policies': parity, 'instrument': {n: sha(Path(__file__).parent / n) for n in ['hosted.py', 'hosted_probe.nim', 'hosted_report.py']},
        'probe_binary_sha256': sha(STUDY / 'hosted-probe'), 'decisions_sha256': sha(OUT / 'decisions.ir.jsonl.gz')})
    text = '# Hosted microplay verification — 2026-09-20\n\n'
    text += ('The enhanced policy was inactive in this hosted study; field improvement is not verified.\n\n' if not active else
             'The enhanced policy activated; this small hosted study does not establish causal superiority.\n\n')
    text += '120 XP games used nine frozen other players, with each subject policy occupying all ten seats four times. Every complete replay, subject command sequence, and hosted VM status passed.\n\n'
    text += '| Arm | Games | Target changes | Basic hits | Self deaths | Other ally deaths | Crowded decisions |\n|---|---:|---:|---:|---:|---:|---:|\n'
    for a, m in arms.items():
        text += f"| {a} | {m['episodes']} | {m['refinements']} | {m['basic_hits']} | {m['deaths']} | {m['allied_deaths']} | {m['crowded_fraction']:.1%} |\n"
    text += '\nCohorts use different seeds. Counts and exposure rates are descriptive; wins are not the objective.\n\n'
    text += f"The48-object budget gate skipped {arms['combined']['crowded_fraction']:.1%} of combined-policy decisions. Its remaining {arms['combined']['eligible_original_unit_decisions']:,} unit-target decisions produced {arms['combined']['picks']} finishing/assistance candidates. Crowding is one blocker; the other reach/target/ally guards also limit opportunities.\n\n"
    for a, values in cf.items():
        text += f'- Combined → {a}, same-tape counterfactuals: `{values}`.\n'
    text += '\nCounterfactual reconstruction reruns the complete alternate subject VM while replaying the other nine players. It checks every command and state hash, and stops at the first different command. Identical full trajectories establish behavioral equivalence in those games; a divergence alone does not prove benefit.\n\n'
    if equivalent:
        text += 'Both alternatives matched every command and world state in all40combined-arm games. The enhanced policy therefore produced no individual or cooperative gameplay change on those trajectories. Differences between the three hosted cohorts cannot be treated as causal evidence for the enhancements.\n\n'
    text += 'Evidence: [semantic research IR](research.ir.json), [prospective plan](plan.ir.json), [decision events](decisions.ir.jsonl.gz), and [manifest](manifest.json). The `evaluated/` policies contain evidence updates with exactly unchanged BASIC. Raw replays and official status receipts are retained under `tmp/gota-ir/microplay-xp-20260920/`, indexed and hashed in the research IR.\n\n'
    for a, r in requests.items():
        text += f'- [{a} XP request]({r["url"]})\n'
    text += '\nNext experiment: redesign the opportunity/VM-budget gate as a separate IR fork, then repeat the frozen-player ablation. Additional unchanged-policy batches are not warranted by these results.\n\n'
    text += 'No league champion was changed. The shared daily allowance was raised from 1,600 to 100,000 by explicit user instruction; this experiment reserved 120 episodes.\n'
    (OUT / 'README.md').write_text(text)
    print(json.dumps({'arms': arms, 'counterfactuals': cf, 'roster_matched': roster_matched, 'output': str(OUT)}, indent=2))


if __name__ == '__main__':
    main()
