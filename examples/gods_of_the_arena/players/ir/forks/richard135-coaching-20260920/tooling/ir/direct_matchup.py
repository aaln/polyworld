"""Frozen side-swapped 40-game team probes against one exact public champion."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys
import time

from hosted_wave import client, create, episodes
from hosted_wave_audit import verify as audit
from policy_ir import HERE, compile_policy, digest, extract, read, write
from release_workspace import RUN
from win_hosted import live


def prepare(root):
    game = live()
    target = read(root / 'target.json')
    expected = 'Jordan-ply_bcb80069-fb0c-4ba5-a45c-06b647870aeb:v148'
    if target['label'] != expected or target['version'] != 148:
        raise ValueError('Exact requested rival was not resolved')
    version = '810d3860-af35-4fed-9364-a4e4bd8b0c2b'
    owned = read(root / 'own-champions.json')
    if len(owned) != 2 or version not in {p['policy_version']['id'] for p in owned}:
        raise ValueError('Unexpected deployed pair')
    ir = read(HERE / 'win_bounded_0916.evaluated.ir.json')
    basic = (HERE / 'win_bounded_0916.evaluated.bas').read_bytes()
    if compile_policy(ir).encode() != basic or extract(basic.decode(), ir) != ir:
        raise ValueError('IR/BASIC parity failed')
    prior = read(RUN / 'win-first-study/rival-matchups/plan.json')
    plan = {k: prior[k] for k in ['target', 'game_version', 'game_source', 'config']}
    if game['version'] != plan['game_version'] or game['manifest']['game']['runnable']['source_url'] != plan['game_source']:
        raise ValueError('Game changed')
    plan.update(policy_version=version, policy_label='aaron-gota-ir-win-bounded-0916:v1',
                rival=target['label'], rival_version=target['id'], episodes_per_color=40,
                basic_sha256=digest(basic), ir_sha256=digest(ir),
                design='Five identical copies per team, forty seeded repeats per color. All ten seats pinned. Finish both colors before interpretation; no interim tuning.',
                interpretation='Two fixed tactical lineups. Measure exact command diversity; seeded repeats need not be independent. This does not estimate single-seat contribution in mixed league teams.')
    if (root / 'plan.json').exists() and read(root / 'plan.json') != plan:
        raise ValueError('Frozen plan changed')
    write(root / 'plan.json', plan)
    for color in ['red', 'blue']:
        folder = root / 'jordan' / color
        folder.mkdir(parents=True, exist_ok=True)
        slots = list(range(5)) if color == 'red' else list(range(5, 10))
        roster = [version if s in slots else target['id'] for s in range(10)]
        arm = plan | {'own_slots': slots, 'roster': roster, 'color': color}
        if (folder / 'plan.json').exists() and read(folder / 'plan.json') != arm:
            raise ValueError('Frozen arm changed')
        write(folder / 'plan.json', arm)
        shutil.copy2(RUN / 'r3/audit', folder / 'audit')
        body = {'idempotency_key': f'gota-direct-0916-{digest(plan)[:16]}-{color}',
                'target': plan['target'], 'game_config_overrides': plan['config'],
                'num_episodes': 40,
                'roster': [{'slot': s, 'player': {'policy_ref': v}} for s, v in enumerate(roster)],
                'notes': f'Exact Jordan v148 direct team probe. Current bounded policy on {color}; 40 seeded repeats. Other color tested separately. No policy tuning or league selection.'}
        with client() as c:
            create(c, body, folder / 'batch', dry_run=True)


def compare(root):
    plan = read(root / 'plan.json')
    rival_key = plan.get('rival_key', 'jordan')
    rows, seen = [], set()
    for color in ['red', 'blue']:
        folder = root / rival_key / color
        arm = read(folder / 'plan.json')
        if read(folder / 'collection.json')['episodes'] != 40:
            raise ValueError('Incomplete collection')
        binary = folder / 'audit'
        sha = digest(binary.read_bytes())
        folders = sorted(p.parent for p in (folder / 'artifacts').glob('*/.done'))
        if len(folders) != 40:
            raise ValueError('Incomplete artifacts')
        for f in folders:
            audit(f, binary, sha)
            ep, result, proof = [read(f / n) for n in ['episode.json', 'results.json', 'audit.json']]
            cfg = {k: v for k, v in ep['game_config'].items() if k not in {'seed', 'players', 'tokens'}}
            if (ep['policy_version_ids'] != arm['roster'] or cfg != plan['config'] or
                ep['coworld_version'] != plan['game_version'] or ep['coworld_id'] != plan['target']['coworld_id'] or result['seed'] in seen):
                raise ValueError('Roster/config/source/seed mismatch')
            seen.add(result['seed'])
            if [h['total_xp'] for h in proof['heroes']] != result['total_xp']:
                raise ValueError('XP mismatch')
            own = {result['scores'][s] for s in arm['own_slots']}
            other = {result['scores'][s] for s in range(10) if s not in arm['own_slots']}
            if len(own) != 1 or len(other) != 1 or not (own | other) <= {0, 1}:
                raise ValueError('Invalid team scores')
            win, loss = next(iter(own)), next(iter(other))
            if win + loss > 1:
                raise ValueError('Both teams won')
            heroes = [proof['heroes'][s] for s in arm['own_slots']]
            rival_heroes = [proof['heroes'][s] for s in range(10) if s not in arm['own_slots']]
            rows.append({'episode': ep['id'], 'seed': result['seed'], 'color': color,
                         'win': win, 'loss': loss, 'draw': int(not win and not loss), 'ticks': result['ticks'],
                         'gear_heroes': sum(h['first_gear_tick'] >= 0 for h in heroes),
                         'deaths': sum(h['deaths'] for h in heroes), 'rival_deaths': sum(h['deaths'] for h in rival_heroes),
                         'replay_sha256': proof['replay_sha256']})
    result = {'label': plan['rival'], 'games': 80,
              **{label: sum(r[k] for r in rows) for k, label in [('win', 'wins'), ('loss', 'losses'), ('draw', 'draws')]},
              'colors': {c: {k: sum(r[k] for r in rows if r['color'] == c) for k in ['win', 'loss', 'draw']} for c in ['red', 'blue']},
              'all_full_audits_passed': True, 'rows': rows}
    write(root / 'result.json', {'policy_version': plan['policy_version'], 'games': 80,
                                'rivals': {rival_key: result}, 'scope': plan['interpretation']})
    print({k: v for k, v in result.items() if k != 'rows'}, flush=True)


def run_prepared(root):
    jobs = []
    rival_key = read(root / 'plan.json').get('rival_key', 'jordan')
    try:
        for color in ['red', 'blue']:
            live()
            folder = root / rival_key / color
            with client() as c:
                request = create(c, read(folder / 'batch/request.json'), folder / 'batch')
                print(color, request, flush=True)
                for cmd, name in [([str(HERE / 'rival_matchups.py'), str(folder), 'harvest'], 'harvest.log'),
                                  ([str(HERE / 'watch_hosted_audit.py'), str(folder), '--workers', '2'], 'audit.log')]:
                    log = (folder / name).open('a')
                    jobs.append((subprocess.Popen([sys.executable, *cmd], stdout=log, stderr=log), log, folder / name))
                while True:
                    entries = episodes(c, request)
                    counts = dict(Counter(e['status'] for e in entries))
                    write(folder / 'server-progress.json', {'request': request, 'statuses': counts, 'checked_at': datetime.now(timezone.utc).isoformat()})
                    if any(e['status'] in {'failed', 'cancelled', 'error'} for e in entries):
                        raise ValueError('Failed episode retained; explicit recovery required')
                    failures = [str(path) for p, _, path in jobs if p.poll() not in (None, 0)]
                    if failures:
                        raise ValueError(f'Collector failed: {failures}')
                    if counts == {'completed': 40}:
                        break
                    time.sleep(15)
            # Drain artifacts and full audits before launching the next arm.
            failures = [str(path) for p, _, path in jobs if p.wait() != 0]
            if failures:
                raise ValueError(f'Collector failed: {failures}')
        failures = [str(path) for p, _, path in jobs if p.wait() != 0]
        if failures:
            raise ValueError(f'Collector failed: {failures}')
        compare(root)
    finally:
        for p, log, _ in jobs:
            if p.poll() is None:
                p.terminate()
                p.wait()
            log.close()


def run(root):
    prepare(root)
    run_prepared(root)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('command', choices=['prepare', 'run', 'compare'])
    args = parser.parse_args()
    globals()[args.command](args.directory.resolve())
