"""Preregistered 100-game broad-field check after fresh hosted confirmation."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import shutil
import time

from economy_hosted import summarize
from hosted_wave import client, create, episodes, fetch, get, TERMINAL
from hosted_wave_audit import verify
from policy_ir import digest, read, write
from prepare_campaign_xp import LEAGUE

OWNED_PLAYERS = ['ply_630a768f-d623-44b2-80fa-36968d6fa75a',
                'ply_594ec24d-d7f3-4370-a000-468354ec41c9']
DIVISION = 'div_a4534073-c5d2-4193-a94a-93d9c5e2e443'


def run(directory, command, dry_run=False):
    root = directory / 'hosted-confirmation'
    plan, verdict = read(root / 'plan.json'), read(root / 'result.json')
    if not verdict['passed']:
        raise ValueError('Fresh hosted confirmation must pass before field advancement')
    name = plan['candidate']
    version = read(directory / 'hosted-discovery' / name / 'uploaded-version.json')['id']
    out = directory / 'field'
    out.mkdir(exist_ok=True)
    body = {'idempotency_key': 'gota-economy-field-20260916-' + version[:8] + '-' + digest(verdict)[:10],
            'target': {'division_id': DIVISION}, 'game_config_overrides': plan['config'],
            'num_episodes': 100, 'excluded_players': OWNED_PLAYERS,
            'roster': [{'slot': -1, 'player': {'policy_ref': version}}] +
                      [{'slot': -1, 'player': {'random': True}} for _ in range(9)],
            'notes': 'Preregistered100episode current-champion field guardrail after fresh400games/arm confirmation. Exclude both owned players from random seats. At least50wins, gear every game, full replay/VM validity; descriptive transfer check, not another A/B.'}
    if command == 'launch':
        field_plan = {'policy_version': version, 'candidate': name,
              'target': plan['target'], 'game_version': plan['game_version'], 'config': plan['config'],
              'excluded_players': OWNED_PLAYERS, 'minimum_wins': 50,
              'confirmation_sha256': digest((root / 'result.json').read_bytes())}
        if (out / 'plan.json').exists() and read(out / 'plan.json') != field_plan:
            raise ValueError('Frozen field plan changed')
        write(out / 'plan.json', field_plan)
        shutil.copy2(root / name / 'part-0/audit', out / 'audit')
        with client() as c:
            league = get(c, '/v2/leagues/' + LEAGUE)
            coworld = get(c, '/v2/coworlds/' + league['game']['coworld_id'])
            if (coworld['id'] != plan['target']['coworld_id'] or coworld['version'] != plan['game_version'] or
                    coworld['manifest']['game']['runnable']['source_url'] != plan['game_source']):
                raise ValueError('Published game changed before field evaluation')
            write(out / 'coworld-before-launch.json', coworld)
            request = create(c, body, out / 'batch', dry_run)
        print({'request': request, 'episodes': 100}, flush=True)
        return
    request = read(out / 'batch/created.json')['id']
    if command == 'harvest':
        with client() as c:
            while True:
                entries = episodes(c, request)
                write(out / 'batch/episodes.json', entries)
                complete = 0
                for ep in entries:
                    if ep['status'] in TERMINAL:
                        fetch(c, ep, out / 'artifacts', version)
                        complete += 1
                print(f'Field: {complete}/100 fetched', flush=True)
                if complete == 100:
                    write(out / 'collection.json', {'episodes': 100, 'request_count': 1})
                    return
                time.sleep(15)
    binary = out / 'audit'
    sha = digest(binary.read_bytes())
    folders = sorted(p.parent for p in (out / 'artifacts').glob('*/.done'))
    if len(folders) != 100:
        raise ValueError('Incomplete field collection')
    with ThreadPoolExecutor(4) as pool:
        list(pool.map(lambda f: verify(f, binary, sha), folders))
    rows = []
    for folder in folders:
        ep, result, audit = [read(folder / n) for n in ['episode.json', 'results.json', 'audit.json']]
        cfg = {k: v for k, v in ep['game_config'].items() if k not in {'seed', 'players', 'tokens'}}
        roster = ep['policy_version_ids']
        if (ep['coworld_id'] != plan['target']['coworld_id'] or ep['coworld_version'] != plan['game_version']
                or cfg != plan['config'] or roster.count(version) != 1):
            raise ValueError('Field subject, game version or configuration changed')
        slot = roster.index(version)
        if any(p['player_id'] in OWNED_PLAYERS for p in ep['participants'] if p['position'] != slot):
            raise ValueError('An owned player leaked into a sampled seat')
        hero = audit['heroes'][slot]
        if [h['total_xp'] for h in audit['heroes']] != result['total_xp']:
            raise ValueError('Field XP disagreement')
        rows.append({'episode': ep['id'], 'slot': slot, 'seed': result['seed'], 'class': hero['class'],
                     'win': hero['score'], 'deaths': hero['deaths'], 'alive_ticks': hero['alive_ticks'],
                     'ticks': result['ticks'], 'xp': hero['total_xp'], 'first_gear_tick': hero['first_gear_tick'],
                     'glory': hero['score'] * (hero['total_xp'] - 100 * result['ticks'] / 1440),
                     'timeout': result['outcome'] == 'time_limit', 'roster': roster})
    prior_seeds = {r['seed'] for path in [root / 'result.json', directory / 'hosted-discovery/result.json']
                   for arm in read(path)['arms'].values() for r in arm['rows']}
    if any(r['seed'] in prior_seeds for r in rows):
        raise ValueError('Field reused a measured seed')
    metrics = summarize([{'rows': rows}])
    checks = {'wins': metrics['wins'] >= 50, 'equipment': metrics['equipment_games'] == 100}
    write(out / 'result.json', {'candidate': name, 'version': version, 'checks': checks,
                                'passed': all(checks.values()), **metrics})
    print({k: v for k, v in read(out / 'result.json').items() if k != 'rows'}, flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory', type=Path)
    p.add_argument('command', choices=['launch', 'harvest', 'report'])
    p.add_argument('--dry-run', action='store_true')
    a = p.parse_args()
    run(a.directory.resolve(), a.command, a.dry_run)
