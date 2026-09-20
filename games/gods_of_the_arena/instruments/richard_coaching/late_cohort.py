"""Late-game interpretation with a four-member cohort, tested as one bundle."""
from copy import deepcopy
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import importlib.util
from pathlib import Path
import pprint
from prepare import ROOT, STUDY as INITIAL, CAMPAIGN, CRITICAL, read, write, digest, bundle, compile_policy, extract, refresh_grounding
from games.gods_of_the_arena.instruments.richard_coaching import contracts_v4
from check_vm import case, run, VM
from test_policy_ir import obj

STUDY=INITIAL/'late-cohort'
NAME='formation4800_cohort'


def prepare():
    STUDY.mkdir(parents=True,exist_ok=True)
    original=read(INITIAL/'visibility-complete/candidates/formation2400_discovery/policy.ir.json')
    p=deepcopy(original);p['id']='gota_richard_coaching_late_cohort_v4'
    p['skill']['observe']['operator']=contracts_v4.NAME
    p['skill']['observe']['parameters']['phase_tick']=4800
    p['situation']['notes'] += (' V4 uses a four-member cohort center when one of '
        'five living allies is a distant outlier; recompute readiness against that '
        'center. It does not treat three allies as a ready assault. The whole '
        'coached red macro starts at tick4800, an authored late-game interpretation.')
    p['belief']['claims']['CoachedFormation']['claim'] += (' The earlier2400 and3600 '
        'starts failed to win red. V3 local review additionally found five sampled '
        'frames where four healthy allies form a valid group but the fifth ally '
        'displaces the global centroid and blocks readiness. V4 preserves more '
        'laning and tests a robust cohort center as one combined late-game bundle. '
        'Neither timing nor trimming is claimed independently beneficial.')
    p['update'].update(revision=p['update']['revision']+1,parent=digest(original),
        change={'origin':'Complete coaching synthesis late-game qualification and native group review',
                'combined_refinement':'late4800 phase + four-member cohort + V3 discovery/defense',
                'session':'2026-09-20t17-21-56-307zf4f7b3'},
        evidence=p['update']['evidence']+[{'artifact':str(INITIAL/'reviews/discovery-local-9890010/outlier-readiness.json')}])
    refresh_grounding(p)
    for name,policy in [('deployed',read(INITIAL/'candidates/deployed/policy.ir.json')),(NAME,p)]:
        dest=STUDY/'candidates'/name
        if not dest.exists():
            dest.parent.mkdir(exist_ok=True);bundle(policy,dest)
            (dest/'policy.py').write_text('"""Primary IR: late-game four-member assault cohort."""\n\nPOLICY = '+pprint.pformat(policy,width=110,sort_dicts=False)+'\n')
        assert compile_policy(policy).encode()==(dest/'policy.bas').read_bytes()
        assert extract(compile_policy(policy),policy)==policy
    write(STUDY/'config.json',read(CAMPAIGN/'config.json')['game_config'])
    if not (STUDY/'plan.json').exists():
        sources={n:str(STUDY/'candidates'/n/'policy.bas') for n in ['deployed',NAME]}
        opponents=read(INITIAL/'plan.json')['opponents']
        inputs=[Path(x) for x in set(sources.values())|set(opponents.values())]
        inputs += [Path(contracts_v4.__file__),Path(__file__),STUDY/'config.json']
        write(STUDY/'plan.json',{'frozen_at':datetime.now(timezone.utc).isoformat(),
            'sources':sources,'opponents':opponents,
            'cases':[{'seed':9900000+i*4+rep*2+side,'opponent':rival,'side':side}
                     for i,rival in enumerate(opponents) for rep in range(2) for side in (0,1)],
            'gate':read(INITIAL/'plan.json')['gate'],
            'inputs_sha256':{str(p):digest(p.read_bytes()) for p in inputs},
            'scope':'24fresh local games. After valid complete VM/replay checks,160 '
                    'Richard games in separate late-cohort cycle: candidate and '
                    'fresh baseline40percolor. Same10k daily ledger, no field claim. '
                    'Adaptive combined discovery, no isolated-edit gain requirement.'})


def scenarios():
    source=STUDY/'candidates'/NAME/'policy.bas';rows=[]
    clustered=case(tick=4800,x=30,y=80)
    clustered['objects'][-1].update(objectX=105,objectY=11)
    a=run(source,[clustered])[0];rows.append(a)
    assert a['memory']['gaReady']==1 and a['memory']['gaNear']==4,a
    outlier=deepcopy(clustered);outlier['self'].update(selfId=104,selfClass=9,selfX=105,selfY=11)
    a=run(source,[outlier])[0];rows.append(a)
    assert a['memory']['gaTethered']==1 and a['memory']['bestId']==0,a
    assert a['memory']['gaMoveX']<35 and a['memory']['gaMoveY']>75,a
    scattered=deepcopy(clustered);scattered['objects'][-2].update(objectX=100,objectY=15)
    a=run(source,[scattered])[0];rows.append(a)
    assert a['memory']['gaReady']==0,a
    for tick in (2400,3600,4799):
        c=case(tick=tick)
        assert run(source,[c])[0]['actions']==run(CRITICAL/'policy.bas',[c],memory=[])[0]['actions']
    for team in (0,1):
        for slot in range(5):
            c=case(team=team,slot=slot,tick=5000)
            c['objects'] += [obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(240-len(c['objects']))]
            a=run(source,[c])[0];rows.append(a)
            if team==1:assert a['actions']==run(CRITICAL/'policy.bas',[c],memory=[])[0]['actions']
    assert max(r['instructions'] for r in rows)<=20000 and max(r['work'] for r in rows)<=50000
    write(STUDY/'vm-proof.json',{'passed':True,'checks':['four healthy heroes plus distant fifth are ready',
        'distant fifth regroups and cannot launch solo attack','three grouped plus two distant are unready',
        'early/middle red preserves parent through4799','all blue classes preserve parent actions',
        'all ten actual classes dense native VM'],
        'max_instructions':max(r['instructions'] for r in rows),'max_work':max(r['work'] for r in rows),
        'vm_sha256':digest(VM.read_bytes())})


def local():
    plan=read(STUDY/'plan.json')
    for p,sha in plan['inputs_sha256'].items():assert digest(Path(p).read_bytes())==sha,p
    spec=importlib.util.spec_from_file_location('coaching_v4_local',ROOT/'games/gods_of_the_arena/instruments/support_repairs/run_local.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner);runner.STUDY=STUDY
    jobs=[(n,c,plan) for c in plan['cases'] for n in plan['sources']]
    with ThreadPoolExecutor(2) as pool:rows=list(pool.map(runner.run,jobs))
    write(STUDY/'local-results.json',{'complete':len(rows)==24,'rows':rows,'scope':plan['scope']})


if __name__=='__main__':prepare();scenarios();local()
