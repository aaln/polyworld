"""Verify release contract evidence and immutable incumbent identity."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

release = read(HERE / 'release.json')
live = read(HERE / 'live-readback.json')
checks = read(HERE / 'checks.json')
assert release['version'] == live['version'] == '2026.9.23.2'
assert release['coworld_id'] == live['coworld_id']
assert release['source_commit'] == checks['engine_commit']
assert release['source_commit'] in live['source_url']
assert release['replay_version'] == checks['replay_version'] == 60
assert all(c['passed'] for c in checks['checks'])
assert sha(ROOT / 'examples/gods_of_the_arena/players/ir/forks/druid-lane20260923-hosted/druid-lane/policy.bas') == checks['source_sha256']
for row in read(HERE / 'input-manifest.json'):
    assert sha(Path(row['path'])) == row['sha256'], row['path']
probe = read(HERE / 'healing-probe.json')
assert len(probe['rows']) == 20 and probe['vm_failures'] == 0
for row in probe['rows']:
    if row['class'] in ['VanguardKnight', 'DeathKnight']:
        assert row['self_healing'] == row['accepted_spell_releases'] == 0
        assert row['home_walks'] > 0 and row['retreat'] == 1
    if row['class'] == 'DruidWarden':
        assert row['self_healing'] == 212 and row['accepted_spell_releases'] == 3
        assert row['home_walks'] == row['retreat'] == 0
smoke = read(HERE / 'smoke.json')
assert smoke['passed'] and smoke['games'] == len(smoke['rows']) == 4
assert all(r['valid'] and r['hash_mismatches'] == 0 for r in smoke['rows'])
ir = read(HERE / 'mechanics-and-coaching.ir.json')
assert {'situation', 'belief', 'goal', 'skill', 'strategy', 'execution', 'update'} <= ir.keys()
assert ir['execution']['executable'] is False and ir['execution']['deployed'] is False
assert checks['new_hosted_games'] == smoke['new_hosted_games'] == 0
print(json.dumps({'passed': True, 'engine': live['version'], 'healing_fixtures': 20, 'complete_native_matches': 4, 'upstream_test_suites': 3, 'new_hosted_games': 0, 'policy_unchanged': True}))
