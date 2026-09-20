"""Native tests of the complete coached controller and its preserved branches."""
from copy import deepcopy
import json
import subprocess
from prepare import CLEAN, STUDY, CRITICAL, write, digest, contracts
from test_policy_ir import obj, fixture
from hero_binding import class_ids

VM=CLEAN.parents[3]/'tmp/gota-ir/scenario-vm'
MEMORY=['gaActive','gaReady','gaNear','gaSpread','gaPhase','gaTethered',
        'gaEmergency','gaEntry','gaMoveX','gaMoveY','bestId']


def case(team=0,slot=0,tick=3000,x=60,y=50,alive=5):
    objects=[obj(1,kind=1,team=0,x=105,y=11,hp=400),
             obj(2,kind=1,team=1,x=11,y=105,hp=400,alive=0),
             obj(19,kind=4,team=1,x=51,y=73,hp=950)]
    for i,cls in enumerate(class_ids(team)):
        hero=obj(100+5*team+i,kind=2,team=team,x=x+i%2,y=y+i//2,
                 hp=300 if i<alive else 0,alive=int(i<alive))
        hero['objectClass']=cls;objects.append(hero)
    c=fixture(objects,selfId=100+team*5+slot,selfTeam=team,selfClass=class_ids(team)[slot],
              selfX=x+slot%2,selfY=y+slot//2,selfHp=300,selfMaxHp=400,worldTick=tick)
    c['returns']={'terrainWalkable':1,'walkTo':1,'attackTarget':1}
    return c


def run(source,cases,memory=MEMORY):
    fields=[contracts.ALIASES.get(x,x) for x in memory]
    p=subprocess.run([str(VM),str(source)],input=json.dumps({'decisions':cases,'memory':fields}),
                     text=True,capture_output=True)
    if p.returncode:raise RuntimeError(p.stderr+'\n'+p.stdout)
    rows=json.loads(p.stdout)
    for row in rows:
        row['memory']={name:row['memory'][field] for name,field in zip(memory,fields)}
    return rows


def main():
    rows=[];checks=[]
    for name in ('formation2400','formation3600','formation2400_weapon'):
        source=STUDY/'candidates'/name/'policy.bas'
        start=3600 if name=='formation3600' else 2400
        ready=case(tick=start);a=run(source,[ready])[0];rows.append(a)
        assert a['memory']['gaReady']==1 and a['memory']['gaPhase']==3
        assert a['memory']['bestId']==19,a
        unready=case(tick=start,alive=3);a=run(source,[unready])[0];rows.append(a)
        assert a['memory']['gaReady']==0 and a['memory']['bestId']==0,a
        tether=case(tick=start);tether['self']['selfX']=100;tether['objects'][3]['objectX']=100
        a=run(source,[tether])[0];rows.append(a)
        assert a['memory']['gaTethered']==1 and a['memory']['bestId']==0,a
        assert not any(x['command']=='attackTarget' for x in a['actions']),a
        for observed,expected in [(2,0),(3,1)]:
            dispersed=case(tick=start)
            for i in range(observed):dispersed['objects'].append(obj(105+i,kind=2,team=1,x=5+i*35,y=90,hp=200))
            a=run(source,[dispersed])[0];rows.append(a)
            assert a['memory']['gaSpread']==expected,a
        emergency=case(tick=start)
        emergency['objects'] += [obj(105+i,kind=2,team=1,x=90+i,y=25,hp=300) for i in range(2)]
        a=run(source,[emergency])[0];rows.append(a)
        assert a['memory']['gaEmergency']==1 and a['memory']['gaPhase']==4,a
        probe=case(tick=start,x=28,y=80)
        a=run(source,[probe])[0];rows.append(a)
        assert a['memory']['gaPhase']==2 and a['memory']['bestId']==0,a
        wave=deepcopy(probe);wave['objects'] += [obj(1000+i,team=0,x=29+i,y=81) for i in range(2)]
        a=run(source,[wave])[0];rows.append(a)
        assert a['memory']['gaPhase']==3 and a['memory']['bestId']==19,a
        for team in (0,1):
            for slot in range(5):
                c=case(team=team,slot=slot,tick=start)
                c['objects'] += [obj(3000+i,team=i%2,x=i%116,y=(i*7)%116) for i in range(240-len(c['objects']))]
                a=run(source,[c])[0];rows.append(a)
                if team==1 and name!='formation2400_weapon':
                    reference=run(CRITICAL/'policy.bas',[c],memory=[])[0]
                    assert a['actions']==reference['actions'],(name,slot)
        if name!='formation2400_weapon':
            early=case(tick=start-1)
            assert run(source,[early])[0]['actions']==run(CRITICAL/'policy.bas',[early],memory=[])[0]['actions']
        checks.append({'candidate':name,'ready_and_shared_structure_target':True,'three_not_ready':True,
            'tether_blocks_departure_attack':True,'two_seen_not_dispersion':True,
            'observed_dispersion':True,'critical_group_defense':True,'probe_and_wave_breach':True})
    assert max(r['instructions'] for r in rows)<=20000
    assert max(r['work'] for r in rows)<=50000
    proof={'passed':True,'checks':checks,'max_instructions':max(r['instructions'] for r in rows),
           'max_work':max(r['work'] for r in rows),'vm_sha256':digest(VM.read_bytes()),
           'scope':'Actual BASIC VM scenario behavior; not competitive win evidence.'}
    write(STUDY/'vm-proof.json',proof);print(json.dumps(proof,indent=2))


if __name__=='__main__':main()
