"""Freeze all tested IR pairs, feed results back into beliefs, retain failures."""
from pathlib import Path
import json
import pprint
import shutil
import build
from environment import h, ROOT, STUDY

PAIR = ROOT / 'examples/gods_of_the_arena/players/ir/forks/balance20260922'
HERE = Path(__file__).resolve().parent


def copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def main():
    result = h.read(STUDY / 'hosted/result.json')
    review = h.read(STUDY / 'review.json')
    assert result['complete'] and result['selected'] == review['selected']
    assert len(result['cells']) == 10 and all(len(c['rows']) == 40 for c in result['cells'])
    assert not PAIR.exists(), 'Preserve earlier captured pairs'
    PAIR.mkdir(parents=True)
    for name in ('control', 'ranger', 'crossbow', 'warlock', 'arcanist'):
        parent = build.PARENT if name == 'control' else STUDY / 'candidates' / name
        p = h.read(parent / 'policy.ir.json')
        original_ir = build.ir.digest(p)
        source = (parent / 'policy.bas').read_bytes()
        if name == 'control':
            build.configure_control()
            p['execution']['game_version'] = build.VERSION
        else:
            build.configure()
        ir = build.ir
        cells = [c for c in result['cells'] if c['name'] == name]
        clean = all(c['invalid'] == 0 for c in cells)
        comparison = next((c for c in result['comparisons'] if c['name'] == name), None)
        p['belief']['claims'] = {
            'CurrentRuntime': {'claim': 'Exact source completed 80 games on 2026.9.22.2, both colors, with all source specs, VM status, replay hashes, lifetime XP and integer scores audited.',
                'status': 'supported' if clean else 'contradicted', 'evidence': [{'artifact': '../evidence/result.json'}]},
            'FrozenScoreGate': {'claim': 'This executable meets the prospectively frozen >=10% aggregate score improvement and >=95% per-color preservation against deployed control.' if comparison else 'This executable is the fresh patched-engine comparison control; being retained does not establish superiority to all possible alternatives.',
                'status': ('supported' if comparison['passed'] else 'contradicted') if comparison else 'supported',
                'evidence': [{'artifact': '../evidence/review.json'}]},
            'Generalization': {'claim': 'Universal hero strength, late-draft performance, new opponent versions and leaderboard #1 remain unestablished.',
                'status': 'requires_review', 'evidence': [{'artifact': '../evidence/experiment.md'}]}}
        p['situation']['notes'] = ('Public patched-host observations only. Experiment uses one subject seat and nine fixed distinct teammates/opponents. '
            'Hero preference can fall back when unavailable; realized-pick splits are descriptive. '
            + ('Retained control uses global coordinates; mirrored alternatives are kept with their results.' if name == 'control' else 'Spatial decisions use team coordinates before rounding; geometry plus draft preference was evaluated jointly.'))
        p['update'] = {'revision': p['update']['revision'] + 1, 'parent': original_ir,
            'change': {'origin': 'User symmetry and hero-balance update; reflect completed current-engine evaluation without rewriting captured inputs',
                       'engine': build.COMMIT, 'selected': result['selected'] == name},
            'needs_review': ['belief/Generalization'], 'evidence': [{'artifact': '../evidence/experiment.md'}, {'artifact': '../evidence/review.json'}]}
        ir.refresh_grounding(p)
        assert ir.compile_policy(p).encode() == source
        assert ir.extract(source.decode(), p) == p
        out = PAIR / name
        out.mkdir()
        for filename, obj in [('policy.ir.json', p), ('extracted.ir.json', p), ('semantics.json', ir.grounded(p))]:
            h.write(out / filename, obj)
        (out / 'policy.py').write_text('POLICY = ' + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
        (out / 'policy.bas').write_bytes(source)
        h.write(out / 'manifest.json', {'variant': name, 'game_version': build.VERSION, 'engine_commit': build.COMMIT,
            'source_sha256': ir.digest(source), 'ir_sha256': ir.digest(p), 'binding': p['execution']['binding'],
            'source_preserved_exactly': True, 'selected': result['selected'] == name, 'runtime_clean': clean,
            'score_improved': comparison['passed'] if comparison else False})
    for name in ('review.json', 'fixtures.json', 'native-admission.json', 'native-plan.json',
                 'calibration-hosted.json', 'calibration-hosted-clean.json', 'baseline-practice.json', 'ranger-practice.json',
                 'bootstrap-proof.json', 'bootstrap-proof-v2.json', 'roster-preflight-pooled.json', 'ownership.json'):
        copy(STUDY / name, PAIR / 'evidence' / name)
    for name in ('plan.json', 'result.json'):
        copy(STUDY / 'hosted' / name, PAIR / 'evidence' / name)
    copy(ROOT / 'games/gods_of_the_arena/experiments/2026-09-22-balance-heroes.md', PAIR / 'evidence/experiment.md')
    for name in ('control-mirrors.log', 'mirrors-memory.log'):
        copy(STUDY / name, PAIR / 'evidence' / name)
    for p in STUDY.glob('*-v3.log'):
        copy(p, PAIR / 'evidence' / p.name)
    for name in ('ranger', 'crossbow', 'warlock', 'arcanist'):
        shutil.copytree(STUDY / 'candidates' / name, PAIR / 'captured/candidates' / name)
    shutil.copytree(STUDY / 'rejected-inputs', PAIR / 'captured/rejected-inputs')
    # Freeze the complete conversion toolchain; no dependency on the active repo.
    for p in HERE.glob('*.py'):
        copy(p, PAIR / 'tooling/balance20260922' / p.name)
    copy(HERE.parent / 'targets20260922/practiced.py', PAIR / 'tooling/targets20260922/practiced.py')
    copy(HERE.parent / 'week20260921/contracts.py', PAIR / 'tooling/week20260921/contracts.py')
    shutil.copytree(HERE.parent / 'week20260921/compiler', PAIR / 'tooling/week20260921/compiler', ignore=shutil.ignore_patterns('__pycache__'))
    for p in HERE.glob('*.nim'):
        copy(p, PAIR / 'evidence/instruments' / p.name)
    for p in [HERE.parent / 'targets20260922/practice.nim', HERE.parent / 'targets20260922/scenarios.nim', HERE.parent / 'week20260921/command_hash.nim']:
        copy(p, PAIR / 'evidence/instruments' / p.name)
    # Store references/hashes, not private API envelopes or duplicate large replays.
    h.write(PAIR / 'evidence/raw-inputs.json', {'root': str(STUDY),
        'files': {str(p.relative_to(STUDY)): h.sha(p.read_bytes()) for p in sorted(STUDY.rglob('*'))
                  if p.is_file() and p.suffix not in ('.log', '.tmp') and 'bin' not in p.parts and 'nimcache' not in p.parts
                  and 'draft-isolation' not in p.parts and 'crossbow_draft' not in p.parts
                  and p.name != 'terminal-requests.json'}})
    rows = '| Policy | Red score | Blue score | Aggregate change | Gate |\n|---|---:|---:|---:|---|\n'
    control = sum(c['score'] for c in review['cells'] if c['name'] == 'control') / 2
    for name in ('control', 'ranger', 'crossbow', 'warlock', 'arcanist'):
        cells = [c for c in review['cells'] if c['name'] == name]
        score = sum(c['score'] for c in cells) / 2
        comparison = next((c for c in result['comparisons'] if c['name'] == name), None)
        gate = 'control' if comparison is None else ('pass' if comparison['passed'] else 'fail')
        rows += f"| {name} | {cells[0]['score']:.2f} | {cells[1]['score']:.2f} | {(score/control-1)*100:+.1f}% | {gate} |\n"
    (PAIR / 'README.md').write_text('# Patched-engine hero comparison\n\n'
        f"Engine **{build.VERSION} / {build.COMMIT[:7]}**. Selected research reference: **{result['selected']}**. "
        'This bundle itself does not deploy a league version. Read deployment receipts for live selection.\n\n'
        + rows + '\n400 games, 40 per policy/color, one first-pick subject and nine frozen distinct players. '
        'All original sources are preserved. Mean integer XP score is primary; fort outcomes are diagnostics. '
        'Four-way selection and fixed rosters limit generalization. No universal hero tier, late-draft or #1 claim. '
        'Blue opposes relh; Jordan and Richard are allies there. Full picks/deaths/uncertainty and opposing-target scores: `evidence/review.json`.\n\n'
        'Each subfolder contains editable `policy.py`, generated BASIC, and exact extracted IR. '
        'Use `python3 convert.py <variant> compile --out <new-directory>` or `extract --source <file>`; '
        '`python3 verify.py` verifies every pair and the evidence hashes offline. '
        'Captured inputs stay under the original raw study path in `evidence/raw-inputs.json`.\n')
    copy(HERE / 'convert_pair.py', PAIR / 'convert.py')
    copy(HERE / 'verify_pair.py', PAIR / 'verify.py')
    h.write(PAIR / 'manifest.json', {'selected': result['selected'], 'game_version': build.VERSION, 'engine_commit': build.COMMIT,
        'games': 400, 'artifacts': {str(p.relative_to(PAIR)): h.sha(p.read_bytes()) for p in sorted(PAIR.rglob('*')) if p.is_file()}})
    print(PAIR)


if __name__ == '__main__':
    main()
