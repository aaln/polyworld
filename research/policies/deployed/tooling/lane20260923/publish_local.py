"""Save the practiced pair while its independent hosted comparison is pending."""
import hashlib
import json
from pathlib import Path
import pprint
import shutil
import subprocess
import sys

import lane_binding as b

ROOT = b.ROOT
STUDY = ROOT.parent / 'polyworld/tmp/gota-lane-recovery-20260923'
OUT = ROOT / 'examples/gods_of_the_arena/players/ir/forks/lane-recovery20260923-local'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2) + '\n')


def main():
    assert not OUT.exists(), 'Preserve sealed evidence'
    local = read(STUDY / 'local-summary.json')
    assert local['passed'] and read(STUDY / 'native-result.json')['passed']
    src = STUDY / 'lane-recovery'
    pair = OUT / 'lane-recovery'
    shutil.copytree(src, pair, ignore=shutil.ignore_patterns('__pycache__'))
    evidence = pair / 'evidence'
    for name in ['local-summary.json', 'native-plan.json', 'native-result.json',
                 'runtime-provenance.json', 'conversion-proof.json',
                 'practice-provenance.json', 'coaching-episode-binding.json',
                 'prospective-experiment.md', 'start.json', 'skill-difference.json',
                 'baseline-practice.json']:
        shutil.copy2(STUDY / name, evidence / name)
    for label in ['practice', 'openings', 'buyback', 'portals', 'scenarios']:
        shutil.copy2(STUDY / f'lane-recovery-{label}.json', evidence / f'{label}.json')
    shutil.copytree(STUDY / 'fixture-expectations-r1', OUT / 'fixture-expectations-r1')
    shutil.copy2(STUDY / 'trial/plan.json', evidence / 'hosted-plan.json')
    write(evidence / 'hosted-preparation.json', {
        'games': 320, 'submitted': 0, 'status': 'prepared_awaiting_budget',
        'inert_policy_version': read(STUDY / 'uploads/lane-recovery/version.json'),
        'dry_run_requests': {str(p.relative_to(STUDY)): read(p)
                             for p in sorted((STUDY / 'trial').glob('*/*/request.json'))}})
    write(evidence / 'native-artifact-index.json', {
        'raw_root': str(STUDY), 'artifacts': {
            str(p.relative_to(STUDY)): sha(p)
            for p in sorted((STUDY / 'native').rglob('*')) if p.is_file()}})
    b.configure()
    ir = b.ir
    policy = read(src / 'policy.ir.json')
    initial = ir.digest(policy)
    policy['belief']['claims']['RecoveryMechanism'].update(
        status='supported',
        claim='All 92 actual-tick recovery fixtures, 100 opening checks, 180 buyback checks, '
              '84 portal checks and 126 broad checks pass; 16 complete native games pass. '
              'Druid heals 135 to 297 of 466 HP and resumes advance without base walks on '
              'both colors, including a three-second cooldown. Affordable missing core gear '
              'preserves shopping; unavailable healing and an expired twelve-second hold '
              'preserve escape. Potions that cannot reach the recovery threshold fall back '
              'after their effect is exhausted. Native games validate runtime, not rival strength.',
        evidence=[{'artifact': 'evidence/practice.json'}, {'artifact': 'evidence/local-summary.json'},
                  {'artifact': 'evidence/native-result.json'}])
    policy['update'] = {
        'revision': 2, 'parent': initial,
        'change': {'origin': 'Validated local behavior reflected into semantic IR; generated BASIC unchanged.'},
        'needs_review': ['belief/CompetitiveGain'],
        'evidence': [{'artifact': 'evidence/local-summary.json'}, {'artifact': 'evidence/hosted-plan.json'}]}
    ir.refresh_grounding(policy)
    source = (src / 'policy.bas').read_text()
    assert ir.compile_policy(policy) == source and ir.extract(source, policy) == policy
    for name, value in [('policy.ir.json', policy), ('extracted.ir.json', policy),
                        ('semantics.json', ir.grounded(policy))]:
        write(pair / name, value)
    (pair / 'policy.py').write_text('POLICY = ' + pprint.pformat(policy, width=110, sort_dicts=False) + '\n')
    write(evidence / 'initial-ir.json', read(src / 'policy.ir.json'))
    verifier = '''from pathlib import Path
import hashlib,json,sys
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'tooling/lane20260923'))
import lane_binding as b
b.configure();ir=b.ir
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(P/'manifest.json');p=read(P/'policy.ir.json');s=(P/'policy.bas').read_text()
assert ir.compile_policy(p)==s and ir.extract(s,p)==p
assert ir.digest(p)==m['ir_sha256'] and sha(P/'policy.bas')==m['source_sha256']
for path,digest in m['artifacts'].items():assert sha(P/path)==digest,path
for name in ['practice','openings','buyback','portals']:assert all(r['passed'] for r in read(P/'evidence'/(name+'.json'))['rows'])
assert read(P/'evidence/scenarios.json')['passed'] and read(P/'evidence/native-result.json')['passed']
print(json.dumps({'verified':True,'source_sha256':m['source_sha256'],'ir_sha256':m['ir_sha256'],'competitive_validation':'pending'}))
'''
    (pair / 'verify.py').write_text(verifier)
    manifest = read(src / 'manifest.json')
    manifest.update(ir_sha256=ir.digest(policy), local_validated=True,
                    hosted_complete=False, deployment_qualified=False)
    manifest['artifacts'] = {str(p.relative_to(pair)): sha(p) for p in pair.rglob('*')
                             if p.is_file() and p.name != 'manifest.json' and '__pycache__' not in p.parts}
    write(pair / 'manifest.json', manifest)
    subprocess.run([sys.executable, str(pair / 'verify.py')], check=True)
    captured = read(evidence / 'session-input-manifest.json')
    for name, metadata in captured['files'].items():
        assert sha(Path(captured['session']) / name) == metadata['sha256']
    write(OUT / 'summary.json', {
        'local': local, 'source_sha256': manifest['source_sha256'],
        'ir_sha256': manifest['ir_sha256'], 'hosted_complete': False,
        'deployment_qualified': False, 'original_session_inputs_unchanged': True})
    print(OUT)


if __name__ == '__main__':
    main()
