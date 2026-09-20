from copy import deepcopy

from binding import CONTRACTS
from policy_ir import digest, read, refresh_grounding
from release_workspace import RUN

VARIANTS = {
    'berserker_plain': 'Disable post-hit recovery for Berserker only; keep building-edge targeting.',
    'berserker_base': 'Disable Berserker recovery and restore its nearest-enemy targeting; retain footprint for other classes.',
}


def make(name):
    parent = read(RUN/'hosted-discovery/footprint/feedback/policy.ir.json')
    p = deepcopy(parent)
    p['id'] = 'gota_release_' + name
    p['skill']['attack'] = {'operator': 'class_cadence', 'parameters':
        p['skill']['attack']['parameters'] | {'plain_class': 9}}
    if name == 'berserker_base':
        p['skill']['observe'] = {'operator': 'class_building', 'parameters':
            p['skill']['observe']['parameters'] | {'plain_class': 9}}
    p['goal']['G_cadence']['preference'] += ' Berserker is explicitly exempt from normal recovery movement.'
    path = RUN/'hosted-discovery/result.json'
    refs = [{'artifact': str(path), 'sha256': digest(path.read_bytes())}]
    p['belief']['claims']['B_candidate'] = {
        'claim': VARIANTS[name] + ' Discovery on2026.9.16.2: footprint49/100, waveguard44, cadence41; '
                 'Berserker1/10 versus waveguard8/10 and cadence0/10. These are small, roster-specific '
                 'class groups, not a universal class conclusion. Test the exception; no advantage is established.',
        'status': 'untested', 'evidence': refs}
    p['update'] = {'revision': parent['update']['revision']+1, 'parent': digest(parent),
                   'change': VARIANTS[name], 'needs_review': ['belief/B_candidate','goal/G_cadence','goal/G_fort'],
                   'evidence': refs}
    refresh_grounding(p)
    return p
