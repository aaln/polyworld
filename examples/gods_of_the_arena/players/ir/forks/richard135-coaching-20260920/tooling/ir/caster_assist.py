from copy import deepcopy
from policy_ir import digest, refresh_grounding
from release_workspace import RUN
from red_pressure import make as pressure

STUDY = RUN / 'coached-lanes/r5-caster-assist'
VARIANTS = ['deployed', 'pressure_parent', 'caster_idle', 'caster_focus']


def make(name):
    if name == 'deployed': return pressure('deployed')
    parent = pressure('pressure20')
    if name == 'pressure_parent': return parent
    p = deepcopy(parent); p['id'] = 'gota_' + name
    p['skill']['observe']['operator'] = 'lineup_caster_assist'
    p['skill']['observe']['parameters'].update(redbranch_assist_tiles=22,
        redbranch_wait_support=0, redbranch_idle_only=int(name == 'caster_idle'))
    p['goal']['G_defense']['preference'] += (
        ' Healthy nearby Lich and Warlock support a publicly observed allied attack on the '
        'leading threat. Preserve melee and Crossbowman targeting exactly; optionally retain '
        'casters existing targets and repair only their idle defensive decisions.')
    evidence = STUDY / 'diagnosis.json'
    p['belief']['claims']['B_caster_assist'] = {'claim': (
        'All-role assistance activated in full games but regressed on two convoy cases. '
        'The coaching replay specifically shows two casters waiting while DK attacks. '
        'Hypothesis: limit assistance to those casters and optionally fill only empty target '
        'decisions, preserving already productive targets. New variant, unvalidated.'),
        'status': 'untested', 'evidence': [{'artifact': str(evidence), 'sha256': digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision'] + 1, parent=digest(parent),
                       change='Repair caster defensive assistance only: ' + name)
    refresh_grounding(p); return p
