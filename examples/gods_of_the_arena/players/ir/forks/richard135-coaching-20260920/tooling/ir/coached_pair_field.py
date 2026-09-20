"""Sampled league guardrail with both candidate players, after matched A/B passes."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import shutil
import subprocess
import sys
import time

from coached_league_live import ROOT as STUDY, AARON, OPTIMIZER
from hosted_wave import client, create, episodes, fetch
from hosted_wave_audit import verify
from policy_ir import HERE, read, write, digest
from release_field import DIVISION
from release_workspace import RUN
from win_hosted import live

ROOT = STUDY / 'field'


def prepare():
    game = live()
    comparison = read(STUDY / 'result.json')
    if not comparison['passed']:
        raise ValueError('Matched both-player comparison failed; no field promotion check')
    parent = read(STUDY / 'plan.json')
    if game['id'] != parent['target']['coworld_id']:
        raise ValueError('Live source changed')
    plan = {k: parent[k] for k in ['target', 'game_version', 'game_source', 'config']}
    plan.update(policy_version=parent['candidate_versions'][0], partner_version=parent['candidate_versions'][1],
                comparison_sha256=digest((STUDY / 'result.json').read_bytes()),
                minimum_allied_win_rate=parent['gates']['minimum_field_allied_win_rate'],
                design='One hundred sampled current-league games with both candidate players '
                       'and eight other players. Rotate both owned seats together. Exclude both '
                       'owned players from sampling. Report allied and opposed outcomes separately; '
                       'allied win fraction is the frozen broad-field guardrail. This sampled '
                       'request is not a matched A/B or independent confirmation of a win-rate gain.')
    ROOT.mkdir(exist_ok=True)
    if (ROOT / 'plan.json').exists() and read(ROOT / 'plan.json') != plan:
        raise ValueError('Frozen field plan changed')
    write(ROOT / 'plan.json', plan)
    shutil.copy2(RUN / 'r5/audit', ROOT / 'audit')
    body = {'idempotency_key': 'gota-pair-field-' + digest(plan)[:20], 'target': {'division_id': DIVISION},
            'game_config_overrides': plan['config'], 'num_episodes': 100,
            'excluded_players': [OPTIMIZER, AARON],
            'roster': [{'slot': -1, 'player': {'policy_ref': v}} for v in
                       [plan['policy_version'], plan['partner_version']]] +
                      [{'slot': -1, 'player': {'random': True}} for _ in range(8)],
            'notes': plan['design']}
    return plan, body


def run():
    plan, body = prepare()
    with client() as c:
        request = create(c, body, ROOT / 'batch')
    print('Paired field:', request, flush=True)
    with (ROOT / 'audit.log').open('a') as log:
        audit = subprocess.Popen([sys.executable, str(HERE / 'watch_hosted_audit.py'), str(ROOT), '--workers', '2'],
                                 stdout=log, stderr=log)
        try:
            with client() as c:
                while True:
                    rows = episodes(c, request)
                    write(ROOT / 'batch/episodes.json', rows)
                    if any(e['status'] in {'failed', 'cancelled', 'error'} for e in rows):
                        raise ValueError('Failed episode retained; do not interpret performance')
                    complete = [e for e in rows if e['status'] == 'completed']
                    for episode in complete:
                        fetch(c, episode, ROOT / 'artifacts', plan['policy_version'])
                    print('Paired field fetched', len(complete), '/100', flush=True)
                    if audit.poll() not in (None, 0):
                        raise ValueError('A full replay or VM check failed')
                    if len(complete) == 100:
                        write(ROOT / 'collection.json', {'episodes': 100, 'request_count': 1})
                        break
                    time.sleep(15)
            if audit.wait() != 0:
                raise ValueError('Full audit failed')
        finally:
            if audit.poll() is None:
                audit.terminate()
                audit.wait()
    report()


def report():
    plan = read(ROOT / 'plan.json')
    folders = [p.parent for p in (ROOT / 'artifacts').glob('*/.done')]
    if len(folders) != 100 or read(ROOT / 'collection.json')['episodes'] != 100:
        raise ValueError('Incomplete field request')
    binary = ROOT / 'audit'
    sha = digest(binary.read_bytes())
    with ThreadPoolExecutor(4) as pool:
        list(pool.map(lambda f: verify(f, binary, sha), folders))
    rows = []
    for folder in folders:
        ep, result, audit = [read(folder / n) for n in ['episode.json', 'results.json', 'audit.json']]
        roster = ep['policy_version_ids']
        if any(roster.count(v) != 1 for v in [plan['policy_version'], plan['partner_version']]):
            raise ValueError('Both owned versions must occur exactly once')
        own, partner = [roster.index(plan[k]) for k in ['policy_version', 'partner_version']]
        config = {k: v for k, v in ep['game_config'].items() if k not in {'seed', 'players', 'tokens'}}
        if (ep['coworld_id'] != plan['target']['coworld_id'] or ep['coworld_version'] != plan['game_version']
                or config != plan['config'] or partner != (own + 1) % 10):
            raise ValueError('Source/config/owned-seat rotation changed')
        owners = {p['position']: p['player_id'] for p in ep['participants']}
        if (owners[own] != OPTIMIZER or owners[partner] != AARON or
                any(v in {OPTIMIZER, AARON} for k, v in owners.items() if k not in {own, partner})):
            raise ValueError('Both owned identities or sampling exclusions differ')
        if [h['total_xp'] for h in audit['heroes']] != result['total_xp']:
            raise ValueError('XP disagrees with hosted result')
        heroes = [audit['heroes'][s] for s in [own, partner]]
        rows.append({'episode': ep['id'], 'seed': result['seed'], 'slot': own, 'partner_slot': partner,
                     'allied': own // 5 == partner // 5, 'win': heroes[0]['score'],
                     'partner_win': heroes[1]['score'], 'ticks': result['ticks'],
                     'both_gear': all(h['first_gear_tick'] >= 0 for h in heroes),
                     'owned_deaths': sum(h['deaths'] for h in heroes),
                     'owned_alive_ticks': sum(h['alive_ticks'] for h in heroes),
                     'owned_glory': [h['score'] * (h['total_xp'] - 200 * result['ticks'] / 1440) for h in heroes],
                     'roster': roster, 'replay_sha256': audit['replay_sha256']})
    if len({r['seed'] for r in rows}) != 100 or Counter(r['slot'] for r in rows) != Counter({s: 10 for s in range(10)}):
        raise ValueError('Wrong effective seeds or role coverage')
    allied = [r for r in rows if r['allied']]
    opposed = [r for r in rows if not r['allied']]
    if len(allied) != 80 or len(opposed) != 20:
        raise ValueError('Unexpected allied/opposed split')
    if any(r['win'] != r['partner_win'] for r in allied) or any(r['win'] + r['partner_win'] > 1 for r in opposed):
        raise ValueError('Invalid paired team outcome')
    wins = sum(r['win'] for r in allied)
    result = {'games': 100, 'allied_games': 80, 'allied_wins': wins,
              'opposed_games': 20, 'opposed_optimizer_wins': sum(r['win'] for r in opposed),
              'opposed_aaron_wins': sum(r['partner_win'] for r in opposed),
              'both_equipment_games': sum(r['both_gear'] for r in rows),
              'passed': wins / 80 >= plan['minimum_allied_win_rate'] and all(r['both_gear'] for r in rows),
              'design': plan['design'], 'rows': rows}
    write(ROOT / 'result.json', result)
    print({k: v for k, v in result.items() if k != 'rows'}, flush=True)


if __name__ == '__main__':
    run()
