"""Accepted-parent children with published physical attack-style cadence scopes."""
from pathlib import Path
from copy import deepcopy
from policy_ir import read,digest,refresh_grounding,bundle
C=Path('/Users/aaln/experiments/softmax/gota-autoresearch');F=C/'forks/fork_20260919_102345_6fb224';STUDY=F/'weapon_dense'
VARIANTS=('parent','dense_reference','weapon_ranged','weapon_all')
def make(name):
    parent=read(C/'snapshots/0000-b2693715459d/policy.ir.json')
    if name=='parent':return parent
    if name=='dense_reference':return read(F/'dense_cadence/candidates/dense_all/policy.ir.json')
    assert name in VARIANTS
    p=deepcopy(parent);p['id']='autoresearch_20260919_'+name
    p['skill']['attack']={'operator':'weapon_dense_defense_cadence_v1','parameters':parent['skill']['attack']['parameters']|{'weapon_melee':int(name=='weapon_all')}}
    p['situation']['notes']='Published2026.9.16.5. Class scope derives from HeroSpec.attackStyle: physical RangedAttack1/6, optionally MeleeAttack0/4/5; Berserker9 inherited exclusion. MagicAttack2/3/7/8 preserves parent commands. Consecutive observed self snapshots, new hit and positive attack cooldown guard dense recovery. Current own-fort terrain-checked destination; no seed/opponent/hidden-state branch. Accepted movement may reset swing without displacement.'
    for claim in p['belief']['claims'].values():claim['claim']='Inherited ancestor evidence, not a measurement of '+name+'. '+claim['claim']
    p['belief']['claims']['B_weapon_cadence']={'status':'untested','claim':read(STUDY/'prospective.json')['hypothesis'],'evidence':[{'artifact':str(STUDY/'prospective.json'),'sha256':digest((STUDY/'prospective.json').read_bytes())}]}
    p['goal']['G_cadence']['preference']='Test post-hit recovery only for the explicit physical attack-style scope, preserving magic-class combat timing. Native first-step reset without movement is a possible mechanism, not an escape or guaranteed higher damage.'
    p['goal']['G_survival']['preference']+=' Check every class and actual full-team survival under both physical-class scopes; class membership does not establish benefit.'
    p['goal']['G_fort']['preference']='Retain every parent/DenseAll screen fort-win cell and add a red win over DenseAll, then meet fresh both-color parent/archives confirmation with>=60%actual parent wins eachcolor and center stress. Faster hits and isolated Crossbow success cannot replace complete fort-win gates.'
    for rule in p['strategy']:
        if rule['id']=='R2':rule['for']=['G_fort','G_cadence','G_survival','G_defense']
    p['execution']['game_version']='2026.9.16.5'
    p['update'].update(parent=digest(parent),revision=parent['update']['revision']+1,change='Physical attack-style dense post-hit recovery '+name,needs_review=['belief/B_weapon_cadence','goal/G_cadence','goal/G_survival','goal/G_fort'])
    refresh_grounding(p);return p
if __name__=='__main__':
    for n in ['weapon_ranged','weapon_all','parent','dense_reference']:bundle(make(n),STUDY/'candidates'/n);print(n,'exact fullroundtrip complete',flush=True)
