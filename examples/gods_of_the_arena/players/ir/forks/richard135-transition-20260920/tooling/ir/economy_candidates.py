"""Successor hypotheses: turn survival/XP into equipment and fort victories."""
from pathlib import Path
import sys

from binding import CONTRACTS
from motion_candidates import make_policy as motion_policy
from policy_ir import ROOT, bundle, digest, refresh_grounding, write

VARIANTS = {
    'center_motion': {'motion': {'targeted': 0}, 'weapon': True, 'center': True},
    'center_loadout_motion': {'motion': {'targeted': 0}, 'center': True, 'loadout': True},
    'center_loadout': {'center': True, 'loadout': True},
    'wave_loadout_motion': {'motion': {'targeted': 0}, 'loadout': True},
    'center_poison_motion': {'motion': {'targeted': 0}, 'weapon': True, 'center': True, 'poison': True},
    'last_hit_motion': {'motion': {'targeted': 0}, 'center': True, 'loadout': True, 'opportunity': {}},
    'farm_motion': {'motion': {'targeted': 0}, 'center': True, 'loadout': True,
                    'opportunity': {'farm_until_level': 3, 'hp_weight': 4}},
    'finish_motion': {'motion': {'targeted': 0}, 'center': True, 'loadout': True,
                      'opportunity': {'objective_bonus': 40000}},
    'farm_plain': {'center': True, 'loadout': True,
                   'opportunity': {'farm_until_level': 3, 'hp_weight': 4}},
    'finish_plain': {'center': True, 'loadout': True,
                     'opportunity': {'objective_bonus': 40000}},
}


def make_policy(name):
    definition = VARIANTS[name]
    p = motion_policy(name, definition)
    parent_hash = digest(p)
    p['id'] = 'gota_economy_campaign_' + name
    if definition.get('center'):
        p['skill']['fallback'] = {'operator': 'walk_point', 'parameters': {'x': 64, 'y': 64}}
    if definition.get('loadout'):
        p['skill']['equipment'] = {'operator': 'buy_ordered_loadout',
                                   'parameters': CONTRACTS['buy_ordered_loadout'].defaults()}
    if definition.get('poison'):
        p['skill']['sustain'] = {'operator': 'buy_consumables', 'parameters': {}}
    if 'opportunity' in definition:
        p['skill']['observe'] = {'operator': 'opportunity_enemy',
                                 'parameters': CONTRACTS['opportunity_enemy'].defaults() | definition['opportunity']}
    paths = [ROOT / 'tmp/gota-ir/motion-campaign-20260915/confirmation-result.json',
             ROOT / 'tmp/gota-ir/motion-campaign-20260915/league/replay-gap.json']
    refs = [{'artifact': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())} for path in paths]
    p['belief']['claims']['B_candidate'] = {
        'claim': (f"Successor candidate {name}: {definition}. The first motion candidate improved death rate "
                  'and XP but failed win qualification on240 fresh cases (125wins vs116v2/135default). '
                  'Test center movement, damage-oriented five-item progression, last-hit opportunities, '
                  'early creep farming and in-range structure pressure, with and without motion feedback. '
                  'Ordered loadout failed its earlier .1 screen; current published balance and kiting interaction '
                  'are distinct conditions. Incumbent equipment/XP observations are not causal evidence. '
                  'This candidate has no validated competitive advantage.'),
        'status': 'untested', 'evidence': refs}
    p['update'] = {'revision': p['update']['revision'] + 1, 'parent': parent_hash,
                   'change': 'Successor hypotheses after failed fresh win qualification; retain that failure.',
                   'needs_review': ['belief/B_candidate', 'goal/G_fort', 'goal/G_survival'], 'evidence': refs}
    refresh_grounding(p)
    return p


if __name__ == '__main__':
    directory = Path(sys.argv[1]); directory.mkdir(parents=True, exist_ok=True)
    for name in VARIANTS:
        manifest = bundle(make_policy(name), directory / name)
        print(name, manifest['source_sha256'])
    write(directory / 'variants.json', VARIANTS)
