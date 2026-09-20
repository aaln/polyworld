"""Follow-up IR cells: preserve wave routing, separate cadence from escape."""
from copy import deepcopy

from binding import CONTRACTS
from policy_ir import HERE, ROOT, digest, read, refresh_grounding

VARIANTS = {
    'cadence_ranged_close': {'operator': 'cadence_motion', 'parameters': {'threat_tiles': 5}},
    'cadence_ranged': {'operator': 'cadence_motion', 'parameters': {'threat_tiles': 7}},
    'cadence_all': {'operator': 'cadence_motion', 'parameters': {'threat_tiles': 7, 'all_classes': 1}},
    'cadence_guard': {'operator': 'cadence_motion', 'parameters': {'threat_tiles': 7, 'all_classes': 1, 'risk_hp': 55}},
    'cadence4_guard': {'operator': 'cadence_motion', 'parameters': {'threat_tiles': 7, 'all_classes': 1, 'risk_hp': 55, 'recovery_ticks': 4}},
    'range_guard': {'operator': 'motion_feedback', 'parameters': {'threat_tiles': 7, 'risk_hp': 55}},
}


def parent_policy():
    return read(HERE / 'optimizer_motion_weapon.evaluated.ir.json')


def make_policy(name):
    parent = parent_policy()
    p = deepcopy(parent)
    definition = VARIANTS[name]
    p['id'] = 'gota_cadence_' + name
    p['skill']['attack'] = {'operator': definition['operator'],
                            'parameters': CONTRACTS[definition['operator']].defaults() |
                            {'targeted': 0} | definition['parameters']}
    paths = [ROOT / 'tmp/gota-ir/autoresearch-20260916/cadence-finding.json',
             ROOT / 'tmp/gota-ir/autoresearch-20260916/hosted-discovery/result.json']
    refs = [{'artifact': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())} for path in paths]
    p['belief']['claims']['B_candidate'] = {
        'claim': f"Untested configuration {name}: {definition}. Retain the deployed wave-following and purchases. "
                 'A bounded legal-command replay probe shortened Crossbow attack intervals from36 to17ticks, '
                 'but all arms died. Test short post-hit recovery steps separately from long danger retreats, '
                 'ranged versus all classes, and threat coverage. The previous center/farming candidates '
                 'lost hosted discovery46/100 and41/100 versus deployed motion54/100; those failures remain. '
                 'No competitive or survival advantage is established for this candidate.',
        'status': 'untested', 'evidence': refs}
    p['update'] = {'revision': parent['update']['revision'] + 1, 'parent': digest(parent),
                   'change': 'Cadence and range follow-up after failed economy transfer; retain wave routing.',
                   'needs_review': ['belief/B_candidate', 'goal/G_fort', 'goal/G_survival'], 'evidence': refs}
    refresh_grounding(p)
    return p
