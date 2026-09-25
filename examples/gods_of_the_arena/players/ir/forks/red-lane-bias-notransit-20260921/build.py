"""Fork formation-adaptive-20260920 with H-RED-LANE-01; never patch generated BASIC.

Red opening evidence (cycle 02 hash-validated trajectory, seed 54): red spawns at ~(107,5); the
nearest friendly creep wave for slot 0 (spawn (110,9)) is the right lane (x~108, y increasing),
so slot 0 escorts it alone while slots 1-4 go left along the top; the caster transit then splits
2 more off -> 1/2/2. Blue's geometry yields 3/2 and wins. This fork biases the red wave choice
in the observe contract: when not retained, a candidate wave at x >= selfX (the right lane from
the red spawn) has red_lane_bias added to its squared distance, so red heroes group on the top
lane. Zero new globals. Variant notransit also disables the caster transit (transit_min_allies 99).
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
VARIANT = 'notransit' if 'notransit' in HERE.name else 'lane'
MIN_ALLIES = 99
LANE_BIAS = 4096
sha = lambda data: hashlib.sha256(data).hexdigest()
read = lambda path: json.loads(path.read_text())

OLD_GUARD = 'if defActive = 0 then\ntransitActive = 1\nend if\n'
NEW_GUARD = 'if defActive = 0 and mAllies >= param_transit_min_allies then\ntransitActive = 1\nend if\n'
OLD_WAVE = 'distance = dx * dx + dy * dy\nif distance < waveDistance or (distance = waveDistance and id < waveChosen) then\n'
NEW_WAVE = 'distance = dx * dx + dy * dy\nif selfTeam = 0 and objectX(index) >= selfX then\ndistance = distance + param_red_lane_bias\nend if\nif distance < waveDistance or (distance = waveDistance and id < waveChosen) then\n'


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
    assert obs.template.count(OLD_WAVE) == 4, obs.template.count(OLD_WAVE)
    lane_name = 'formation_profile_observe_red_lane_bias_v1'
    lane = replace(obs, template=obs.template.replace(OLD_WAVE, NEW_WAVE),
                   parameters=obs.parameters | {'red_lane_bias': (LANE_BIAS, 0, 65536)},
                   meaning=obs.meaning + ' H-RED-LANE-01: for red (selfTeam = 0), a non-retained candidate creep wave whose x >= selfX (the right lane from the red spawn) gets red_lane_bias added to its squared distance so red heroes converge on the top lane instead of a 1/2/2 opening. Blue unchanged. Hypothesis, not a validated gain: falsified if red still loses seeds 54/101/202 vs Richard v135 or regresses vs the parent.')
    CONTRACTS[lane_name] = lane
    contracts[lane_name] = {'template': lane.template, 'meaning': lane.meaning, 'parameters': {k: list(v) for k,v in lane.parameters.items()},
                            'reads': list(lane.reads), 'writes': list(lane.writes), 'actions': list(lane.actions), 'memory': list(lane.memory)}
    old_name = parent['skill']['transit_state']['operator']
    old = CONTRACTS[old_name]
    assert old.template.count(OLD_GUARD) == 1
    new_name = 'formation_profile_transit_state_gated_v1'
    t = old.template.replace(OLD_GUARD, NEW_GUARD, 1)
    new = replace(old, template=t,
                  parameters=old.parameters | {'transit_min_allies': (MIN_ALLIES, 0, 99)},
                  memory=old.memory,
                  meaning=old.meaning + ' H-RED-TRANSIT-01: the red caster pair (classes 7/8) only starts the centre transit while the previous tick\'s weighted nearby-ally count mAllies (attack-scan global: allied hero within 6 tiles = 3, creep = 1) is >= transit_min_allies, so slots 2-3 no longer walk alone to (58,56) into the enemy stack. mAllies is read one tick stale by design (zero new globals; parent sits at the 256 VM global cap). Variant off (99) disables the transit entirely as the mechanism control. Hypothesis, not a validated gain: falsified if red still loses seeds 54/101/202 vs Richard v135 with early deaths, or red regresses vs Alex g002 / Jordan v268 / the parent.')
    CONTRACTS[new_name] = new
    contracts[new_name] = {'template': new.template, 'meaning': new.meaning, 'parameters': {k: list(v) for k,v in new.parameters.items()},
                           'reads': list(new.reads), 'writes': list(new.writes), 'actions': list(new.actions), 'memory': list(new.memory)}
    p = deepcopy(parent)
    p['id'] = 'gota_formation3600_red_lane_' + VARIANT
    p['skill']['observe'] = {'operator': lane_name, 'parameters': {'red_lane_bias': LANE_BIAS}}
    if VARIANT == 'notransit':
        p['skill']['transit_state'] = {'operator': new_name, 'parameters': {'transit_min_allies': MIN_ALLIES}}
    p['belief']['claims']['RedLaneSplit'] = {
        'claim': 'H-RED-LANE-01: in red losses vs Richard v135 (local seed 54) and relh v159 (hosted 0-40) the red opening is a 1/2/2 dispersal; slots 2-3 (casters) transit alone to (58,56) at tick ~450-850 and die by ~950 against a 3-hero stack. Gating the transit on >=2 nearby allied heroes (or disabling it) is predicted to cut early red deaths. Falsifiers: red still loses seeds 54/101/202 vs Richard, or red regresses vs Alex g002v1 / Jordan v268 / parent.', 'status': 'untested',
        'evidence': [{'artifact': '.gota/cycles/20260920T2340Z-devin/local-richard/red-54.observer-slot2.jsonl'}, {'artifact': 'docs/reports/2026-09-21-devin-cycle-06/hosted-ab-summary.json'}]}
    p['update'].update(revision=p['update']['revision']+1, parent=digest(parent),
        change={'origin': 'Devin cycle 09 fork for Richard/relh red trigger', 'hypothesis': 'H-RED-LANE-01 ' + VARIANT + ' (red wave-choice bias %d; notransit also disables caster transit)' % LANE_BIAS,
                'layer': 'skill/strategy (transit_state) + belief', 'rule': 'R1 (+R_profile_transit)'},
        needs_review=['local red screen vs Richard/Alex/Jordan/parent', 'blue unchanged (rule is red-only) - verify hashes', 'hosted A/B vs relh v159'])
    refresh_grounding(p)
    source = compile_policy(p)
    assert extract(source, p) == p
    out = HERE/'bundle'
    import shutil
    if out.exists(): shutil.rmtree(out)
    bundle(p, out)
    for f in out.iterdir(): shutil.move(str(f), HERE/f.name)
    out.rmdir()
    (HERE/'policy.py').write_text('"""H-RED-LANE-01 fork of the adaptive formation3600 IR; untested until README says otherwise."""\nPOLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    (HERE/'contracts.json').write_text(json.dumps(contracts, indent=1, sort_keys=True))
    (HERE/'compiler.zip').write_bytes((PARENT/'compiler.zip').read_bytes())
    cm = dict(m); cm['source_sha256'] = sha(source.encode()); cm['contracts_sha256'] = sha((HERE/'contracts.json').read_bytes())
    cm['interpretation'] = 'Parent frozen compiler modules; contracts add formation_profile_observe_red_lane_bias_v1 (+transit gated) (template-level, no BASIC patch).'
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
