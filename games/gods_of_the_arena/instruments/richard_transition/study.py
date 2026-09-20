"""Freeze and evaluate the complete second coaching-session behavior."""
from copy import deepcopy
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import importlib.util
from pathlib import Path
import pprint
import sys

ROOT=Path(__file__).resolve().parents[4]
OLD_TOOLS=ROOT/'games/gods_of_the_arena/instruments/richard_coaching'
sys.path.insert(0,str(OLD_TOOLS))
from prepare import CLEAN, CAMPAIGN, read, write, digest, bundle, compile_policy, extract, refresh_grounding
from games.gods_of_the_arena.instruments.richard_transition import contracts
from check_vm import case, run, VM
from test_policy_ir import obj

STUDY=ROOT/'tmp/gota-ir/richard-transition-20260920'
PARENT=ROOT/'examples/gods_of_the_arena/players/ir/forks/richard135-coaching-20260920/evaluated/formation4800_budget'
NAMES=('coached_baseline','transition','transition_armor')


def prepare():
    original=read(PARENT/'policy.ir.json')
    assert compile_policy(original).encode()==(PARENT/'policy.bas').read_bytes()
    for name in NAMES:
        p=deepcopy(original)
        if name!='coached_baseline':
            p['id']='gota_richard_transition_'+name
            p['skill']['observe']['operator']=contracts.NAME
            p['skill']['observe']['parameters'].update(home_radius=28,home_commit_ticks=360,
                clear_ticks=72,scout_quiet_ticks=240)
            p['skill']['attack']['operator']=contracts.ATTACK
            if name=='transition_armor':p['skill']['equipment']['operator']=contracts.EQUIPMENT
            p['situation']['notes']+=(
                ' Coaching session2026-09-20t19-10-35-082z64deb6 binds exact episode '
                'ereq_b3f6d7ee-c7da-41b3-8ecc-70b9a790208a to the formation4800_budget '
                'red baseline. PerimeterCleared means no currently observed '
                'hostile hero/creep inside36tiles of home after a complete '
                '128-object scan; truncated scans are unknown. HostilesUnobserved '
                'means no enemy hero visible for240ticks, not an empty enemy map. '
                'Thresholds, scout class and finite timers are authored choices.')
            p['goal']['G_group_siege']['preference']=(
                'Convert defended waves into offensive objective pressure. Hold '
                'only under current observed pressure or bounded recent evidence. '
                'Scout with a healthy Crossbowman during observed quiet periods. '
                'Prioritize a visible threatening Ranger with coordinated legal '
                'strikes, including when fewer than four healthy defenders remain.')
            p['goal']['G_defense']['preference']=(
                'Coached red defense expires or releases after continuous observed '
                'perimeter clearance. New core damage is evidence; old damage '
                'alone does not renew the alarm. Preserve blue behavior.')
            p['belief']['claims']['CoachedTransition']={
                'claim':'Hypothesis: the combined bounded alarm, observed-clear '
                    'offensive release, designated scout, shared Ranger priority '
                    'and coordinated strikes counter the exact coached stall '
                    'and improve Richard135 red fort wins. The armor variant '
                    'also funds HP before later damage/mana equipment. No '
                    'individual edit is required to improve independently.',
                'status':'untested','evidence':[{'artifact':str(STUDY/'captured-inputs.json')},
                    {'artifact':str(STUDY/'session-binding.json')},
                    {'artifact':str(STUDY/'defense-state/equivalence.json')}]}
            p['belief']['claims']['CoachedFormation']['claim']=(
                'Historical parent outcome: formation4800_budget scored0/40red '
                'and40/40blue versus Richard135. New transition source requires '
                'its own measured result; this inherited result does not qualify it.')
            p['belief']['claims']['CoachedFormation']['status']='requires_review'
            p['update'].update(revision=p['update']['revision']+1,parent=digest(original),
                change={'origin':'User19:10coaching plus exact native reconstruction',
                        'combined_behavior':name,'session':read(STUDY/'captured-inputs.json')['session']},
                needs_review=['belief/CoachedTransition','goal/G_group_siege'])
            refresh_grounding(p)
        dest=STUDY/'candidates'/name
        if not dest.exists():
            dest.parent.mkdir(exist_ok=True);bundle(p,dest)
            (dest/'policy.py').write_text('"""Primary IR for the complete coached transition."""\n\nPOLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
        assert compile_policy(p).encode()==(dest/'policy.bas').read_bytes()
        assert extract((dest/'policy.bas').read_text(),p)==p
        print('BUILT',name,digest((dest/'policy.bas').read_bytes()),flush=True)
    write(STUDY/'config.json',read(CAMPAIGN/'config.json')['game_config'])
    if not (STUDY/'plan.json').exists():
        sources={n:str(STUDY/'candidates'/n/'policy.bas') for n in NAMES}
        opponents={'default':str(ROOT.parent/'gota-research-20260916/r5/default.bas'),
            'deployed':str(ROOT/'examples/gods_of_the_arena/players/ir/forks/jordan268/policy.bas'),
            'coached_baseline':sources['coached_baseline']}
        inputs=[Path(x) for x in set(sources.values())|set(opponents.values())]
        inputs += [Path(contracts.__file__),Path(__file__),STUDY/'config.json',STUDY/'captured-inputs.json']
        write(STUDY/'plan.json',{'created_at':datetime.now(timezone.utc).isoformat(),
            'sources':sources,'opponents':opponents,
            'cases':[{'seed':9950000+i*4+rep*2+side,'opponent':rival,'side':side}
                     for i,rival in enumerate(opponents) for rep in range(2) for side in (0,1)],
            'inputs_sha256':{str(p):digest(p.read_bytes()) for p in inputs},
            'gate':{'fidelity':'Actual native scenarios: stale-damage release, no release under positive pressure, finite fog memory, observed-clear transition, quiet healthy scout, carry priority despite reduced allied readiness, legal strike attempts, early/blue parity, honest unknown after truncated scan.',
                    'runtime':'All native scenarios and36local games <=19000instructions, <=50000work, full replays and all VM checks. No hosted source failing this gate.',
                    'local':'Behavior/regression diagnosis only; local bots are not Richard proxies. Record every cell and survival.',
                    'Richard':'Two complete combined candidates and exact coached baseline, fresh40percolor each. >=30wins EACH color and>=8aggregate wins gained over contemporaneous baseline. Generated hosted seeds differ; correlated trajectories are not independent trials.',
                    'promotion':'Retain all prior target/field/survival checks. No promotion from mechanism fidelity or a Richard-only screen.'},
            'scope':'36paired local games, then at most240hosted Richard135 games after fidelity/runtime gate. No component-alone gain requirement. All captured inputs and failures preserved.'})


def scenarios():
    rows=[];checks=[]
    for name in NAMES[1:]:
        path=STUDY/'candidates'/name/'policy.bas'
        memory=['gaActive','gaReady','gaTethered','gaEmergency','gaMoveX','gaMoveY','bestId',
                'defUntil','criticalUntil','perimeterEnabled','backdoorActive']
        # Consecutive ticks are essential: gaps deliberately invalidate memory.
        quiet=[case(tick=5000+i,x=98,y=18) for i in range(362)]
        for c in quiet:c['objects'][0]['objectHp']=350
        q=run(path,quiet,memory);rows+=q
        assert q[-1]['memory']['gaEmergency']==0,'Old damage renewed defense'
        scout=[case(slot=1,tick=5000+i,x=98,y=18) for i in range(242)]
        a=run(path,scout,memory)[-1];rows.append(a)
        assert a['memory']['perimeterEnabled']==1 and a['memory']['gaMoveX']<95 and a['memory']['gaMoveY']>24,a
        low=deepcopy(scout[-1]);low['self']['selfHp']=80
        a=run(path,scout[:-1]+[low],memory)[-1];rows.append(a)
        assert a['memory']['perimeterEnabled']==0
        threat=case(tick=5000,x=97,y=18)
        ranger=obj(106,kind=2,team=1,x=96,y=20,hp=600);ranger['objectClass']=1;ranger['objectTarget']=29
        tank=obj(105,kind=2,team=1,x=97,y=19,hp=150);tank['objectClass']=0
        threat['objects'] += [ranger,tank]
        a=run(path,[threat],memory)[0];rows.append(a)
        assert a['memory']['gaEmergency']==1 and a['memory']['bestId']==106,a
        reduced=deepcopy(threat)
        for o in reduced['objects']:
            if o['objectId'] in (102,103,104):o['objectHp']=0;o['objectAlive']=0
        a=run(path,[reduced],memory)[0];rows.append(a)
        assert a['memory']['gaReady']==0 and a['memory']['bestId']==106,a
        assert any(x['command']=='attackTarget' and x['arguments']==[106] for x in a['actions'])
        hold=[deepcopy(threat) for _ in range(100)]
        for i,c in enumerate(hold):c['self']['worldTick']=5000+i
        h=run(path,hold,memory);rows+=h
        assert all(r['memory']['gaEmergency'] for r in h)
        cleared=[case(tick=5100+i,x=97,y=18) for i in range(74)]
        h=run(path,hold+cleared,memory);rows+=h[-74:]
        assert h[-1]['memory']['gaEmergency']==0
        for count in (60,64,65,80,81,128,240):
            for team in (0,1):
                for slot in range(5):
                    c=case(team=team,slot=slot,tick=5000)
                    c['objects'] += [obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(count-len(c['objects']))]
                    a=run(path,[c],memory)[0];rows.append(a)
                    if team==1:assert a['actions']==run(PARENT/'policy.bas',[c],memory=[])[0]['actions']
        for slot in range(5):
            c=case(slot=slot,tick=4799)
            a=run(path,[c],memory)[0];rows.append(a)
            if name=='transition':assert a['actions']==run(PARENT/'policy.bas',[c],memory=[])[0]['actions']
        checks.append({'candidate':name,'mechanisms_passed':True})
    assert max(r['instructions'] for r in rows)<=19000
    assert max(r['work'] for r in rows)<=50000
    write(STUDY/'vm-proof.json',{'passed':True,'checks':checks,'max_instructions':max(r['instructions'] for r in rows),
        'max_work':max(r['work'] for r in rows),'vm_sha256':digest(VM.read_bytes()),'scope':'Native mechanism checks; not a win-rate verdict.'})
    print('SCENARIOS PASSED',flush=True)


def local():
    plan=read(STUDY/'plan.json')
    for p,sha in plan['inputs_sha256'].items():assert digest(Path(p).read_bytes())==sha,p
    spec=importlib.util.spec_from_file_location('transition_local',ROOT/'games/gods_of_the_arena/instruments/support_repairs/run_local.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner);runner.STUDY=STUDY
    with ThreadPoolExecutor(2) as pool:
        rows=list(pool.map(runner.run,[(n,c,plan) for c in plan['cases'] for n in NAMES]))
    write(STUDY/'local-results.json',{'complete':len(rows)==36,'rows':rows,'scope':plan['scope']})
    assert all(r['valid'] and r['max_instructions']<=19000 and r['gear_heroes']==5 for r in rows)
    write(STUDY/'runtime-margin.json',{'passed':True,'games':36,'max_instructions':max(r['max_instructions'] for r in rows)})


if __name__=='__main__':prepare();scenarios();local()
