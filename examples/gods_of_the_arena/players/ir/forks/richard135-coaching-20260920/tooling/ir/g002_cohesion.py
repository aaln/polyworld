"""Deadline contingency: retain both attackers through the defensive fight."""
from copy import deepcopy
from g002_arrival import make as arrival
from policy_ir import digest,refresh_grounding
from release_workspace import RUN
STUDY=RUN/'coached-lanes/r5-g002-cohesion'
VARIANTS=['deployed','pressure_parent','cohesion20']


def make(name):
    if name in VARIANTS[:2]:return arrival(name)
    if name!='cohesion20':raise ValueError(name)
    parent=arrival('arrive20');p=deepcopy(parent);p['id']='gota_g002_cohesion20'
    p['skill']['observe']['parameters'].update(redbranch_pressure_hold=1440,redbranch_pressure_continue=48)
    p['goal']['G_defense']['preference']+=' Keep both attacking roles available through a threatened-tower fight with the deployed60second recall and48tile continuation; release arrived defenders when actual pressure becomes quiet.'
    p['belief']['claims']['B_cohesive_counterpush']={'status':'untested','claim':'DeployedG won24/40red againstg002; anchorH won4/40. H shortened attacker recall from1440to480ticks and disabled survivor continuation. Hypothesis: combine deployed recall cohesion with Hcaster support and arrival-qualified quiet release. This paired behavior aims to fight together, then leave together; compare fullgames. Sparse deadline local validation is not the original full-field suite.','evidence':[{'artifact':str(STUDY/'hypothesis.json'),'sha256':digest((STUDY/'hypothesis.json').read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Retain group fight before arrival-qualified counterpush')
    refresh_grounding(p);return p
