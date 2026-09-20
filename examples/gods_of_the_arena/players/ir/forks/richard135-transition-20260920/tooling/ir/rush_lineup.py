"""Combine color-specific defense evidence while preserving inactive combat."""
from binding import CONTRACTS
from policy_ir import digest, refresh_grounding
from rush_persistent import make as parent_make, STUDY

VARIANTS = {
    'lineup': {},
    'four': {'blue_group': 4},
    'five': {'group_size': 5, 'blue_group': 5},
    'blue_memory': {'blue_group': 4, 'blue_hold': 1200, 'blue_continue': 24},
}


def make(name):
    parent = parent_make('sticky')
    p = parent_make('sticky')
    p['id'] = 'gota_lineup_defense_'+name
    p['skill']['observe'] = {'operator': 'rush_defense_v4', 'parameters':
        CONTRACTS['rush_defense_v4'].defaults() | parent['skill']['observe']['parameters'] | VARIANTS[name]}
    p['skill']['attack'] = {'operator': 'defense_cadence', 'parameters':
        CONTRACTS['defense_cadence'].defaults() | parent['skill']['attack']['parameters'] |
        {'motion_object_limit': 80, 'defense_motion_limit': 40}}
    evidence = [STUDY/'screen-v2/result.json', STUDY/'screen-v3/result.json']
    p['belief']['claims']['B_lineup_defense'] = {
        'claim': 'Previous six-case screens show opposing color responses: shorter simple rally '
                 'won blue vs center proxy; survivor-persistent defense won red. Neither qualified '
                 'overall. Both also changed ordinary combat cost limits. Test the combination '
                 'with original combat preserved outside defense, plus four/five-hero detection '
                 'thresholds. Color-specific behavior is a hypothesis, not a validated improvement.',
        'status': 'untested', 'evidence': [{'artifact': str(p), 'sha256': digest(p.read_bytes())} for p in evidence]}
    p['goal']['G_defense']['preference'] += ' Match defensive commitment to the fixed class lineup; retain ordinary combat outside the threat response.'
    p['update'].update(revision=parent['update']['revision']+1, parent=digest(parent),
                        change='Lineup-specific defense with unchanged inactive combat: '+name,
                        needs_review=['belief/B_lineup_defense', 'goal/G_defense', 'goal/G_survival'])
    refresh_grounding(p)
    return p
