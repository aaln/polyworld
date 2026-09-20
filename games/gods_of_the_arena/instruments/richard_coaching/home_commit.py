"""Combined gathered assault with a bounded remembered defensive return."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import pprint
from prepare import STUDY as INITIAL, CAMPAIGN, CRITICAL, read, write, digest, bundle, compile_policy, extract, refresh_grounding
from games.gods_of_the_arena.instruments.richard_coaching import contracts_v5
from check_vm import case, run, VM
from test_policy_ir import obj
import late_cohort

STUDY=INITIAL/'committed-return'
NAME='formation2400_commit'


def prepare():
    STUDY.mkdir(parents=True,exist_ok=True)
    original=read(INITIAL/'late-cohort/candidates/formation4800_cohort/policy.ir.json')
    p=deepcopy(original);p['id']='gota_richard_coaching_committed_return_v5'
    p['skill']['observe']['operator']=contracts_v5.NAME
    p['skill']['observe']['parameters'].update(phase_tick=2400,home_commit_ticks=1200)
    p['situation']['notes'] += (' V5 supersedes the V4 timing: starts at2400 because '
        'the observed structure attack arrives before4800. Positive home pressure '
        'starts a1200tick remembered return; temporary fog does not clear it. '
        'Remembered threat coordinates are navigation goals, never invisible targets.')
    p['belief']['claims']['HomePressurePersistence']={'claim':
        'Exact V3 Richard red reconstruction shows nine sampled transitions into '
        'or out of home defense. Temporary visibility loss repeatedly reverses '
        'the group before it can return. Keeping the positive sighting for1200ticks '
        'and suppressing remote attack pursuit during that return may make '
        'the coordinated defense arrive in time; competitive value is untested.',
        'status':'untested','evidence':[{'artifact':str(INITIAL/'reviews/richard-discovery-red/defense-reversals.json')}]}
    p['update'].update(revision=p['update']['revision']+1,parent=digest(original),
        change={'origin':'Audited coached group reversals through fog',
                'combined_refinement':'cohort assault + remembered home front + return precedence',
                'session':'2026-09-20t17-21-56-307zf4f7b3'},
        evidence=p['update']['evidence']+[{'artifact':str(INITIAL/'reviews/richard-discovery-red/equivalence.json')}])
    refresh_grounding(p)
    for name,policy in [('deployed',read(INITIAL/'candidates/deployed/policy.ir.json')),(NAME,p)]:
        dest=STUDY/'candidates'/name
        if not dest.exists():
            dest.parent.mkdir(exist_ok=True);bundle(policy,dest)
            (dest/'policy.py').write_text('"""Primary IR: gathered assault with remembered home return."""\n\nPOLICY = '+pprint.pformat(policy,width=110,sort_dicts=False)+'\n')
        assert compile_policy(policy).encode()==(dest/'policy.bas').read_bytes()
        assert extract(compile_policy(policy),policy)==policy
    write(STUDY/'config.json',read(CAMPAIGN/'config.json')['game_config'])
    if not (STUDY/'plan.json').exists():
        sources={n:str(STUDY/'candidates'/n/'policy.bas') for n in ['deployed',NAME]}
        opponents=read(INITIAL/'plan.json')['opponents']
        inputs=[Path(x) for x in set(sources.values())|set(opponents.values())]
        inputs += [Path(contracts_v5.__file__),Path(__file__),STUDY/'config.json']
        write(STUDY/'plan.json',{'frozen_at':datetime.now(timezone.utc).isoformat(),
            'sources':sources,'opponents':opponents,
            'cases':[{'seed':9910000+i*4+rep*2+side,'opponent':rival,'side':side}
                     for i,rival in enumerate(opponents) for rep in range(2) for side in (0,1)],
            'gate':read(INITIAL/'plan.json')['gate'],
            'inputs_sha256':{str(p):digest(p.read_bytes()) for p in inputs},
            'scope':'24fresh local games. If complete native fidelity/runtime passes, '
                    '80Richard games40percolor alongside the160late-cohort '
                    'candidate/control study, total240in the bounded follow-up cycle. '
                    'Use its contemporaneous fresh baseline, retain all-color/field '
                    'gates. Adaptive discovery, not independent confirmation.'})


def scenarios():
    source=STUDY/'candidates'/NAME/'policy.bas';rows=[]
    alarm=case(tick=3000)
    enemy=obj(109,kind=2,team=1,x=91,y=25,hp=450);enemy['objectTarget']=18
    alarm['objects'].append(enemy)
    # An enemy near the outbound group must not hold the return hostage.
    alarm['objects'].append(obj(108,kind=2,team=1,x=61,y=52,hp=300))
    a=run(source,[alarm])[0];rows.append(a)
    assert a['memory']['gaEmergency']==1 and a['memory']['gaPhase']==4 and a['memory']['bestId']==0,a
    hidden=case(tick=3001)
    a=run(source,[alarm,hidden])[-1];rows.append(a)
    assert a['memory']['gaEmergency']==1 and (a['memory']['gaMoveX'],a['memory']['gaMoveY'])==(91,25),a
    quiet=run(source,[hidden])[0];rows.append(quiet)
    assert quiet['memory']['gaEmergency']==0,quiet
    sequence=[alarm]
    for tick in range(3001,4201):
        c=deepcopy(hidden);c['self']['worldTick']=tick;sequence.append(c)
    elapsed=run(source,sequence)
    assert elapsed[-2]['memory']['gaEmergency']==1 and elapsed[-1]['memory']['gaEmergency']==0
    rows += elapsed[-2:]
    for team in (0,1):
        for slot in range(5):
            c=case(team=team,slot=slot,tick=3000)
            c['objects'] += [obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(240-len(c['objects']))]
            a=run(source,[c])[0];rows.append(a)
            if team==1:assert a['actions']==run(CRITICAL/'policy.bas',[c],memory=[])[0]['actions']
    assert max(r['instructions'] for r in rows)<=20000 and max(r['work'] for r in rows)<=50000
    write(STUDY/'vm-proof.json',{'passed':True,'checks':[
        'positive observed structure pressure starts return','brief fog preserves remembered navigation goal',
        'unobserved pressure does not create a commitment','remote local target cannot block home return',
        'commitment expires at1200consecutive decisions without renewed pressure',
        'all blue classes preserve parent actions','all ten actual classes dense native VM'],
        'max_instructions':max(r['instructions'] for r in rows),'max_work':max(r['work'] for r in rows),
        'vm_sha256':digest(VM.read_bytes())})


if __name__=='__main__':
    prepare();scenarios();late_cohort.STUDY=STUDY;late_cohort.local()
