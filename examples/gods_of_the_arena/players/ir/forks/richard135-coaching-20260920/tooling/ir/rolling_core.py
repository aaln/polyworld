from copy import deepcopy
from policy_ir import read,digest,refresh_grounding
from release_workspace import RUN

STUDY=RUN/'coached-lanes/r5-rolling-core'
PARENT=RUN/'coached-lanes/r5-jordan-lineup/deployment-requested/policy'
VARIANTS=['deployed','pressure_parent','scan8','scan16']


def make(name):
    parent=read(PARENT/'policy.ir.json')
    if name in ('deployed','pressure_parent'):return parent
    if name not in VARIANTS:raise ValueError(name)
    p=deepcopy(parent);p['id']='gota_rolling_creep_'+name
    p['skill']['observe']={'operator':'lineup_rolling_creep_observe','parameters':
        parent['skill']['observe']['parameters']|{'redbranch_creep_response':24,
            'redbranch_creep_radius':8,'redbranch_creep_checks':int(name[4:])}}
    p['goal']['G_defense']['preference'] += (' Nearby red heroes must respond to visible hostile '
        'creeps within8tiles of our god even without a hero-group trigger or near the old rally. '
        'Rotate a bounded scan across all visible objects and retain an eligible target; preserve '
        'the deployed red recall retention and blue execution.')
    ev=STUDY/'diagnosis.json'
    p['belief']['claims']['B_core_creep_emergency']={'claim':(
        'Round380 vanguard-rally-hold loss: all five owned heroes alive at tick12147; three '
        'defenders near90,5 while hostile creeps near105,15 destroyed god1. The failed core96 '
        'candidate also lost its11HPgod to a late creep while defenders fought elsewhere. '
        'An independent rotating creep emergency may close this gap. No measured win gain yet.'),
        'status':'untested','evidence':[{'artifact':str(ev),'sha256':digest(ev.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Bounded independent red core-creep emergency '+name)
    refresh_grounding(p);return p
