from copy import deepcopy
from policy_ir import digest, refresh_grounding
from release_workspace import RUN
from red_pressure import make as pressure
from hero_binding import CLASS_ID, CONTENT

STUDY = RUN/'coached-lanes/r5-caster-binding-repair'
VARIANTS = ['deployed', 'pressure_parent', 'bound_idle', 'bound_focus']


def make(name):
    if name == 'deployed': return pressure('deployed')
    parent = pressure('pressure20')
    if name == 'pressure_parent': return parent
    p = deepcopy(parent); p['id'] = 'gota_caster_' + name
    p['skill']['observe']['operator'] = 'lineup_caster_assist_v2'
    p['skill']['observe']['parameters'].update(redbranch_assist_tiles=22,
        redbranch_wait_support=0, redbranch_idle_only=int(name == 'bound_idle'))
    p['goal']['G_defense']['preference'] += (
        ' Red Lich and Warlock, engine global classes7/8, support a nearby healthy ally '
        'already attacking the leading threat. Preserve red classes5/6/9 and all blue '
        'behavior. The idle variant preserves existing caster targets. Team slots must '
        'never substitute for global hero-class IDs in semantic lowering or fixtures.')
    evidence = STUDY/'diagnosis.json'
    p['belief']['claims']['B_class_binding_repair'] = {'claim': (
        'Prior caster variants mistakenly tested red classes2/3, which are blue heroes. '
        'Their real red branch was inactive; synthetic fixtures used the same wrong IDs '
        'and falsely suggested behavioral coverage. Engine content.nim and bots.nim '
        'prove actual Lich7/Warlock8 IDs. Correct the contract and source-derived fixtures, '
        'then require native in-game activation plus fresh full-game/hosted comparison. '
        'Prior all-role support beatRichard80/80 but lostJordan red17/40; do not promote it.'),
        'status': 'untested', 'evidence': [
            {'artifact': str(evidence), 'sha256': digest(evidence.read_bytes())},
            {'artifact': str(CONTENT), 'sha256': digest(CONTENT.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1, parent=digest(parent),
                       change='Source-grounded red caster repair: '+name)
    refresh_grounding(p); return p
