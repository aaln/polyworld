"""Final coupled observation/combat budget repair, preserving every prior result."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import pprint
from prepare import STUDY as INITIAL, CAMPAIGN, CRITICAL, read, write, digest, bundle, compile_policy, extract, refresh_grounding
from games.gods_of_the_arena.instruments.richard_coaching import contracts_v7
from check_vm import case, run, VM
from test_policy_ir import obj
import late_cohort

STUDY=INITIAL/'bounded-combat'
NAME='formation4800_budget'


def prepare():
    STUDY.mkdir(parents=True,exist_ok=True)
    original=read(INITIAL/'bounded-cohort/candidates/formation4800_bounded/policy.ir.json')
    p=deepcopy(original);p['id']='gota_richard_coaching_bounded_combat_v8'
    p['skill']['attack']['operator']=contracts_v7.NAME
    p['belief']['claims']['CoachingRuntimeMargin']['claim'] += (
        ' The first bounded observer stayed below the hard limit but reached19105 '
        'instructions at tick4857, failing the stronger19000gate. Exact full-game '
        'reconstruction found gaActive=1 in this medium-density case. V8 also '
        'reduces the coached combat fast-path threshold from80to64, while '
        'keeping blue and pre-coaching thresholds unchanged.')
    p['update'].update(revision=p['update']['revision']+1,parent=digest(original),
        change={'origin':'Full native instruction-margin regression',
                'combined_refinement':'V7 complete coached bundle + coordinated combat-density budget',
                'session':'2026-09-20t17-21-56-307zf4f7b3'},
        evidence=p['update']['evidence']+[{'artifact':str(INITIAL/'reviews/bounded-runtime-margin/equivalence.json')}])
    refresh_grounding(p)
    for name,policy in [('deployed',read(INITIAL/'candidates/deployed/policy.ir.json')),(NAME,p)]:
        dest=STUDY/'candidates'/name
        if not dest.exists():
            dest.parent.mkdir(exist_ok=True);bundle(policy,dest)
            (dest/'policy.py').write_text('"""Primary IR: complete coached bundle with coordinated VM budgets."""\n\nPOLICY = '+pprint.pformat(policy,width=110,sort_dicts=False)+'\n')
        assert compile_policy(policy).encode()==(dest/'policy.bas').read_bytes()
        assert extract(compile_policy(policy),policy)==policy
    write(STUDY/'config.json',read(CAMPAIGN/'config.json')['game_config'])
    if not (STUDY/'plan.json').exists():
        sources={n:str(STUDY/'candidates'/n/'policy.bas') for n in ['deployed',NAME]}
        opponents=read(INITIAL/'plan.json')['opponents']
        inputs=[Path(x) for x in set(sources.values())|set(opponents.values())]
        inputs += [Path(contracts_v7.__file__),Path(__file__),STUDY/'config.json']
        gate=deepcopy(read(INITIAL/'bounded-cohort/plan.json')['gate'])
        cases=[{'seed':9940000+i*4+rep*2+side,'opponent':rival,'side':side}
               for i,rival in enumerate(opponents) for rep in range(2) for side in (0,1)]
        cases[4]['seed']=9930006
        assert cases[4]['opponent']=='deployed' and cases[4]['side']==0
        write(STUDY/'plan.json',{'frozen_at':datetime.now(timezone.utc).isoformat(),
            'sources':sources,'opponents':opponents,'cases':cases,
            'gate':gate,'inputs_sha256':{str(p):digest(p.read_bytes()) for p in inputs},
            'scope':'24matched local games:22fresh and2repeats of the paired known '
                    'runtime regression seed9930006. Then the remaining80Richard '
                    'games of follow-up400only if every game and scenario is '
                    '<=19000instructions. V7 is preserved and not submitted. '
                    'All target/field gates unchanged; adaptive combined discovery.'})
        write(INITIAL/'bounded-cohort/hosted-disposition.json',{'status':'not_submitted',
            'reason':'Full native game reached19105, failing the preregistered19000instruction margin. '
                'All24local results preserved; do not weaken the gate.',
            'replacement_plan':str(STUDY/'plan.json')})


def scenarios():
    source=STUDY/'candidates'/NAME/'policy.bas';rows=[]
    for count in (60,64,65,80,81,128,240):
        for team in (0,1):
            for slot in range(5):
                c=case(team=team,slot=slot,tick=5000)
                c['objects'] += [obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(count-len(c['objects']))]
                a=run(source,[c])[0];rows.append(a)
                if team==1:assert a['actions']==run(CRITICAL/'policy.bas',[c],memory=[])[0]['actions']
    assert max(r['instructions'] for r in rows)<=19000 and max(r['work'] for r in rows)<=50000
    write(STUDY/'vm-proof.json',{'passed':True,'checks':[
        'all ten actual classes at60,64,65,80,81,128and240visible objects',
        'blue actions preserved on both sides of both density thresholds',
        '1000instruction margin in all tested density scenarios'],
        'inherited_controller_proof':str(INITIAL/'bounded-cohort/vm-proof.json'),
        'max_instructions':max(r['instructions'] for r in rows),'max_work':max(r['work'] for r in rows),
        'vm_sha256':digest(VM.read_bytes())})


if __name__=='__main__':
    prepare();scenarios();late_cohort.STUDY=STUDY;late_cohort.local()
    rows=read(STUDY/'local-results.json')['rows']
    assert all(r['valid'] and r['max_instructions']<=19000 for r in rows)
    write(STUDY/'runtime-margin.json',{'passed':True,'games':24,
        'max_instructions':max(r['max_instructions'] for r in rows),'headroom':20000-max(r['max_instructions'] for r in rows)})
