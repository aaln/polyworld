"""Build an isolated seven-layer fork; never patch generated BASIC."""
from pathlib import Path
import sys
from copy import deepcopy
import pprint
import re
from dataclasses import replace

ROOT = Path(__file__).resolve().parents[4]
CLEAN = ROOT.parent/'polyworld-gota-clean-20260916-r5'
IR = CLEAN/'examples/gods_of_the_arena/players/ir'
STUDY = ROOT/'tmp/gota-ir/formation-adaptive-20260920'
sys.path[:0] = [str(ROOT), str(IR)]
from policy_ir import read, write, digest, refresh_grounding, bundle, compile_policy, extract
from binding import CONTRACTS
from games.gods_of_the_arena.instruments.formation_adaptive import contracts


def main():
    fold='--fold' in sys.argv
    prune='--prune' in sys.argv
    candidate='profile_pruned' if prune else ('profile_fold' if fold else 'profile_switch')
    for name, original in contracts.POLICIES.items():
        assert compile_policy(original).encode() == (STUDY/'inputs'/name/'policy.bas').read_bytes(), name
    p = deepcopy(contracts.POLICIES['formation'])
    p['id'] = 'gota_formation3600_'+candidate+'_v1'
    p['skill']['observe'] = {'operator':'formation_profile_observe_v1','parameters':{}}
    p['skill']['fallback'] = {'operator':'formation_profile_route_v1','parameters':{}}
    for name in ('transit_state','tower_handoff'):
        p['skill'][name] = {'operator':'formation_profile_'+name+'_v1','parameters':{}}
    p['goal']['G_profile'] = {'preference':'Choose previously tested response components from public '
        'opening equipment profiles while preserving fort wins across Richard, Alex and Jordan. '
        'A profile is uncertain opponent-style evidence, never an oracle identity.','provenance':'authored'}
    p['strategy'].insert(2, {'id':'R_profile_transit','when':'always','skill':'transit_state','for':['G_profile']})
    p['strategy'].append({'id':'R_profile_tower','when':'always','skill':'tower_handoff','for':['G_profile']})
    for r in p['strategy']:
        if r['skill'] in ('observe','fallback'):r['for'].append('G_profile')
    p['situation']['notes'] += ' Public visible enemy inventory is six objectItemId slots. No opponent name, UUID, outcome, seed or hidden object is read. Modes0unknown,1boots+elixir,2boots,3dagger. Profiles share inventory with other policies; mixed/unrecognized evidence abstains.'
    p['belief']['claims']['ProfileSwitch'] = {'claim':'Coordinated hypothesis: distinguish early equipment profiles and select Alex-style historical defense, Jordan-style counterpressure, or Richard formation. Early red caster transit and tower handoff may preserve the tested Alex/Jordan red wins. Delayed classification, shared equipment and composition can defeat this hypothesis.','status':'untested','evidence':[{'artifact':str(STUDY/'detection/result.json')}]}
    # Compact long implementation-only storage names consistently across every
    # skill. Keep predicate variables unchanged; no action or guard is removed.
    templates='\n'.join(CONTRACTS[s['operator']].template for s in p['skill'].values())
    words=sorted(set(re.findall(r'\b(?:backdoor\w*|perimeter\w*|response\w*|observedObjectCount|defenseRefreshes|defenseDecisions)\b',templates)))
    aliases={word:'ap'+str(i) for i,word in enumerate(words)}
    aliases.update(transitDx='mDx',transitDy='mDy',transitObservedDefense='defActive',
                   distanceKind='buildingWeight',macroIndex='index',gaReady='waveCached')
    for skill in p['skill'].values():
        old=CONTRACTS[skill['operator']]
        name=skill['operator']+('_profile_pruned_v1' if prune else ('_profile_fold_v1' if fold else '_profile_storage_v1'))
        original=old.source(skill['parameters']) if fold else old.template
        if prune and skill['operator']=='formation_profile_observe_v1':
            original,ordinary=original.split('\nif gaActive = 0 then',1)
            a=contracts.formation.ALIASES
            lines=[f"{a['gaSx']} = {a['gaOx']} - selfX",f"{a['gaSy']} = {a['gaOy']} - selfY",
                   f"{a['gaSelfD']} = {a['gaSx']} * {a['gaSx']} + {a['gaSy']} * {a['gaSy']}"]
            for line in lines:
                assert original.count(line)==1,line
                original=re.sub(r'(?m)^ *'+re.escape(line)+r'\n','',original)
            token=f"if {a['gaSelfD']} <= 36 and {a['gaSelfD']} < {a['gaLocalD']} then"
            assert original.count(token)==1
            original=original.replace(token,'\n'.join(lines)+'\n'+token)
            original+='\nif gaActive = 0 then'+ordinary
        source=re.sub(r'\b\w+\b',lambda m:aliases.get(m[0],m[0]),original)
        if fold:
            source=source.replace('defI = 0\n  while defI < objectCount() and defI < 64',
                                  aliases['observedObjectCount']+' = objectCount()\n  defI = 0\n  while defI < '+aliases['observedObjectCount']+' and defI < 64')
            previous=None
            while previous!=source:
                previous=source
                source=re.sub(r'\b(\d+) \* (\d+)\b',lambda m:str(int(m[1])*int(m[2])) if int(m[1])*int(m[2])<2147483648 else m[0],source)
        if source == original:
            continue
        source='\n'.join(line.lstrip() for line in source.splitlines())
        CONTRACTS[name]=replace(old,template=source,parameters={} if fold else old.parameters,memory=tuple(aliases.get(v,v) for v in old.memory),
            meaning=old.meaning+' Storage-only alias map: '+str(aliases)+'.')
        skill['operator']=name
        if fold:skill['parameters']={}
    write(STUDY/'storage-aliases.json',aliases)
    p['update'].update(revision=p['update']['revision']+1,parent=digest(contracts.POLICIES['formation']),
        change={'origin':'User requests formation3600 fork beating Alex and Jordan with opponent detection',
                'inputs':str(STUDY/'inputs.json'),'experiment':'2026-09-20-formation-adaptive'},
        needs_review=['belief/ProfileSwitch','goal/G_profile'])
    refresh_grounding(p)
    d=STUDY/'candidates'/candidate;d.parent.mkdir(exist_ok=True)
    if not (d/'policy.bas').exists():bundle(p,d)
    assert compile_policy(p).encode()==(d/'policy.bas').read_bytes()
    assert extract((d/'policy.bas').read_text(),p)==p
    (d/'policy.py').write_text('"""Primary IR: observed-profile formation3600 fork, unvalidated."""\nPOLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    print('Built',digest((d/'policy.bas').read_bytes()),len((d/'policy.bas').read_bytes()),flush=True)


if __name__=='__main__':main()
