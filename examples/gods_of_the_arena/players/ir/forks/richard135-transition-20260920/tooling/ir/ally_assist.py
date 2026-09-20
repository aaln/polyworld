from copy import deepcopy
from policy_ir import digest, refresh_grounding
from release_workspace import RUN
from red_pressure import make as pressure

STUDY = RUN / 'coached-lanes/r5-ally-assist'
VARIANTS = ['deployed', 'pressure_parent', 'assist18', 'assist22', 'assist_wait']


def make(name):
    if name == 'deployed': return pressure('deployed')
    parent = pressure('pressure20')
    if name == 'pressure_parent': return parent
    p = deepcopy(parent); p['id'] = 'gota_' + name
    p['skill']['observe']['operator'] = 'lineup_ally_assist'
    p['skill']['observe']['parameters'].update(redbranch_assist_tiles=22 if name == 'assist22' else 18,
                                              redbranch_wait_support=int(name == 'assist_wait'))
    p['goal']['G_defense']['preference'] += (
        ' While already defending, support a nearby healthy ally who is visibly attacking '
        'the same leading threat, instead of waiting for that enemy to enter each individual '
        '10tile circle. Preserve wave pressure, recall timing, and original rally geometry.')
    evidence = STUDY / 'diagnosis.json'
    p['belief']['claims']['B_ally_assist'] = {'claim': (
        'The coached Richard78 loss has a104tick delay between DK and caster attacks. '
        'Broad local-recall/shared-rally variants failed every red screen game. Hypothesis: '
        'bridge the target gap using public allied attack intent while preserving the macro '
        'policy. This narrower change is not yet validated.'), 'status': 'untested',
        'evidence': [{'artifact': str(evidence), 'sha256': digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision'] + 1, parent=digest(parent),
                       change='Public allied intent assistance: ' + name)
    refresh_grounding(p); return p
