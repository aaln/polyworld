from copy import deepcopy
from bounded_core import STUDY as BOUNDED,make as bounded_make
from policy_ir import read,digest,refresh_grounding
from release_workspace import RUN

STUDY=RUN/'coached-lanes/r5-warlock-cadence'
VARIANTS=['deployed','pressure_parent','warlock']


def make(name):
    if name=='deployed':return bounded_make(name)
    parent=read(BOUNDED/'local/comparison-feedback/core96/policy.ir.json')
    if name=='pressure_parent':return parent
    if name!='warlock':raise ValueError(name)
    p=deepcopy(parent);p['id']='gota_warlock_cadence'
    p['skill']['attack']['operator']='red_warlock_cadence'
    p['goal']['G_defense']['preference'] += ' Red Warlock can use offensive slots1and2 while moving after a confirmed hit, subject to normal host checks.'
    evidence=STUDY/'diagnosis.json'
    p['belief']['claims']['B_warlock_mapping']={'claim':(
        'Pinned .5 class3 isWarlock, with offensiveMothHex/DreadTotem atslots1/2; '
        'the inheritedretreatfilter misidentifiesclass3asDruid and suppressesboth. '
        'CorrectredWarlock eligibility only. Earlier contracts/testsremainhistorical; '
        'thismechanicalcorrectiondoesnotbyitselfestablishawinimprovement.'),
        'status':'untested','evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Correct red Warlock spell eligibility during accepted retreat')
    refresh_grounding(p);return p
