"""Follow up a hosted loss just outside the rounded core-response boundary."""
from copy import deepcopy
from policy_ir import read,digest,refresh_grounding
from rolling_core import STUDY as PRIOR
from release_workspace import RUN

STUDY=RUN/'coached-lanes/r5-creep-reach'
VARIANTS=['deployed','pressure_parent','reach28','reach32']


def make(name):
    if name=='deployed':return read(PRIOR/'local/candidates/deployed/policy.ir.json')
    parent=read(PRIOR/'local/comparison-feedback/scan8/policy.ir.json')
    if name=='pressure_parent':return parent
    if name not in VARIANTS:raise ValueError(name)
    p=deepcopy(parent);p['id']='gota_creep_'+name;radius=int(name[5:])
    p['skill']['observe']['parameters']['redbranch_creep_response']=radius
    p['goal']['G_defense']['preference'] += f' Use a{radius}tile nearby response radius to cover the standing inner-lane sentry rally beyond24roundedtiles; retain8tilecreep threat radius and8checks.'
    ev=STUDY/'diagnosis.json'
    p['belief']['claims']['B_creep_reach']={'claim':(
        'Hosted scan8 vanguard loss ereq_0853d786-2c6d-4159-a49a-c078dbe25f5f: three healthy '
        'sentries near108,34.6 remain stationary while core creeps destroy god. Pinned mapCoordinate '
        'floors positions: observed home105,10 and self108,34 have squared distance585>576. '
        'Widen only the self-response radius to28or32; distant offensive heroes remain exempt. '
        'This is an unvalidated followup; captured scan8 and its frozen hosted cohort stay unchanged.'),
        'status':'untested','evidence':[{'artifact':str(ev),'sha256':digest(ev.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Cover rounded core response boundary '+name)
    refresh_grounding(p);return p
