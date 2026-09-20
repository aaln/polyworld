"""Freeze and evaluate the coordinated visibility/response correction."""
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import pprint
from prepare import ROOT, STUDY as INITIAL, CAMPAIGN, CRITICAL, read, write, digest, bundle, compile_policy, extract, refresh_grounding
from games.gods_of_the_arena.instruments.richard_coaching import contracts_v3
from check_vm import case, run, VM
from test_policy_ir import obj

STUDY = INITIAL / 'visibility-complete'
NAME = 'formation2400_discovery'


def prepare():
    STUDY.mkdir(parents=True, exist_ok=True)
    original = read(INITIAL/'refined-breach/candidates/formation2400_breach/policy.ir.json')
    p = deepcopy(original)
    p['id'] = 'gota_richard_coaching_visibility_v3'
    p['skill']['observe']['operator'] = contracts_v3.NAME
    p['skill']['observe']['parameters']['home_radius'] = 60
    p['situation']['notes'] += (' Missing visible objective means unknown next objective, not a cleared '
        'base. A ready group scouts toward the fixed enemy-base coordinate until an exposed '
        'target enters team vision. A visible structure attacker inside60tiles of home '
        'triggers gathered defense even when it is the only observed attacker.')
    p['belief']['claims']['CoachedFormation']['claim'] += (
        ' Complete native reconstruction of the V1 Richard red loss found a visibility '
        'dead end after tower20: no visible exposed target, group near31,82, '
        'default28,79 goal, sustained creep-triggered breach. V3 adds forward '
        'discovery under readiness/tether and earlier response to observed '
        'structure attackers. These coordinated corrections need live validation.')
    p['update'].update(revision=p['update']['revision']+1, parent=digest(original),
        change={'origin':'Coaching plus audited Richard135 mechanism failure',
                'combined_refinement':'shared forward discovery + supported breach + observed structure defense',
                'session':'2026-09-20t17-21-56-307zf4f7b3'},
        evidence=p['update']['evidence']+[{'artifact':str(INITIAL/'reviews/richard-formation2400-red/equivalence.json')}])
    refresh_grounding(p)
    for name, policy in [('deployed',read(INITIAL/'candidates/deployed/policy.ir.json')),(NAME,p)]:
        dest = STUDY/'candidates'/name
        if not dest.exists():
            dest.parent.mkdir(exist_ok=True);bundle(policy,dest)
            (dest/'policy.py').write_text('"""Primary coached IR: visibility-complete team assault."""\n\nPOLICY = '+pprint.pformat(policy,width=110,sort_dicts=False)+'\n')
        assert compile_policy(policy).encode() == (dest/'policy.bas').read_bytes()
        assert extract(compile_policy(policy),policy) == policy
    write(STUDY/'config.json',read(CAMPAIGN/'config.json')['game_config'])
    if not (STUDY/'plan.json').exists():
        sources = {n:str(STUDY/'candidates'/n/'policy.bas') for n in ['deployed',NAME]}
        opponents = read(INITIAL/'plan.json')['opponents']
        inputs = [Path(x) for x in set(sources.values())|set(opponents.values())]
        inputs += [Path(contracts_v3.__file__),Path(__file__),STUDY/'config.json']
        write(STUDY/'plan.json',{'frozen_at':datetime.now(timezone.utc).isoformat(),
            'sources':sources,'opponents':opponents,
            'cases':[{'seed':9890000+i*4+rep*2+side,'opponent':rival,'side':side}
                     for i,rival in enumerate(opponents) for rep in range(2) for side in (0,1)],
            'gate':read(INITIAL/'plan.json')['gate'],
            'inputs_sha256':{str(p):digest(p.read_bytes()) for p in inputs},
            'scope':'24fresh local games then80Richard games under original coaching400cycle. '
                    'V2 is preserved as a failed local refinement; its no-target visibility '
                    'bug was discovered before any V2 hosted request. Use this new frozen '
                    'source for remaining80. Existing all-color/field gates unchanged.'})
        write(INITIAL/'refined-breach/hosted-disposition.json',{
            'status':'not_submitted','reason':'Audited live V1 revealed shared missing-target discovery failure; '
                'V2 preserves that defect. Preserve its24local results and evaluate corrected V3.',
            'replacement_plan':str(STUDY/'plan.json')})


