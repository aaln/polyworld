"""Audit public round replays and compare descriptive, class-confounded behavior."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import gzip
import json
from pathlib import Path
import re
import subprocess
import sys

from hosted_wave import client
from policy_ir import digest, read, write


def run(directory):
    live = directory / 'live'
    binary = (directory.parent / 'motion-campaign-20260915/audit-field').resolve()
    binary_hash = digest(binary.read_bytes())
    labels = {m['policy_version']['id']: m['policy_version']['label'] for m in read(live / 'champions.json')}
    episodes = [ep for path in live.glob('round_*-episodes.json') for ep in read(path)['entries']]
    out = directory / 'league-replays'
    out.mkdir(exist_ok=True)

    def inspect(ep):
        folder = out / ep['id']
        folder.mkdir(exist_ok=True)
        write(folder / 'episode.json', ep)
        if ep['status'] != 'completed':
            raise ValueError('Retain incomplete league episode')
        with client() as c:
            for kind, name in [('results', 'results.json'), ('replay', 'replay.bin'), ('logs', 'game.log')]:
                path = folder / name
                if path.exists():
                    continue
                response = c.get(f"/v2/episode-requests/{ep['id']}/artifacts/{kind}")
                response.raise_for_status()
                data = response.content
                if kind == 'replay' and data.startswith(b'\x1f\x8b'):
                    data = gzip.decompress(data)
                path.write_bytes(data)
        result = read(folder / 'results.json')
        if not (folder / 'audit.json').exists():
            proc = subprocess.run([str(binary), '--replay', str((folder / 'replay.bin').resolve())],
                                  capture_output=True, text=True, timeout=600, check=True)
            audit = json.loads(proc.stdout.splitlines()[-1])
            audit.update(binary_sha256=binary_hash, replay_sha256=digest((folder / 'replay.bin').read_bytes()))
            write(folder / 'audit.json', audit)
        audit = read(folder / 'audit.json')
        active = re.findall(r'scripts: (\d+)/10 active', (folder / 'game.log').read_text())
        if (audit['binary_sha256'] != binary_hash or audit['replay_sha256'] != digest((folder / 'replay.bin').read_bytes())
                or audit['hash_mismatches'] or audit['ticks'] != result['ticks']
                or audit['recorded_ticks'] != result['ticks'] or audit['actions_consumed'] != audit['recorded_actions']
                or audit['seed'] != result['seed'] or [h['score'] for h in audit['heroes']] != result['scores']
                or [h['total_xp'] for h in audit['heroes']] != result['total_xp'] or not active or active[-1] != '10'):
            raise ValueError('Incomplete replay or VM validity: ' + ep['id'])
        return [{'episode': ep['id'], 'round': ep['round_id'], 'version': ep['policy_version_ids'][slot],
                 'ticks': result['ticks'], 'replay_sha256': audit['replay_sha256'], **hero}
                for slot, hero in enumerate(audit['heroes'])]

    with ThreadPoolExecutor(3) as pool:
        rows = [row for rr in pool.map(inspect, episodes) for row in rr]
    metrics = {}
    for version in sorted({r['version'] for r in rows}):
        rr = [r for r in rows if r['version'] == version]
        metrics[version] = {'label': labels.get(version, version), 'games': len(rr),
                            'wins': sum(r['score'] for r in rr),
                            'xp_per_minute': sum(r['total_xp'] for r in rr) * 1440 / sum(r['ticks'] for r in rr),
                            'deaths_per_alive_minute': sum(r['deaths'] for r in rr) * 1440 / sum(r['alive_ticks'] for r in rr),
                            'stationary_alive_share': sum(r['stationary_alive_ticks'] for r in rr) / sum(r['alive_ticks'] for r in rr),
                            'items': dict(Counter(item for r in rr for item in r['inventory'] if item != 'NoItem')),
                            'classes': dict(Counter(r['class'] for r in rr))}
    report = {'audited_episodes': len(episodes), 'game_version': read(live / 'snapshot.json')['game_version'],
              'metrics': metrics, 'rows': rows,
              'limitations': 'Observational league games with different classes/teams/durations: not causal policy A/B. No opponent source or private policy logs accessed. Movement measured from replay states; stationary includes useful attacks.'}
    write(out / 'report.json', report)
    print(json.dumps({'episodes': len(episodes), 'metrics': metrics}, indent=2), flush=True)


if __name__ == '__main__':
    run(Path(sys.argv[1]).resolve())
