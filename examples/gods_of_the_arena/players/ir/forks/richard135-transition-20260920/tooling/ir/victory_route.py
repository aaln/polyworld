"""Preserve deployed combat rally geometry while testing victory transitions."""
from copy import deepcopy
from victory_counterpush import make as victory, PARENT
from release_workspace import RUN
from policy_ir import read,digest,refresh_grounding

STUDY=RUN/'coached-lanes/r5-victory-route'
VARIANTS=['deployed','plain_all','plain_four']


def make(name):
    parent=read(PARENT/'policy.ir.json')
    if name in ('deployed','pressure_parent'):return parent
    p=deepcopy(victory({'plain_all':'victory_all','plain_four':'victory_four'}[name]))
    p['id']='gota_'+name
    p['skill']['fallback']=deepcopy(parent['skill']['fallback'])
    p['goal']['G_defense']['preference']=p['goal']['G_defense']['preference'].replace(
        'Separate active defenders by class. ','Preserve original rally geometry during combat. ')
    ev=STUDY/'diagnosis.json'
    p['belief']['claims']['B_rally_ablation']={'claim':(
        'The spaced victory candidate lost a local game that deployed won; all51409owned '
        'commands and10382hashes reconstructed, with2actual victory-release decisions. '
        'Both changed geometry and release may matter; their individual causes are not '
        'established. Test the same observed-victory transition with original red navigation.'),
        'status':'untested','evidence':[{'artifact':str(ev),'sha256':digest(ev.read_bytes())}]}
    p['update'].update(revision=p['update']['revision']+1,parent=digest(victory(
        {'plain_all':'victory_all','plain_four':'victory_four'}[name])),change='Victory transition with original rally: '+name)
    refresh_grounding(p);return p
