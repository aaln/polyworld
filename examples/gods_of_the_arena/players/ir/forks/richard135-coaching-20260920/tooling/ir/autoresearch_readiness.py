"""Accepted-parent siblings with an observed first-level-up recovery gate."""
from copy import deepcopy
from pathlib import Path
from policy_ir import read, digest, refresh_grounding, bundle

C = Path('/Users/aaln/experiments/softmax/gota-autoresearch')
F = C / 'forks/fork_20260919_102345_6fb224'
STUDY = F / 'readiness'
VARIANTS = ('parent', 'weapon_reference', 'first_level', 'first_level_defense')


def make(name):
    parent = read(C / 'snapshots/0000-b2693715459d/policy.ir.json')
    if name == 'parent': return parent
    if name == 'weapon_reference':
        return read(F / 'weapon_dense/candidates/weapon_all/policy.ir.json')
    assert name in VARIANTS
    p = deepcopy(parent)
    p['id'] = 'autoresearch_20260919_readiness_' + name
    p['situation']['notes'] = ('Published2026.9.16.5. Use observed selfLevel, '
        'whose first progression transition is level2, and inherited defActive. '
        'first_level requires level2 for all additional physical dense recovery; '
        'first_level_defense requires it only during active defense alarms. '
        'Other eligibility, consecutive-hit/cooldown/terrain guards, one-tile '
        'homeward destination and sparse recovery remain. Never infer collision '
        'or use hidden enemies, labels, seeds or elapsed match-time thresholds.')
    for claim in p['belief']['claims'].values():
        claim['claim'] = 'Inherited evidence, not a measurement of ' + name + '. ' + claim['claim']
    p['belief']['claims']['B_readiness'] = {
        'status': 'untested', 'claim': read(STUDY/'prospective.json')['hypothesis'],
        'evidence': [{'artifact': str(STUDY/'prospective.json'),
                      'sha256': digest((STUDY/'prospective.json').read_bytes())}]}
    p['goal']['G_cadence']['preference'] = ('Test whether dense recovery after the '
        'first level-up retains useful combat while protecting initial engagement '
        'timing; swing resets, displacement and damage are not fort-win verdicts.')
    p['goal']['G_defense']['preference'] = ('Preserve accepted-parent dense attack '
        'orders for level1 heroes in the declared context. The level gate does '
        'not change inherited defense detection, target ranking or alarm expiry.')
    p['goal']['G_survival']['preference'] += ' Require fixed complete local survival gates and every-class inspection.'
    p['goal']['G_fort']['preference'] = read(STUDY/'prospective.json')['decision_rule']
    p['skill']['attack'] = {'operator': 'first_level_weapon_cadence_v1',
        'parameters': parent['skill']['attack']['parameters'] |
        {'weapon_melee': 1, 'level_defense_only': int(name == 'first_level_defense')}}
    for rule in p['strategy']:
        if rule['id'] == 'R2': rule['for'] = ['G_fort','G_defense','G_cadence','G_survival']
    p['execution']['game_version'] = '2026.9.16.5'
    p['update'].update(parent=digest(parent), revision=parent['update']['revision']+1,
        change='Physical dense recovery after observed first level-up: '+name,
        needs_review=['belief/B_readiness','goal/G_defense','goal/G_cadence','goal/G_fort'])
    refresh_grounding(p)
    return p


if __name__ == '__main__':
    for name in VARIANTS:
        bundle(make(name), STUDY/'candidates'/name)
        print(name, 'exact full IR roundtrip complete', flush=True)
