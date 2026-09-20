from copy import deepcopy
from policy_ir import digest,refresh_grounding
from core_pressure import make as core_make
from sentry_farm import make as farm_make
from release_workspace import RUN

STUDY=RUN/'coached-lanes/r5-bounded-core'
VARIANTS=['deployed','pressure_parent','core96','core128','farm96','farm128']
CANDIDATES=['core96','farm96']  # 128 failed the retained adversarial runtime screen.


def make(name):
    if name in ('deployed','pressure_parent'):return core_make(name)
    if name not in VARIANTS:raise ValueError(name)
    farm=name.startswith('farm')
    parent=farm_make('farm32') if farm else core_make('core')
    p=deepcopy(parent);p['id']='gota_bounded_'+name
    p['skill']['observe']={'operator':'lineup_bounded_farm_observe' if farm else 'lineup_bounded_core_observe',
        'parameters':p['skill']['observe']['parameters'] | {'redbranch_defense_target_scan':int(name[4:])}}
    p['goal']['G_defense']['preference'] += (
        ' Reserve runtime for a complete decision by bounding the active red target scan; '
        'all visible heroes precede creeps on the pinned source. Do not alter the blue branch.')
    evidence=STUDY/'diagnosis.json'
    p['belief']['claims']['B_bounded_core']={'claim':(
        'Unbounded core and farm prototypes exceeded the20000instruction limit in a240hostilecreep '
        'stress fixture. The deployed red parent passed that fixture. Bound only the active red '
        'target scan to96or128objects, retaining all visibleheroes and accepting incompletecreep '
        'coverage. Existingbluepathological240creepfixturealsofailsbutisunchanged; normalblue '
        'parity and actual full-game budgets are verified separately. Hosted gain untested.'),
        'status':'untested','evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Bounded red core/farm complete-decision budget: '+name)
    refresh_grounding(p);return p
