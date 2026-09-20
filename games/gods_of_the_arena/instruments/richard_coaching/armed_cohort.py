"""Couple the corrected formation/return with full-class equipment progression."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import pprint
from prepare import STUDY as INITIAL, CAMPAIGN, CRITICAL, read, write, digest, bundle, compile_policy, extract, refresh_grounding
from games.gods_of_the_arena.instruments.richard_coaching import contracts_v5
from binding import CONTRACTS
from check_vm import case, run, VM
from test_policy_ir import obj
import late_cohort

STUDY=INITIAL/'armed-cohort'
NAME='formation2400_armed'


def prepare():
    STUDY.mkdir(parents=True,exist_ok=True)
    original=read(INITIAL/'committed-return/candidates/formation2400_commit/policy.ir.json')
    p=deepcopy(original);p['id']='gota_richard_coaching_armed_cohort_v6'
    equipment=p['skill']['equipment']
    equipment['operator']='buy_ordered_loadout'
    equipment['parameters']={k:equipment['parameters'][k] for k in CONTRACTS['buy_ordered_loadout'].parameters}
    ref=INITIAL/'committed-return/hosted/formation2400_commit/red/artifacts/ereq_0e520f69-15b9-4756-b360-8d97db7ef0c2/audit.json'
    a=read(ref);assert a['hash_mismatches']==0 and a['ticks']==13235
    p['belief']['claims']['FormationEquipmentInteraction']={'claim':
        'In the first diagnostic audited13235tick V5 loss, Richard DemonHunter died6times '
        'but finished level10 with advanced damage/HP gear. Our DeathKnight died8times, '
        'finished level3 with LeatherGauntlets/SteelHelmet and17basic hits. The observed '
        'V5 defense now fights the threat, but team scaling remains weak. Test full-class '
        'ordered equipment together with V5, not as an isolated starter-weapon edit. '
        'This selected diagnostic is hypothesis evidence, not a cohort win estimate.',
        'status':'untested','evidence':[{'artifact':str(ref),'sha256':digest(ref.read_bytes())}]}
    p['goal']['G_group_siege']['preference'] += (' Fund the group sustained damage and '
        'survivability through the existing five-item ordered loadout on every class; '
        'avoid filling red inventory with the baseline weaker progression.')
    p['update'].update(revision=p['update']['revision']+1,parent=digest(original),
        change={'origin':'Coached return now engages Richard; audited equipment/level gap',
                'combined_refinement':'V5 formation and remembered return + all-class ordered equipment',
                'session':'2026-09-20t17-21-56-307zf4f7b3'},
        evidence=p['update']['evidence']+[{'artifact':str(ref),'sha256':digest(ref.read_bytes())}])
    refresh_grounding(p)
    for name,policy in [('deployed',read(INITIAL/'candidates/deployed/policy.ir.json')),(NAME,p)]:
        dest=STUDY/'candidates'/name
        if not dest.exists():
            dest.parent.mkdir(exist_ok=True);bundle(policy,dest)
            (dest/'policy.py').write_text('"""Primary IR: equipped cohort with remembered home return."""\n\nPOLICY = '+pprint.pformat(policy,width=110,sort_dicts=False)+'\n')
        assert compile_policy(policy).encode()==(dest/'policy.bas').read_bytes()
        assert extract(compile_policy(policy),policy)==policy
    write(STUDY/'config.json',read(CAMPAIGN/'config.json')['game_config'])
    if not (STUDY/'plan.json').exists():
        sources={n:str(STUDY/'candidates'/n/'policy.bas') for n in ['deployed',NAME]}
        opponents=read(INITIAL/'plan.json')['opponents']
        inputs=[Path(x) for x in set(sources.values())|set(opponents.values())]
        inputs += [Path(__file__),STUDY/'config.json',ref]
        write(STUDY/'plan.json',{'frozen_at':datetime.now(timezone.utc).isoformat(),
            'sources':sources,'opponents':opponents,
            'cases':[{'seed':9920000+i*4+rep*2+side,'opponent':rival,'side':side}
                     for i,rival in enumerate(opponents) for rep in range(2) for side in (0,1)],
            'gate':read(INITIAL/'plan.json')['gate'],
            'inputs_sha256':{str(p):digest(p.read_bytes()) for p in inputs},
            'scope':'24fresh local games; native fidelity/runtime gate before80Richard '
                    'games40percolor. Adds80to follow-up cycle240, total320<400, '
                    'same10kshared day ledger and existing fresh control. Adaptive '
                    'combined-equipment interaction, no independent confirmation '
                    'or field claim; existing gates retained.'})


def scenarios():
    source=STUDY/'candidates'/NAME/'policy.bas';rows=[]
    for team in (0,1):
        for slot in range(5):
            c=case(team=team,slot=slot,tick=1)
            c['self'].update(selfGold=150,selfMana=200,selfMaxMana=200)
            a=run(source,[c])[0];rows.append(a)
            buys=[x['arguments'][0] for x in a['actions'] if x['command']=='buyItem']
            assert 11 in buys and not any(x in buys for x in (5,7,12)),(team,slot,a)
            c=case(team=team,slot=slot,tick=3000)
            c['objects'] += [obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(240-len(c['objects']))]
            a=run(source,[c])[0];rows.append(a)
            if team==1:assert a['actions']==run(CRITICAL/'policy.bas',[c],memory=[])[0]['actions']
    assert max(r['instructions'] for r in rows)<=20000 and max(r['work'] for r in rows)<=50000
    write(STUDY/'vm-proof.json',{'passed':True,'checks':[
        'every actual class starts ordered CrimsonDagger rather than baseline weaker equipment',
        'same existing supported ordered-loadout lowering, no new untested equipment operator',
        'blue actual-class actions preserve critical60','all ten actual classes dense native VM'],
        'inherited_controller_proof':str(INITIAL/'committed-return/vm-proof.json'),
        'max_instructions':max(r['instructions'] for r in rows),'max_work':max(r['work'] for r in rows),
        'vm_sha256':digest(VM.read_bytes())})


if __name__=='__main__':
    prepare();scenarios();late_cohort.STUDY=STUDY;late_cohort.local()
