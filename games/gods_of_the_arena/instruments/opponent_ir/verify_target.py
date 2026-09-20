"""Verify exact rosters, frozen forecasts, and primary IR compatibility for a study."""
import copy
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
LOCAL = ROOT / 'examples/gods_of_the_arena/players/ir'
sys.path.insert(0, str(LOCAL))
sys.path.insert(0, str(ROOT))
import opponent_ir


def read(path):
    return json.loads(path.read_text())


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def verify(study):
    plan = read(study / 'study-plan.json')
    out = ROOT / 'docs/opponents' / plan['target_slug']
    basename = 'richard_v135' if plan['target_slug'] == 'richard-v135' else 'alex_g002_v1'
    model_path = LOCAL / 'opponents' / (basename + '.py')
    prior_path = LOCAL / 'opponents' / (basename + '_population.py')
    model = opponent_ir.load(model_path)
    opponent_ir.load(prior_path)
    assert model['belief']['grounded']['opponent_version'] == plan['target_version']
    evidence = read(out / 'evidence.json')
    freeze = read(out / 'model-freeze.json')
    for filename in ('semantics.py', 'segment.py', 'evaluate_target.py', 'fit.py', 'decode.py'):
        assert sha(HERE / filename) == freeze['source_sha256'][filename], filename
    assert sha(out / 'model-freeze.json') == evidence['model_freeze_sha256']
    with gzip.open(out / 'heldout-predictions.jsonl.gz', 'rt') as stream:
        records = list(map(json.loads, stream))
    predictions = {record['observation']: record for record in records}
    assert len(records) == len(predictions) == evidence['heldout']['n']
    matched = set()
    with gzip.open(out / 'observations.jsonl.gz', 'rt') as stream:
        for line in stream:
            row = json.loads(line)
            if row['id'] not in predictions:
                continue
            forecast = opponent_ir.predict(model, row['situation'], row['affordances'])
            expected = predictions[row['id']]
            assert forecast['skill'] == expected['prediction']
            assert forecast['probabilities'] == expected['probabilities']
            assert row['id'] not in matched
            matched.add(row['id'])
    assert len(matched) == len(predictions)

    provenance = read(out / 'probe-provenance.json')
    assert sha(Path(provenance['binary'])) == provenance['sha256']
    assert sha(Path(provenance['source'])) == provenance['source_sha256']
    assert provenance['version'] == '2026.9.16.5'
    episode_hashes = {}
    for item in plan['episodes']:
        folder = study / 'artifacts' / item['id']
        checksums = read(folder / 'checksums.json')
        for name, expected in checksums.items():
            assert sha(folder / name) == expected, (item['id'], name)
        metadata = read(folder / 'episode.json')
        results = read(folder / 'results.json')
        proof = read(folder / 'observer-validation.json')
        roster = {p['position']: p['policy_version_id'] for p in metadata['participants']}
        assert set(roster) == set(range(10))
        own = range(item['observer_slot'], item['observer_slot'] + 5)
        enemy = range(5, 10) if item['observer_slot'] == 0 else range(5)
        assert all(roster[i] == item['own_version'] for i in own)
        assert all(roster[i] == item['opponent_version'] for i in enemy)
        assert metadata['coworld_version'] == item['version'] == provenance['version']
        assert proof['all_state_hashes_equal'] and proof['ticks'] == results['ticks']
        assert 'scripts: 10/10 active' in (folder / 'game.log').read_text()
        if item['split'] != 'population':
            assert item['opponent_version'] == plan['target_version']
            assert all(results['scores'][i] == 1 for i in enemy)
            assert all(results['scores'][i] == 0 for i in own)
        episode_hashes[item['id']] = {
            p.name: sha(p) for p in sorted(folder.iterdir()) if p.is_file()
        }
    own_cases = read(out / 'own-decision-analysis.json')['cases']
    owned_commands = 0
    for case in own_cases:
        proof = read(study / 'artifacts' / case['episode'] / 'own-command-proof.json')
        assert proof['all_state_hashes_equal'] and proof['all_actions_consumed']
        owned_commands += proof['owned_commands_matched']

    clean = ROOT.parent / 'polyworld-gota-clean-20260916-r5/examples/gods_of_the_arena/players/ir'
    sys.path.insert(0, str(clean))
    import policy_ir
    from games.gods_of_the_arena.instruments.jordan268_counter import contracts  # noqa: F401
    parent = policy_ir.read(out / 'observer-policy.ir.json')
    baseline = policy_ir.compile_policy(parent)
    assert baseline == (out / 'observer-policy.bas').read_text()
    baseline_sha = hashlib.sha256(baseline.encode()).hexdigest()
    assert baseline_sha == plan['our_policy']['basic_sha256']
    candidate = copy.deepcopy(parent)
    for filename in ('richard_v135.py', 'alex_g002_v1.py'):
        other = opponent_ir.load(LOCAL / 'opponents' / filename)
        candidate['belief']['claims'].update(opponent_ir.belief_patch(other))
    policy_ir.validate(candidate)
    assert policy_ir.compile_policy(candidate) == baseline
    assert tuple(opponent_ir.LAYERS) == tuple(policy_ir.LAYERS)
    assert set(model) == set(parent)
    assert all(set(rule) == {'id', 'when', 'skill', 'for'} for rule in model['strategy'])
    try:
        policy_ir.compile_policy(model)
    except ValueError:
        pass
    else:
        raise AssertionError('Observation model accepted as executable policy')
    receipt = {
        'schema': 'gota-opponent-python-compatibility/1',
        'verified_at': datetime.now(timezone.utc).isoformat(),
        'opponent_version': plan['target_version'],
        'seven_layer_layout_matches_primary': True,
        'strategy_rule_layout_matches_primary': True,
        'all_heldout_predictions_reproduced': len(matched),
        'both_belief_patches_pass_primary_validator': True,
        'both_belief_patches_preserve_exact_primary_basic': True,
        'primary_basic_sha256': baseline_sha,
        'action_compiler_rejects_observation_model': True,
        'episode_source_checksums_and_rosters_verified': len(episode_hashes),
        'all_episode_runtime_logs_have_10_active_vms': True,
        'representative_own_commands_matched': owned_commands,
        'live_primary_policy_modified': False,
        'proxy_usable': False,
    }
    write(out / 'python-compatibility.json', receipt)
    manifest = {
        'schema': 'gota-opponent-artifacts/1',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'study_directory': str(study),
        'opponent_version': plan['target_version'],
        'published_files': {p.name: sha(p) for p in sorted(out.iterdir())
                            if p.is_file() and p.name != 'artifact-manifest.json'},
        'python_models': {str(p.relative_to(ROOT)): sha(p) for p in (model_path, prior_path)},
        'instrumentation': {str(p.relative_to(ROOT)): sha(p) for p in sorted(HERE.glob('*.py'))},
        'raw_episode_files': episode_hashes,
        'guide_sha256': sha(out / 'guide-opponent-model-ir.md'),
        'native_probe': provenance,
    }
    write(out / 'artifact-manifest.json', manifest)
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == '__main__':
    for directory in sys.argv[1:]:
        verify(Path(directory).resolve())