def scenarios():
    source = STUDY/'candidates'/NAME/'policy.bas'; rows=[]
    missing = case(tick=3600,x=31,y=82)
    missing['objects'] = [o for o in missing['objects'] if o['objectId'] != 19]
    missing['objects'] += [obj(1000+i,team=0,x=32+i,y=83) for i in range(2)]
    a = run(source,[missing])[0];rows.append(a)
    assert a['memory']['gaReady']==1 and a['memory']['gaPhase']==2 and a['memory']['bestId']==0,a
    assert (a['memory']['gaMoveX'],a['memory']['gaMoveY'])==(11,105),a
    assert any(x['command']=='walkTo' and x['arguments']==[11,105] for x in a['actions']),a
    seen = deepcopy(missing);seen['self']['worldTick']=3601
    seen['objects'].append(obj(21,kind=4,team=1,x=25,y=88,hp=1300))
    a = run(source,[missing,seen])[-1];rows.append(a)
    assert a['memory']['gaPhase']==3 and a['memory']['bestId']==21,a
    unready = case(tick=3600,x=31,y=82,alive=3)
    unready['objects']=[o for o in unready['objects'] if o['objectId']!=19]
    a=run(source,[unready])[0];rows.append(a)
    assert a['memory']['gaReady']==0 and a['memory']['gaPhase']==1,a
    threat=case(tick=3000)
    enemy=obj(109,kind=2,team=1,x=79,y=37,hp=450);enemy['objectTarget']=18
    threat['objects'].append(enemy)
    a=run(source,[threat])[0];rows.append(a)
    assert a['memory']['gaEmergency']==1 and a['memory']['gaPhase']==4,a
    quiet=deepcopy(threat);quiet['objects'][-1]['objectTarget']=0
    a=run(source,[quiet])[0];rows.append(a)
    assert a['memory']['gaEmergency']==0,a
    for team in (0,1):
        for slot in range(5):
            c=case(team=team,slot=slot,tick=3000)
            c['objects'] += [obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(240-len(c['objects']))]
            a=run(source,[c])[0];rows.append(a)
            if team==1:
                assert a['actions']==run(CRITICAL/'policy.bas',[c],memory=[])[0]['actions']
    early=case(tick=2399)
    assert run(source,[early])[0]['actions']==run(CRITICAL/'policy.bas',[early],memory=[])[0]['actions']
    assert max(r['instructions'] for r in rows)<=20000 and max(r['work'] for r in rows)<=50000
    write(STUDY/'vm-proof.json',{'passed':True,'checks':[
        'ready group advances for vision when no exposed target is visible even with creep cover',
        'newly visible exposed target restores synchronized breach',
        'unready group does not advance into unseen base',
        'one observed structure attacker triggers gathered home response; nontargeting enemy does not',
        'all ten actual classes dense native VM','blue and early-red native action parity'],
        'max_instructions':max(r['instructions'] for r in rows),
        'max_work':max(r['work'] for r in rows),'vm_sha256':digest(VM.read_bytes())})


def local():
    plan=read(STUDY/'plan.json')
    for p,sha in plan['inputs_sha256'].items():assert digest(Path(p).read_bytes())==sha,p
    spec=importlib.util.spec_from_file_location('coaching_v3_local',ROOT/'games/gods_of_the_arena/instruments/support_repairs/run_local.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner);runner.STUDY=STUDY
    jobs=[(n,c,plan) for c in plan['cases'] for n in plan['sources']]
    with ThreadPoolExecutor(2) as pool:rows=list(pool.map(runner.run,jobs))
    write(STUDY/'local-results.json',{'complete':len(rows)==24,'rows':rows,'scope':plan['scope']})


if __name__=='__main__':
    prepare();scenarios();local()
