"""Coordinated anti-rush hypotheses grounded in the user's exact khors loss."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import read, digest, refresh_grounding
from release_workspace import RUN

STUDY = RUN / 'coached-lanes/r5-rush-defense'
VARIANTS = {
    'rally': {},
    'clear_wave': {'creep_first': 1},
    'deep': {'home_tiles': 40, 'hold_ticks': 720},
    'close': {'intercept_tiles': 7, 'behind_tiles': 6},
    'clear_kite': {'creep_first': 1, 'intercept_tiles': 7},
}


def make(name):
    parent = read(RUN / 'coached-lanes/r5-asymmetric/hosted/blue_damage/team-feedback/policy.ir.json')
    p = deepcopy(parent)
    p['id'] = 'gota_rush_defense_' + name
    p['skill']['observe'] = {'operator': 'rush_defense_v2', 'parameters':
                            CONTRACTS['rush_defense_v2'].defaults() | parent['skill']['observe']['parameters'] | VARIANTS[name]}
    p['skill']['fallback']['operator'] = 'defend_or_wave'
    p['skill']['attack']['parameters']['motion_object_limit'] = 40
    if name == 'clear_kite':
        p['skill']['attack']['parameters'].update(targeted=1, risk_hp=35)
    p['goal']['G_defense'] = {
        'preference': 'When a visible enemy hero group threatens a standing friendly lane tower or '
                      'god, suspend the split push and regroup to defend. Remove creep cover or '
                      'focus local heroes according to the configured skill. Keep a bounded '
                      'commitment through temporary loss of vision, then resume wave pressure.',
        'provenance': 'authored'}
    for rule in p['strategy']:
        if rule['skill'] in {'observe', 'attack', 'fallback'}:
            rule['for'] = list(dict.fromkeys(rule['for'] + ['G_defense']))
    p['goal']['G_base']['preference'] = 'React to an observed coordinated rush before ordinary offensive target selection; preserve inventory and class combat arbitration.'
    paths = [RUN / 'coached-lanes/khors-defense/review-summary.json',
             RUN / 'coached-lanes/khors-defense/rush-rivals.json']
    p['belief']['claims']['B_rush_defense'] = {
        'claim': 'Exact current-release khors:v1 replay: five blue heroes were visible attacking '
                 'middle tower by40s. Our red heroes split3/2 across outer lanes and the god died '
                 'at3008ticks(125.33s), with no hero deaths on either side. Shared vision makes '
                 'the threat observable. Test coordinated rally, creep-support removal, and '
                 'optional retreat. User also identifies red-kite:v20 and gota-g001:v1. '
                 'Blue-loadout mixed-team evidence alone cannot validate this two-player mode.',
        'status': 'untested', 'evidence': [{'artifact': str(path), 'sha256': digest(path.read_bytes())} for path in paths]}
    p['update'].update(revision=parent['update']['revision'] + 1, parent=digest(parent),
                        change='Shared-vision defense against clustered lane rush, bounded detection and motion cost: ' + name,
                        needs_review=['belief/B_rush_defense', 'goal/G_defense', 'goal/G_survival'])
    refresh_grounding(p)
    return p
