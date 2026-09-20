from copy import deepcopy
from policy_ir import read, digest, refresh_grounding
from release_workspace import RUN
from red_pressure import make as pressure

STUDY = RUN / 'coached-lanes/r5-shared-engagement'
VARIANTS = ['deployed', 'pressure_parent', 'shared_two', 'shared_three', 'tower_hold']


def make(name):
    if name == 'deployed': return pressure('deployed')
    parent = pressure('pressure20')
    if name == 'pressure_parent': return parent
    p = deepcopy(parent)
    p['id'] = 'gota_' + name
    p['skill']['observe']['operator'] = 'lineup_shared_engagement'
    p['skill']['observe']['parameters'].update(redbranch_ready_count={
        'shared_two': 2, 'shared_three': 3, 'tower_hold': 6}[name], redbranch_ready_hp=150)
    p['goal']['G_defense']['preference'] += (
        ' Coordinate the nearby defensive group on a shared visible threat. Count healthy '
        'support before charging; when insufficient, hold at the current friendly tower '
        'until the enemy enters its firing zone. Recall only heroes already near our core '
        'for small raids. Do not count critically wounded heroes as combat support.')
    evidence = STUDY / 'diagnosis.json'
    p['belief']['claims']['B_shared_engagement'] = {'claim': (
        'The exact Richard78 pressure20 loss shows DK attacking104ticks before both casters, '
        'dying first; Warlock had14HP. Hypothesis: use a common opponent, support readiness '
        'and tower zone instead of separate10tile engagement gates. Combined changes are '
        'unvalidated and do not imply all heroes should always charge.'), 'status': 'untested',
        'evidence': [{'artifact': str(evidence), 'sha256': digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision'] + 1, parent=digest(parent),
                       change='Coached shared defensive engagement: ' + name)
    refresh_grounding(p)
    return p
