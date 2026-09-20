"""Fetch and fully audit watched league games; reconstruct only our actual slots."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess

from hosted_wave import client, fetch, get
from hosted_wave_audit import verify
from inspect_backdoor import inspect as backdoor
from league_threat_watch import ROOT
from policy_ir import ROOT as REPO, digest, read, write
from release_workspace import RUN, VERSION
from review_defense_stalls import inspect as stalls


def run_native(binary, tape, output, env=None):
    if output.exists():
        last = json.loads(output.read_text().splitlines()[-1])
        if last.get('type') == 'summary': return last
        raise ValueError('Incomplete retained trace: ' + str(output))
    tmp = output.with_suffix('.tmp')
    with tmp.open('w') as f:
        subprocess.run([str(RUN / 'r5' / binary), '--replay', str(tape)], cwd=REPO,
                       env=dict(os.environ, **(env or {})), stdout=f, check=True, timeout=600)
    last = json.loads(tmp.read_text().splitlines()[-1])
    if last.get('type') != 'summary': raise ValueError('Incomplete native reconstruction')
    tmp.replace(output)
    return last


def one(item, registry):
    eid, rows = item
    out = ROOT / 'artifacts' / eid
    ready = out / 'review.json'
    if ready.exists(): return read(ready)
    with client() as c:
        episode = get(c, '/v2/episode-requests/' + eid)
        if episode['coworld_version'] != VERSION:
            raise ValueError('New release requires a source-matched auditor: ' + episode['coworld_version'])
        version = rows[0]['own_versions'][0]
        fetch(c, episode, out.parent, version, allow_repeated_subject=True)
    binary = RUN / 'r5/fast/audit-hosted'
    calibration = read(RUN / 'r5/fast/audit-calibration/proof.json')
    if digest(binary.read_bytes()) != calibration['optimized_binary_sha256']:
        raise ValueError('Auditor calibration changed')
    verify(out, binary, digest(binary.read_bytes()))
    replay = out / 'decoded.jsonl'
    decoded = run_native('macro-replay-v5', out / 'replay.bin', replay)
    if decoded['hash_mismatches']: raise ValueError('Decoded replay failed')
    reviews = []
    for row in rows:
        versions = row['own_versions']
        sources = [registry[v] for v in versions]
        if len({x['sha256'] for x in sources}) != 1:
            raise ValueError('Mixed owned source programs need separate slot reconstructions')
        source = Path(sources[0]['path'])
        if digest(source.read_bytes()) != sources[0]['sha256']:
            raise ValueError('Owned source registry changed')
        team = row['team']
        summary = run_native('replay-slots-probe', out / 'replay.bin', out / f'decisions-team-{team}.jsonl',
                             {'PROBE_POLICY': str(source), 'PROBE_SLOTS': ','.join(map(str, row['own_slots']))})
        if not summary['all_state_hashes_equal'] or not summary['all_actions_consumed']:
            raise ValueError('Owned replay reconstruction failed')
        idle = stalls(replay, team)
        idle['stationary_repeated_order_windows'] = [r for r in idle['stationary_repeated_order_windows'] if r['slot'] in row['own_slots']]
        write(out / f'stalls-team-{team}.json', idle)
        response = backdoor(replay, team, row['own_slots'])
        write(out / f'backdoor-team-{team}.json', response)
        reviews.append(row | {'reconstruction': summary, 'source_sha256': sources[0]['sha256'],
                       'stationary_owned_windows': len(idle['stationary_repeated_order_windows']),
                       'visible_base_attack_samples': response['visible_structure_attack_samples'],
                       'isolated_attack_samples': response['isolated_samples']})
    result = {'episode': eid, 'ticks': decoded['ticks'], 'winner': decoded['winner'],
              'full_audit': True, 'teams': reviews, 'replay_sha256': digest((out / 'replay.bin').read_bytes()),
              'note': 'Complete source-matched replay and all actual owned commands reconstructed. Stationary windows can include intentional guard duty; mixed wins/losses do not isolate opponent causality.'}
    write(ready, result)
    print(eid, [(r['outcome'], r['stationary_owned_windows']) for r in reviews], flush=True)
    return result


def main():
    state = read(ROOT / 'state.json')
    registry = read(ROOT / 'source-registry.json')
    # Prioritize defeats, then gather wins/draws as comparison evidence.
    items = sorted(state['episodes'].items(), key=lambda item: not any(r['needs_replay_review'] for r in item[1]))
    with ThreadPoolExecutor(2) as pool:
        rows = list(pool.map(lambda item: one(item, registry), items))
    write(ROOT / 'reviews.json', {'episodes': len(rows), 'rows': rows})


if __name__ == '__main__': main()
