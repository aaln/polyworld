from copy import deepcopy
from victory_route import make as plain
from release_workspace import RUN
from policy_ir import read,digest,refresh_grounding

STUDY=RUN/'coached-lanes/r5-counterwatch'
VARIANTS=['deployed','watch_all','watch_four']


def make(name):
    if name in ('deployed','pressure_parent'):return plain('deployed')
    parent=plain({'watch_all':'plain_all','watch_four':'plain_four'}[name])
    p=deepcopy(parent);p['id']='gota_counterwatch_'+name
    p['skill']['observe']['operator']='lineup_counterwatch_observe'
    p['goal']['G_defense']['preference'] += (
        ' Leaving the defensive rally must not erase threat monitoring. Keep a persistent '
        'counterattack mode; reacquire defense if a visible hero attacks a standing friendly '
        'anchor, enters24tiles of the god near an anchor, or forms a nearby three-hero group. '
        'Retain original role commitment when recalled. No creep-only coverage claim.')
    ev=STUDY/'diagnosis.json'
    p['belief']['claims']['B_counterwatch']={'claim':(
        'Quiet and victory-release variants regressed against the local convoy. Their '
        'release cleared defUntil; original red survivor recall requires worldTick<defUntil, '
        'so a returning smaller attack could no longer renew duty. Hypothesis: counterattack '
        'while keeping a separately armed public threat response. This source mechanism '
        'does not establish that it caused every previous loss; paired full games required.'),
        'status':'untested','evidence':[{'artifact':str(ev),'sha256':digest(ev.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Counterattack without forgetting base watch: '+name)
    refresh_grounding(p);return p
