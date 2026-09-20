from copy import deepcopy
from policy_ir import read, digest, refresh_grounding
from release_workspace import RUN

STUDY = RUN/'coached-lanes/r5-breach-pressure'
PARENT = RUN/'coached-lanes/r5-red-pressure/hosted/pressure20/jordan-feedback'
DEPLOYED = RUN/'coached-lanes/r5-jordan-lineup/deployment-requested/policy'
VARIANTS = ['deployed','pressure_parent','near24','near32','near40']


def make(name):
    if name == 'deployed': return read(DEPLOYED/'policy.ir.json')
    parent = read(PARENT/'policy.ir.json')
    if name == 'pressure_parent': return parent
    if name not in VARIANTS: raise ValueError(name)
    p = deepcopy(parent); p['id'] = 'gota_breach_' + name
    params = p['skill']['observe']['parameters'] | {'redbranch_breach_radius':int(name[4:]),'redbranch_breach_group':3}
    p['skill']['observe'] = {'operator':'lineup_breach_observe','parameters':params}
    p['goal']['G_defense']['preference'] += (f' On red, use three-hero recall only when the closest visible enemy is within {int(name[4:])}tiles of home; '
        'keep four-hero recall farther out. Preserve pressure20 attacker release, three long-duty sentries, and exact blue policy.')
    evidence = STUDY/'diagnosis.json'
    p['belief']['claims']['B_breach_scope'] = {'claim':(
        'Unconditional three-hero recall regressed on red in full local confirmation. The first '
        'selected loss recalled toward a group47tiles away; actualdeployed won samecase. '
        'Actual league red-kite27 loss instead had three attackers around the base gate20tiles away. '
        'Test spatially limited three-hero recall on the pressure20parent that won80/80black-kite '
        'and80/80Jordan. Existing completed evidence does not establish this further change helps.'),
        'status':'untested','evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Proximity-qualified red breach recall: '+name)
    refresh_grounding(p);return p
