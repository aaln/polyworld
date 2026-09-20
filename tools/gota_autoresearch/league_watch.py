"""Read-only three-hour league checks feeding the existing research worker."""
from collections import Counter
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import sys

ROOT = Path(os.environ.get('GOTA_RESEARCH_ROOT', '/Users/aaln/experiments/softmax/gota-autoresearch'))
LEAGUE = 'league_3c60897b-25cf-4b37-9d1a-8554c1198f28'
DIVISION = 'div_a4534073-c5d2-4193-a94a-93d9c5e2e443'
OWN = {'Aaron': 'ply_630a768f-d623-44b2-80fa-36968d6fa75a',
       'Coach': 'ply_594ec24d-d7f3-4370-a000-468354ec41c9'}
RIVALS = {'Richard': 'ply_ded11f40-3e30-4921-b019-f7f6bc3e9c83',
          'Alex Smith': 'ply_4e9a2db0-dbc2-4283-b4cc-3ce79e9f8d40',
          'Jordan': 'ply_bcb80069-fb0c-4ba5-a45c-06b647870aeb'}

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(json.dumps(data, indent=2) + '\n')
    os.replace(temp, path)

def head_to_head(episodes, champions):
    """Only completed uniform 5v5 games between the exact current champions."""
    counts, evidence, seen = {}, [], set()
    for ep in episodes:
        if ep['id'] in seen or ep.get('status') != 'completed':
            continue
        seen.add(ep['id'])
        parts = {p['position']: p for p in ep.get('participants', [])}
        scores = {p['position']: p['score'] for p in ep.get('participant_scores', [])}
        if set(parts) != set(range(10)) or set(scores) != set(range(10)):
            continue
        teams = [{(parts[i].get('player_id'), parts[i].get('policy_version_id'))
                  for i in range(start, start + 5)} for start in (0, 5)]
        if any(len(team) != 1 for team in teams):
            continue
        for name, player in OWN.items():
            if player not in champions:
                continue
            own = (player, champions[player]['version'])
            for side, team in enumerate(teams):
                if own not in team:
                    continue
                for rival_name, rival in RIVALS.items():
                    if rival not in champions or (rival, champions[rival]['version']) not in teams[1-side]:
                        continue
                    a = {scores[i] for i in range(side*5, side*5+5)}
                    b = {scores[i] for i in range((1-side)*5, (1-side)*5+5)}
                    if len(a) != 1 or len(b) != 1 or not a <= {0, 1} or not b <= {0, 1}:
                        continue
                    us, them = next(iter(a)), next(iter(b))
                    if us + them > 1:
                        continue
                    key = name + '/' + rival_name + '/' + ('red' if side == 0 else 'blue')
                    outcome = 'wins' if us else 'losses' if them else 'draws'
                    counts.setdefault(key, Counter())[outcome] += 1
                    evidence.append({'episode': ep['id'], 'comparison': key, 'outcome': outcome,
                        'own_version': own[1], 'rival_version': champions[rival]['version'],
                        'game_version': ep.get('coworld_version'), 'completed_at': ep.get('completed_at')})
    return {k: {x: v[x] for x in ('wins', 'losses', 'draws')} for k, v in counts.items()}, evidence

