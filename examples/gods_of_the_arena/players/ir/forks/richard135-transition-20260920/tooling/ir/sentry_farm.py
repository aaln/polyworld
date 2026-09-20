from copy import deepcopy
from policy_ir import digest,refresh_grounding
from core_pressure import make as core_make
from release_workspace import RUN

STUDY=RUN/'coached-lanes/r5-sentry-farm'
VARIANTS=['deployed','pressure_parent','core_parent','farm24','farm32','farm40']


def make(name):
    if name in ('deployed','pressure_parent'):return core_make(name)
    parent=core_make('core')
    if name=='core_parent':return parent
    if name not in VARIANTS:raise ValueError(name)
    p=deepcopy(parent);p['id']='gota_sentry_'+name
    p['skill']['observe']={'operator':'lineup_farm_core_observe','parameters':
        p['skill']['observe']['parameters'] | {'redbranch_farm_home':int(name[4:]),
            'redbranch_farm_reach':32,'redbranch_farm_safe':40,'redbranch_farm_scan':64}}
    p['goal']['G_defense']['preference'] += (
        ' Keep red sentries useful during quiet duty: when no visible hero is within40tiles '
        'of home and no combat/core target exists, clear a nearby visible enemy creep while '
        'staying within the declared home/reach bounds. Maintain defensive commitment.')
    evidence=STUDY/'diagnosis.json'
    p['belief']['claims']['B_sentry_farm']={'claim':(
        'Actual pressure20 red-kite loss leaves DK level2 after600seconds of long sentry duty. '
        'Pinned simulator awards XP/gold to the hero landing a killing hit, with no passive '
        'shared experience. A bounded quiet creep-clearing fallback may improve sentry '
        'progression without globally releasing defense. No win/survival gain established.'),
        'status':'untested','evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Bounded quiet sentry farm with core priority: '+name)
    refresh_grounding(p);return p
