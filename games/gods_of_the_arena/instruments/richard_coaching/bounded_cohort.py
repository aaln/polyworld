"""Complete coordinated late-game bundle with an explicit runtime margin."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import pprint
from prepare import STUDY as INITIAL, CAMPAIGN, CRITICAL, read, write, digest, bundle, compile_policy, extract, refresh_grounding
from games.gods_of_the_arena.instruments.richard_coaching import contracts_v6
from check_vm import case, run, VM
from test_policy_ir import obj
import late_cohort

STUDY=INITIAL/'bounded-cohort'
NAME='formation4800_bounded'


def prepare():
    STUDY.mkdir(parents=True,exist_ok=True)
    original=read(INITIAL/'armed-cohort/candidates/formation2400_armed/policy.ir.json')
    p=deepcopy(original);p['id']='gota_richard_coaching_bounded_cohort_v7'
    p['skill']['observe']['operator']=contracts_v6.NAME
    p['skill']['observe']['parameters']['phase_tick']=4800
    p['situation']['notes'] += (' V7 combines the4800late phase with remembered '
        'home pressure and all-class ordered equipment. The selection pass uses '
        'the first128visible objects; all fixed structures/heroes precede creeps '
        'in this pinned engine. Truncated creep observations remain unknown.')
    ref=INITIAL/'reviews/late-cohort-failure.jsonl'
    p['belief']['claims']['CoachingRuntimeMargin']={'claim':
        'V4 reproduced the hosted DeathKnight VM failure exactly at tick5274, '
        'matching24936previous owned commands and every prior state hash. '
        'Its dense/local checks were insufficient. The coordinated final bundle '
        'reduces bounded creep scanning, skips irrelevant cohort getters, and '
        'requires a1000instruction local margin. This is a measured runtime '
        'repair hypothesis, not permission to count invalid games as losses.',
        'status':'untested','evidence':[{'artifact':str(ref),'sha256':digest(ref.read_bytes())}]}
    p['update'].update(revision=p['update']['revision']+1,parent=digest(original),
        change={'origin':'Complete coaching bundle plus reproduced runtime failure',
                'combined_refinement':'late4800 + robust four-member cohort + visibility discovery + remembered return + all-class equipment + bounded observations',
                'session':'2026-09-20t17-21-56-307zf4f7b3'},
        evidence=p['update']['evidence']+[{'artifact':str(ref),'sha256':digest(ref.read_bytes())}])
    refresh_grounding(p)
    for name,policy in [('deployed',read(INITIAL/'candidates/deployed/policy.ir.json')),(NAME,p)]:
        dest=STUDY/'candidates'/name
        if not dest.exists():
            dest.parent.mkdir(exist_ok=True);bundle(policy,dest)
            (dest/'policy.py').write_text('"""Primary IR: complete late-game coached bundle with runtime margin."""\n\nPOLICY = '+pprint.pformat(policy,width=110,sort_dicts=False)+'\n')
        assert compile_policy(policy).encode()==(dest/'policy.bas').read_bytes()
        assert extract(compile_policy(policy),policy)==policy
    write(STUDY/'config.json',read(CAMPAIGN/'config.json')['game_config'])
    if not (STUDY/'plan.json').exists():
        sources={n:str(STUDY/'candidates'/n/'policy.bas') for n in ['deployed',NAME]}
        opponents=read(INITIAL/'plan.json')['opponents']
        inputs=[Path(x) for x in set(sources.values())|set(opponents.values())]
        inputs += [Path(contracts_v6.__file__),Path(__file__),STUDY/'config.json',ref]
        gate=deepcopy(read(INITIAL/'plan.json')['gate'])
        gate['runtime_margin']='Every native scenario and all24local games <=19000instructions, retaining1000below the hard20000limit. Hosted all-ten-VM gate still mandatory.'
        write(STUDY/'plan.json',{'frozen_at':datetime.now(timezone.utc).isoformat(),
            'sources':sources,'opponents':opponents,
            'cases':[{'seed':9930000+i*4+rep*2+side,'opponent':rival,'side':side}
                     for i,rival in enumerate(opponents) for rep in range(2) for side in (0,1)],
            'gate':gate,'inputs_sha256':{str(p):digest(p.read_bytes()) for p in inputs},
            'scope':'24fresh local games then80Richard games40percolor only after '
                    'runtime-margin gate. Final80of follow-up400cycle (160+80+80+80); '
                    'same10kdayledger, exactRichard135, existing fresh control. '
                    'Preserve all invalid V4 episodes; never replace their cohort.'})


def scenarios():
    source=STUDY/'candidates'/NAME/'policy.bas';rows=[]
    c=case(tick=4800,x=30,y=80);c['objects'][-1].update(objectX=105,objectY=11)
    a=run(source,[c])[0];rows.append(a);assert a['memory']['gaReady']==1 and a['memory']['gaNear']==4,a
    c=case(tick=5000)
    e=obj(109,kind=2,team=1,x=91,y=25,hp=450);e['objectTarget']=18;c['objects'].append(e)
    hidden=case(tick=5001)
    a=run(source,[c,hidden])[-1];rows.append(a)
    assert a['memory']['gaEmergency']==1 and a['memory']['gaPhase']==4,a
    missing=case(tick=5000,x=31,y=82);missing['objects']=[o for o in missing['objects'] if o['objectId']!=19]
    a=run(source,[missing])[0];rows.append(a)
    assert (a['memory']['gaMoveX'],a['memory']['gaMoveY'])==(11,105),a
    for team in (0,1):
        for slot in range(5):
            for tick in (4799,5000):
                c=case(team=team,slot=slot,tick=tick)
                c['objects'] += [obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(240-len(c['objects']))]
                a=run(source,[c])[0];rows.append(a)
                if team==1:assert a['actions']==run(CRITICAL/'policy.bas',[c],memory=[])[0]['actions']
    assert max(r['instructions'] for r in rows)<=19000 and max(r['work'] for r in rows)<=50000
    write(STUDY/'vm-proof.json',{'passed':True,'checks':['robust four-member cohort',
        'remembered home return through fog','forward discovery of missing objective',
        'all ten actual classes before/after transition with240objects','exact blue actions',
        '1000instruction margin in tested scenarios'],
        'max_instructions':max(r['instructions'] for r in rows),'max_work':max(r['work'] for r in rows),
        'vm_sha256':digest(VM.read_bytes())})


if __name__=='__main__':
    prepare();scenarios();late_cohort.STUDY=STUDY;late_cohort.local()
    rows=read(STUDY/'local-results.json')['rows']
    assert all(r['valid'] and r['max_instructions']<=19000 for r in rows)
    write(STUDY/'runtime-margin.json',{'passed':True,'games':24,
        'max_instructions':max(r['max_instructions'] for r in rows),'headroom':20000-max(r['max_instructions'] for r in rows)})
