"""Accepted-parent economic ablation and coordinated physical-recovery sibling."""
from copy import deepcopy
from pathlib import Path
from policy_ir import read, digest, refresh_grounding, bundle

C=Path('/Users/aaln/experiments/softmax/gota-autoresearch')
F=C/'forks/fork_20260919_102345_6fb224'
STUDY=F/'last_slot_axe'
VARIANTS=('parent','readiness_reference','axe_only','readiness_axe')

def make(name):
    parent=read(C/'snapshots/0000-b2693715459d/policy.ir.json')
    if name=='parent': return parent
    reference=read(F/'readiness/candidates/first_level/policy.ir.json')
    if name=='readiness_reference': return reference
    assert name in VARIANTS
    p=deepcopy(parent)
    p['id']='autoresearch_20260919_'+name
    p['situation']['notes']='Published2026.9.16.5; observe own six-slot inventory and physical melee class. At exactly five equipment, no sword13/axe18, reserve last slot for180gold axe18. No hidden state, seed, opponent, or match clock. Earlier sustain and all unrelated purchase logic remain. '+('Combine first-level physical dense recovery using observed selfLevel>=2.' if name=='readiness_axe' else 'Attack/defense/navigation remain accepted-parent behavior.')
    for claim in p['belief']['claims'].values():
        claim['claim']='Inherited evidence, not a measurement of '+name+'. '+claim['claim']
    prospective=STUDY/'prospective.json'
    p['belief']['claims']['B_last_slot_axe']={'status':'untested','claim':read(prospective)['hypothesis'],'evidence':[{'artifact':str(prospective),'sha256':digest(prospective.read_bytes())}]}
    p['goal']['G_capacity']['preference']='Avoid permanent loss of last equipment capacity to a150gold sword when saving30moregold buys14damage rather than10. Observe actual accepted inventory changes and timing; no gold or damage surrogate for fort wins.'
    p['goal']['G_survival']['preference']+=' Delay risk must pass prospective native gear, all-class survival and complete fort gates.'
    p['goal']['G_fort']['preference']=read(prospective)['screen']['decision_rule']
    p['skill']['equipment']['operator']='last_slot_melee_axe_v1'
    if name=='readiness_axe':
        p['skill']['attack']=deepcopy(reference['skill']['attack'])
        p['goal']['G_cadence']['preference']='Test first-level physical dense recovery jointly with last-slot equipment capacity. Readiness alone is hosted-rejected; no transfer or superiority assumed.'
    for rule in p['strategy']:
        if rule['id']=='E2':rule['for']=['G_capacity','G_glory','G_fort','G_survival']
    p['execution']['game_version']='2026.9.16.5'
    p['update'].update(parent=digest(parent),revision=parent['update']['revision']+1,change='Final-slot melee axe reservation '+name,needs_review=['belief/B_last_slot_axe','goal/G_capacity','goal/G_cadence','goal/G_fort','goal/G_survival'])
    refresh_grounding(p)
    return p

if __name__=='__main__':
    for name in VARIANTS:
        bundle(make(name),STUDY/'candidates'/name)
        print(name,'exact full IR roundtrip complete',flush=True)
