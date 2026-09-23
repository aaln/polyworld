"""Seal local evidence and reviewed IR without changing the tested BASIC bytes."""
import json
import pprint
import shutil
from pathlib import Path
import control_binding as b
from check import RAW, COMMIT, sha

ROOT = b.ROOT
AUDIT = ROOT / 'games/gods_of_the_arena/release-audits/2026-09-23-crowd-control'
PAIR = ROOT / 'examples/gods_of_the_arena/players/ir/forks/control20260923-local/control-legality'
read = lambda path: json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    assert not PAIR.exists() and not AUDIT.exists(), 'Preserve sealed evidence'
    practice = read(RAW / 'practice-comparison.json')
    native = read(RAW / 'native-comparison.json')
    assert practice['passed'] and native['passed']
    shutil.copytree(RAW / 'control-legality', PAIR, ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy2(b.HERE / 'control_binding.py', PAIR / 'tooling/control20260923/control_binding.py')
    b.configure()
    p = read(PAIR / 'policy.ir.json')
    previous = b.ir.digest(p)
    source = (PAIR / 'policy.bas').read_text()
    p['belief']['claims']['SilenceLegality'].update(status='supported', claim='104 matched status fixtures (208 executions) remove388silenced casts while preserving every other command and all120per-tick gameplay samples. Root permits healing/attacks/items; silence permits attacks/movement/potions; spells resume after expiry. Eight responsive native games pass replay/runtime checks; four paired score deltas are zero.')
    p['belief']['claims']['CompetitiveGain'].update(claim='No score improvement established: four paired local responsive matches have zero score delta. Fewer rejected casts are not additional XP. Current league remains source29f6d7e6; any score-changing successor requires separately frozen paired current-release controls.', evidence=[{'artifact': 'evidence/native-comparison.json'}])
    p['update'].update(revision=2, parent=previous, needs_review=['belief/CompetitiveGain'],
        change={'origin': 'Reflect complete local mechanism and native results; tested BASIC unchanged.', 'deployment_qualified': False},
        evidence=[{'artifact': 'evidence/practice-comparison.json'}, {'artifact': 'evidence/native-comparison.json'}])
    b.ir.refresh_grounding(p)
    assert b.ir.compile_policy(p) == source and b.ir.extract(source, p) == p
    for name, value in [('policy.ir.json', p), ('extracted.ir.json', p), ('semantics.json', b.ir.grounded(p))]:
        write(PAIR / name, value)
    (PAIR / 'policy.py').write_text('POLICY = ' + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
    for name in ['practice-comparison.json', 'native-comparison.json', 'native-result.json', 'native-plan-with-hashes.json', 'runtime-provenance.json', 'skill-difference.json']:
        write(PAIR / 'evidence' / name, read(RAW / name))
    (PAIR / 'verify.py').write_text('''from pathlib import Path
import hashlib,json,runpy,sys
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'tooling/control20260923'))
import control_binding as b
b.configure();ir=b.ir
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(P/'manifest.json');p=read(P/'policy.ir.json');s=(P/'policy.bas').read_text()
assert runpy.run_path(str(P/'policy.py'))['POLICY']==p
assert ir.compile_policy(p)==s and ir.extract(s,p)==p
assert read(P/'extracted.ir.json')==p and read(P/'semantics.json')==ir.grounded(p)
assert ir.digest(p)==m['ir_sha256'] and sha(P/'policy.bas')==m['source_sha256']
for path,digest in m['artifacts'].items():assert sha(P/path)==digest,path
assert read(P/'evidence/practice-comparison.json')['passed']
assert read(P/'evidence/native-comparison.json')['passed']
assert not m['deployment_qualified'] and not m['hosted_complete']
print(json.dumps({'verified':True,'source_sha256':m['source_sha256'],'ir_sha256':m['ir_sha256'],'deployment_qualified':False}))
''')
    manifest = read(PAIR / 'manifest.json')
    manifest.update(ir_sha256=b.ir.digest(p), local_validated=True, reviewed_ir_preserves_tested_source=True,
                    score_gate_passed=None, deployment_qualified=False,
                    artifacts={str(f.relative_to(PAIR)): sha(f) for f in sorted(PAIR.rglob('*')) if f.is_file() and f.name != 'manifest.json' and '__pycache__' not in f.parts})
    write(PAIR / 'manifest.json', manifest)
    AUDIT.mkdir(parents=True)
    for name in ['release.json', 'checks.json', 'game-config.json', 'practice-comparison.json', 'native-comparison.json', 'native-result.json', 'native-plan-with-hashes.json', 'skill-difference.json', 'runtime-provenance.json']:
        write(AUDIT / name, read(RAW / name))
    shutil.copy2(RAW / 'request.txt', AUDIT / 'request.txt')
    for f in RAW.glob('test_gota_*-run.log'):
        (AUDIT / 'tests').mkdir(exist_ok=True)
        shutil.copy2(f, AUDIT / 'tests' / f.name)
    live = read(RAW / 'live-readback.json')
    live['champions'] = {k: {field: v[field] for field in ['id', 'status', 'substatus', 'is_champion']} |
                         {'policy_version_id': v['policy_version']['id']} for k, v in live['champions'].items()}
    write(AUDIT / 'live-readback.json', live)
    write(AUDIT / 'input-manifest.json', {
        'raw_root': str(RAW), 'engine_commit': COMMIT,
        'files': {str(f.relative_to(RAW)): sha(f) for f in sorted(RAW.rglob('*'))
                  if f.is_file() and 'deps' not in f.relative_to(RAW).parts and 'bin' not in f.relative_to(RAW).parts and '__pycache__' not in f.parts},
        'scope': 'Original release/league captures, frozen initial IR, corrected fixture history, all commands/gameplay traces and eight complete native replays retained privately. No new hosted requests.'})
    print(json.dumps({'pair': str(PAIR.relative_to(ROOT)), 'source_sha256': manifest['source_sha256'], 'ir_sha256': manifest['ir_sha256']}))


if __name__ == '__main__':
    main()
