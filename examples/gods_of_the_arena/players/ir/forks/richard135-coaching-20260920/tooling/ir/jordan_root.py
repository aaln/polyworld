"""Root-cause variants grounded in exact replay/VM reconstruction."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import read,digest,refresh_grounding
from release_workspace import RUN
from mixed_blue import make as prior
STUDY=RUN/'coached-lanes/r5-jordan-root'
VARIANTS=['deployed_parent','blue_assigned','perimeter18','perimeter24','release20','release_all20','front20','blue_front20']

def make(name):
    if name in ('deployed_parent','blue_assigned'):return prior(name)
    parent=read(RUN/'coached-lanes/r5-mixed-blue/hosted/blue_assigned/mixed-feedback/policy.ir.json')
    p=deepcopy(parent);p['id']='gota_root_'+name
    params=CONTRACTS['objective_perimeter'].defaults()|parent['skill']['observe']['parameters']
    params['perimeter_tiles']=18 if name=='perimeter18' else 24
    if name=='release20':params['release_mode']=1
    if name in ('release_all20','front20','blue_front20'):params['release_mode']=2
    if name=='blue_front20':params['perimeter_team']=1
    p['skill']['observe']={'operator':'objective_perimeter','parameters':params}
    p['skill']['fallback']={'operator':'forward_perimeter','parameters':CONTRACTS['forward_perimeter'].defaults()|parent['skill']['fallback']['parameters']|{'forward_rally':int('front' in name)}}
    p['goal']['G_defense']['preference']=(
        'Preserve existing rush/solo triggers, direct core emergency and equipment. During '
        'defense, cover the protected structure perimeter, not only the hero current position. '
        f'Radius{params["perimeter_tiles"]}, reach{params["response_reach"]}, release mode{params["release_mode"]} '
        f'after{params["idle_ticks"]}quiet ticks; team scope{params["perimeter_team"]}. '
        'Release clears all relevant commitment clocks so wave attack selection can resume. '
        'Forward formation is '+str('front' in name)+'. Hidden threats are not presumed absent.')
    evidence=STUDY/'diagnosis.json'
    p['belief']['claims']['B_objective_dead_zone']={'claim':(
        'Exact own policy reconstruction matched78022commands and16513state hashes in Jordan186 '
        'blue loss ereq_2103ec78. At16440 four defenders reject visible Warlock103 outside '
        'self-centred10tile radius and repeat a rear rally; Vanguard attacks. God dies73ticks '
        'later. Persistent rally orders/target filtering, not collision physics alone, explain '
        'the clump. New objective-relative selection and optional quiet release/forward rally '
        'are untested hypotheses; evaluate coordinated effects and retained mixed response.'),
        'status':'untested','evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Fix objective coverage and productive defense transitions: '+name)
    refresh_grounding(p);return p
