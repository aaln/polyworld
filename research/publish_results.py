"""Preserve the frozen experiment and reflect its evidence into the IR."""
from pathlib import Path
import hashlib
import importlib.util
import json
import pprint
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT.parent / 'polyworld/tmp/gota-weak-neutral62-20260924'
OUT = ROOT / 'research/results'
CLASSES = ['Vanguard', 'Ranger', 'Arcanist', 'Druid', 'Demon Hunter',
           'Death Knight', 'Crossbowman', 'Lich', 'Warlock', 'Berserker']
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2) + '\n')


def main():
    report = read(RAW / 'statistics.json')
    assert report['complete'] and report['games'] == 180
    assert not OUT.exists(), 'Preserve the existing publication'
    OUT.mkdir()
    for name in ['hosted-plan.json', 'statistics.json', 'baseline-pool.json',
                 'practice.json', 'native-comparison.json', 'native-result.json',
                 'native-plan-with-hashes.json', 'camp-income-deployed.json',
                 'camp-income-previous.json', 'camp-income-weak-neutral.json']:
        shutil.copy2(RAW / name, OUT / name)
    for arm in ['previous', 'weak-neutral']:
        shutil.copy2(RAW / 'counterfactual' / arm / 'paired-results.json',
                     OUT / (arm + '-pairs.json'))
    shutil.copytree(RAW / 'own-probes', OUT / 'own-probes')
    index = {}
    for folder in (RAW / 'artifacts').iterdir():
        if not (folder / 'audit-result.json').exists():
            continue
        index[folder.name] = {name: sha(folder / name) for name in
            ['replay.bin', 'results.json', 'spec.json', 'player-status.json', 'audit-result.json']}
    assert len(index) == 180
    write(OUT / 'raw-artifact-index.json', {'root': str(RAW / 'artifacts'), 'episodes': index})

    pair = ROOT / 'research/policies/weak-neutral'
    old = read(pair / 'policy.ir.json')
    write(pair / 'evidence/frozen-input.ir.json', old)
    frozen_manifest = read(pair / 'manifest.json')
    write(pair / 'evidence/frozen-input-manifest.json', frozen_manifest)
    for source, dest in [('practice.json', 'practice-comparison.json'),
                         ('statistics.json', 'statistics.json'),
                         ('native-comparison.json', 'native-comparison.json'),
                         ('camp-income-weak-neutral.json', 'camp-income.json')]:
        shutil.copy2(RAW / source, pair / 'evidence' / dest)
    sys.path.insert(0, str(pair / 'tooling/khors18020260924'))
    import recovery_binding as b
    b.configure()
    p = read(pair / 'policy.ir.json')
    s = report['contrasts']['weak-neutral']['overall']
    p['belief']['claims'] = {
        'WeakNeutralMechanism': {
            'status': 'supported',
            'claim': 'The 160 constructed host fixtures passed. In controlled level-4 tier-1 encounters on both sides, all ten hero classes secured at least one neutral kill. This establishes bounded mechanical capability, not league score improvement or successful camp routing.',
            'evidence': [{'artifact': 'evidence/practice-comparison.json'}, {'artifact': 'evidence/camp-income.json'}]},
        'WeakHeroScore': {
            'status': 'contradicted' if s['delta975'][1] < 0 else 'requires_review',
            'claim': f"The 60 matched current-release games gave mean score delta {s['mean_delta']:.2f}, with adjusted 97.5% paired interval {s['delta975']}. Neutral targeting has not been independently confirmed as a score repair. Use actual class-specific neutral XP receipts and scores; do not infer benefit from kills alone.",
            'evidence': [{'artifact': 'evidence/statistics.json'}]},
    }
    p['situation']['notes'] = (
        'Current authority is game 2026.9.23.4, engine 2c8db6ebe1dc785ce1eea87496505d1244ee4c44. '
        'Drafting, skill spending, decimal actions, own-keep shopping, portals, explicit casts, crowd control and neutral camps are current mechanics. '
        'Only public observations are controller inputs. Unseen camp occupancy and respawn remain unknown. '
        'Neutral XP requires eligible living recipients within six tiles on the same navigation layer; kills alone do not establish XP income. '
        'The exact executable is unchanged from the frozen experiment. Historical prose is preserved in evidence/frozen-input.ir.json. '
        'Frozen bindings reproduce inherited behavior; their history is not evidence of present score efficacy. '
        'The neutral rule excludes Ranger and Crossbowman; weak-hero class is a policy grouping, not a claim that every such hero is intrinsically weak.'
    )
    p['update'] = {
        'revision': old['update']['revision'] + 1,
        'parent': b.ir.digest(old),
        'change': {'origin': 'Current-engine reset and completed matched comparison',
                   'executable_changed': False, 'deployment_qualified': False},
        'needs_review': ['belief/WeakHeroScore'],
        'evidence': [{'artifact': 'evidence/' + n} for n in
                     ['request.json', 'frozen-input.ir.json', 'statistics.json',
                      'practice-comparison.json', 'native-comparison.json', 'camp-income.json']],
    }
    b.ir.refresh_grounding(p)
    source = (pair / 'policy.bas').read_text()
    assert b.ir.compile_policy(p) == source and b.ir.extract(source, p) == p
    for name, value in [('policy.ir.json', p), ('extracted.ir.json', p), ('semantics.json', b.ir.grounded(p))]:
        write(pair / name, value)
    (pair / 'policy.py').write_text('POLICY = ' + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
    manifest = dict(frozen_manifest, ir_sha256=b.ir.digest(p), hosted_complete=True,
                    score_gate_passed=s['mean_delta'] > 0 and s['delta975'][0] > 0,
                    deployment_qualified=False,
                    frozen_ir_sha256=frozen_manifest['ir_sha256'])
    manifest['artifacts'] = {str(x.relative_to(pair)): sha(x) for x in pair.rglob('*')
                             if x.is_file() and '__pycache__' not in x.parts and x.name != 'manifest.json'}
    write(pair / 'manifest.json', manifest)
    assert sha(pair / 'policy.bas') == frozen_manifest['source_sha256']

    lines = ['# Current-engine recovery comparison', '',
             '180 hosted games: 60 current-policy controls and two responsive 60-pair comparisons. '
             'All ten side/seat positions, frozen rosters and seeds. Each request had at most 60 games. '
             'Full replay hashes, all ten VM statuses, XP and integer score accounting were audited.', '',
             '| Policy | Mean score | Positive-score games | Mean among positive games | Paired gain and adjusted 97.5% interval |',
             '|---|---:|---:|---:|---|']
    base = report['contrasts']['previous']['overall']['baseline']
    lines.append(f"| Deployed | {base['mean']:.1f} | {60-base['zero_games']}/60 | {base['nonzero_mean']:.1f} | Reference |")
    for arm, d in report['contrasts'].items():
        a = d['overall']; c = a['candidate']; lo, hi = a['delta975']
        lines.append(f"| {arm} | {c['mean']:.1f} | {60-c['zero_games']}/60 | {c['nonzero_mean']:.1f} | {a['mean_delta']:+.1f} [{lo:+.1f}, {hi:+.1f}] |")
    lines += ['', 'The intervals resample whole matched games within side/seat strata and adjust for two baseline contrasts. '
              'Hero slices below are exploratory. Conditional positive-score means select different outcomes and must be read alongside the overall mean. '
              'The legacy helper additionally reports a >=500-point productivity threshold; this is a diagnostic, not the promotion objective.', '',
              '## Neutral income by hero', '',
              '| Hero | Games per arm | Deployed / candidate neutral XP | Deployed / candidate neutral kills | Candidate score change |',
              '|---|---:|---:|---:|---:|']
    d = report['contrasts']['weak-neutral']
    for k, v in sorted(d['by_class'].items(), key=lambda x: int(x[0])):
        t = d['class_telemetry'][k]; xp = [t[a]['means']['neutral_xp'] for a in ['baseline', 'candidate']]
        kills = [t['neutral_mechanism'][a]['neutral_kills'] for a in ['baseline', 'candidate']]
        lines.append(f"| {CLASSES[int(k)]} | {v['n']} | {xp[0]:.1f} / {xp[1]:.1f} | {kills[0]:.1f} / {kills[1]:.1f} | {v['mean_delta']:+.1f} |")
    lines += ['', 'Warlock and Demon Hunter were absent from this natural-draft panel; no hosted efficacy claim applies to them. '
              'All ten classes did secure neutral kills in the controlled camp encounters. The candidate and deployed policy each earned 400 total neutral XP there; '
              'the previous policy earned 970. The candidate did not improve this local mechanism test. The 12 native full games also favored deployed source in total score '
              '(9,942 versus 9,177 candidate and 8,164 previous); these are runtime/mechanism checks, not hosted outcome evidence.', '',
              'The complete own-source reconstructions of three poor league games matched every command and state hash. '
              'The Vanguard saw an eligible camp on only 15 of 1,553 active decisions and selected it every time. '
              'That is an opportunity/routing hypothesis, not proof that a camp route will improve score. '
              'Druid and Arcanist observations also show retreat, health and competing-target restrictions.', '',
              '## Decision and continuation', '',
              'The fresh workspace and all three references are preserved. No automatic rollback or league promotion follows from this study. '
              'Any advancing candidate requires an independent fresh confirmation under the frozen rule. '
              'The next repair should test bounded camp access and income per travel/death time, while protecting the deployed policy’s productive-game rate. '
              'Do not select a hero-specific hybrid on this sample and call the same sample confirmation.', '',
              '[Current research contract](CURRENT_CONTRACT.md) · [Full statistics](results/statistics.json) · '
              '[Khors v180 observations](opponents/khors-v180/README.md) · [Frozen plan](results/hosted-plan.json)', '',
              f'Raw captures remain at `{RAW}`. Historical workspace and session inputs remain intact.']
    (ROOT / 'research/RESULTS.md').write_text('\n'.join(lines) + '\n')
    top = read(ROOT / 'research/manifest.json')
    top['policies']['weak-neutral']['semantic_ir_status'] = 'Reviewed with current local/hosted evidence; no independent confirmation or deployment qualification.'
    top['results'] = 'research/RESULTS.md'
    write(ROOT / 'research/manifest.json', top)
    write(OUT / 'manifest.json', {'files': {str(p.relative_to(OUT)): sha(p) for p in OUT.rglob('*') if p.is_file()}})
    print(json.dumps({'published': True, 'source_unchanged': True, 'score_gate_passed': manifest['score_gate_passed'], 'ir_sha256': manifest['ir_sha256']}))


if __name__ == '__main__':
    main()
