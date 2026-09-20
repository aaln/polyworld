"""Accepted-parent child with new versioned active-defense recovery scope."""
from copy import deepcopy
from pathlib import Path
from policy_ir import read,digest,refresh_grounding,bundle
C=Path('/Users/aaln/experiments/softmax/gota-autoresearch');F=C/'forks/fork_20260919_102345_6fb224';STUDY=F/'guard_dense'
VARIANTS=('parent','role64_reference','dense_reference','role_dense_reference','role_guard_dense')
def make(name):
    parent=read(C/'snapshots/0000-b2693715459d/policy.ir.json')
    paths={'parent':C/'snapshots/0000-b2693715459d','role64_reference':F/'role_dense/candidates/role64_reference','dense_reference':F/'dense_cadence/candidates/dense_all','role_dense_reference':F/'role_dense/candidates/role_dense'}
    if name in paths:return read(paths[name]/'policy.ir.json')
    assert name=='role_guard_dense';p=deepcopy(read(paths['role_dense_reference']/'policy.ir.json'));p['id']='autoresearch_20260919_role_guard_dense';p['skill']['attack']['operator']='guarded_dense_defense_cadence_v1'
    p['situation']['notes']='Published2026.9.16.5. Current defActive is the observer\'s current defense commitment, not a ground-truth threat oracle. Inactive defense excludes all new dense movement, including fresh-hit decisions. Active defense uses current hit/cooldown/tick/terrain guards. Role-specific visible-pair recruitment remains as versioned; no opponent, seed or hidden-state branch.'
    for b in p['belief']['claims'].values():b['claim']='Inherited component evidence, not a measurement of RoleGuardDense. '+b['claim']
    p['belief']['claims']['B_guard_dense']={'status':'untested','claim':read(STUDY/'prospective.json')['hypothesis'],'evidence':[{'artifact':str(STUDY/'prospective.json'),'sha256':digest((STUDY/'prospective.json').read_bytes())}]}
    p['goal']['G_cadence']['preference']='During current active defense and dense observations only, attempt one terrain-checked homeward step after a new confirmed hit. Preserve ordinary-push commands and sparse recovery exactly. Resume attack next decision without a new hit; blocked/failed steps attack immediately. New scope may still alter the battle adversely.'
    p['goal']['G_defense']['preference']+=' Dense recovery is now strictly conditioned on current defActive. Preserve the original scoped pair recruitment and pre-alarm behavior; do not infer alarm or tower preservation from the desired goal.'
    p['goal']['G_fort']['preference']='Actual fortwins determine qualification. Retain all four screencontrol cells; in freshconfirmation beat Role64 on red archives and win>=60%against acceptedparent eachcolor without parent/component cell regression or excess deaths. No step/kill/gold proxy.'
    p['goal']['G_survival']['preference']+=' Verify all ten classes and complete parent-comparable deaths under the scoped policy; no early success claim.'
    for rule in p['strategy']:
        if rule['id']=='R2':rule['for']=['G_fort','G_cadence','G_survival','G_defense']
    p['execution']['game_version']='2026.9.16.5'
    p['update'].update(parent=digest(parent),revision=parent['update']['revision']+1,change='New active-defense-only dense recovery combined with scoped sentry-pair response; direct accepted-parent lineage.',needs_review=['belief/B_guard_dense','goal/G_cadence','goal/G_defense','goal/G_fort'])
    refresh_grounding(p);return p
if __name__=='__main__':
    # Author new candidate first; exact known reference bundles are independently verified too.
    for n in ['role_guard_dense',*VARIANTS[:-1]]:bundle(make(n),STUDY/'candidates'/n);print(n,'exact fullroundtrip complete',flush=True)
