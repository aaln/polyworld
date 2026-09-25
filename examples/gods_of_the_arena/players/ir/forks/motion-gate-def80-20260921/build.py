"""H-MOTION-GATE-01: parameter-only fork of the adaptive formation3600 IR.

The combat controller (rule R2, richard_formation_combat_v1) skips its whole
motion/threat scan when objectCount() exceeds motion_object_limit (80), or
defense_motion_limit (40) during shared defense. Hosted observer trajectories
show 65-94 objects around team fights, so kiting/threat tracking is disabled
exactly then. This fork raises the limits within the contract's declared
ranges; no template change, frozen parent compiler, zero new globals.
"""
import hashlib, json, pprint, runpy, sys, tempfile, zipfile
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'formation-adaptive-20260920'
VARIANT = 'mol120' if 'mol120' in HERE.name else 'def80'
LIMITS = {'def80': {'defense_motion_limit': 80}, 'mol120': {'defense_motion_limit': 80, 'motion_object_limit': 120}}[VARIANT]

def sha(b): return hashlib.sha256(b).hexdigest()
def read(p): return json.loads(Path(p).read_text())

def main():
    m = read(PARENT/'compiler-manifest.json')
    assert sha((PARENT/'compiler.zip').read_bytes()) == m['compiler_zip_sha256']
    tmp = tempfile.mkdtemp(prefix='motion-gate-ir-')
    with zipfile.ZipFile(PARENT/'compiler.zip') as z:
        z.extractall(tmp)
    sys.path.insert(0, str(Path(tmp)/'examples/gods_of_the_arena/players/ir'))
    from binding import CONTRACTS, Contract
    contracts = read(PARENT/'contracts.json')
    for name, fields in contracts.items():
        f = dict(fields)
        for key in ('reads','writes','actions','memory'):
            f[key] = tuple(f[key])
        f['parameters'] = {k: tuple(v) for k,v in f['parameters'].items()}
        CONTRACTS[name] = Contract(**f)
    from policy_ir import compile_policy, extract, digest, bundle, refresh_grounding
    parent = runpy.run_path(str(PARENT/'policy.py'))['POLICY']
    assert compile_policy(parent).encode() == (PARENT/'policy.bas').read_bytes()
    p = deepcopy(parent)
    p['id'] = 'gota_formation3600_motion_gate_' + VARIANT
    p['skill']['attack'] = {'operator': parent['skill']['attack']['operator'],
                            'parameters': dict(parent['skill']['attack']['parameters']) | LIMITS}
    p['belief']['claims']['MotionGateSkipsTeamFights'] = {
        'claim': 'H-MOTION-GATE-01: R2 skips the threat/kite scan above motion_object_limit (80) or defense_motion_limit (40 during '
                 'shared defense). Hosted relh v159 observer trajectories count 65-94 objects around ticks 1000-2400, so the '
                 'controller degrades to plain attackTarget exactly in team fights. Raising the limits (%s) is predicted to '
                 'restore kiting in fights; falsifiers: VM instruction limit (20,000) exceeded / INVALID games, or red/blue '
                 'regression vs Richard v135 or the parent.' % LIMITS, 'status': 'untested',
        'evidence': [{'artifact': 'docs/reports/2026-09-21-devin-cycle-06/hosted-ab-summary.json'}]}
    p['update'].update(revision=p['update']['revision']+1, parent=digest(parent),
        change={'origin': 'Devin cycle 08', 'hypothesis': 'H-MOTION-GATE-01 ' + VARIANT, 'layer': 'skill (attack) parameters', 'rule': 'R2'},
        needs_review=['local screen vs Richard/parent both colours', 'max instructions < 20000, 0 INVALID'])
    refresh_grounding(p)
    source = compile_policy(p)
    assert extract(source, p) == p
    out = HERE/'bundle'
    import shutil
    if out.exists(): shutil.rmtree(out)
    bundle(p, out)
    for f in out.iterdir(): shutil.move(str(f), HERE/f.name)
    out.rmdir()
    (HERE/'policy.py').write_text('"""H-MOTION-GATE-01 fork of the adaptive formation3600 IR; untested until README says otherwise."""\nPOLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    (HERE/'contracts.json').write_text(json.dumps(contracts, indent=1, sort_keys=True))
    (HERE/'compiler.zip').write_bytes((PARENT/'compiler.zip').read_bytes())
    cm = dict(m); cm['source_sha256'] = sha(source.encode()); cm['contracts_sha256'] = sha((HERE/'contracts.json').read_bytes())
    cm['interpretation'] = 'Parent frozen compiler modules and contracts; parameter-only change (%s).' % LIMITS
    (HERE/'compiler-manifest.json').write_text(json.dumps(cm, indent=1))
    (HERE/'verify.py').write_text((PARENT/'verify.py').read_text())
    manifest = read(HERE/'manifest.json')
    manifest['artifacts'] = {str(path.relative_to(HERE)): sha(path.read_bytes())
                             for path in sorted(HERE.rglob('*')) if path.is_file() and path.name != 'manifest.json'}
    (HERE/'manifest.json').write_text(json.dumps(manifest, indent=1))
    print(json.dumps({'variant': VARIANT, 'source_sha256': sha(source.encode()), 'policy_sha256': digest(p), 'parent_source': sha((PARENT/'policy.bas').read_bytes()),
                      'bytes': len(source), 'parent_bytes': len((PARENT/'policy.bas').read_bytes())}))

if __name__ == '__main__':
    main()
