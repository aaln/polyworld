"""Accepted-parent target geometry siblings; rejected readiness is only a control."""
from pathlib import Path
from copy import deepcopy
from policy_ir import read, digest, refresh_grounding, bundle

C = Path('/Users/aaln/experiments/softmax/gota-autoresearch')
F = C/'forks/fork_20260919_212453_e79df8'
STUDY = F/'target_geometry'
VARIANTS = ('parent', 'readiness_reference', 'suppress_toward', 'reverse_toward')


def make(name):
    parent = read(C/'snapshots/0000-b2693715459d/policy.ir.json')
    if name == 'parent': return parent
    if name == 'readiness_reference':
        return read(C/'forks/fork_20260919_102345_6fb224/readiness/candidates/first_level/policy.ir.json')
    assert name in VARIANTS
    plan = read(STUDY/'prospective.json')
    p = deepcopy(parent)
    p['id'] = 'autoresearch_20260919_geometry_'+name
    p['situation']['notes'] = ('Published2026.9.16.5. Dense recovery uses only '
        'current own hit/level/cooldown snapshots, selected visible object kind '
        'and integer coordinates. A positive tile-step dot product denotes '
        'intent toward that target, never actual displacement or collision. '
        'Current target may differ from the last hit or the main threat.')
    for claim in p['belief']['claims'].values():
        claim['claim'] = 'Inherited ancestor evidence, not a measurement of '+name+'. '+claim['claim']
    p['belief']['claims']['B_recovery_geometry'] = {
        'status':'untested', 'claim':plan['hypothesis'],
        'evidence':[{'artifact':str(STUDY/'prospective.json'),
                     'sha256':digest((STUDY/'prospective.json').read_bytes())}]}
    p['goal']['G_cadence']['preference'] = ('Test post-hit physical recovery with '
        'a selected-target direction guard; preserve useful attack timing while '
        'measuring the costs of suppressed swing resets or extra turning.')
    p['goal']['G_survival']['preference'] = ('Preserve the prospective survival '
        'gate and inspect every class; target-relative stepping may still approach '
        'other threats or lose attack range. No inferred collision avoidance.')
    p['goal']['G_fort']['preference'] = plan['screen']['decision_rule']+' '+plan['confirmation']['decision_rule']
    p['skill']['attack'] = {'operator':'target_geometry_cadence_v1',
        'parameters':parent['skill']['attack']['parameters'] |
        {'weapon_melee':1, 'level_defense_only':0,
         'reverse_toward':int(name=='reverse_toward')}}
    for rule in p['strategy']:
        if rule['id']=='R2':rule['for']=['G_fort','G_cadence','G_survival','G_defense']
    p['execution'] = {'binding':'gota-basic/1','game_version':'2026.9.16.5','language':'BASIC'}
    p['update'].update(parent=digest(parent),revision=parent['update']['revision']+1,
        change='Observed selected-target dense recovery geometry: '+name,
        needs_review=['belief/B_recovery_geometry','goal/G_cadence','goal/G_survival','goal/G_fort'])
    refresh_grounding(p)
    return p


if __name__ == '__main__':
    for name in VARIANTS:
        bundle(make(name),STUDY/'candidates'/name)
        print(name,'exact full IR reverse parity complete',flush=True)
