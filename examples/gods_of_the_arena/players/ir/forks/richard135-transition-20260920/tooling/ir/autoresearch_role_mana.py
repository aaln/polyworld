"""Coordinated sentry response and mana purchasing, directly from accepted parent."""
from copy import deepcopy
from pathlib import Path
from autoresearch_role_raid import make as role_make
from policy_ir import read, digest, refresh_grounding, bundle

C=Path('/Users/aaln/experiments/softmax/gota-autoresearch')
STUDY=C/'forks/fork_20260919_022654_d61958/role_mana'
VARIANTS=('parent','role64_reference','rolebuy40')

def make(name):
    parent=role_make('parent')
    if name=='parent':return parent
    reference=read(STUDY.parent/'role_raid/candidates/role64/policy.ir.json')
    if name=='role64_reference':return reference
    assert name=='rolebuy40'
    p=deepcopy(reference)
    p['id']='autoresearch_20260919_rolebuy40'
    p['skill']['sustain']['operator']='buy_mana_aligned_v1'
    p['situation']['notes']=(
        'Published 2026.9.16.5. Visible damaged tower pairs, current living ally '
        'geometry and public sentry roles drive bounded recruitment. Own starting '
        'mana/maxmana and live inventory presence drive purchases. Strict40% mana '
        'buying aligns with consumption; no inference about future regeneration, '
        'arrival or enemy identity. All ancestor evidence is explicitly historical.')
    for claim in p['belief']['claims'].values():
        claim['claim']='Inherited component evidence, not a measurement of rolebuy40. '+claim['claim']
    p['belief']['claims']['B_role_mana']={
        'status':'untested','claim':read(STUDY/'prospective.json')['hypothesis'],
        'evidence':[{'artifact':str(STUDY/'prospective.json'),'sha256':digest((STUDY/'prospective.json').read_bytes())}]}
    p['goal']['G_capacity']['preference']=(
        'Buy mana only strictly below40%, retain immediate emergency healing, '
        'consumption and class gear progression. Test whether lower spending '
        'reduces sentry death cost while preserving fort wins; no guaranteed gain.')
    p['goal']['G_defense']['preference']+=(
        ' Mana purchasing is coordinated with this bounded response; fort wins '
        'must not regress against the unchanged Role64 component reference.')
    p['goal']['G_survival']['preference']+=(
        ' Require strictly fewer deaths than the Role64 reference in screen and '
        'across confirmation plus stress, within the accepted-parent survival ceiling.')
    for rule in p['strategy']:
        if rule['id'] in ('E0','E1','E2'):
            rule['for']=list(dict.fromkeys(rule['for']+['G_capacity','G_survival','G_fort','G_defense']))
    p['execution']['game_version']='2026.9.16.5'
    p['update'].update(parent=digest(parent),revision=parent['update']['revision']+1,
        change='Direct accepted-parent child: bounded sentry response plus aligned40% mana purchasing. Role64 is a reference, not accepted lineage.',
        needs_review=['belief/B_role_mana','goal/G_capacity','goal/G_defense','goal/G_survival'])
    refresh_grounding(p)
    return p

if __name__=='__main__':
    for name in VARIANTS:
        bundle(make(name),STUDY/'candidates'/name)
        print(name+' exact compile/full reverse parity complete',flush=True)
