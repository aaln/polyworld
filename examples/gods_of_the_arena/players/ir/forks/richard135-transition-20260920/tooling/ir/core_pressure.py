"""Red sentries prioritize a visible attacker of the god during active defense."""
from copy import deepcopy
from policy_ir import read, digest, refresh_grounding
from release_workspace import RUN
from breach_pressure import PARENT, DEPLOYED

STUDY = RUN/'coached-lanes/r5-core-pressure'
VARIANTS = ['deployed', 'pressure_parent', 'core', 'core_near24', 'core_near32']


def make(name):
    if name == 'deployed': return read(DEPLOYED/'policy.ir.json')
    parent = read(PARENT/'policy.ir.json')
    if name == 'pressure_parent': return parent
    if name not in VARIANTS: raise ValueError(name)
    p = deepcopy(parent); p['id'] = 'gota_red_' + name
    params = p['skill']['observe']['parameters'] | {'redbranch_core_response_tiles':24, 'redbranch_core_radius':14}
    operator = 'lineup_core_pressure_observe'
    if name != 'core':
        operator = 'lineup_core_breach_observe'
        params.update(redbranch_breach_radius=int(name.removeprefix('core_near')),redbranch_breach_group=3)
    p['skill']['observe'] = {'operator':operator, 'parameters':params}
    p['goal']['G_defense']['preference'] += (
        ' During active red defense, heroes within24tiles of home prioritize a visible god attacker '
        'within14tiles over ordinary combat targets. Other visible enemies within6tiles of the god '
        'are also eligible. Distant attackers keep pressure; exact blue behavior is preserved.')
    if name != 'core':
        p['goal']['G_defense']['preference'] += f' Recall for three enemies only inside{params["redbranch_breach_radius"]}tiles of home; farther away require four.'
    evidence=STUDY/'diagnosis.json'
    p['belief']['claims']['B_red_core_priority'] = {'claim':(
        'Round378 gota-g002 loss: after the last guard fell, at tick15360 the red DK and Warlock '
        'selected Druid108 while Ranger106 targeted god1. All three sentries eventually selected '
        'Ranger, but god died15428. A fused objective-priority scan may prevent wasted focus; '
        'this hypothesis is untested and does not assert collision or guarantee a counter.'),
        'status':'untested','evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Red god-attacker priority with optional nearby breach recall: '+name)
    refresh_grounding(p); return p
