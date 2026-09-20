from copy import deepcopy
from binding import CONTRACTS
from policy_ir import read,digest,refresh_grounding
from release_workspace import RUN

STUDY=RUN/'coached-lanes/r5-victory-counterpush'
PARENT=RUN/'coached-lanes/r5-jordan-lineup/deployment-requested/policy'
VARIANTS=['deployed','pressure_parent','victory_all','victory_four','victory_three']


def make(name):
    parent=read(PARENT/'policy.ir.json')
    if name in ('deployed','pressure_parent'):return parent
    if name not in VARIANTS:raise ValueError(name)
    p=deepcopy(parent);p['id']='gota_'+name
    p['skill']['observe']={'operator':'lineup_victory_observe','parameters':parent['skill']['observe']['parameters']|{
        'redbranch_victory_allies':3 if name=='victory_three' else 4,
        'redbranch_leave_tank':int(name=='victory_four')}}
    p['skill']['fallback']={'operator':'lineup_counterpush_route','parameters':
        CONTRACTS['lineup_counterpush_route'].defaults()|parent['skill']['fallback']['parameters']}
    p['goal']['G_defense']['preference']=(
        'Convert an observed local victory into creep-backed lane pressure: require two '
        'visible enemy corpses within24tiles, no living enemy heroes within24tiles, and '
        f'{3 if name=="victory_three" else 4} living allies within14tiles. '
        +('Retain DeathKnight as rear guard. ' if name=='victory_four' else 'Release all qualifying roles. ')+
        'Otherwise preserve the original red defense retention and fresh-rush recall. '
        'Separate active defenders by class. Preserve exact blue behavior and buying.')
    evidence=STUDY/'diagnosis.json'
    p['belief']['claims']['B_victory_counterpush']={'claim':(
        'Exact Richard78 replay at8760 exposes four living allies and two dead enemy heroes '
        'near each defender, with no living nearby enemy hero. All four still defend a stale '
        'rally. Generic quiet20/40/tank60 candidates failed local retention guardrails '
        '(48/53/48 wins vs55/60). Hypothesis: retain old defense unless an actual public '
        'local victory supports counterattack; missing enemies do not count as dead.'),
        'status':'untested','evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Observed-victory counterpush: '+name)
    refresh_grounding(p);return p
