"""IR-authored coordinated lane rush variants, derived from the Jordan probe."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import read, digest, refresh_grounding
from release_workspace import RUN

VARIANTS = {'outer': (2, 0), 'center': (1, 0), 'clear': (2, 5)}


def make(name):
    parent = read(RUN / 'jordan-v148-probe/feedback/policy.ir.json')
    p = deepcopy(parent)
    p['id'] = 'gota_rush_' + name
    lane, radius = VARIANTS[name]
    p['skill']['observe'] = {'operator': 'rush_objective', 'parameters': {'lane': lane, 'clear_tiles': radius}}
    p['skill']['attack'] = {'operator': 'attack_candidate', 'parameters': {}}
    p['skill']['fallback'] = {'operator': 'rush_route', 'parameters': {'lane': lane, 'arrival_tiles': 6}}
    for rule in p['strategy']:
        if rule['skill'] == 'attack': rule['when'] = 'candidate_exists'
        if rule['skill'] == 'fallback': rule['when'] = 'no_candidate'
    p['goal']['G_fort']['preference'] = 'Win the fort race: concentrate all same-policy heroes on one lane, clear outer/inner/gate in order, then immediately attack the exposed fort. Barracks are optional and excluded.'
    p['goal']['G_wave']['preference'] = 'Coordinate classes through a shared mirrored lane and objective, independent of nearest creep or hero slot.'
    p['goal']['G_cadence']['preference'] = 'Maintain attacks on the shared objective and let host automatic spells operate. No retreat controller interrupts this initial rush hypothesis.'
    for claim in p['belief']['claims'].values():
        claim['claim'] = 'Inherited evidence about the previous executable; not a measurement of this new rush candidate. ' + claim['claim']
    p['belief']['claims']['B_shared_rush'] = {'claim': f'User-proposed shared-lane rush; mirroredlane{lane}, nearbyclearingradius{radius}. All5copies commit to towers then fort. Existing consumables/equipment retained. Test local team games first, then hosted exactJordanv148 on both sides and field guardrails. Competitive effects untested.', 'status': 'untested', 'evidence': []}
    p['update'] = {'revision': parent['update']['revision'] + 1, 'parent': digest(parent),
                  'change': 'Coordinated tower-to-fort rush, variant ' + name,
                  'needs_review': ['belief/B_shared_rush', 'goal/G_fort', 'goal/G_survival'],
                  'evidence': parent['update']['evidence']}
    refresh_grounding(p)
    return p
