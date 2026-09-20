"""Freeze, submit and audit the microplay ablation against nine real players.

Creation uses the supervised researcher's shared allowance and request lock.
Uploads are inert; this module never selects league champions.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import gzip
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
CLEAN = ROOT.parent / 'polyworld-gota-clean-20260916-r5'
CAMPAIGN = ROOT.parent / 'gota-autoresearch'
STUDY = ROOT / 'tmp/gota-ir/microplay-xp-20260920'
TOOLING = CLEAN / 'examples/gods_of_the_arena/players/ir'
PLAYER = 'ply_630a768f-d623-44b2-80fa-36968d6fa75a'
PARENT = '4cdbbf36-3d70-4ea3-8aed-c92ee0e024be'
CYCLE = 'interactive-microplay-xp-20260920'
OTHER_PLAYERS = [
    'ply_ded11f40-3e30-4921-b019-f7f6bc3e9c83',
    'ply_bcb80069-fb0c-4ba5-a45c-06b647870aeb',
    'ply_4e9a2db0-dbc2-4283-b4cc-3ce79e9f8d40',
    'ply_18302115-9fc9-482d-a2f3-f4c592bf9e57',
    'ply_5b832230-f519-4af8-adda-bb3e02349b7d',
    'ply_0f9ea7d3-fa48-4586-9df3-123e9ee21f1c',
    'ply_ac7e5318-5781-4ed6-8fc9-d9f66d6b1637',
    'ply_b7fd1a00-9728-455c-98bc-3b5788ee9784',
    'ply_44ae9048-3242-4654-881f-6d9d43347fa3',
]


def read(path):
    return json.loads(Path(path).read_text())


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n')


def freeze(path, data):
    if path.exists() and read(path) != data:
        raise ValueError(f'Frozen artifact changed: {path}')
    write(path, data)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare():
    import ir_v4
    sys.path.insert(0, str(TOOLING))
    import httpx
    from hosted_wave import client, get
    from release_deploy_pair import verify_owned
    cfg = read(CAMPAIGN / 'config.json')
    bundle = ROOT / 'examples/gods_of_the_arena/players/ir/forks/microplay'
    arms = {}
    with client() as c:
        game = get(c, '/v2/coworlds/' + cfg['target']['coworld_id'])
        assert game['version'] == cfg['game_version'] == '2026.9.16.5'
        assert '/tree/' + cfg['engine_commit'] + '/' in game['manifest']['game']['runnable']['source_url']
        members = read(STUDY / 'live-members.json')
        by_player = {r['player']['id']: r for r in members}
        opponents = [{'player_id': p, 'name': by_player[p]['player']['name'],
                      'version': by_player[p]['policy_version']['id'],
                      'label': by_player[p]['policy_version']['label']} for p in OTHER_PLAYERS]
        assert len({v['version'] for v in opponents}) == 9
        for name, folder, stem in [('parent', bundle.parent / 'jordan268', 'policy'),
                                   ('finish', bundle, 'finish'), ('combined', bundle, 'policy')]:
            source_path, ir_path = folder / (stem + '.bas'), folder / (stem + '.ir.json')
            source, policy = source_path.read_bytes(), read(ir_path)
            assert ir_v4.compiler.compile_policy(policy).encode() == source
            assert ir_v4.compiler.extract(source.decode(), policy) == policy
            out = STUDY / name
            out.mkdir(parents=True, exist_ok=True)
            (out / 'policy.bas').write_bytes(source)
            freeze(out / 'policy.ir.json', policy)
            version = PARENT
            if name != 'parent':
                meta = {'name': 'aaron-gota-microplay-' + name + '-0920',
                        'content_hash': sha(source_path), 'size_bytes': len(source),
                        'player_id': PLAYER, 'attributes': {}, 'tags': {
                            'game': 'gods_of_the_arena', 'game_version': cfg['game_version'],
                            'semantic_ir_sha256': ir_v4.compiler.digest(policy),
                            'change': name, 'validation': 'Local microplay qualified; hosted unvalidated; inert upload'}}
                freeze(out / 'upload-request.json', meta)
                receipt = out / 'uploaded-version.json'
                if not receipt.exists():
                    response = c.post('/stats/policies/files/upload', json=meta)
                    if response.status_code == 409:
                        response = c.post('/stats/policies/files/complete', json=meta)
                        response.raise_for_status()
                        uploaded = response.json()
                    else:
                        response.raise_for_status()
                        payload = response.json()
                        uploaded = payload.get('existing_policy_version')
                        if uploaded is None:
                            stored = httpx.put(payload['upload_url'], content=source,
                                               headers={'Content-Type': 'application/octet-stream'}, timeout=120)
                            stored.raise_for_status()
                            response = c.post('/stats/policies/files/complete', json=meta)
                            response.raise_for_status()
                            uploaded = response.json()
                    write(receipt, uploaded)
                uploaded = read(receipt)
                write(out / 'owned-readback.json', verify_owned(c, uploaded, PLAYER))
                version = uploaded['id']
            arms[name] = {'version': version, 'source_sha256': sha(source_path),
                          'ir_sha256': ir_v4.compiler.digest(policy)}
    plan = {'schema': 'gota-microplay-hosted-experiment/1', 'id': CYCLE,
            'target': cfg['target'], 'config': cfg['game_config'],
            'game_version': cfg['game_version'], 'engine_commit': cfg['engine_commit'],
            'subject_player': PLAYER, 'arms': arms, 'other_players': opponents,
            'episodes_per_arm': 40,
            'interventions': {'finish_minus_parent': 'Low-HP enemy hero priority',
                              'combined_minus_finish': 'Guarded lower-ID ally assistance'},
            'primary_checks': ['All ten VMs finish successfully', 'All replay ticks and actions match',
                               'Exact subject VM reconstructs hosted commands',
                               'Measure refinements and actual attack commands after refinement',
                               'Compare subject deaths/basic hits and allied deaths per exposure'],
            'interpretation': {'activation_required': True, 'superiority_claim': 'Not established by small unpaired cohort alone',
                               'seeds': 'Independently generated across requests; not seed-paired',
                               'roster': 'Frozen nine other players, subject rotates through ten seats',
                               'macro': 'Wins are diagnostic only', 'promotion': False}}
    freeze(STUDY / 'plan.ir.json', plan)
    for name, arm in arms.items():
        body = {'idempotency_key': CYCLE + '-' + name + '-40', 'target': cfg['target'],
                'game_config_overrides': cfg['game_config'], 'num_episodes': 40,
                'roster': [{'slot': -1, 'player': {'policy_ref': v}}
                           for v in [arm['version']] + [r['version'] for r in opponents]],
                'notes': f'Microplay counterfactual ablation {name}. Frozen nine other players; ten-seat rotation. Independent seeds across arms. Full replay and VM audit; micro metrics primary; no league promotion.'}
        freeze(STUDY / name / 'request.json', body)
    print(json.dumps(plan, indent=2), flush=True)


def submit():
    sys.path.insert(0, str(ROOT / 'tools/gota_autoresearch'))
    import researcher
    # Reserve the complete ablation before spending any part of it.
    with researcher.lock(CAMPAIGN / 'microplay-plan.lock'):
        for name in ['parent', 'finish', 'combined']:
            researcher.reserve(CAMPAIGN, read(STUDY / name / 'request.json'), STUDY / name / 'batch', CYCLE)
    os.environ['GOTA_RESEARCH_CYCLE'] = CYCLE
    for name in ['parent', 'finish', 'combined']:
        print(name, researcher.xp_create(CAMPAIGN, STUDY / name / 'request.json', STUDY / name / 'batch'), flush=True)


def harvest_arm(name):
    from hosted_wave import client, episodes, fetch
    from hosted_wave_audit import verify
    plan = read(STUDY / 'plan.ir.json')
    version = plan['arms'][name]['version']
    binary = Path(read(CAMPAIGN / 'config.json')['auditor'])
    binary_hash = sha(binary)
    folder = STUDY / name
    request = read(folder / 'batch/created.json')['id']
    with client() as c:
        while True:
            rows = episodes(c, request)
            write(folder / 'batch/episodes.json', rows)
            for ep in rows:
                if ep['status'] in {'failed', 'error', 'cancelled'}:
                    raise ValueError(f'Hosted episode failed: {ep["id"]}')
                if ep['status'] != 'completed':
                    continue
                fetch(c, ep, folder / 'artifacts', version)
                dest = folder / 'artifacts' / ep['id']
                verify(dest, binary, binary_hash)
            completed = sum(e['status'] == 'completed' for e in rows)
            progress = {'request': request, 'total': len(rows), 'completed': completed,
                        'audited': len(list((folder / 'artifacts').glob('*/audit.json')))}
            write(folder / 'progress.json', progress)
            print(name, progress, flush=True)
            if len(rows) == plan['episodes_per_arm'] and completed == len(rows):
                return progress
            time.sleep(20)


def harvest():
    sys.path.insert(0, str(TOOLING))
    with ThreadPoolExecutor(max_workers=3) as pool:
        for result in pool.map(harvest_arm, ['parent', 'finish', 'combined']):
            print(result, flush=True)


def probe_one(job):
    folder, source_arm, recorded_arm = job
    plan = read(STUDY / 'plan.ir.json')
    ep = read(folder / 'episode.json')
    slot = ep['policy_version_ids'].index(plan['arms'][recorded_arm]['version'])
    binary = STUDY / 'hosted-probe'
    source = STUDY / source_arm / 'policy.bas'
    prefix = 'probe' if source_arm == recorded_arm else 'counterfactual-' + source_arm
    receipt = folder / (prefix + '.json')
    identity = {'binary_sha256': sha(binary), 'source_sha256': sha(source),
                'replay_sha256': sha(folder / 'replay.bin'), 'source_arm': source_arm,
                'recorded_arm': recorded_arm, 'episode': ep['id']}
    if receipt.exists():
        result = read(receipt)
        assert all(result[k] == v for k, v in identity.items())
        return result
    env = dict(os.environ, PROBE_SLOT=str(slot), PROBE_POLICY=str(source))
    proc = subprocess.run([str(binary), '--replay', str(folder / 'replay.bin')],
                          env=env, text=True, capture_output=True, timeout=600)
    records = [json.loads(line) for line in proc.stdout.splitlines() if line.startswith('{')]
    if proc.returncode:
        if source_arm == recorded_arm or proc.returncode != 2 or not records or records[-1]['type'] != 'command_mismatch':
            raise ValueError(f'Probe failed {folder}: {proc.returncode} {proc.stderr} {proc.stdout[-3000:]}')
        result = identity | {'counterfactual': 'first_command_divergence', 'first_divergence': records[-1],
                             'limitation': 'Stops before divergent transition; no counterfactual outcome claim'}
    else:
        assert records[-1]['type'] == 'summary'
        assert records[-1]['ticks'] == read(folder / 'results.json')['ticks']
        result = identity | records[-1]
        if source_arm != recorded_arm:
            result['counterfactual'] = 'identical_full_trajectory_with_other_players_commands'
    raw = ('\n'.join(json.dumps(r, separators=(',', ':')) for r in records) + '\n').encode()
    trace = folder / (prefix + '.jsonl.gz')
    trace.write_bytes(gzip.compress(raw, mtime=0))
    result['trace_sha256'] = sha(trace)
    write(receipt, result)
    return result


def probe():
    """Audit every actual subject and both ablations on combined-arm tapes."""
    done = set()
    with ThreadPoolExecutor(max_workers=3) as pool:
        pending = {}
        while True:
            for future, key in list(pending.items()):
                if future.done():
                    result = future.result()
                    done.add(key)
                    del pending[future]
                    print('probe', len(done), key[1:], result.get('refinements', result.get('counterfactual')), flush=True)
            for arm in ['parent', 'finish', 'combined']:
                for marker in sorted((STUDY / arm / 'artifacts').glob('*/vm-validity.json')):
                    for source in ([arm, 'parent', 'finish'] if arm == 'combined' else [arm]):
                        key = (marker.parent, source, arm)
                        if key in done or key in pending.values() or len(pending) >= 3:
                            continue
                        pending[pool.submit(probe_one, key)] = key
            if len(done) == 200:
                return
            time.sleep(2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'submit', 'harvest', 'probe'])
    args = parser.parse_args()
    globals()[args.command]()
