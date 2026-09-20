"""Keep proven red behavior while retaining the measured blue repair."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import read,refresh_grounding,digest
from release_workspace import RUN
from jordan_root import STUDY as PRIOR
STUDY=RUN/'coached-lanes/r5-jordan-lineup'


def make(name='blue_repair'):
    if name!='blue_repair':raise ValueError(name)
    red=read(PRIOR/'local/candidates/deployed_parent/policy.ir.json')
    blue=read(PRIOR/'hosted/release20/jordan-feedback/policy.ir.json')
    p=deepcopy(blue);p['id']='gota_lineup_blue_repair'
    for skill,operator in (('observe','lineup_perimeter_observe'),('fallback','lineup_perimeter_route')):
        parameters={'redbranch_'+k:v for k,v in red['skill'][skill]['parameters'].items()}|blue['skill'][skill]['parameters']
        assert set(parameters)==set(CONTRACTS[operator].parameters)
        p['skill'][skill]={'operator':operator,'parameters':parameters}
    p['goal']['G_defense']['preference']=(
        'On red retain the exact deployed long_three observer and defense/wave navigation. '
        'On blue use the validated release20 perimeter observer and class-separated rally: '
        'protect structures within24tiles, bounded32tile response, keep three sentries and '
        'release the two attacking roles after20quietseconds. Retain blue solo-backdoor '
        'response and nearby core emergencies. No claim that all idle duty is eliminated. '
        'All other skills are identical between both parents.')
    evidence=PRIOR/'hosted/release20/jordan-result.json'
    p['belief']['claims']['B_lineup_interaction']={'claim':(
        'The full80game Jordan186 repair trial won40/40blue and0/40red, versus deployed '
        '0/40blue and40/40red. It is rejected as a both-color replacement. Exact reconstruction '
        'of supplied red regression confirms51441commands and9634hashes: three sentries '
        'retain long passive duty while two attackers leave. Preserve the deployed red '
        'execution and repaired blue execution as explicit separately parameterized branches. '
        'Require entirelocalgame action/statehash parity to their respective parents plus '
        'fresh80hosted Jordan games; combined win rate is not established by joining old scores.'),
        'status':'untested','evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
    p['update'].update(revision=blue['update']['revision']+1,parent=digest(blue),change='Preserve exact red champion branch; retain validated blue perimeter repair')
    refresh_grounding(p);return p
