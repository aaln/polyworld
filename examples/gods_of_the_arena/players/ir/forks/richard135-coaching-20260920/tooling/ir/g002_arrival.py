"""Count quiet defense after arrival, preserving observed frontline pressure."""
from copy import deepcopy
from g002_coordination import make as prior, STUDY as PREVIOUS
from policy_ir import digest,refresh_grounding
from release_workspace import RUN
STUDY=RUN/'coached-lanes/r5-g002-arrival-release'
VARIANTS=['deployed','pressure_parent','arrive10','arrive20','arrive30','arrive30wide']


def make(name):
    if name in VARIANTS[:2]:return prior(name)
    if name not in VARIANTS[2:]:raise ValueError(name)
    p=deepcopy(prior('release20' if name=='arrive20' else 'release10'));parent=digest(p)
    p['id']='gota_g002_'+name
    p['skill']['observe']['operator']='lineup_post_arrival'
    p['skill']['observe']['parameters'].update(redbranch_arrival_tiles=6,
        redbranch_quiet_ticks=240 if name=='arrive10' else (480 if name=='arrive20' else 720),
        redbranch_tank_quiet_ticks=1080 if name=='arrive10' else (1440 if name=='arrive20' else 2880),
        redbranch_hero_home_tiles=40 if name=='arrive30wide' else 24)
    p['goal']['G_defense']['preference']+=' A quiet timeout starts only after physical rally arrival; travelling to a threatened tower and current observed groups remain defensive work.'
    e=STUDY/'diagnosis.json'
    p['belief']['claims']['B_arrival_quiet']={'status':'untested','claim':'M release10 failed both red center-proxy games. Exact native reconstruction shows four heroes cancel defense at1088/1135 while far from their assigned rally; last pressure was848/895. Travel is not post-defense idleness. Hypothesis: count quiet only within6tiles of the rally, retain current anchored-group pressure, test10/20/30second quiet and wider approaching-threat protection. Retain distinct destinations and current-point refresh.','evidence':[{'artifact':str(e),'sha256':digest(e.read_bytes())}]}
    p['update'].update(revision=p['update']['revision']+1,parent=parent,change='Arrival-qualified post-defense release: '+name)
    refresh_grounding(p);return p
