"""Read frozen gates, record failures, and attach evidence to unchanged Python IR."""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import pprint

from prepare import ROOT, STUDY, NAMES, read, write, digest, compile_policy, extract


def main():
    plan = read(STUDY / 'plan.json')
    results = read(STUDY / 'local-results.json')
    assert results['complete'] and len(results['rows']) == 24
    rows = results['rows']
    assert all(r['valid'] for r in rows)
    assert {(r['candidate'], r['seed']) for r in rows} == {
        (n, c['seed']) for n in NAMES for c in plan['cases']}
    for r in rows:
        folder = STUDY / 'local' / r['candidate'] / str(r['seed'])
        assert digest((folder / 'replay.bin').read_bytes()) == r['replay_sha256']
        assert digest((folder / 'audit.json').read_bytes()) == r['audit_sha256']
        assert r['all_replay_hashes_actions_budgets']
    metrics = {}
    for name in NAMES:
        rr = [r for r in rows if r['candidate'] == name]
        metrics[name] = {'games': len(rr), 'wins': sum(r['win'] for r in rr),
                         'red_wins': sum(r['win'] for r in rr if r['side'] == 0),
                         'blue_wins': sum(r['win'] for r in rr if r['side'] == 1),
                         'deaths': sum(r['deaths'] for r in rr),
                         'all_gear': all(r['gear_heroes'] == 5 for r in rr)}
    proofs = []
    for name in ('anchored', 'unanchored'):
        for case in plan['cases']:
            if case['side'] != 0:
                continue
            folder = STUDY / 'local' / name / str(case['seed'])
            proof = read(folder / 'own-proof.json')
            assert proof['all_state_hashes_equal'] and proof['all_actions_consumed']
            assert proof['controlled_slots'] == list(range(5))
            proofs.append({'candidate': name, 'seed': case['seed'], **proof,
                           'trace_sha256': digest((folder / 'own-trace.jsonl').read_bytes())})
    commands = read(STUDY / 'command-comparison.json')
    control = {r['seed']: r for r in rows if r['candidate'] == 'deployed'}
    max_deaths = max(1.15 * metrics['deployed']['deaths'], metrics['deployed']['deaths'] + 5)
    verdicts = {}
    for name in ('anchored', 'unanchored'):
        rr = [r for r in rows if r['candidate'] == name]
        checks = {
            'retain_deployed_wins': all(r['win'] >= control[r['seed']]['win'] for r in rr),
            'extra_red_win': metrics[name]['red_wins'] >= metrics['deployed']['red_wins'] + 1,
            'all_gear': metrics[name]['all_gear'],
            'survival': metrics[name]['deaths'] <= max_deaths,
            'expanded_assistance_in_full_red_game': any(
                sum(p['expanded_assist_decisions']) > 0 for p in proofs if p['candidate'] == name),
        }
        verdicts[name] = {'checks': checks, 'advances': all(checks.values()),
                          'all_six_command_streams_equal_to_control': all(
                              x['all10_commands_equal_to_deployed'] for x in commands['comparisons'][name]),
                          'verdict': 'Rejected for advancement: no extra red win and no expanded assistance in sampled games.'}
    result = {'closed_at': datetime.now(timezone.utc).isoformat(), 'metrics': metrics,
              'max_deaths': max_deaths, 'verdicts': verdicts, 'red_source_proofs': proofs,
              'owned_commands_matched': sum(p['owned_commands_matched'] for p in proofs),
              'scope': 'Complete frozen local screen; no new Richard/Alex/Jordan competitive claim.',
              'new_hosted_requests': 0, 'live_policy_changed': False}
    write(STUDY / 'verdict.json', result)
    for name in ('anchored', 'unanchored'):
        parent = read(STUDY / 'candidates' / name / 'policy.ir.json')
        p = deepcopy(parent)
        evidence = {'artifact': str(STUDY / 'verdict.json'), 'sha256': digest((STUDY / 'verdict.json').read_bytes())}
        p['belief']['claims']['RestoredCasterSupport']['status'] = 'requires_review'
        p['belief']['claims']['RestoredCasterSupport']['evidence'].append(evidence)
        p['belief']['claims']['SupportRestoreLocalGain'] = {
            'claim': 'This standalone restoration adds a red fort win in the frozen six-case '
                     'local screen. Refuted: 0/3 red, 3/3 blue, 25 deaths, exactly matching '
                     'deployed; all six complete command streams match. This does not '
                     'refute a separately tested interaction with transit or timely recall.',
            'status': 'contradicted', 'evidence': [evidence]}
        p['update'].update(revision=parent['update']['revision'] + 1, parent=digest(parent),
            change={'origin': 'Complete local screen and full red source reconstruction',
                    'candidate': name, 'verdict': verdicts[name]['verdict']},
            needs_review=['belief/RestoredCasterSupport'])
        assert compile_policy(p) == compile_policy(parent)
        assert extract(compile_policy(p), p) == p
        out = STUDY / 'feedback' / name
        out.mkdir(parents=True, exist_ok=True)
        write(out / 'policy.ir.json', p)
        (out / 'policy.py').write_text('"""Primary IR with measured local failure evidence; executable unchanged."""\nPOLICY = '
            + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
        (out / 'policy.bas').write_text(compile_policy(p))
        write(out / 'parity.json', {'exact_compiled_basic_unchanged': True,
                                    'exact_compile_extract': True,
                                    'basic_sha256': digest(compile_policy(p).encode())})
    lines = ['# Standalone red caster support: completed repair experiment', '',
             'Neither restoration passed its pre-registered local screen. Both compiled correctly '
             'and activated in the real-VM fixture, but neither changed a single canonical game '
             'command from the deployed policy across the six complete cases.', '',
             '| Source | Red wins / 3 | Blue wins / 3 | Total wins / 6 | Deaths | Decision |',
             '|---|---:|---:|---:|---:|---|']
    for name, m in metrics.items():
        status = 'Control' if name == 'deployed' else ('Historical reference only' if name == 'historical_anchor' else 'Reject standalone restoration')
        lines.append(f"| {name} | {m['red_wins']} | {m['blue_wins']} | {m['wins']} | {m['deaths']} | {status} |")
    lines += ['', 'All 24 games passed full replay hash/action, score, native VM budget and equipment checks. '
              'Each case pins the same seed, side and opponent across sources. The opponents were default, '
              'deployed and historical anchor; these games do not measure Richard135 or Alex directly.', '',
              f"All {len(proofs)} complete red source reconstructions matched {result['owned_commands_matched']:,} "
              'own commands and every state hash. Expanded support beyond the old 10-tile range executed zero '
              'times. The observer extension is behind existing active-defense and idle-target gates; merely '
              'restoring its code did not produce the intended gameplay intervention in this sample.', '',
              'The exact historical anchor won one additional local red game but had 39 deaths versus the '
              'frozen limit of 30. It was a descriptive reference and is not a qualified replacement. Its '
              'historical Alex red score is only 4/40 against the same current opponent UUID.', '',
              'The useful next experiment must change when or where support becomes available—for example '
              'a separately attributed interaction with caster transit or a selective timely defense response. '
              'Do not spend another hosted batch on an unchanged standalone restoration from this screen. '
              'The existing supervised worker owns those followups and all hosted requests.', '',
              'Evidence: [frozen plan](plan.json), [all results](local-results.json), [verdict and source proofs](verdict.json), '
              '[canonical command comparison](command-comparison.json), [real-VM checks](vm-proof.json). '
              'Updated Python IR records the measured failure in [anchored feedback](feedback/anchored/policy.py) '
              'and [unanchored feedback](feedback/unanchored/policy.py), with byte-identical BASIC.', '',
              'Scope: local diagnosis and advancement rejection only. Six cases are not independent league trials. '
              'No hosted XP or live policy change was made by this isolated experiment.']
    (STUDY / 'REPORT.md').write_text('\n'.join(lines) + '\n')
    manifest = {str(p.relative_to(STUDY)): digest(p.read_bytes()) for p in STUDY.rglob('*')
                if p.is_file() and p.name != 'artifact-manifest.json'}
    write(STUDY / 'artifact-manifest.json', {'files': manifest,
        'instrumentation': {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in Path(__file__).parent.glob('*.py')}})
    print(json.dumps({'metrics': metrics, 'verdicts': verdicts,
                      'owned_commands_matched': result['owned_commands_matched']}, indent=2))


if __name__ == '__main__':
    main()
