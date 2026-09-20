"""New accepted-parent combination; failed component evidence remains explicit."""
from pathlib import Path
from copy import deepcopy
from policy_ir import read,digest,refresh_grounding,bundle
C=Path('/Users/aaln/experiments/softmax/gota-autoresearch');F=C/'forks/fork_20260919_102345_6fb224';STUDY=F/'role_dense'
VARIANTS=('parent','role64_reference','dense_reference','role_dense')
def make(name):
    parent=read(C/'snapshots/0000-b2693715459d/policy.ir.json')
    role=read(C/'forks/fork_20260919_022654_d61958/role_raid/discovery-rejection-feedback/role64/policy.ir.json')
    dense=read(F/'dense_cadence/candidates/dense_all/policy.ir.json')
    if name=='parent':return parent
    if name=='role64_reference':return role
    if name=='dense_reference':return dense
    assert name=='role_dense'
    p=deepcopy(parent);p['id']='autoresearch_20260919_role_dense';p['skill']['observe']=deepcopy(role['skill']['observe']);p['skill']['attack']=deepcopy(dense['skill']['attack'])
    p['situation']['notes']='Published2026.9.16.5. Use current observed damaged standing towers, visible enemy pairs, own class and relative living-ally rank for scoped sentry recruitment. Use only current self-hit/cooldown and consecutive decision timing for bounded dense recovery. No opponent label, seed branch, hidden state or assumption of arrival from a command. Missing enemies remain unobserved.'
    for b in p['belief']['claims'].values():b['claim']='Inherited ancestor evidence, not a measurement of RoleDense. '+b['claim']
    p['belief']['claims']['B_role_dense']={'status':'untested','claim':read(STUDY/'prospective.json')['hypothesis'],'evidence':[{'artifact':str(STUDY/'prospective.json'),'sha256':digest((STUDY/'prospective.json').read_bytes())}]}
    p['belief']['claims']['B_failed_role_component']={'status':'requires_review','claim':'Role64 failed its unchanged hosted discovery count gate. Reusing its bounded response contract here does not qualify that policy or establish additive benefit. This combined package needs its own complete local and fresh hosted evidence.','evidence':[{'artifact':str(C/'forks/fork_20260919_022654_d61958/role_raid/hosted/discovery-result.json'),'sha256':digest((C/'forks/fork_20260919_022654_d61958/role_raid/hosted/discovery-result.json').read_bytes())}]}
    p['goal']['G_defense']['preference']=role['goal']['G_defense']['preference']+' While dense combat prevents the full recovery scan, use the separately bounded post-hit recovery skill. Response and combat may interact; measure the combined policy against both components.'
    p['goal']['G_cadence']['preference']=dense['goal']['G_cadence']['preference']+' RoleDense uses the all-eligible scope; this choice is adaptive from the completed standalone screen.'
    p['goal']['G_fort']['preference']='Actual fort wins decide improvement. Retain every parent and component opponent/color count, add red wins over each standalone component, and satisfy fresh parent win and survival gates. Kills and recovery events are diagnostics only.'
    p['goal']['G_survival']['preference']+=' Scoped recruitment and recovery can delay progress or lose attack range; complete audited games must satisfy the precommitted parent death ceiling.'
    for rule in p['strategy']:
        if rule['id'] in ('R1','R2','R4'):rule['for']=list(dict.fromkeys(rule['for']+['G_fort','G_defense']))
    p['execution']['game_version']='2026.9.16.5'
    p['update'].update(parent=digest(parent),revision=parent['update']['revision']+1,change='New coordinated role-specific small-raid response plus constant-work dense recovery; direct accepted-parent lineage.',needs_review=['belief/B_role_dense','belief/B_failed_role_component','goal/G_fort','goal/G_survival'])
    refresh_grounding(p);return p
if __name__=='__main__':
    for n in VARIANTS:bundle(make(n),STUDY/'candidates'/n);print(n,'exact full roundtrip complete',flush=True)
