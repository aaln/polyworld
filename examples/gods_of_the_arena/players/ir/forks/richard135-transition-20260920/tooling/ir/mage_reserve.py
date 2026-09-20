from copy import deepcopy
from bounded_core import STUDY as BOUNDED,make as bounded_make
from policy_ir import read,digest,refresh_grounding
from release_workspace import RUN

STUDY=RUN/'coached-lanes/r5-mage-reserve'
VARIANTS=['deployed','pressure_parent','cap4','cap5']


def make(name):
    if name=='deployed':return bounded_make(name)
    parent=read(BOUNDED/'local/comparison-feedback/core96/policy.ir.json')
    if name=='pressure_parent':return parent
    if name not in VARIANTS:raise ValueError(name)
    p=deepcopy(parent);p['id']='gota_mage_reserve_'+name
    old=p['skill']['equipment']
    p['skill']['equipment']={'operator':'mage_reserve','parameters':old['parameters']|{'reserve_cap':int(name[3:])}}
    p['goal']['G_defense']['preference'] += (
        f' Red Lich and Warlock reserve consumable capacity by buying at most{int(name[3:])}permanentitems. '
        'Retain ordinary healing/mana purchase thresholds and all other loadouts.')
    evidence=STUDY/'diagnosis.json'
    p['belief']['claims']['B_mage_consumable_space']={'claim':(
        'Actual Richard78 red loss: at17040 Lich249/579HP with1215goldand6permanentitems; '
        'Warlock90/640HP with155gold,5permanentitemsandmanapotion. Both lackroomforhealing '
        'beforefatalfight. No selling/replacement hostAPI exists. Reservingoneortwoslots '
        'fromtheoutset may improve sustain at costofgearstats. Improvementuntested.'),
        'status':'untested','evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Red mage permanent-gear cap: '+name)
    refresh_grounding(p);return p
