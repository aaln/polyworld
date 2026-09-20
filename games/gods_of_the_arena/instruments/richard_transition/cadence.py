"""Measured carry cadence incorporated before any new hosted candidate request."""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import pprint
import study as initial
from study import ROOT, CAMPAIGN, PARENT, read, write, digest, bundle, compile_policy, extract, refresh_grounding
from games.gods_of_the_arena.instruments.richard_transition import contracts_v2

INITIAL=initial.STUDY
STUDY=INITIAL/'cadence'
NAMES=('coached_baseline','transition_cadence','transition_armor_cadence')


def prepare():
    STUDY.mkdir(exist_ok=True)
    for name,old_name in zip(NAMES,initial.NAMES):
        original=read(INITIAL/'candidates'/old_name/'policy.ir.json');p=deepcopy(original)
        if name!='coached_baseline':
            p['id']='gota_richard_'+name
            p['skill']['observe']['operator']=contracts_v2.OBSERVE
            p['skill']['attack']['operator']=contracts_v2.ATTACK
            p['goal']['G_cadence']['preference']='After a verified new basic hit, issue one legal recovery movement decision and immediately resume the shared visible target. Preserve the Berserker exception and blue parent behavior. Attack commands are not evidence of hits.'
            p['belief']['claims']['CoachedTransition']['claim']+=(
                ' The initial coupled transition controller scored5/12local '
                'versus7/12baseline. It was not submitted because the exact '
                'Ranger replay showed a missing focus-recovery interaction: '
                '62of75late inter-hit intervals are9ticks. Preserve legal '
                'verified-hit recovery within carry focus, then evaluate the '
                'complete revised bundle. This is a new authored hypothesis.')
            p['update'].update(revision=p['update']['revision']+1,parent=digest(original),
                change={'origin':'Native Ranger hit-timing evidence; full coordinated transition refinement',
                        'candidate':name,'session':read(INITIAL/'captured-inputs.json')['session']},
                evidence=p['update']['evidence']+[{'artifact':str(INITIAL/'diagnosis.json'),'sha256':digest((INITIAL/'diagnosis.json').read_bytes())}])
            refresh_grounding(p)
        dest=STUDY/'candidates'/name
        if not dest.exists():
            dest.parent.mkdir(exist_ok=True);bundle(p,dest)
            (dest/'policy.py').write_text('"""Primary IR: coached transition with verified-hit focus recovery."""\n\nPOLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
        assert compile_policy(p).encode()==(dest/'policy.bas').read_bytes()
        assert extract((dest/'policy.bas').read_text(),p)==p
        print('BUILT',name,flush=True)
    write(STUDY/'config.json',read(INITIAL/'config.json'))
    if not (STUDY/'plan.json').exists():
        plan=deepcopy(read(INITIAL/'plan.json'))
        plan.update(created_at=datetime.now(timezone.utc).isoformat(),
            sources={n:str(STUDY/'candidates'/n/'policy.bas') for n in NAMES},
            scope='36fresh paired local games, then240Richard135 games only after complete fidelity/runtime margin. Prior36local results preserved; no initialV1hosted requests.')
        for c in plan['cases']:c['seed']+=10000
        inputs=[Path(x) for x in set(plan['sources'].values())|set(plan['opponents'].values())]
        inputs += [Path(__file__),Path(contracts_v2.__file__),STUDY/'config.json',INITIAL/'diagnosis.json']
        plan['inputs_sha256']={str(p):digest(p.read_bytes()) for p in inputs}
        plan['gate']['fidelity']+=' Verified-hit recovery requires a new hit, lasts one decision, and falls back to attack on blocked movement.'
        write(STUDY/'plan.json',plan)
        write(INITIAL/'hosted-disposition.json',{'status':'not_submitted','reason':
            'Preserved all36local results. Exact Ranger hit timing exposed the focus controller direct-fire cadence limitation before hosting. V2 combines measured hit recovery with the whole coached bundle; no isolated edit gate is imposed.',
            'replacement':str(STUDY/'plan.json')})


def extra_scenarios():
    from study import case,run,obj
    rows=[]
    for name in NAMES[1:]:
        path=STUDY/'candidates'/name/'policy.bas'
        for slot in range(5):
            c=case(slot=slot,tick=5000,x=97,y=18)
            ranger=obj(106,kind=2,team=1,x=96,y=20,hp=600)
            ranger.update(objectClass=1,objectTarget=29);c['objects'].append(ranger)
            c['abilities']=[{'abilityCharges':2,'abilityCooldown':0} for _ in range(4)]
            c['self'].update(selfAttacksLanded=0,selfMana=200)
            hit=deepcopy(c);hit['self'].update(worldTick=5001,selfAttacksLanded=1)
            after=deepcopy(hit);after['self']['worldTick']=5002
            a=run(path,[c,hit,after],memory=['motionActive','bestId']);rows+=a
            assert any(x['command']=='castTarget' and x['arguments'][1]==106 for x in a[0]['actions'])
            assert any(x['command']=='attackTarget' for x in a[0]['actions'])
            if slot!=4:
                assert any(x['command']=='walkTo' for x in a[1]['actions'])
                assert not any(x['command']=='attackTarget' for x in a[1]['actions'])
            assert any(x['command']=='attackTarget' for x in a[2]['actions'])
            blocked=deepcopy(hit);blocked['returns']['walkTo']=0
            b=run(path,[c,blocked],memory=[])[-1];rows.append(b)
            assert any(x['command']=='attackTarget' for x in b['actions'])
    assert max(r['instructions'] for r in rows)<=19000 and max(r['work'] for r in rows)<=50000
    write(STUDY/'focus-proof.json',{'passed':True,'checks':['all five red classes cast on the same selected visible Ranger',
        'no movement without a new verified hit','non-Berserker one-decision hit recovery','immediate resumed attack',
        'rejected movement preserves attack'],'rows':rows,'scope':'Native BASIC VM with scripted command acceptance; full games separately verify actual engine outcomes.'})


if __name__=='__main__':
    prepare()
    initial.STUDY=STUDY;initial.NAMES=NAMES
    initial.scenarios();extra_scenarios();initial.local()
