"""Final boundary correction with all prior plans/results left unchanged."""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import pprint
import study as shared
import cadence as prior
from study import ROOT,read,write,digest,bundle,compile_policy,extract,refresh_grounding,case,run,obj
from games.gods_of_the_arena.instruments.richard_transition import contracts_v3

INITIAL=shared.STUDY
STUDY=INITIAL/'fresh-hit'
NAMES=('coached_baseline','transition_freshhit','transition_armor_freshhit')


def prepare():
    STUDY.mkdir(exist_ok=True)
    for name,old in zip(NAMES,prior.NAMES):
        original=read(prior.STUDY/'candidates'/old/'policy.ir.json');p=deepcopy(original)
        if name!='coached_baseline':
            p['id']='gota_richard_'+name;p['skill']['attack']['operator']=contracts_v3.ATTACK
            p['belief']['claims']['CoachedTransition']['claim']+=' Only a consecutive-decision hit increase permits recovery; cold entry and decision gaps initialize memory without a spurious move.'
            p['update'].update(revision=p['update']['revision']+1,parent=digest(original),change={
                'origin':'Carry-focus boundary validation','candidate':name,
                'session':read(INITIAL/'captured-inputs.json')['session'],
                'parent_disposition':str(prior.STUDY/'admission-stopped.json')})
            refresh_grounding(p)
        dest=STUDY/'candidates'/name
        if not dest.exists():
            dest.parent.mkdir(exist_ok=True);bundle(p,dest)
            (dest/'policy.py').write_text('"""Primary IR: coached transition with fresh hit memory."""\n\nPOLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
        assert compile_policy(p).encode()==(dest/'policy.bas').read_bytes()
        assert extract((dest/'policy.bas').read_text(),p)==p
        print('BUILT',name,flush=True)
    write(STUDY/'config.json',read(INITIAL/'config.json'))
    if not (STUDY/'plan.json').exists():
        plan=deepcopy(read(prior.STUDY/'plan.json'));plan.update(created_at=datetime.now(timezone.utc).isoformat(),
            sources={n:str(STUDY/'candidates'/n/'policy.bas') for n in NAMES},
            scope='36fresh local games of the complete bundle with consecutive-decision hit memory. Prior72local results and inert versions retained. Candidate hosted admission requires full fidelity/runtime checks; already-purchased baseline40blue is retained and audited, never recreated.')
        for c in plan['cases']:c['seed']+=10000
        inputs=[Path(x) for x in set(plan['sources'].values())|set(plan['opponents'].values())]
        inputs += [Path(__file__),Path(contracts_v3.__file__),STUDY/'config.json',INITIAL/'diagnosis.json']
        plan['inputs_sha256']={str(p):digest(p.read_bytes()) for p in inputs}
        plan['gate']['fidelity']+=' Cold focus entry and decision gaps must not treat historical hits as a new hit.'
        write(STUDY/'plan.json',plan)
        write(prior.STUDY/'hosted-disposition.json',{'status':'candidate_admission_stopped',
            'reason':'Consecutive-decision freshness missing at focus entry. Both inert candidates withheld before their XP. Preserve baseline request and all72preceding local games.',
            'replacement':str(STUDY/'plan.json')})


def boundary_scenarios():
    rows=[]
    for name,old_name in zip(NAMES[1:],prior.NAMES[1:]):
        path=STUDY/'candidates'/name/'policy.bas'
        c=case(slot=1,tick=5000,x=97,y=18);enemy=obj(106,kind=2,team=1,x=96,y=20,hp=600)
        enemy.update(objectClass=1,objectTarget=29);c['objects'].append(enemy);c['self']['selfAttacksLanded']=20
        old=run(prior.STUDY/'candidates'/old_name/'policy.bas',[c],memory=[])[0]
        assert any(x['command']=='walkTo' for x in old['actions']),'Regression trigger changed'
        a=run(path,[c],memory=[])[0];rows.append(a)
        assert not any(x['command']=='walkTo' for x in a['actions'])
        assert any(x['command']=='attackTarget' for x in a['actions'])
        gap=deepcopy(c);gap['self'].update(worldTick=5100,selfAttacksLanded=21)
        a=run(path,[c,gap],memory=[])[-1];rows.append(a)
        assert not any(x['command']=='walkTo' for x in a['actions'])
    write(STUDY/'boundary-proof.json',{'passed':True,'checks':['old source reproduces stale initial recovery',
        'new source attacks on cold focus entry','decision gap prevents stale recovery'],'rows':rows})


if __name__=='__main__':
    prepare();shared.STUDY=STUDY;shared.NAMES=NAMES
    shared.scenarios();prior.STUDY=STUDY;prior.NAMES=NAMES;prior.extra_scenarios()
    # Restore the original source location for the explicit old/new regression.
    prior.STUDY=INITIAL/'cadence';prior.NAMES=('coached_baseline','transition_cadence','transition_armor_cadence')
    boundary_scenarios();shared.local()
