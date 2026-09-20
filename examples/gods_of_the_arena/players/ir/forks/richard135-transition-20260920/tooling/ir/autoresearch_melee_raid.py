"""Accepted-parent child retaining melee small-raid response and ranged attacks."""
from copy import deepcopy
from pathlib import Path
from binding import CONTRACTS
from policy_ir import read, digest, refresh_grounding, bundle

C = Path('/Users/aaln/experiments/softmax/gota-autoresearch')
STUDY = C/'forks/fork_20260919_022654_d61958/melee_raid'
VARIANTS = ('parent', 'melee64')


def make(name):
    parent = read(C/'snapshots/0000-b2693715459d/policy.ir.json')
    if name == 'parent':
        return parent
    assert name == 'melee64'
    p = deepcopy(parent)
    p['id'] = 'autoresearch_20260919_melee64'
    operator = 'lineup_red_melee_raid_v1'
    old = parent['skill']['observe']['parameters']
    params = {k:old.get(k,v[0]) for k,v in CONTRACTS[operator].parameters.items()}
    params.update(redbranch_raid_damage=150, redbranch_raid_opening=7200,
                  redbranch_raid_responders=2, redbranch_raid_hold=720,
                  redbranch_raid_response=64)
    p['skill']['observe'] = {'operator':operator, 'parameters':params}
    p['situation']['notes'] = (
        'Published2026.9.16.5. Own class distinguishes the heavy ranged carry '
        'from melee and established sentry roles. Current allied positions support '
        'geometric rank; visible enemy clusters and observed standing towerHP '
        'establish the added alarm. Missing enemies are unobserved and coordinate '
        'distance is not arrival. Historical evidence belongs to named ancestors.')
    for claim in p['belief']['claims'].values():
        claim['claim'] = 'Inherited ancestor evidence; not a measurement of melee64. ' + claim['claim']
    evidence = {'artifact':str(STUDY/'prospective.json'),
                'sha256':digest((STUDY/'prospective.json').read_bytes())}
    p['belief']['claims']['B_melee_raid'] = {
        'status':'untested', 'claim':read(STUDY/'prospective.json')['hypothesis'],
        'evidence':[evidence]}
    p['goal']['G_defense']['preference'] = (
        'Retain parent red larger-group defense, class-specific holds and remembered '
        'duties for every hero, and all blue behavior. Before7200ticks, add red '
        'response to a visible pair at a standing lane tower missing150HP. '
        'Exempt Crossbowman from that added trigger; Berserker and existing sentries '
        'remain eligible only among the two nearest living allies and within64 '
        'coordinate tiles. An added-alarm commitment and survivor refresh uses720ticks; '
        'a larger group restores ordinary hold. Existing duties are never canceled '
        'by class, rank or distance. Measure missed coverage and hero survival.')
    p['goal']['G_wave']['preference'] += (
        ' Crossbowman keeps parent local combat and routing during small skirmishes. '
        'Other unassigned heroes keep original wave escort and exposed-objective '
        'selection; no forced lane or post-alarm release is added.')
    p['goal']['G_fort']['preference'] = (
        'Win by destroying the enemy fort while preserving own fort. Actual fort '
        'wins on each color and fixed opponent/survival gates decide qualification. '
        'Kills, gold, XP, time alive and changed routes are diagnostics only.')
    p['goal']['G_glory']['preference'] = 'Historical XP/time diagnostics do not substitute for actual fort wins.'
    for rule in p['strategy']:
        if rule['id'] in ('R1','R4'):
            rule['for'] = list(dict.fromkeys(rule['for']+['G_wave','G_fort']))
    p['execution']['game_version'] = '2026.9.16.5'
    p['update'].update(parent=digest(parent), revision=parent['update']['revision']+1,
        change='New versioned Crossbowman exemption retaining melee small-raid recruitment.',
        needs_review=['belief/B_melee_raid','goal/G_defense','goal/G_wave','goal/G_fort'])
    refresh_grounding(p)
    return p


if __name__ == '__main__':
    for name in VARIANTS:
        bundle(make(name), STUDY/'candidates'/name)
        print(name+' exact compile/reverse extraction complete', flush=True)
