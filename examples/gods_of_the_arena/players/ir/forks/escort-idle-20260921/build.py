"""Fork formation-adaptive-20260920 with H-ESCORT-IDLE-01; never patch generated BASIC.

Command-stream evidence (cycle 11, red-54 loss vs Richard v135, replay_command_stream_v1): our five
heroes issue walkTo on 77-82% of their ticks and attackTarget on ~18%; Richard's issue attackTarget on
>= 1 command/tick from tick ~450. Engine acquireRadius() returns 0 for a hero that hasMoveTarget and is
not attackMoving, so a hero escorting a wave with walkTo every tick never auto-acquires anything in
range; it attacks only when R2 explicitly targets. applyAttackMove clears the same target fields as
applyWalkTo, so replacing the route contract's escort walkTo(moveX, moveY) with attackMove(moveX, moveY)
keeps arbitration identical but lets escorting heroes engage enemies they pass (melee 8 tiles / ranged
attack range). Both colours. Zero new globals, parameter-free template change.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import pprint
import runpy
import sys
import tempfile
import zipfile
from dataclasses import replace

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent/'formation-adaptive-20260920'
VARIANT = 'escidle'
sha = lambda data: hashlib.sha256(data).hexdigest()
read = lambda path: json.loads(path.read_text())

OLD_REL = 'moveAccepted = walkTo(moveX, moveY)\nif moveAccepted = 0 then\nescortId = 0\nmoveAccepted = walkTo(64, 64)\nend if\n'
NEW_REL = 'ax = selfX - moveX\nay = selfY - moveY\nif ax < 0 then\nax = 0 - ax\nend if\nif ay < 0 then\nay = 0 - ay\nend if\nif ax > 1 or ay > 1 then\nmoveAccepted = walkTo(moveX, moveY)\nif moveAccepted = 0 then\nescortId = 0\nmoveAccepted = walkTo(64, 64)\nend if\nelse\nmoveAccepted = 1\nend if\n'


def main():
    m = read(PARENT/'compiler-manifest.json')
    assert sha((PARENT/'compiler.zip').read_bytes()) == m['compiler_zip_sha256']
    tmp = tempfile.mkdtemp(prefix='red-transit-ir-')
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
    from policy_ir import compile_policy, extract, digest, grounded, bundle, refresh_grounding
    parent = runpy.run_path(str(PARENT/'policy.py'))['POLICY']
    assert compile_policy(parent).encode() == (PARENT/'policy.bas').read_bytes()

    obs_name = parent['skill']['fallback']['operator']
    obs = CONTRACTS[obs_name]
    assert obs.template.count(OLD_REL) == 2, obs.template.count(OLD_REL)
    lane_name = 'formation_profile_route_escort_idle_v1'
    lane = replace(obs, template=obs.template.replace(OLD_REL, NEW_REL), 
                   parameters=obs.parameters,
                   meaning=obs.meaning + ' H-ESCORT-IDLE-01: the escort/route destination is issued with attackMove instead of walkTo so a hero following its wave auto-acquires enemies within melee attack-move range (8 tiles) or its ranged attack range; walkTo suppresses acquisition entirely (acquireRadius = 0 while moving). Cycle 11 showed a per-tick attackMove reissue clears the acquired target before any hit (red trajectory identical to parent, blue regressed); this variant issues the command only on branch entry and every 48 ticks (>= one full attack period of every class, max 36) so acquisition -> swing -> hit can complete. Hypothesis, not a validated gain: falsified if red still loses seeds 54/101/202 vs Richard v135 with no basic-hit increase, or blue/red regress vs the parent.')
    CONTRACTS[lane_name] = lane
    contracts[lane_name] = {'template': lane.template, 'meaning': lane.meaning, 'parameters': {k: list(v) for k,v in lane.parameters.items()},
                            'reads': list(lane.reads), 'writes': list(lane.writes), 'actions': list(lane.actions), 'memory': list(lane.memory)}
    p = deepcopy(parent)
    p['id'] = 'gota_formation3600_red_' + VARIANT
    p['skill']['fallback'] = {'operator': lane_name, 'parameters': dict(parent['skill']['fallback']['parameters'])}
    p['belief']['claims']['EscortNeverAcquires'] = {
        'claim': 'H-ESCORT-IDLE-01: in the red-54 loss vs Richard v135 our heroes issue walkTo 77-82% of ticks and attackTarget ~18%, slot 0 issues zero attacks for ticks 0-900 while escorting; Richard issues >=1 attackTarget per tick from ~450 and out-farms us 45-133 vs 7-30 basic hits. Engine: walking heroes never auto-acquire (acquireRadius 0), attack-moving heroes do. Predicted: escorting heroes gain basic hits/XP on both colours, red survives past the ~5900-tick collapse. Falsifiers: red still 0-3 vs Richard with no basic-hit increase, or regression vs parent on either colour, or instruction headroom < 1000.', 'status': 'untested',
        'evidence': [{'artifact': 'docs/reports/2026-09-21-devin-cycle-11/command-stream-red-54.md'}]}
    p['update'].update(revision=p['update']['revision']+1, parent=digest(parent),
        change={'origin': 'Devin cycle 13 fork for Richard/relh trigger (farm-rate mechanism)', 'hypothesis': 'H-ESCORT-IDLE-01 (route escort: skip the per-tick walkTo once within 1 tile of the escort point so hasMoveTarget clears and the engine idle acquisition (melee 2.5 tiles / ranged attack range) can attack; zero new globals)',
                'layer': 'skill/execution (fallback route) + belief', 'rule': 'R4 route escort'},
        needs_review=['local red screen vs Richard/Alex/Jordan/parent', 'blue non-regression vs Richard/parent (change applies to both colours)', 'hosted A/B vs relh v159'])
    refresh_grounding(p)
    source = compile_policy(p)
    assert extract(source, p) == p
    out = HERE/'bundle'
    import shutil
    if out.exists(): shutil.rmtree(out)
    bundle(p, out)
    for f in out.iterdir(): shutil.move(str(f), HERE/f.name)
    out.rmdir()
    (HERE/'policy.py').write_text('"""H-ESCORT-IDLE-01 fork of the adaptive formation3600 IR; untested until README says otherwise."""\nPOLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    (HERE/'contracts.json').write_text(json.dumps(contracts, indent=1, sort_keys=True))
    (HERE/'compiler.zip').write_bytes((PARENT/'compiler.zip').read_bytes())
    cm = dict(m); cm['source_sha256'] = sha(source.encode()); cm['contracts_sha256'] = sha((HERE/'contracts.json').read_bytes())
    cm['interpretation'] = 'Parent frozen compiler modules; contracts add formation_profile_route_escort_idle_v1 (template-level, no BASIC patch).'
    (HERE/'compiler-manifest.json').write_text(json.dumps(cm, indent=1))
    (HERE/'verify.py').write_text((PARENT/'verify.py').read_text())
    manifest = read(HERE/'manifest.json')
    manifest['artifacts'] = {str(path.relative_to(HERE)): sha(path.read_bytes())
                             for path in sorted(HERE.rglob('*')) if path.is_file() and path.name != 'manifest.json'}
    (HERE/'manifest.json').write_text(json.dumps(manifest, indent=1))
    print(json.dumps({'source_sha256': sha(source.encode()), 'policy_sha256': digest(p), 'parent_source': sha((PARENT/'policy.bas').read_bytes()),
                      'bytes': len(source), 'parent_bytes': len((PARENT/'policy.bas').read_bytes())}))


if __name__ == '__main__':
    main()
