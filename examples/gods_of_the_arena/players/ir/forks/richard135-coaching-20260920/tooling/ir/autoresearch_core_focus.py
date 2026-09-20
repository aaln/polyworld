"""Direct accepted-parent children for a scoped structural-pressure hypothesis."""
from pathlib import Path
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import read,digest,refresh_grounding,bundle
C=Path('/Users/aaln/experiments/softmax/gota-autoresearch')
F=C/'forks/fork_20260919_022654_d61958';STUDY=F/'core_focus'
VARIANTS=('parent','role64_reference','core20','rolecore20')

def make(name):
    parent=read(C/'snapshots/0000-b2693715459d/policy.ir.json')
    role=read(F/'role_raid/candidates/role64/policy.ir.json')
    if name=='parent':return parent
    if name=='role64_reference':return role
    assert name in ('core20','rolecore20')
    p=deepcopy(role if name=='rolecore20' else parent)
    operator='lineup_red_role_core_focus_v1' if name=='rolecore20' else 'lineup_red_core_focus_v1'
    old=p['skill']['observe']['parameters']
    parameters={k:old.get(k,v[0]) for k,v in CONTRACTS[operator].parameters.items()}
    parameters['redbranch_focus_radius']=20
    p['id']='autoresearch_20260919_'+name
    p['skill']['observe']={'operator':operator,'parameters':parameters}
    p['situation']['notes']='Published2026.9.16.5. Use current observed enemy kind/alive/HP/target and the newly selected positive-HP friendly anchor relative to own fort. No private source, hidden unit, opponent label or seed matching. An observed target is an order, not proof of damage. Preserve all original geometry and blue behavior.'
    for claim in p['belief']['claims'].values():
        claim['claim']='Inherited component/ancestor evidence, not a measurement of '+name+'. '+claim['claim']
    p['belief']['claims']['B_core_focus']={'status':'untested','claim':read(STUDY/'prospective.json')['hypothesis'],
        'evidence':[{'artifact':str(STUDY/'prospective.json'),'sha256':digest((STUDY/'prospective.json').read_bytes())}]}
    p['goal']['G_defense']['preference']+=' During active red defense, give first target priority to an already eligible hostile creep visibly targeting the newly watched friendly base anchor within20tiles of own fort. Never reuse a missing or dead priority anchor. Keep original alarms and commitment geometry; compare hero survival and actual structural progress.'
    p['goal']['G_survival']['preference']+=' Core-pressure targeting may leave attacking heroes alive longer; require the prospectively fixed survival ceilings versus parent and the relevant Role64 control.'
    p['goal']['G_fort']['preference']='Actual fort wins on each color decide improvement. Core20 needs parent/archive red gain; Rolecore20 must additionally add red fort wins over unchanged Role64 and retain every control win. No kill, gold, creep count or defense-duration substitution.'
    for rule in p['strategy']:
        if rule['id']=='R1':rule['for']=list(dict.fromkeys(rule['for']+['G_defense','G_survival','G_fort']))
    p['execution']['game_version']='2026.9.16.5'
    p['update'].update(parent=digest(parent),revision=parent['update']['revision']+1,
        change='New watched-base creep priority '+name+'; Role64 component retained only for the combined variant.',
        needs_review=['belief/B_core_focus','goal/G_defense','goal/G_survival','goal/G_fort'])
    refresh_grounding(p);return p

if __name__=='__main__':
    for name in VARIANTS:
        bundle(make(name),STUDY/'candidates'/name);print(name,'exact compile/reverse complete',flush=True)
