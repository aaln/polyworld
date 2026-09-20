"""Accepted-parent child with measured hypothesis and role-specific recruitment."""
from copy import deepcopy
from pathlib import Path
from binding import CONTRACTS
from policy_ir import read, digest, refresh_grounding, bundle

C = Path('/Users/aaln/experiments/softmax/gota-autoresearch')
STUDY = C / 'forks/fork_20260919_022654_d61958/role_raid'
VARIANTS = ('parent', 'role64')


def make(name):
    parent = read(C / 'snapshots/0000-b2693715459d/policy.ir.json')
    if name == 'parent':
        return parent
    assert name == 'role64'
    p = deepcopy(parent)
    p['id'] = 'autoresearch_20260919_role64'
    operator = 'lineup_red_role_raid_v1'
    old = parent['skill']['observe']['parameters']
    params = {k: old.get(k, v[0]) for k, v in CONTRACTS[operator].parameters.items()}
    params.update(redbranch_raid_damage=150, redbranch_raid_opening=7200,
                  redbranch_raid_responders=2, redbranch_raid_hold=720,
                  redbranch_raid_response=64)
    p['skill']['observe'] = {'operator': operator, 'parameters': params}
    p['situation']['notes'] = (
        'Published2026.9.16.5. Allied current positions and own class support '
        'geometric recruitment and existing sentry-role arbitration. Only visible '
        'enemy clusters and observed standing towerHP establish a small alarm. '
        'Missing enemies remain unobserved; geometry is not arrival. Historical '
        'validation belongs to the named ancestor in each belief, not this candidate.')
    for claim in p['belief']['claims'].values():
        claim['claim'] = 'Inherited ancestor evidence; not a measurement of role64. ' + claim['claim']
    evidence = {'artifact': str(STUDY/'prospective.json'),
                'sha256': digest((STUDY/'prospective.json').read_bytes())}
    p['belief']['claims']['B_role_raid'] = {
        'status': 'untested', 'claim': read(STUDY/'prospective.json')['hypothesis'],
        'evidence': [evidence]}
    p['goal']['G_defense']['preference'] = (
        'Retain parent red larger-group alarms, class-specific holds and remembered '
        'duties for every hero, and all blue behavior. Before7200ticks, additionally '
        'allow red sentry roles to respond to a visible pair at a standing lane tower '
        'missing150HP. New responders must rank among the two nearest living allies '
        'and be within64coordinate tiles. An added-alarm commitment and survivor '
        'refresh lasts720ticks; a larger group restores ordinary hold. Do not cancel '
        'existing commitments. Attack roles retain parent small-skirmish decisions. '
        'Measure missed coverage, survival and fort wins.')
    p['goal']['G_wave']['preference'] += (
        ' Preserve original local combat, wave escort and exposed-objective selection '
        'for non-recruited heroes. No forced lane or post-alarm release is added.')
    p['goal']['G_fort']['preference'] = (
        'Win by destroying the enemy fort while preserving own fort. Actual fort wins '
        'on each color decide qualification. Kills, gold, XP and movement are diagnostics. '
        'Require prospective opponent/color nonregression and survival checks.')
    p['goal']['G_glory']['preference'] = 'Historical XP/time diagnostics never substitute for actual fort wins.'
    for rule in p['strategy']:
        if rule['id'] in ('R1', 'R4'):
            rule['for'] = list(dict.fromkeys(rule['for'] + ['G_wave', 'G_fort']))
    p['execution']['game_version'] = '2026.9.16.5'
    p['update'].update(parent=digest(parent), revision=parent['update']['revision']+1,
        change='New versioned sentry-only small-raid recruitment, role64.',
        needs_review=['belief/B_role_raid', 'goal/G_defense', 'goal/G_wave', 'goal/G_fort'])
    refresh_grounding(p)
    return p


if __name__ == '__main__':
    for name in VARIANTS:
        bundle(make(name), STUDY/'candidates'/name)
        print(name+' exact compile/reverse extraction complete', flush=True)
