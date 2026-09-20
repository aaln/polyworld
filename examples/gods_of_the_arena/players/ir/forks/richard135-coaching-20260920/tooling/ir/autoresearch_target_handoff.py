"""Accepted-parent siblings for observed target handoff and hit readiness."""
from pathlib import Path
from copy import deepcopy
from policy_ir import read, digest, refresh_grounding, bundle

C = Path('/Users/aaln/experiments/softmax/gota-autoresearch')
F = C/'forks/fork_20260920_045449_29b23b'
STUDY = F/'target_handoff'
REFERENCE = C/'forks/fork_20260919_212453_e79df8/target_geometry/candidates/suppress_toward'
VARIANTS = ('parent','suppression_reference','handoff','handoff_hits8')


def make(name):
    parent = read(C/'snapshots/0000-b2693715459d/policy.ir.json')
    if name == 'parent':
        return parent
    reference = read(REFERENCE/'policy.ir.json')
    if name == 'suppression_reference':
        return reference
    assert name in VARIANTS
    plan = read(STUDY/'prospective.json')
    evidence = dict(artifact=str(STUDY/'prospective.json'),sha256=digest((STUDY/'prospective.json').read_bytes()))
    p = deepcopy(parent)
    p['id'] = 'autoresearch_20260920_'+name
    p['situation']['notes'] = ('Published2026.9.16.5. Current bestId/object kind and '
        'public selfTarget identify an intended nonhero attack handoff. selfTarget '
        'is current ordered/auto-acquired target, not necessarily the last-hit victim. '
        'Observed lifetime basic hits can differ from earned level; hits persist '
        'through respawns. No hidden state or opponent/seed predicates.')
    for claim in p['belief']['claims'].values():
        claim['claim'] = 'Inherited ancestor evidence, not a measurement of '+name+'. '+claim['claim']
    p['belief']['claims']['B_nonhero_handoff'] = dict(status='untested',claim=plan['hypothesis'],evidence=[evidence])
    p['belief']['claims']['B_hit_readiness_scope'] = dict(status='untested',
        claim=('This sibling additionally permits level1 recovery after8observed lifetime basic hits; unchanged new-hit, gap, cooldown, physical-class and geometry guards still apply.' if name=='handoff_hits8' else 'This sibling retains the suppression reference level2 gate; verified-hit fallback disabled.'),evidence=[evidence])
    p['goal']['G_cadence']['preference'] = ('Commit a newly selected nonhero attack before '
        'an extra recovery walk, preserving hero-to-hero and same-target recovery. '
        'Test the optional public hit-count fallback separately; neither change '
        'is presumed to improve damage, safety or fort conversion.')
    p['goal']['G_survival']['preference'] = ('Retain both comparator survival bounds and '
        'inspect every class. A target handoff is an order-priority choice; it '
        'does not establish collision, a safer path or the identity of the last victim.')
    p['goal']['G_fort']['preference'] = plan['screen']['decision_rule']+' '+plan['confirmation']['decision_rule']
    p['skill']['attack'] = dict(operator='target_handoff_cadence_v1',
        parameters=reference['skill']['attack']['parameters'] | {'verified_hits':8 if name=='handoff_hits8' else 0})
    for rule in p['strategy']:
        if rule['id']=='R2':
            rule['for'] = ['G_fort','G_cadence','G_survival','G_defense']
    p['execution'] = dict(binding='gota-basic/1',game_version='2026.9.16.5',language='BASIC')
    p['update'].update(parent=digest(parent),revision=parent['update']['revision']+1,
        change='Accepted-parent coordinated physical recovery and nonhero target handoff: '+name,
        evidence=p['update']['evidence']+[evidence],
        needs_review=['belief/B_nonhero_handoff','belief/B_hit_readiness_scope','goal/G_cadence','goal/G_survival','goal/G_fort'])
    refresh_grounding(p)
    return p


if __name__ == '__main__':
    for name in VARIANTS:
        bundle(make(name),STUDY/'candidates'/name)
        print(name,'full IR compile and reverse parity complete',flush=True)
