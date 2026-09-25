"""Fork formation-adaptive-20260920 with H-RED-DEFREL-01; never patch generated BASIC.

Observer evidence (cycle 09 red-54 loss vs Richard v135, slot-0 view): our red heroes carry no
attack target for 80-85% of visible ticks and target enemy structures ~95 ticks each, while in
the blue-54 win the same policy has no target 55% of ticks and hits structures 900-1100 ticks
per hero. The observe contract releases shared defense (defActive/defUntil) when a hero is
> 28 tiles from home only for selfTeam = 1 (blue); red keeps defActive, so R2 runs its 40-object
degraded branch and R4 holds formation goals. This fork applies the same release to red.
Zero new globals, parameter-free template change.
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
VARIANT = 'defrel'
sha = lambda data: hashlib.sha256(data).hexdigest()
read = lambda path: json.loads(path.read_text())

OLD_REL = 'if selfTeam = 1 then\ndefDx = selfX - defHomeX\ndefDy = selfY - defHomeY\nif defDx * defDx + defDy * defDy > 28 * 28 and adMode <> 1 and worldTick >= criticalUntil then\n'
NEW_REL = 'if selfTeam = 1 or selfTeam = 0 then\ndefDx = selfX - defHomeX\ndefDy = selfY - defHomeY\nif defDx * defDx + defDy * defDy > 28 * 28 and adMode <> 1 and worldTick >= criticalUntil then\n'


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

    obs_name = parent['skill']['observe']['operator']
    obs = CONTRACTS[obs_name]
    assert obs.template.count(OLD_REL) == 1, obs.template.count(OLD_REL)
    lane_name = 'formation_profile_observe_red_def_release_v1'
    lane = replace(obs, template=obs.template.replace(OLD_REL, NEW_REL, 1),
                   parameters=obs.parameters,
                   meaning=obs.meaning + ' H-RED-DEFREL-01: the far-from-home (> 28 tiles) shared-defense release that previously applied only to blue now also applies to red, so red heroes far from their fort leave defActive and return to lane/push control instead of holding formation goals without an attack target. Hypothesis, not a validated gain: falsified if red still loses seeds 54/101/202 vs Richard v135 or blue/red regress vs the parent.')
    CONTRACTS[lane_name] = lane
    contracts[lane_name] = {'template': lane.template, 'meaning': lane.meaning, 'parameters': {k: list(v) for k,v in lane.parameters.items()},
                            'reads': list(lane.reads), 'writes': list(lane.writes), 'actions': list(lane.actions), 'memory': list(lane.memory)}
    p = deepcopy(parent)
    p['id'] = 'gota_formation3600_red_' + VARIANT
    p['skill']['observe'] = {'operator': lane_name, 'parameters': {}}
    p['belief']['claims']['RedDefenseStuck'] = {
        'claim': 'H-RED-DEFREL-01: in the red-54 loss vs Richard v135 our red heroes have no attack target 80-85% of visible ticks and hit structures ~95 ticks/hero, vs 55% / 900-1100 ticks in the blue-54 win; the observe rule releases shared defense far from home only for blue. Applying the release to red is predicted to raise red basic hits/structure pressure and delay/avoid the ~6000-tick collapse. Falsifiers: red still 0-3 vs Richard, or regression vs parent on either colour.', 'status': 'untested',
        'evidence': [{'artifact': 'docs/reports/2026-09-21-devin-cycle-10/target-stats.md'}]}
    p['update'].update(revision=p['update']['revision']+1, parent=digest(parent),
        change={'origin': 'Devin cycle 10 fork for Richard/relh red trigger', 'hypothesis': 'H-RED-DEFREL-01 (blue far-from-home defense release applied to red, zero new globals)',
                'layer': 'skill/strategy (transit_state) + belief', 'rule': 'R1 observe (defense release)'},
        needs_review=['local red screen vs Richard/Alex/Jordan/parent', 'blue hash-identical to parent (change is red-only)', 'hosted A/B vs relh v159'])
    refresh_grounding(p)
    source = compile_policy(p)
    assert extract(source, p) == p
    out = HERE/'bundle'
    import shutil
    if out.exists(): shutil.rmtree(out)
    bundle(p, out)
    for f in out.iterdir(): shutil.move(str(f), HERE/f.name)
    out.rmdir()
    (HERE/'policy.py').write_text('"""H-RED-DEFREL-01 fork of the adaptive formation3600 IR; untested until README says otherwise."""\nPOLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    (HERE/'contracts.json').write_text(json.dumps(contracts, indent=1, sort_keys=True))
    (HERE/'compiler.zip').write_bytes((PARENT/'compiler.zip').read_bytes())
    cm = dict(m); cm['source_sha256'] = sha(source.encode()); cm['contracts_sha256'] = sha((HERE/'contracts.json').read_bytes())
    cm['interpretation'] = 'Parent frozen compiler modules; contracts add formation_profile_observe_red_def_release_v1 (template-level, no BASIC patch).'
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
