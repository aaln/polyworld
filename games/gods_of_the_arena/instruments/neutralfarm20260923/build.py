"""Freeze the user's lane-sharing hypothesis as a convertible semantic pair."""
import json
import pprint
import re
import shutil
import camp_binding as b

RAW = b.ROOT.parent / 'polyworld/tmp/gota-lane-neutral62-20260923'
COMMIT = '2c8db6ebe1dc785ce1eea87496505d1244ee4c44'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    out = RAW / 'lane-neutral'
    assert not out.exists(), 'Preserve captured inputs'
    request = {
        'user': 'Neutral camps are live in GotA. Three tiers, leaders, XP and gold. Pull into a creep wave; leash and respawn. Continue testing less-crowded lanes for individual score.',
        'objective': 'Expected individual floor(max(0, XP - 200 * elapsed minutes)); no team-win gate.',
        'engine': COMMIT,
        'mechanics': {'neutral_kind':6, 'neutral_faction':2, 'hp_by_tier':[100,180,300], 'xp_by_tier':[20,35,50], 'gold_by_tier':[10,20,30], 'leader_reward_multiplier':2, 'leash_tiles':12, 'respawn_seconds':60, 'respawn_blocked_by_hero_radius':10, 'xp_recipient_range':6, 'xp_eligible_team':'last-hitting unit team', 'last_hit_reserved_percent':15},
        'sources': ['sim.nim:gainCreepRewards', 'sim.nim:updateCamps', 'bots.nim:campProc', 'players/puller.bas'],
        'hypothesis': 'Retain productive lane selection and harvest visible neutral downtime opportunities, optionally transferring neutral damage to nearby allied creeps. More rewards must outweigh pulling time, damage and missed lane/hero XP.',
        'scope': 'Fresh release62 discovery: four side/seat contexts, ten fresh baseline games each, forty matched lane-only counterfactuals and forty matched lane-plus-camp counterfactuals. Every request<=100 and all newgames journaled. No deployment from a directional pilot.',
    }
    write(RAW / 'request.json', request)
    p = json.loads((b.PARENT / 'policy.ir.json').read_text())
    parent_digest = b.ir.digest(p)
    specs = b.configure()
    p['id'] = 'gota_lane_neutral20260923'
    p['execution'].update(binding=b.VERSION, game_version='2026.9.23.4')
    p['skill'] = {k: {'operator': 'neutralfarm_' + k, 'parameters': p['skill'][k]['parameters'] if k in p['skill'] else spec.defaults()} for k, spec in specs.items()}
    rules = {r['skill']: r for r in p['strategy']}
    p['strategy'] = [dict(rules[k], **{'for': ['Score']}) if k in rules else {'id': 'R_' + k, 'when': 'active', 'skill': k, 'for': ['Score']} for k in specs]
    p['situation']['notes'] += ' Release62 adds neutral kind6/faction2, visible camp/leader/returning fields and public static camp geometry. Returning mobs are immune. Camp life/respawn knowledge remains visibility-limited. Lane XP sharing remains15percent last-hit reserve plus85percent nearby share; neutral recipients must be on the last-hitting unit team.'
    p['belief']['claims'] = {
        'CampMechanism': {'status':'requires_review','claim':'Bounded safe wave pulls and tier/HP-guarded visible neutral fallback turn otherwise idle time into XP without surrendering nearby lane or hero targets.','evidence':[{'artifact':'evidence/practice-comparison.json'}]},
        'CurrentScoreGain': {'status':'requires_review','claim':'The inherited lane gain was measured on replay61. Fresh replay62 controls must compare baseline, lane-only, and lane-plus-neutral. Compare individual-score means with paired uncertainty; no causal component claim from an unpaired cohort.','evidence':[{'artifact':'evidence/statistics.json'}]},
    }
    p['goal']['Score']['preference'] = 'Maximize expected individual floor(max(0, XP - 200 * elapsed minutes)). Lane occupancy, survival, team victory and game duration have value only through this score. Compare marginal expected XP against travel/death downtime and time penalty.'
    p['update'] = {'revision': 1, 'parent': parent_digest, 'change': {'origin': request['user'], 'deployment_qualified': False}, 'needs_review': ['belief/CampMechanism', 'belief/CurrentScoreGain'], 'evidence': [{'artifact': 'evidence/request.json'}]}
    b.ir.refresh_grounding(p)
    source = b.ir.compile_policy(p)
    assert b.ir.extract(source, p) == p
    out.mkdir()
    for name, value in [('policy.ir.json', p), ('extracted.ir.json', p), ('semantics.json', b.ir.grounded(p))]: write(out / name, value)
    (out / 'policy.py').write_text('POLICY = ' + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
    (out / 'policy.bas').write_text(source)
    shutil.copytree(b.PARENT / 'tooling', out / 'tooling', ignore=shutil.ignore_patterns('__pycache__'))
    (out / 'tooling/neutralfarm20260923').mkdir()
    shutil.copy2(b.HERE / 'camp_binding.py', out / 'tooling/neutralfarm20260923/camp_binding.py')
    converter = (b.PARENT / 'convert.py').read_text().replace('crowd-control tactics', 'lane occupancy').replace('tooling/lanefarm20260923', 'tooling/neutralfarm20260923').replace('occupancy_binding', 'camp_binding')
    (out / 'convert.py').write_text(converter)
    write(out / 'evidence/request.json', request)
    manifest = {'source_sha256': b.ir.digest(source.encode()), 'ir_sha256': b.ir.digest(p), 'binding': b.VERSION, 'parent_source_sha256': b.ir.digest((b.PARENT / 'policy.bas').read_bytes()), 'engine_commit': COMMIT, 'game_version': '2026.9.23.4', 'hosted_complete': False, 'deployment_qualified': False, 'score_gate_passed': None}
    write(out / 'manifest.json', manifest)
    split = lambda s: dict(re.findall(r"' @rule (\w+)\n(.*?)(?=\n' @rule |\Z)", s, re.S))
    old, new = split((b.PARENT / 'policy.bas').read_text()), split(source)
    write(RAW / 'skill-difference.json', {'changed': [k for k in old if old[k] != new[k]], 'added': [k for k in new if k not in old], 'unchanged': [k for k in old if old[k] == new[k]]})
    print(json.dumps(manifest))


if __name__ == '__main__': main()
