"""Fresh combined V2 comparison prompted by complete V1 mechanism review."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import pprint
from prepare import ROOT, CLEAN, CAMPAIGN, STUDY as INITIAL, read, write, digest, bundle, compile_policy, extract, refresh_grounding
from games.gods_of_the_arena.instruments.richard_coaching import contracts_v2
from check_vm import case, run, VM

STUDY=INITIAL/'refined-breach'
NAME='formation2400_breach'


def prepare():
    STUDY.mkdir(parents=True,exist_ok=True)
    source=INITIAL/'candidates/formation2400'
    original=read(source/'policy.ir.json');p=deepcopy(original)
    p['id']='gota_richard_coaching_breach_v2'
    p['skill']['observe']['operator']=contracts_v2.NAME
    p['belief']['claims']['CoachedFormation']['claim'] += (
        ' V1 full-game review showed correctly gathered heroes but premature '
        'perimeter probing before clearing outer objectives, hero chasing even '
        'during a supported breach, and remote-centroid regrouping during home '
        'emergency. V2 coordinates objective-stage selection, supported structure '
        'priority and the emergency rendezvous. Competitive benefit is untested.')
    p['update'].update(revision=p['update']['revision']+1,parent=digest(original),
        change={'origin':'Same user coaching; full V1 native behavior review',
                'combined_refinement':'objective phase + breach arbitration + home rendezvous',
                'session':'2026-09-20t17-21-56-307zf4f7b3'},
        evidence=p['update']['evidence']+[{'artifact':str(INITIAL/'reviews/formation2400-9870000/equivalence.json')}])
    refresh_grounding(p)
    for name,policy in [('deployed',read(INITIAL/'candidates/deployed/policy.ir.json')),(NAME,p)]:
        dest=STUDY/'candidates'/name
        if not dest.exists():
            dest.parent.mkdir(exist_ok=True);bundle(policy,dest)
            (dest/'policy.py').write_text('"""Primary coached IR with reviewed phase/arbitration refinement."""\n\nPOLICY = '+pprint.pformat(policy,width=110,sort_dicts=False)+'\n')
        assert compile_policy(policy).encode()==(dest/'policy.bas').read_bytes()
        assert extract(compile_policy(policy),policy)==policy
    c=read(CAMPAIGN/'config.json');write(STUDY/'config.json',c['game_config'])
    if not (STUDY/'plan.json').exists():
        sources={n:str(STUDY/'candidates'/n/'policy.bas') for n in ['deployed',NAME]}
        opponents=read(INITIAL/'plan.json')['opponents']
        inputs=[Path(x) for x in set(sources.values())|set(opponents.values())]
        inputs += [Path(contracts_v2.__file__),Path(__file__),STUDY/'config.json']
        write(STUDY/'plan.json',{'frozen_at':datetime.now(timezone.utc).isoformat(),
            'sources':sources,'opponents':opponents,
            'cases':[{'seed':9880000+i*4+rep*2+side,'opponent':rival,'side':side}
                     for i,rival in enumerate(opponents) for rep in range(2) for side in (0,1)],
            'gate':read(INITIAL/'plan.json')['gate'],'inputs_sha256':{str(p):digest(p.read_bytes()) for p in inputs},
            'scope':'24fresh local games and80Richardgames, combined cycle320+80=400. No field qualification from a target-only result.'})


def scenarios():
    source=STUDY/'candidates'/NAME/'policy.bas';rows=[]
    outer=case(tick=2400,x=45,y=68);a=run(source,[outer])[0];rows.append(a)
    assert a['memory']['gaPhase']==3 and a['memory']['bestId']==19,a
    inner=case(tick=2400,x=28,y=80);inner['objects'][2].update(objectX=34,objectY=86)
    a=run(source,[inner])[0];rows.append(a);assert a['memory']['gaPhase']==2,a
    from test_policy_ir import obj
    breach=deepcopy(inner)
    breach['objects'] += [obj(105,kind=2,team=1,x=35,y=84,hp=200),
        obj(106,kind=2,team=1,x=5,y=100,hp=200),obj(107,kind=2,team=1,x=85,y=60,hp=200)]
    a=run(source,[breach])[0];rows.append(a)
    assert a['memory']['gaSpread']==1 and a['memory']['gaPhase']==3 and a['memory']['bestId']==19,a
    emergency=case(tick=2400,alive=3)
    emergency['objects'] += [obj(105+i,kind=2,team=1,x=90+i,y=25,hp=300) for i in range(2)]
    a=run(source,[emergency])[0];rows.append(a)
    assert a['memory']['gaReady']==0 and a['memory']['gaEmergency']==1 and a['memory']['gaMoveX']>=97,a
    assert a['memory']['bestId']==0,a
    for team in (0,1):
        for slot in range(5):
            c=case(team=team,slot=slot,tick=3000)
            c['objects'] += [obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(240-len(c['objects']))]
            rows += run(source,[c])
    assert max(r['instructions'] for r in rows)<=20000 and max(r['work'] for r in rows)<=50000
    write(STUDY/'vm-proof.json',{'passed':True,'checks':['outer objective precedes perimeter','inner perimeter probe',
        'observed dispersion accelerates supported structure breach','unready home emergency rendezvous',
        'all ten actual classes dense native VM'],'max_instructions':max(r['instructions'] for r in rows),
        'max_work':max(r['work'] for r in rows),'vm_sha256':digest(VM.read_bytes())})


def local():
    plan=read(STUDY/'plan.json')
    for p,sha in plan['inputs_sha256'].items():assert digest(Path(p).read_bytes())==sha,p
    spec=importlib.util.spec_from_file_location('coaching_v2_local',ROOT/'games/gods_of_the_arena/instruments/support_repairs/run_local.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner);runner.STUDY=STUDY
    jobs=[(n,c,plan) for c in plan['cases'] for n in plan['sources']]
    with ThreadPoolExecutor(2) as pool:rows=list(pool.map(runner.run,jobs))
    write(STUDY/'local-results.json',{'complete':len(rows)==24,'rows':rows,'scope':plan['scope']})


if __name__=='__main__':
    prepare();scenarios();local()
