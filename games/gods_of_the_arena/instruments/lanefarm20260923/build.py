"""Freeze the user's lane-sharing hypothesis as a convertible semantic pair."""
import json
import pprint
import re
import shutil
import occupancy_binding as b

RAW = b.ROOT.parent / 'polyworld/tmp/gota-lane-occupancy61-20260923'
COMMIT = 'e42c4822f44e04726b09bb4ffe853152c7a18207'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    out = RAW / 'lane-occupancy'
    assert not out.exists(), 'Preserve captured inputs'
    request = {
        'user': "Players that have their own lane may get more xp than players that don't. Let's try the strategy of going to a lane where other players aren't going to to try to score more points",
        'objective': 'Individual floor(max(0, XP - 200 * elapsed minutes)); wins and deaths are diagnostics only.',
        'mechanics': {'engine': COMMIT, 'creep_pool_xp': 15, 'nearby_range_tiles': 6,
                     'last_hit_reserved_percent': 15, 'shared_percent_if_last_hitter_nearby': 85,
                     'solo_share': 15, 'two_allies_last_hitter_share': 8.625,
                     'two_allies_other_share': 6.375,
                     'sources': ['sim.nim:gainCreepRewards', 'sim.nim:objectVisibleTo', 'sim.nim:scriptObjectKey']},
        'hypothesis': 'One early commitment to fewer allied heroes can increase own recurring creep XP enough to pay routing and combat opportunity costs. Ally angular positions are a proxy, not guaranteed future occupancy.',
        'falsifier': 'No matched individual-score improvement, or no own creep-XP increase when the mechanism activates. More isolation itself is not success.',
        'selection': 'Keep all eighty prior control-tactics candidate episodes as reused baseline; no favorable subsets. Eight matched native comparisons first. New responsive counterfactual request n80 only after local validity. Discovery study, not independent confirmation or deployment qualification.',
    }
    write(RAW / 'request.json', request)
    p = json.loads((b.PARENT / 'policy.ir.json').read_text())
    parent_digest = b.ir.digest(p)
    specs = b.configure()
    p['id'] = 'gota_lane_occupancy20260923'
    p['execution'].update(binding=b.VERSION, game_version='2026.9.23.3')
    p['skill'] = {k: {'operator': 'lanefarm_' + k, 'parameters': p['skill'][k]['parameters'] if k in p['skill'] else spec.defaults()} for k, spec in specs.items()}
    rules = {r['skill']: r for r in p['strategy']}
    p['strategy'] = [dict(rules[k], **{'for': ['Score']}) if k in rules else {'id': 'R_' + k, 'when': 'active', 'skill': k, 'for': ['Score']} for k in specs]
    p['situation']['notes'] += ' Public allied positions identify estimated lane commitment via positive angular projection from home onto the three existing waypoints. Alive allies within12tiles of home are uncommitted. Shared-XP eligibility depends on actual six-tile range and navigation layer; estimated lane counts do not assert eligibility.'
    p['belief']['claims'] = {
        'LaneIntent': {'status': 'requires_review', 'claim': 'At leasttwo public allied departures provide enough evidence for one early less-crowded lane choice; persist it through death and avoid repeated switching.', 'evidence': [{'artifact': 'evidence/practice-comparison.json'}]},
        'ScoreGain': {'status': 'requires_review', 'claim': 'Lower competition for nearby creep XP can outweigh route distance, reduced kill support and isolation costs. Judge mean individual score only, retaining all paired games.', 'evidence': [{'artifact': 'evidence/statistics.json'}]},
    }
    p['goal']['Score']['preference'] = 'Maximize expected individual floor(max(0, XP - 200 * elapsed minutes)). Lane occupancy, survival, team victory and game duration have value only through this score. Compare marginal expected XP against travel/death downtime and time penalty.'
    p['update'] = {'revision': 1, 'parent': parent_digest, 'change': {'origin': request['user'], 'deployment_qualified': False}, 'needs_review': ['belief/LaneIntent', 'belief/ScoreGain'], 'evidence': [{'artifact': 'evidence/request.json'}]}
    b.ir.refresh_grounding(p)
    source = b.ir.compile_policy(p)
    assert b.ir.extract(source, p) == p
    out.mkdir()
    for name, value in [('policy.ir.json', p), ('extracted.ir.json', p), ('semantics.json', b.ir.grounded(p))]: write(out / name, value)
    (out / 'policy.py').write_text('POLICY = ' + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
    (out / 'policy.bas').write_text(source)
    shutil.copytree(b.PARENT / 'tooling', out / 'tooling', ignore=shutil.ignore_patterns('__pycache__'))
    (out / 'tooling/lanefarm20260923').mkdir()
    shutil.copy2(b.HERE / 'occupancy_binding.py', out / 'tooling/lanefarm20260923/occupancy_binding.py')
    converter = (b.PARENT / 'convert.py').read_text().replace('crowd-control tactics', 'lane occupancy').replace('tooling/controltactics20260923', 'tooling/lanefarm20260923').replace('tactics_binding', 'occupancy_binding')
    (out / 'convert.py').write_text(converter)
    write(out / 'evidence/request.json', request)
    manifest = {'source_sha256': b.ir.digest(source.encode()), 'ir_sha256': b.ir.digest(p), 'binding': b.VERSION, 'parent_source_sha256': b.ir.digest((b.PARENT / 'policy.bas').read_bytes()), 'engine_commit': COMMIT, 'game_version': '2026.9.23.3', 'hosted_complete': False, 'deployment_qualified': False, 'score_gate_passed': None}
    write(out / 'manifest.json', manifest)
    split = lambda s: dict(re.findall(r"' @rule (\w+)\n(.*?)(?=\n' @rule |\Z)", s, re.S))
    old, new = split((b.PARENT / 'policy.bas').read_text()), split(source)
    write(RAW / 'skill-difference.json', {'changed': [k for k in old if old[k] != new[k]], 'added': [k for k in new if k not in old], 'unchanged': [k for k in old if old[k] == new[k]]})
    print(json.dumps(manifest))


if __name__ == '__main__': main()
