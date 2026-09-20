"""Arrival-qualified defense release, motivated by reconstructed mixed-team losses."""
from copy import deepcopy
from policy_ir import read, digest, refresh_grounding
from release_workspace import RUN

STUDY = RUN / 'coached-lanes/r5-ranger-guard'
PARENT = RUN / 'coached-lanes/r5-jordan-lineup/deployment-requested/policy'
VARIANTS = ['deployed', 'arrival12', 'arrival18', 'arrival24', 'arrival18_40']


def make(name):
    parent = read(PARENT / 'policy.ir.json')
    if name == 'deployed': return parent
    if name not in VARIANTS: raise ValueError(name)
    p = deepcopy(parent); p['id'] = 'gota_ranger_' + name
    parameters = p['skill']['observe']['parameters'] | {'arrival_tiles': int(name.split('_')[0].replace('arrival', ''))}
    if name.endswith('_40'): parameters['idle_ticks'] = 960
    p['skill']['observe'] = {'operator': 'lineup_arrival_observe', 'parameters': parameters}
    p['goal']['G_defense']['preference'] += (
        f' For blue recalled heroes, start quiet-release eligibility only within {parameters["arrival_tiles"]} '
        f'tiles of the remembered protected structure; quiet window {parameters["idle_ticks"]}/24 seconds. '
        'Absence of a nearby target while traveling home is not a completed defense. '
        'Do not change red behavior, ordinary duty expiration, purchases, or threat selection.')
    evidence = STUDY / 'diagnosis.json'
    p['belief']['claims']['B_recall_travel'] = {'claim': (
        'In the fully reconstructed mixed blue Ranger/Vanguard loss ereq_02a54296, Ranger accepts '
        'a recall around tick8412. At8880 it is still roughly63tiles from the newly protected '
        'tower15, last actionable combat8412. By9000 it has cleared its defense clock and '
        'returned to offense. The20-second quiet release counts transit as quiet defense. '
        'Arrival-qualified timers may preserve the successful Jordan objective defense while '
        'recovering mixed-team recall. This hypothesis requires fresh complete local and hosted tests.'),
        'status': 'untested', 'evidence': [{'artifact': str(evidence), 'sha256': digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision'] + 1, parent=digest(parent),
                       change='Do not release blue defenders while they are still traveling to the protected objective: ' + name)
    refresh_grounding(p)
    return p
