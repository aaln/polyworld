"""Keep defending surviving invaders; test tighter focus and group arrival."""
from binding import CONTRACTS
from policy_ir import digest, refresh_grounding
from rush_defense import make as parent_make, STUDY

VARIANTS = {
    'sticky': {},
    'tight': {'intercept_tiles': 6, 'behind_tiles': 2},
    'shield': {'intercept_tiles': 6, 'behind_tiles': 2, 'creep_first': 1},
    'together': {'intercept_tiles': 6, 'behind_tiles': 2, 'gather_heroes': 3},
    'shield_together': {'intercept_tiles': 6, 'behind_tiles': 2, 'gather_heroes': 3, 'creep_first': 1},
}


def make(name):
    parent = parent_make('rally')
    p = parent_make('rally')
    p['id'] = 'gota_persistent_defense_'+name
    p['skill']['observe'] = {'operator': 'rush_defense_v3', 'parameters':
        CONTRACTS['rush_defense_v3'].defaults() | parent['skill']['observe']['parameters'] |
        {'group_size': 4, 'hold_ticks': 1440} | VARIANTS[name]}
    evidence = STUDY/'screen-v2/result.json'
    p['belief']['claims']['B_persistent_defense'] = {
        'claim': 'All five previous six-case candidates failed local gates. Rally stopped the blue '
                 'proxy once but lost red: sampled replay shows most attackers dead by80s, two '
                 'survivors remaining near our base, and defenders returning to split offense by100s. '
                 'A later rush then wins. Test continuation for surviving deep invaders, tighter '
                 'combat radius, creep focus, and regrouping before attack. Replays also show late '
                 'and staggered initial arrival. These coordinated changes remain unvalidated.',
        'status': 'untested', 'evidence': [{'artifact': str(evidence), 'sha256': digest(evidence.read_bytes())}]}
    p['goal']['G_defense']['preference'] += ' Continue defending while surviving invaders remain near the base; optionally gather before fighting.'
    p['update'].update(revision=parent['update']['revision']+1, parent=digest(parent),
                        change='Persistent group defense: '+name,
                        needs_review=['belief/B_persistent_defense', 'goal/G_defense', 'goal/G_survival'])
    refresh_grounding(p)
    return p
