from copy import deepcopy
from caster_binding_repair import make as caster
from policy_ir import digest, refresh_grounding
from release_workspace import RUN

STUDY = RUN/'coached-lanes/r5-supported-defense'
VARIANTS = ['deployed', 'pressure_parent', 'idle_hold', 'focus_hold']


def make(name):
    if name == 'deployed': return caster('deployed')
    # Explicitly compare the added wait rule to the corrected idle-caster parent.
    if name == 'pressure_parent': return caster('bound_idle')
    parent = caster('bound_focus' if name == 'focus_hold' else 'bound_idle')
    p = deepcopy(parent); p['id'] = 'gota_supported_defense_' + name
    p['skill']['observe']['operator'] = 'lineup_supported_defense'
    p['goal']['G_defense']['preference'] += (
        ' Coordinate initiation as well as follow-up: DeathKnight waits at the '
        'existing defensive rally if nearby allies cannot support him, unless '
        'the enemy has already entered tower/core defense range. Healthy casters '
        'join public allied attack intent. Preserve attack pressure elsewhere.')
    evidence = STUDY/'diagnosis.json'
    p['belief']['claims']['B_supported_initiation'] = {'claim': (
        'Coaching asks for both coordinated attacks and waiting for tower support. '
        'Corrected caster support is real but local deaths increased. Hypothesis: '
        'pair support with a narrow global-class5 initiation gate when no nearby '
        'healthy ally exists. No new recall or rally. Compare complete outcomes '
        'to corrected idle-caster parent; do not extrapolate synthetic tests.'),
        'status': 'untested', 'evidence': [
            {'artifact': str(evidence), 'sha256': digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1, parent=digest(parent),
                       change='Coordinated caster support and unsupported DeathKnight wait: '+name)
    refresh_grounding(p); return p
