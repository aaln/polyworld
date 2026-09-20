"""Red non-sentry release hypotheses from the fully reconstructed black-kite draw."""
from copy import deepcopy
from policy_ir import read, digest, refresh_grounding
from release_workspace import RUN

STUDY = RUN / 'coached-lanes/r5-red-pressure'
PARENT = RUN / 'coached-lanes/r5-jordan-lineup/deployment-requested/policy'
VARIANTS = {'deployed': {}, 'pressure20': {'pressure_hold': 480, 'pressure_continue': 0},
            'pressure40': {'pressure_hold': 960, 'pressure_continue': 0},
            'pressure60': {'pressure_hold': 1440, 'pressure_continue': 0},
            'pressure20_near': {'pressure_hold': 480, 'pressure_continue': 16}}


def make(name):
    parent = read(PARENT / 'policy.ir.json')
    if name == 'deployed': return parent
    p = deepcopy(parent); p['id'] = 'gota_red_' + name
    parameters = p['skill']['observe']['parameters'] | {'redbranch_' + k: v for k, v in VARIANTS[name].items()}
    p['skill']['observe'] = {'operator': 'lineup_pressure_observe', 'parameters': parameters}
    p['goal']['G_defense']['preference'] += (
        f' Keep all three red sentries committed; release Crossbowman and Berserker '
        f'{VARIANTS[name]["pressure_hold"]}/24 seconds after the last observed group trigger. '
        f'Only a survivor within {VARIANTS[name]["pressure_continue"]} tiles of home may refresh their duty. '
        'A fresh observed group recalls them again. Preserve blue behavior exactly.')
    evidence = STUDY / 'diagnosis.json'
    p['belief']['claims']['B_red_pressure'] = {'claim': (
        'In the source-matched black-kite13 red draw ereq_04b38f64, all209417ownedcommands '
        'and28800statehashes were reconstructed. From400seconds onward, both attacking roles '
        'repeatedly retained defense with only one visible enemy counted near home; their '
        'short clocks were continually refreshed. Enemy towers all survived and both gods '
        'finished full health despite89enemyhero deaths. Hypothesis: retain three sentries '
        'while requiring a fresh group to renew attacker recalls, restoring objective pressure. '
        'This replay diagnoses retention; it does not prove this change wins.'),
        'status': 'untested', 'evidence': [{'artifact': str(evidence), 'sha256': digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision'] + 1, parent=digest(parent),
                       change='Role-specific red recall retention: ' + name)
    refresh_grounding(p)
    return p
