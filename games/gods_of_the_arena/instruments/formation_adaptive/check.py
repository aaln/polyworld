"""Real VM tests of observable profile selection and component boundaries."""
from copy import deepcopy
import json
import subprocess
import sys
from build import STUDY, ROOT, read, write, digest
from test_policy_ir import obj, fixture
from hero_binding import class_ids

NAME='profile_pruned' if '--prune' in sys.argv else ('profile_fold' if '--fold' in sys.argv else 'profile_switch')
SOURCE=STUDY/'candidates'/NAME/'policy.bas'
VM=STUDY/'fixture-vm'


def case(team=1,slot=0,tick=960,items=(),enemies=2):
    objects=[obj(1,kind=1,team=0,x=105,y=11,hp=400),obj(2,kind=1,team=1,x=11,y=105,hp=400),
             obj(25,kind=4,team=team,x=60,y=50,hp=1950)]
    for i,cls in enumerate(class_ids(team)):
        o=obj(100+team*5+i,kind=2,team=team,x=60+i,y=50,hp=300);o['objectClass']=cls;objects.append(o)
    for i in range(enemies):
        o=obj(100+(1-team)*5+i,kind=2,team=1-team,x=64+i,y=52,hp=300)
        o.update(objectClass=class_ids(1-team)[i],items=list(items)+[0]*(6-len(items)));objects.append(o)
    c=fixture(objects,selfId=100+team*5+slot,selfTeam=team,selfClass=class_ids(team)[slot],selfX=60+slot,selfY=50,
        selfHp=300,selfMaxHp=400,selfGold=150,selfAttackRange=360000,selfAttackDamage=30,selfAttackCooldown=5,
        selfAttacksLanded=20,worldTick=tick)
    c['returns']={'terrainWalkable':1,'walkTo':1,'attackTarget':1}
    return c


def run(source,decisions,memory=('adMode','gaActive','bestId','defActive','criticalUntil')):
    p=subprocess.run([str(VM),str(source)],input=json.dumps({'decisions':decisions,'memory':list(memory)}),
        capture_output=True,text=True)
    if p.returncode:raise ValueError(p.stderr)
    return json.loads(p.stdout)


def main():
    rows=[];checks=[]
    for team in (0,1):
        for slot in range(5):
            for items,mode in [((8,2),1),((8,),2),((11,),3),((),0)]:
                c=case(team,slot,items=items)
                a=run(SOURCE,[c])[0];rows.append(a);assert a['memory']['adMode']==mode
                late=deepcopy(c);late['self']['worldTick']=6000
                a=run(SOURCE,[c,late])[-1];rows.append(a)
                assert a['memory']['adMode']==mode
                assert a['memory']['gaActive']==int(team==0 and mode in (0,3))
                if team==1:
                    ref={1:'legacy',2:'jordan',3:'formation',0:'formation'}[mode]
                    old=run(STUDY/'inputs'/ref/'policy.bas',[c,late],())[1]
                    assert a['actions']==old['actions'],(slot,mode,a['actions'],old['actions'])
    c=case(items=(8,),enemies=1)
    sequence=[deepcopy(c) for _ in range(4)]
    for i,f in enumerate(sequence):f['self']['worldTick']=960+i*24
    assert all(x['memory']['adMode']==0 for x in run(SOURCE,sequence))
    for variant in ('mixed','dead','late','extra_item'):
        c=case(items=(8,2))
        if variant=='mixed':c['objects'][-1]['items']=[8,0,0,0,0,0]
        if variant=='dead':
            for o in c['objects'][-2:]:o.update(objectHp=0,objectAlive=0)
        if variant=='late':c['self']['worldTick']=1824
        if variant=='extra_item':
            for o in c['objects'][-2:]:o['items']=[8,2,11,0,0,0]
        a=run(SOURCE,[c])[0];rows.append(a);assert a['memory']['adMode']==0,variant
    # Sampling skips at non24 ticks; later enemy absence or new purchases do not
    # silently replace a latched episode profile.
    c=case(items=(8,2));skip=deepcopy(c);skip['self']['worldTick']=961
    assert run(SOURCE,[skip])[0]['memory']['adMode']==0
    later=case(tick=984,items=(11,));assert run(SOURCE,[c,later])[-1]['memory']['adMode']==1
    for team in (0,1):
        for slot in range(5):
            for total in (64,128,240):
                c=case(team,slot,items=(11,))
                c['objects'] += [obj(3000+i,kind=3,team=i%2,x=i%116,y=i*7%116) for i in range(total-len(c['objects']))]
                early=run(SOURCE,[c])[0];rows.append(early)
                late=deepcopy(c);late['self']['worldTick']=6000
                rows.append(run(SOURCE,[c,late])[-1])
    proof={'passed':True,'checks':['all ten fixed classes select intended profile','single hero repeated frames cannot vote twice',
        'mixed,dead,late,extra-item evidence abstains','latched profile persists','blue representative commands equal exact specialist branches',
        'late red formation guarded by unknown/dagger profile','dense budget and hard global limits'],
        'max_instructions':max(r['instructions'] for r in rows),'max_work':max(r['work'] for r in rows),
        'globals':max(r['globals'] for r in rows),'source_sha256':digest(SOURCE.read_bytes()),'rows':rows}
    write(STUDY/('vm-proof-'+NAME+'.json'),proof)
    assert proof['max_instructions']<=19000 and proof['max_work']<=50000 and proof['globals']<=256,proof|{'rows':None}
    print({k:v for k,v in proof.items() if k!='rows'},flush=True)


if __name__=='__main__':main()
