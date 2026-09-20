from copy import deepcopy
from caster_binding_repair import make as caster
from supported_defense import make as supported
from policy_ir import digest, refresh_grounding
from release_workspace import RUN

STUDY = RUN/'coached-lanes/r5-reachable-support'
VARIANTS = ['deployed', 'pressure_parent', 'ready10', 'ready12']


def make(name):
    if name == 'deployed': return caster('deployed')
    if name == 'pressure_parent': return caster('bound_idle')
    parent=supported('idle_hold');p=deepcopy(parent)
    p['id']='gota_reachable_support_'+name
    p['skill']['observe']['operator']='lineup_reachable_support'
    p['skill']['observe']['parameters']['redbranch_ready_tiles']=int(name[5:])
    p['goal']['G_defense']['preference'] += (
        ' Count support by proximity to the enemy or public attack commitment, '
        'as well as teammate proximity. Otherwise wait for tower/core defense range.')
    e=STUDY/'diagnosis.json'
    p['belief']['claims']['B_reachable_support']={'status':'untested','claim':(
        'Corrected caster policy joins the coached fight at5537 but DK still dies. '
        'An ally6tiles behind him and15tiles from the enemy is not immediate support. '
        'Hypothesis: require a healthy nearby ally within10/12tiles of that enemy '
        'or already targeting it before DK initiates, keeping emergency exceptions. '
        'Do not infer improved full-game survival from earlier attack orders.'),
        'evidence':[{'artifact':str(e),'sha256':digest(e.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),
                       change='Reachable ally readiness plus caster support: '+name)
    refresh_grounding(p);return p
