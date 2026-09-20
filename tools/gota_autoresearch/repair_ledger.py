"""Publish measured repair outcomes, with separate local and hosted evidence."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAMPAIGN = ROOT.parent / 'gota-autoresearch'
WORK = CAMPAIGN / 'forks/fork_20260920_045449_29b23b'
OUT = ROOT / 'docs/experiments/gota-repairs-20260920'
OUT.mkdir(parents=True, exist_ok=True)


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hosted(path):
    result = read(path)
    rows = result['rows']
    n = result.get('n', result.get('games'))
    assert len(rows) == n
    assert result.get('all_replay_vm_roster_checks', result.get('all_vm_replay_identity_checks'))
    for key, field in [('wins', 'win'), ('losses', 'loss'), ('draws', 'draw')]:
        assert result[key] == sum(r[field] for r in rows)
    for r in rows:
        folder = path.parent / 'artifacts' / r['episode']
        audit = read(folder / 'audit.json')
        assert audit['hash_mismatches'] == 0 and audit['ticks'] == r['ticks']
        assert audit['recorded_actions'] == audit['actions_consumed']
        validity = read(folder / 'vm-validity.json')
        # Preserve the full official-log / structured status receipt by hash.
        if validity['method'] == 'headless_summary':
            log = folder / 'game.log'
            assert sha(log) == validity['log_sha256']
            assert 'scripts: 10/10 active' in log.read_text()
        else:
            assert validity  # Original auditor's structured-status receipt remains linked.
        if 'replay_sha256' in r:
            assert sha(folder / 'replay.bin') == r['replay_sha256']
        if 'audit_sha256' in r:
            assert sha(folder / 'audit.json') == r['audit_sha256']
    return {'n': n, 'wins': result['wins'], 'losses': result['losses'], 'draws': result['draws'],
            'request': result['request'], 'evidence': str(path), 'evidence_sha256': sha(path)}


def local(path):
    result = read(path)
    rows = result['rows']
    assert result['verified_games'] == len(rows)
    for name, metric in result['metrics'].items():
        rr = [r for r in rows if r['name'] == name]
        assert len(rr) == metric['games']
        assert sum(r['win'] for r in rr) == metric['wins']
        assert sum(r['deaths'] for r in rr) == metric['deaths']
    return {'metrics': result['metrics'], 'evidence': str(path), 'evidence_sha256': sha(path),
            'scope': 'Owned-program local games only; no Richard or Alex transfer claim.'}


def main():
    old = ROOT / 'tmp/gota-ir/richard-counter-20260920/hosted'
    cells = {}
    for name in ('parent', 'critical40', 'critical60', 'weapon'):
        stage = 'baseline' if name == 'parent' else 'screen'
        cells[name] = {side: hosted(old / stage / name / side / 'result.json')
                       for side in (('red',) if name == 'weapon' else ('red', 'blue'))}
    middle = local(WORK / 'richard_middle_cached_v2/screen/result.json')
    transit = local(WORK / 'middle_transit_v4/confirmation/result.json')
    scoped = local(WORK / 'scoped_core_response_v3/screen/result.json')
    transit_hosted = {name: hosted(WORK / 'middle_transit_v4/hosted-discovery' / name / 'result.json')
                      for name in ('parent-red', 'parent-blue', 'richard135-red')}
    support = read(ROOT / 'tmp/gota-ir/support-repairs-20260920/verdict.json')
    for name in ('anchored', 'unanchored'):
        assert not support['verdicts'][name]['advances']
    entries = [
        {'repair': '40-tile critical recall', 'hosted': cells['critical40'],
         'verdict': 'Small Richard screen: red 0/4, blue 2/4. Insufficient; no promotion.'},
        {'repair': '60-tile critical recall', 'hosted': cells['critical60'], 'local': middle,
         'verdict': 'Richard blue 4/4, red 0/4; local 1/12 versus deployed 6/12, deaths 329 versus 61. Reject this broad variant.'},
        {'repair': 'Red weapon-first equipment', 'hosted': cells['weapon'],
         'verdict': 'Richard red 0/4. No gain in this screen; no promotion.'},
        {'repair': 'Static middle Warlock plus critical recall', 'local': middle,
         'verdict': '1/12 local wins versus 6/12 deployed, deaths 310 versus 61. Reject the exact combination.'},
        {'repair': 'One-time red caster transit', 'local': transit, 'hosted': transit_hosted,
         'verdict': 'Local 30/32 versus 16/32; hosted accepted-ancestor 40/40 both colors, Richard135 red 0/40. Useful local component; insufficient target repair.'},
        {'repair': 'Transit plus 240-tick blue response', 'local': scoped,
         'verdict': '9/16 versus transit 15/16; blue 1/8 versus 7/8 and deaths 193 versus deployed 103. Reject.'},
        {'repair': 'Transit plus 720-tick blue response', 'local': scoped,
         'verdict': '9/16 versus transit 15/16; blue 1/8 versus 7/8 and deaths 261 versus deployed 103. Reject.'},
        {'repair': 'Restore anchored idle caster support', 'local_metrics': support['metrics']['anchored'],
         'evidence': str(ROOT / 'tmp/gota-ir/support-repairs-20260920/REPORT.md'),
         'verdict': '3/6, matching deployed; every game command identical. No expanded support in all three red games. Reject standalone restoration.'},
        {'repair': 'Restore unanchored idle caster support', 'local_metrics': support['metrics']['unanchored'],
         'evidence': str(ROOT / 'tmp/gota-ir/support-repairs-20260920/REPORT.md'),
         'verdict': '3/6, matching deployed; every game command identical. No expanded support in all three red games. Reject standalone restoration.'},
    ]
    document = {'schema': 'gota-repair-ledger/1', 'as_of': datetime.now(timezone.utc).isoformat(),
                'deployed_basic_sha256': 'be6affd3b3b9516a15dc8b32687c29b728adc4aa367fc651ba5c0fcefb9cbf73',
                'exact_richard_version': '7c370daf-3c5f-42f8-870b-54b79c495a44',
                'exact_alex_version': 'a30542cb-54de-4109-92e6-bcabca7db4d8',
                'current_richard_control': cells['parent'], 'repairs': entries,
                'jointly_qualified_repair': None,
                'limitations': ['Local opponents are owned references, not private target policies.',
                    'Four-game screens are directional only.',
                    'The 40 Richard transit losses share one complete command trajectory.',
                    'None of these repairs has fresh joint Richard/Alex/Jordan and field qualification.']}
    (OUT / 'ledger.json').write_text(json.dumps(document, indent=2) + '\n')
    lines = ['# GOTA repair results', '', f"Updated {document['as_of']}. Exact Richard v135 and Alex g002:v1 remain the targets; Jordan preservation is mandatory.", '',
             '**No tested repair in this ledger qualifies as the combined solution.** The red caster-transit component '
             'improved local play and beat the accepted ancestor 40/40 on both colors, but lost every one of its 40 '
             'Richard135 red games. Broad defensive recall hurt general play. Standalone caster support was inactive '
             'in the fresh gameplay screen despite passing activation fixtures.', '',
             '| Repair | Measured result and decision |', '|---|---|']
    for entry in entries:
        evidence = entry.get('evidence')
        if not evidence:
            evidence = next(iter(entry['hosted'].values()))['evidence'] if 'hosted' in entry else entry['local']['evidence']
        lines.append(f"| [{entry['repair']}]({evidence}) | {entry['verdict']} |")
    lines += ['', '## What the tests establish', '',
              '- Moving red casters through the middle changes behavior and improves the measured owned-reference matchups. It does not yet solve Richard135.',
              '- Increasing recall broadly can turn a favorable target screen into a large field regression. Both response duration variants dropped from the transit control’s 7/8 blue wins to 1/8.',
              '- Restoring an assistance rule behind existing defense/idle gates can add code without changing gameplay. Both fresh support variants reproduced every canonical command in all six cases, with zero expanded support in six complete red source reconstructions.',
              '- The historical anchor reference improved the new local sample from 3/6 to 4/6 but raised deaths from 25 to 39, above the frozen limit of 30. Its known exact-Alex red weakness remains.', '',
              '## Evidence and interpretation', '',
              'The isolated interactive study ran 24 new complete native games, real-VM activation/negative/dense-class checks '
              'and complete source reconstructions for all six repaired red games. '
              f"Those reconstructions matched {support['owned_commands_matched']:,} own commands and every state hash. "
              'The supervised researcher separately completed and audited 120 hosted component-discovery games. '
              'This ledger recomputes result totals and checks the linked replay/VM receipts; original plans, failures and source identities remain intact.', '',
              '[Detailed support experiment](' + str(ROOT / 'tmp/gota-ir/support-repairs-20260920/REPORT.md') + ') · '
              '[Machine-readable ledger](ledger.json) · '
              '[Opponent IR analysis](' + str(ROOT / 'docs/opponents/richard-alex-20260920/analysis.md') + ')', '',
              'These local screens and repeated fixed-lineup trajectories are not independent league trials. '
              'Fresh current-control comparisons, Richard/Alex/Jordan on both colors and broad-field checks '
              'remain required for one final executable. The current live policies are unchanged by the interactive study.', '',
              'The next useful tests must alter actual response timing, allocation or the interaction with transit. '
              'The existing supervised worker owns those followups and all hosted requests. Rerun '
              '`tools/gota_autoresearch/repair_ledger.py` after audited results change; it never creates requests or changes policies.']
    (OUT / 'README.md').write_text('\n'.join(lines) + '\n')
    (OUT / 'artifact-manifest.json').write_text(json.dumps({
        'as_of': document['as_of'], 'files': {n: sha(OUT / n) for n in ('README.md', 'ledger.json')},
        'instrument': {str(Path(__file__).relative_to(ROOT)): sha(Path(__file__))}}, indent=2) + '\n')
    print(json.dumps({'repairs_recorded': len(entries), 'report': str(OUT / 'README.md'),
                      'jointly_qualified_repair': None}, indent=2))


if __name__ == '__main__':
    main()
