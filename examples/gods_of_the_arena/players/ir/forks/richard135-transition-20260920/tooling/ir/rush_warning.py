"""Earlier evidence-triggered defense without an unconditional opening detour."""
from copy import deepcopy
from policy_ir import digest, read, refresh_grounding
from rush_defense import STUDY as PARENT

STUDY = PARENT.parent/'r5-rush-warning'
VARIANTS = {
    'defense_parent': {},
    'early_blue': {'blue_group': 3},
    'early_both': {'group_size': 3, 'blue_group': 3},
    'early_radius': {'tower_tiles': 22},
    'early_mix': {'tower_tiles': 22, 'blue_group': 3},
}


def make(name):
    parent=read(PARENT/'hosted/blue_memory/final-feedback/policy.ir.json')
    if name=='defense_parent':return parent
    p=deepcopy(parent);p['id']='gota_rush_warning_'+name
    p['skill']['observe']['parameters'].update(VARIANTS[name])
    paths=[PARENT/'hosted/blue_memory/result.json',PARENT/'gota-g001-review/review.json',
           PARENT/'opening-screen/result.json']
    p['belief']['claims']['B_earlier_warning']={
        'claim':'Reactive defense won 207/240 versus the deployed control’s 80/240, but red-kite '
                'blue won only 23/40, missing the frozen 24/40 target. Unconditional central '
                'openings then failed all proxy rush cases, so reject that detour. Test earlier '
                'reaction to observed evidence: a larger structure-warning radius, a three-visible-hero '
                'blue threshold, or both. Partial shared vision can undercount an actual group, as '
                'the gota-g001 control replay shows. False defensive alarms remain a risk; retain '
                'default and deployed-opponent tests. The mechanism and transfer remain unvalidated.',
        'status':'untested','evidence':[{'artifact':str(p),'sha256':digest(p.read_bytes())} for p in paths]}
    p['goal']['G_defense']['preference'] += ' Prefer earlier response when the configured visible-group and structure-distance evidence supports a rush; avoid an unconditional opening detour.'
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),
                        change='Earlier observed rush warning: '+name,
                        needs_review=['belief/B_earlier_warning','goal/G_defense','goal/G_wave'])
    refresh_grounding(p);return p