def run():
    cfg = json.loads((ROOT / 'config.json').read_text())
    sys.path.insert(0, cfg['tooling'])
    from hosted_wave import client, get
    at = datetime.now(timezone.utc)
    folder = ROOT / 'league-watch' / at.strftime('%Y%m%dT%H%M%S.%fZ')
    with client() as c:
        board = get(c, f'/v2/divisions/{DIVISION}/leaderboard?include_recent_rounds=false')
        members = get(c, f'/v2/league-policy-memberships?league_id={LEAGUE}&champions_only=true&limit=100')
        game = get(c, '/v2/coworlds/' + cfg['target']['coworld_id'])
        rounds = get(c, f'/v2/rounds?division_id={DIVISION}&limit=12')
        episodes = []
        for row in rounds['entries']:
            data = get(c, f"/v2/rounds/{row['id']}/episodes?limit=1000")
            episodes.extend(data if isinstance(data, list) else data['entries'])
    champions = {}
    for row in members:
        if row['is_champion'] and row['status'] == 'competing':
            key = row['player']['id']
            if key in champions:
                raise ValueError('Multiple champion rows for one player')
            champions[key] = {'name': row['player']['name'], 'membership': row['id'],
                'version': row['policy_version']['id'], 'label': row['policy_version']['label'],
                'substatus': row.get('substatus')}
    counts, evidence = head_to_head(episodes, champions)
    ranks = {r['player_id']: {'rank': r['rank'], 'name': r['player_name'],
                             'score': r['score'], 'score_label': r['score_label']} for r in board}
    source = game['manifest']['game']['runnable']['source_url']
    release_matches = game['version'] == cfg['game_version'] and f"/tree/{cfg['engine_commit']}/" in source
    alerts = []
    if not release_matches:
        alerts.append('Published game changed: re-establish a clean compatible baseline before comparative tests.')
    for name, player in OWN.items():
        if player not in champions:
            alerts.append(name + ' has no competing champion.')
    if not any(ranks.get(p, {}).get('rank') == 1 for p in OWN.values()):
        alerts.append('Neither requested player is #1; inspect current leaders and recent losses.')
    for name in RIVALS:
        if not any('/'+name+'/' in key for key in counts):
            alerts.append('No recent exact-current-version head-to-head evidence against ' + name + '.')
    for key, value in counts.items():
        if value['losses'] or value['draws']:
            alerts.append(key + ' has unresolved losses/draws: ' + str(value))
    previous = ROOT / 'LEAGUE_STATUS.json'
    if previous.exists():
        old = json.loads(previous.read_text()).get('champions', {})
        for name, player in RIVALS.items():
            if old.get(player, {}).get('version') != champions.get(player, {}).get('version'):
                alerts.append(name + ' champion changed; pin fresh tests while preserving old evidence.')
    result = {'checked_at': at.isoformat(), 'interval_seconds': 10800,
        'league_id': LEAGUE, 'division_id': DIVISION, 'game_version': game['version'],
        'release_matches_campaign': release_matches, 'champions': champions,
        'standings': ranks, 'top_player': min(board, key=lambda r: r['rank']) if board else None,
        'recent_exact_matchups': counts, 'episodes': evidence, 'alerts': alerts,
        'rounds_checked': [r['id'] for r in rounds['entries']],
        'evidence_scope': 'Latest 12 rounds, completed exact-current-champion uniform 5v5 games. Observational API scores; replays must be audited before experimental conclusions.',
        'research_action': 'Read FOCUS.md. Resume existing requests, diagnose losses, test IR forks against exact Richard135 and Alex gota-g002:v1 plus current rivals and Jordan preservation; deploy only a fully validated improvement.',
        'raw_directory': str(folder)}
    for filename, value in [('leaderboard.json', board), ('memberships.json', members),
                            ('rounds.json', rounds), ('episodes.json', episodes), ('check.json', result)]:
        write(folder / filename, value)
    write(previous, result)
    lines = ['# Latest league check', '', 'Checked ' + result['checked_at'], '',
             'A successful check records this timestamp; scheduling is managed by the operator.', '',
             '| Player | Rank | Score | Current policy |', '|---|---:|---:|---|']
    for name, player in {**OWN, **RIVALS}.items():
        rank = ranks.get(player, {})
        lines.append(f"| {name} | {rank.get('rank', 'unranked')} | {rank.get('score', '')} | {champions.get(player, {}).get('label', 'inactive')} |")
    lines += ['', result['evidence_scope'], '', 'Research signals:', '']
    lines += ['- ' + text for text in alerts] or ['- Keep validating both target matchups and the field.']
    lines += ['', 'Raw evidence: ' + str(folder), '', 'See FOCUS.md for current authorization and validation gates.']
    (ROOT / 'LEAGUE_STATUS.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps({'checked_at': result['checked_at'], 'ranks': {name: ranks.get(p, {}).get('rank') for name, p in {**OWN, **RIVALS}.items()},
                      'alerts': alerts, 'report': str(ROOT / 'LEAGUE_STATUS.md')}), flush=True)

if __name__ == '__main__':
    ROOT.mkdir(parents=True, exist_ok=True)
    with (ROOT / 'league-watch.lock').open('a+') as held:
        try:
            fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            sys.exit(0)
        try:
            run()
        except Exception as error:
            write(ROOT / 'league-watch-error.json', {'at': datetime.now(timezone.utc).isoformat(),
                'type': type(error).__name__, 'success': False,
                'action': 'Check service stderr/auth/network; previous LEAGUE_STATUS timestamp is stale.'})
            raise
