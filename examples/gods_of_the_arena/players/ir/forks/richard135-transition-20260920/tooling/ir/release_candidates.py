"""Rebase semantic claims without silently modifying the deployed controls."""
from copy import deepcopy

from binding import CONTRACTS
from policy_ir import HERE, compile_policy, digest, read, refresh_grounding
from release_workspace import RUN, SOURCE, VERSION

VARIANTS = {
    'footprint': 'Approximate building-edge distance when choosing a target, including barracks.',
    'siege': 'Building-edge targeting plus twice the weight on mobile units; prioritize opening lanes.',
    'short_step': 'Two-tile recovery destination search fits narrower building gaps than three tiles.',
    'wave_spacing': 'Follow two tiles behind the retained wave instead of its front creep; denser waves may absorb pressure.',
}


def rebase(filename):
    parent = read(HERE / filename)
    p = deepcopy(parent)
    p['execution']['game_version'] = VERSION
    refs = [{'artifact': str(RUN / 'live-before/coworld.json'),
             'sha256': digest((RUN / 'live-before/coworld.json').read_bytes())}]
    p['situation']['notes'] = f'Published {VERSION}, source {SOURCE}; clean engine and locked dependencies. Six creeps/lane/480ticks; building occupancy and barracks kind5. Runtime hero stats remain authoritative.'
    p['belief']['claims']['B_release'] = {
        'claim': 'Source and live manifest agree on the announced wave, building/pathing and hero changes. '
                 'Existing nearest-enemy accepts barracks through host exposure predicates. Existing item buying '
                 'and automatic class abilities use live game rules. Earlier win and survival evidence is scoped '
                 'to its recorded release, not evidence of competitive strength on this release.',
        'status': 'supported', 'evidence': refs}
    p['update'] = {'revision': parent['update']['revision'] + 1, 'parent': digest(parent),
                   'change': 'Rebind to verified live release; refresh environmental beliefs without changing BASIC.',
                   'needs_review': ['goal/G_fort', 'goal/G_survival', 'goal/G_wave'], 'evidence': refs}
    refresh_grounding(p)
    assert compile_policy(p) == compile_policy(parent)
    return p


def make(name):
    parent = rebase('cadence_all.evaluated.ir.json')
    p = deepcopy(parent)
    p['id'] = 'gota_release_' + name
    if name in ('footprint', 'siege'):
        p['skill']['observe'] = {'operator': 'building_enemy', 'parameters':
            CONTRACTS['building_enemy'].defaults() | {'unit_weight': 2 if name == 'siege' else 1}}
        p['goal']['G_base']['preference'] = 'Select exposed targets using the declared approximate building-edge distance; preserve baseline inventory accounting.'
    elif name == 'short_step':
        p['skill']['attack']['parameters']['step_tiles'] = 2
    elif name == 'wave_spacing':
        p['skill']['fallback']['parameters']['offset_tiles'] = 2
    else:
        raise ValueError(name)
    p['belief']['claims']['B_candidate'] = {'claim': VARIANTS[name] + ' Untested on the new release; no strength or survival claim.', 'status': 'untested', 'evidence': []}
    p['update'] = {'revision': parent['update']['revision'] + 1, 'parent': digest(parent),
                   'change': VARIANTS[name], 'needs_review': ['belief/B_candidate', 'goal/G_fort', 'goal/G_survival'], 'evidence': []}
    refresh_grounding(p)
    return p
