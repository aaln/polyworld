"""Test coordinated pursuit, objective scoring, and wave spacing on the baseline."""
from copy import deepcopy
from coached_strike import make as strike_make
from policy_ir import HERE, read, digest, refresh_grounding
from release_workspace import RUN

STUDY = RUN / 'coached-lanes/r5-pressure'
VARIANTS = {
    'short': (8, 1, 7, 0),
    'close': (4, 1, 7, 0),
    'structure': (8, 2, 7, 0),
    'all_edges': (12, 1, 9, 0),
    'edges_short': (8, 2, 9, 0),
    'behind_wave': (8, 1, 7, 1),
    'behind_edges': (8, 2, 9, 2),
    'focus6': None,
}


def make(name):
    if name == 'focus6':
        return strike_make(name)
    parent = read(HERE / 'win_bounded_0916.r5.evaluated.ir.json')
    policy = deepcopy(parent)
    policy['id'] = 'gota_coached_pressure_' + name
    pursuit, unit_weight, extra_class, offset = VARIANTS[name]
    policy['skill']['observe']['parameters'].update(
        pursuit_tiles=pursuit, unit_weight=unit_weight, extra_class=extra_class)
    policy['skill']['fallback']['parameters']['offset_tiles'] = offset
    policy['goal']['G_fort']['preference'] = (
        'Maintain existing wave escort and class combat while reducing distant mobile pursuit. '
        'Apply configured building-edge preference; do not infer unseen structure destruction. '
        'Wave spacing and local clearing must preserve progress to both guards and the exposed god.')
    evidence = RUN / 'coached-lanes/r5-finish/screen/result.json'
    policy['belief']['claims']['B_pressure_coaching'] = {
        'claim': 'Terminal-only overrides did not improve any of the four local cases. '
                 'Test the coordinated earlier decisions: pursuit radius, building versus mobile '
                 'selection, Lich building-edge selection, and distance behind the retained wave. '
                 'These are hypotheses, not guarantees of safe creep cover or superior wins.',
        'status': 'untested',
        'evidence': [{'artifact': str(evidence), 'sha256': digest(evidence.read_bytes())}],
    }
    policy['update'].update(revision=parent['update']['revision'] + 1, parent=digest(parent),
                            change='Coached pressure with existing wave controller: ' + name,
                            needs_review=['belief/B_pressure_coaching', 'goal/G_fort'])
    refresh_grounding(policy)
    return policy
