"""Prospectively registered wave counterpressure fork, September 19 cycle one."""
from copy import deepcopy
from pathlib import Path
from binding import CONTRACTS
from policy_ir import read, digest, refresh_grounding, bundle

FORK = Path('/Users/aaln/experiments/softmax/gota-autoresearch/forks/fork_20260919_022654_d61958')
STUDY = FORK / 'wave_followup'
VARIANTS = ('parent', 'wave_release', 'outer_converge')


def make(name):
    parent = read(STUDY / 'captured-parent/policy.ir.json')
    if name == 'parent':
        return parent
    assert name in VARIANTS
    p = deepcopy(parent)
    p['id'] = 'autoresearch_20260919_' + name
    changes = {'observe': 'lineup_autowave_v1' if name == 'wave_release' else 'lineup_autoouter_v1'}
    if name == 'outer_converge':
        changes['fallback'] = 'lineup_autoouter_route_v1'
    for key, operator in changes.items():
        prior = p['skill'][key]['parameters']
        p['skill'][key] = {'operator': operator, 'parameters': {
            k: prior.get(k, v[0]) for k, v in CONTRACTS[operator].parameters.items()}}
    p['skill']['observe']['parameters'].update(redbranch_split_quiet=360, redbranch_rear_radius=30)
    p['situation']['notes'] += (' Current experiment distinguishes shared living allied '
        'outer-lane progress from a forced center assault. Only current observations '
        'and retained own decisions enter execution. Enemy absence is not death.')
    p['belief']['claims']['B_wave_counterpressure'] = {
        'status': 'untested', 'claim': read(STUDY / 'prospective.json')['hypothesis'],
        'evidence': [{'artifact': str(STUDY / 'prospective.json'),
                      'sha256': digest((STUDY / 'prospective.json').read_bytes())}]}
    p['goal']['G_defense']['preference'] = (
        'Retain initial parent red defense and blue behavior. After an actual red '
        'alarm, release only after 15 seconds with fewer than three living visible '
        'enemies within60 home, none within10 home and three allies assembled '
        'within28 home. During advance, at most Lich and Warlock cover visible '
        'hero pressure within30 home or recent core creeps. Three returning visible '
        'heroes or observed fort damage recall the team. No guarantee of safe release.')
    p['goal']['G_wave']['preference'] = (
        'After release preserve the original allied wave escort and ordinary '
        'structure selection.' if name == 'wave_release' else
        'After release converge on the outer lane containing the living allied '
        'hero nearest the enemy fort, then follow its public waypoints; retain '
        'local combat and focus that lane plus guards and fort.')
    p['goal']['G_fort']['preference'] += ' Judge counterpressure by actual fort wins on each color; draws count zero.'
    for rule in p['strategy']:
        if rule['id'] in ('R1', 'R4'):
            rule['for'] = list(dict.fromkeys(rule['for'] + ['G_wave', 'G_fort']))
    p['execution']['game_version'] = '2026.9.16.5'
    p['update'].update(revision=parent['update']['revision'] + 1,
        parent=digest(parent), change='Versioned wave counterpressure: ' + name,
        needs_review=['belief/B_wave_counterpressure', 'goal/G_wave', 'goal/G_defense'])
    refresh_grounding(p)
    return p


if __name__ == '__main__':
    for name in VARIANTS:
        bundle(make(name), STUDY / 'candidates' / name)
        print(name, flush=True)
