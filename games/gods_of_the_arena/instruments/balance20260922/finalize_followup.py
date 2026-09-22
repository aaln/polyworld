"""Preserve the complete draft-only follow-up and validated semantic feedback."""
from pathlib import Path
import json
import pprint
import shutil
import draft_only
from environment import h, ROOT, STUDY

HERE = Path(__file__).resolve().parent
PAIR = ROOT / 'examples/gods_of_the_arena/players/ir/forks/balance-draft20260922'


def copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def main():
    result = h.read(STUDY / 'draft-isolation/result.json')
    assert result['complete'] and sum(c['games'] for c in result['cells']) == 80
    assert not PAIR.exists()
    draft_only.configure()
    ir = draft_only.build.ir
    original = STUDY / 'candidates/crossbow_draft'
    p = h.read(original / 'policy.ir.json')
    parent = ir.digest(p)
    source = (original / 'policy.bas').read_bytes()
    clean = all(c['invalid']==0 for c in result['cells'])
    p['belief']['claims'] = {
        'DraftIsolation': {'claim': 'Crossbowman-only draft priority passes the frozen >=10% aggregate gain and >=95% per-color score preservation gate on the fixed current-engine roster.',
            'status': 'supported' if result['passed'] else 'contradicted', 'evidence': [{'artifact': 'evidence/result.json'}]},
        'Runtime': {'claim': 'Eighty current-engine games have exact source/VM/replay/XP/integer-score checks, and non-draft templates, parameters and order remain unchanged from the deployed controller.',
            'status': 'supported' if clean else 'contradicted', 'evidence': [{'artifact': 'evidence/result.json'}, {'artifact': 'evidence/experiment.md'}]},
        'Generalization': {'claim': 'The follow-up reuses earlier controls and fixed rosters; it is not independent confirmation, late-draft validation, a universal hero ranking or proof of #1.',
            'status': 'requires_review', 'evidence': [{'artifact': 'evidence/experiment.md'}]}}
    p['update'] = {'revision': 2, 'parent': parent,
        'change': {'origin': 'User balance update; retain exact tested Crossbowman draft source and reflect completed follow-up evidence', 'passed': result['passed']},
        'needs_review': ['belief/Generalization'], 'evidence': [{'artifact': 'evidence/experiment.md'}, {'artifact': 'evidence/result.json'}]}
    ir.refresh_grounding(p)
    assert ir.compile_policy(p).encode() == source
    assert ir.extract(source.decode(), p) == p
    PAIR.mkdir()
    for name, value in [('policy.ir.json', p), ('extracted.ir.json', p), ('semantics.json', ir.grounded(p))]:
        h.write(PAIR / name, value)
    (PAIR / 'policy.py').write_text('POLICY = ' + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
    (PAIR / 'policy.bas').write_bytes(source)
    shutil.copytree(original, PAIR / 'captured')
    previous = PAIR.parent / 'balance20260922'
    shutil.copytree(previous / 'tooling', PAIR / 'tooling', ignore=shutil.ignore_patterns('__pycache__'))
    for name in ('draft_only.py', 'build.py'):
        copy(HERE / name, PAIR / 'tooling/balance20260922' / name)
    for name in ('plan.json', 'result.json', 'review.json'):
        copy(STUDY / 'draft-isolation' / name, PAIR / 'evidence' / name)
    controls = h.read(STUDY / 'hosted/result.json')['cells'][:2]
    h.write(PAIR / 'evidence/controls.json', controls)
    copy(ROOT / 'games/gods_of_the_arena/experiments/2026-09-22-crossbow-draft-isolation.md', PAIR / 'evidence/experiment.md')
    for name in ('crossbow-draft-native.json', 'crossbow-draft-scenarios.json', 'crossbow-draft-practice.json'):
        copy(STUDY / name, PAIR / 'evidence' / name)
    copy(STUDY / 'red-controller-equivalence/result.json', PAIR / 'evidence/red-controller-equivalence.json')
    for name in ('followup.py', 'draft_practice.nim'):
        copy(HERE / name, PAIR / 'evidence/instruments' / name)
    version = h.read(STUDY / 'uploads/crossbow_draft/uploaded-version.json')
    h.write(PAIR / 'evidence/registration.json', {k:version[k] for k in ('id','name','version')})
    h.write(PAIR / 'evidence/raw-inputs.json', {'root': str(STUDY / 'draft-isolation'),
        'files': {str(f.relative_to(STUDY / 'draft-isolation')):h.sha(f.read_bytes()) for f in sorted((STUDY / 'draft-isolation').rglob('*')) if f.is_file() and f.suffix not in ('.log','.tmp')}})
    copy(HERE / 'convert_followup.py', PAIR / 'convert.py')
    copy(HERE / 'verify_followup.py', PAIR / 'verify.py')
    table = '| Color | Control score | Crossbow draft score | Change |\n|---|---:|---:|---:|\n'
    for c,b in zip(result['cells'],controls):
        table += f"| {('Red','Blue')[c['side']]} | {b['score']:.2f} | {c['score']:.2f} | {100*(c['score']/b['score']-1):+.1f}% |\n"
    (PAIR / 'README.md').write_text('# Crossbowman draft-only follow-up\n\n'
        f"Engine **2026.9.22.2 / ffcedcd**. Source **{ir.digest(source)}**. Score gate **{'passed' if result['passed'] else 'failed'}**; this bundle itself does not select a league champion.\n\n"
        + table + f"\nMean score {result['score']:.2f} versus {result['control_score']:.2f}, {result['uplift_percent']:+.1f}%. "
        'Fort outcomes and deaths are diagnostics. Only draft priority changes; existing post-draft behavior is retained. '
        '40 games/color, one subject seat, exact roster/configuration and all ten VMs/replay hashes/source specs/XP/integer scores checked. '
        'The 80 control games come from the preceding study: this is a sequential follow-up, not independent confirmation. '
        'No universal hero ranking or late-draft/#1 claim. All failed mirrored alternatives remain in the sibling `balance20260922` bundle.\n\n'
        'Edit `policy.py`; `python3 convert.py compile --out <new-directory>` regenerates BASIC. '
        'Use `extract --source <file>` for reverse extraction, and `python3 verify.py` for offline pair/evidence verification.\n')
    h.write(PAIR / 'manifest.json', {'source_sha256': ir.digest(source), 'ir_sha256': ir.digest(p),
        'game_version': '2026.9.22.2', 'engine_commit': draft_only.build.COMMIT, 'binding': draft_only.BINDING,
        'games': 80, 'score_gate_passed': result['passed'], 'runtime_clean': clean,
        'artifacts': {str(f.relative_to(PAIR)):h.sha(f.read_bytes()) for f in sorted(PAIR.rglob('*')) if f.is_file()}})
    print(PAIR)


if __name__ == '__main__':
    main()
