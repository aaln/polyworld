"""Accepted-parent children for constant-work dense post-hit recovery."""
from pathlib import Path
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import read,digest,refresh_grounding,bundle,HERE
C=Path('/Users/aaln/experiments/softmax/gota-autoresearch')
F=C/'forks/fork_20260919_102345_6fb224';STUDY=F/'dense_cadence'
VARIANTS=('parent','dense_all','dense_ranged')

def make(name):
    parent=read(C/'snapshots/0000-b2693715459d/policy.ir.json')
    if name=='parent':return parent
    assert name in VARIANTS
    p=deepcopy(parent);p['id']='autoresearch_20260919_'+name
    p['skill']['attack']={'operator':'dense_defense_cadence_v1','parameters':parent['skill']['attack']['parameters']|{'dense_all_classes':int(name=='dense_all')}}
    p['situation']['notes']='Published2026.9.16.5. Current visible objects determine original scan fallback. Only consecutive living self snapshots and an increased basic-hit counter with positive cooldown permit new dense recovery. Current own-fort coordinates and terrain query select one homeward tile per axis. No seed, opponent label, hidden state or rival implementation. Accepted movement does not prove displacement or improved damage.'
    for claim in p['belief']['claims'].values():claim['claim']='Inherited ancestor evidence, not a measurement of '+name+'. '+claim['claim']
    p['belief']['claims']['B_dense_cadence']={'status':'untested','claim':read(STUDY/'prospective.json')['hypothesis'],
        'evidence':[{'artifact':str(STUDY/'prospective.json'),'sha256':digest((STUDY/'prospective.json').read_bytes())}]}
    p['goal']['G_cadence']['preference']='Test whether one terrain-checked homeward movement decision after a confirmed hit improves useful combat recovery in dense observations. The all-eligible and ranged-only scopes are separate candidates. Preserve the original sparse controller and immediate attack fallback after failed movement.'
    p['goal']['G_survival']['preference']+=' Dense homeward movement can lose range or delay spells. Require fixed deaths ceiling on each complete local study; no claim that a one-tick movement is an escape.'
    p['goal']['G_fort']['preference']='Improve actual fort wins on both colors. Require cellwise local nonregression and added red parent/archive wins before hosted discovery. Kills, post-hit steps, gold or attack rate cannot substitute for fort wins.'
    for rule in p['strategy']:
        if rule['id']=='R2':rule['for']=['G_fort','G_cadence','G_survival','G_defense']
    p['execution']['game_version']='2026.9.16.5'
    p['update'].update(parent=digest(parent),revision=parent['update']['revision']+1,change='Constant-work dense post-hit recovery '+name,
        needs_review=['belief/B_dense_cadence','goal/G_cadence','goal/G_survival','goal/G_fort'])
    refresh_grounding(p);return p

if __name__=='__main__':
    for name in VARIANTS:
        bundle(make(name),STUDY/'candidates'/name);print(name,'exact compile/reverse complete',flush=True)
