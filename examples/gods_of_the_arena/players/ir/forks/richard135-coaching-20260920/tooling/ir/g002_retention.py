"""Deadline final bounded repair from the deployed G source, preserving combat."""
from copy import deepcopy
from red_pressure import make as base
from policy_ir import digest,refresh_grounding
from release_workspace import RUN
STUDY=RUN/'coached-lanes/r5-g002-retention'
VARIANTS=['deployed','short60','near60']
def make(name):
    parent=base('deployed')
    if name=='deployed':return parent
    if name not in VARIANTS:raise ValueError(name)
    p=deepcopy(parent);p['id']='gota_g002_'+name
    p['skill']['observe']['parameters']['redbranch_sentry_hold']=1440
    if name=='near60':p['skill']['observe']['parameters']['redbranch_continue_home']=24
    p['goal']['G_defense']['preference']+=' Deadline retention experiment: retain deployed combat and navigation; red sentries remember actual rushes for60seconds rather than300. '+('Only a survivor within24tiles of home renews existing defense.' if name=='near60' else 'Keep the deployed48tile survivor renewal.')+' A fresh observed group still recalls all roles. Blue behavior unchanged.'
    e=STUDY/'prospective.json'
    p['belief']['claims']['B_deadline_retention']={'status':'untested','claim':'The deployedG previously won24/40red vs g002 while Hcaster-expanded anchor won4/40; the new rally variant won0/40 and cohesion has already lost22red. Expanded support and quietrelease combinations did not improve actual g002. Hypothesis: reduce only the deployed long red retention, optionally narrow isolated survivor renewal. Twelve local games per arm are a deadline screen, not broad validation. Complete40red40blue with32/38floors beforepromotion.','evidence':[{'artifact':str(e),'sha256':digest(e.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Deadline direct deployed retention: '+name)
    refresh_grounding(p);return p
