"""Separate local refinements; never mutate the frozen live defense candidate."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import digest, read, refresh_grounding
from rush_defense import STUDY

VARIANTS = ['defense_parent', 'focus_low', 'short_focus', 'cover_kite', 'focus_kite']


def make(name):
    parent = read(STUDY/'local/context-feedback/blue_memory/policy.ir.json')
    if name == 'defense_parent':
        return parent
    p = deepcopy(parent)
    p['id'] = 'gota_defense_survival_'+name
    if name in ['focus_low','short_focus','focus_kite']:
        p['skill']['observe']['parameters']['hp_weight'] = 4
    if name == 'short_focus':
        p['skill']['observe']['parameters']['intercept_tiles'] = 8
    if name in ['cover_kite','focus_kite']:
        p['skill']['attack'] = {'operator':'defensive_recovery','parameters':
            CONTRACTS['defensive_recovery'].defaults() | parent['skill']['attack']['parameters'] |
            {'defense_motion_limit':60}}
    path = STUDY/'local/result.json'
    p['belief']['claims']['B_defense_survival'] = {
        'claim':'Parent defense won60/60local against default/deployed/centerproxy versus27/60 '
                'deployed, but incurred587hero deaths versus130. Some difference is longer winning '
                'games and actual defensive engagement. Test stronger low-HP focus, shorter pursuit, '
                'and recovery thresholds restricted to active defense. Preserve the frozen hosted '
                'candidate unchanged; no live result is assumed for these new variants.',
        'status':'untested','evidence':[{'artifact':str(path),'sha256':digest(path.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),
                        change='Separate defense survival experiment: '+name,
                        needs_review=['belief/B_defense_survival','goal/G_survival','goal/G_defense'])
    refresh_grounding(p)
    return p
