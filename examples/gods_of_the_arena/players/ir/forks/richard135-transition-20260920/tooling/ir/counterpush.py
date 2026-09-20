"""Coached Richard78 macro hypotheses; preserve the deployed blue branch."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import read, digest, refresh_grounding
from release_workspace import RUN

STUDY = RUN / 'coached-lanes/r5-counterpush'
PARENT = RUN / 'coached-lanes/r5-jordan-lineup/deployment-requested/policy'
VARIANTS = ['deployed', 'pressure_parent', 'release20', 'release40', 'tank60']
PARAMS = {'release20': (480, 480), 'release40': (960, 960), 'tank60': (480, 1440)}


def make(name):
    parent = read(PARENT / 'policy.ir.json')
    if name in ('deployed', 'pressure_parent'): return parent
    quiet, tank = PARAMS[name]
    p = deepcopy(parent); p['id'] = 'gota_counterpush_' + name
    p['skill']['observe'] = {'operator': 'lineup_counterpush_observe_v2', 'parameters':
        parent['skill']['observe']['parameters'] | {
            'redbranch_counter_quiet': quiet, 'redbranch_tank_quiet': tank}}
    route = parent['skill']['fallback']['parameters']
    p['skill']['fallback'] = {'operator': 'lineup_counterpush_route', 'parameters':
        CONTRACTS['lineup_counterpush_route'].defaults() | route}
    p['goal']['G_defense']['preference'] = (
        f'Red defense is a temporary response to observed pressure. Retire destroyed anchors; '
        f'release roles after {quiet}/24 seconds without actual pressure or combat, with '
        f'DeathKnight retaining {tank}/24 seconds. Resume creep-backed lane objectives through '
        'the existing objective selector. Reacquire defense on a fresh visible rush. Use '
        'class-separated rally points while defending. Preserve blue behavior, purchases, '
        'and combat survival. Do not infer hidden attackers are absent.')
    evidence = STUDY / 'diagnosis.json'
    p['belief']['claims']['B_counterpush'] = {'claim': (
        'In Richard78 league loss ereq_9a4bd7d2, all 105265 owned commands and 17356 state '
        'hashes were reconstructed. At8760 four living defenders had no target and shared '
        'rally73,11 after their anchor tower11 was destroyed. Three retained duty until15811. '
        'The paired XP cohort is blue40W versus red11W24L5D; blue-only wins do not establish '
        'red strength. Hypothesis: retire stale anchors and convert quiet defense into '
        'coordinated lane pressure, keeping public threat detection. This is unvalidated.'),
        'status': 'untested', 'evidence': [{'artifact': str(evidence), 'sha256': digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision'] + 1, parent=digest(parent),
                       change='Richard78 defense-to-counterpush transition and spacing: ' + name)
    refresh_grounding(p)
    return p
