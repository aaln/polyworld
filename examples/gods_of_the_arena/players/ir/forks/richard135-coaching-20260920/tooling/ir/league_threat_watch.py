"""Bounded league-round watch; persist actual losses for replay-guided research.

Read-only on the service. Wins, defeats, draws and same-owner policy duels stay
distinct. A losing mixed roster identifies a replay to inspect, not a causal
claim against every opponent in that team.
"""
import argparse
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
import time

from hosted_wave import client, get
from jordan_lineup import STUDY
from policy_ir import HERE, read, write
from prepare_campaign_xp import DIVISION, LEAGUE
from release_deploy import AARON, champions
from release_hosted import OPTIMIZER

ROOT = STUDY / 'league-watch'
OWNERS = {AARON, OPTIMIZER}


def classify(episode, versions):
    if episode['status'] != 'completed': return []
    scores = {p['position']: p['score'] for p in episode['participant_scores']}
    participants = {p['position']: p for p in episode['participants']}
    if set(scores) != set(range(10)) or set(participants) != set(range(10)):
        raise ValueError('Incomplete ten-hero result')
    own = [p for p in participants.values() if p['player_id'] in OWNERS
           and p['policy_version_id'] in versions[p['player_id']]]
    rows = []
    for team in sorted({p['position'] // 5 for p in own}):
        slots = list(range(5 * team, 5 * team + 5))
        wins = {scores[s] for s in slots}
        losses = {scores[s] for s in range(10) if s not in slots}
        if len(wins) != 1 or len(losses) != 1 or not (wins | losses) <= {0, 1}:
            raise ValueError('Invalid team scores')
        win, loss = next(iter(wins)), next(iter(losses))
        if win + loss > 1: raise ValueError('Both teams won')
        opposing = [p for s, p in participants.items() if s not in slots]
        opposing_ids = {p['player_id'] for p in opposing}
        self_duel = opposing_ids <= OWNERS
        rivals = {p['policy_version_id']: {'id': p['policy_version_id'], 'player_id': p['player_id'],
                   'label': p['policy_name'] + ':v' + str(p['version'])} for p in opposing if p['player_id'] not in OWNERS}
        rows.append({'episode': episode['id'], 'team': team,
                     'own_slots': [p['position'] for p in own if p['position'] in slots],
                     'owners': sorted({p['player_id'] for p in own if p['position'] in slots}),
                     'own_versions': sorted({p['policy_version_id'] for p in own if p['position'] in slots}),
                     'outcome': 'win' if win else 'loss' if loss else 'draw',
                     'self_duel': self_duel, 'opponents': list(rivals.values()),
                     'distinct_players': len({p['player_id'] for p in participants.values()}),
                     'needs_replay_review': bool(loss and not self_duel),
                     'scope': 'One team outcome, not five independent hero results. Mixed opponents are observational associations.'})
    return rows


def page_all(c, path, stop_before=None):
    entries = []
    while True:
        response = get(c, path)
        entries.extend(response['entries'])
        if stop_before and response['entries'] and response['entries'][-1]['created_at'] < stop_before:
            return entries
        cursor = response.get('next_cursor')
        if not cursor: return entries
        # Callers begin with a simple URL; retain its original filters each page.
        path = path.split('&cursor=')[0] + '&' + urlencode({'cursor': cursor})


def poll():
    plan = read(ROOT / 'plan.json')
    state = read(ROOT / 'state.json') if (ROOT / 'state.json').exists() else {'versions': {p: [] for p in OWNERS}, 'episodes': {}, 'rounds': {}}
    now = datetime.now(timezone.utc)
    with client() as c:
        owned = champions(c)
        if len(owned) != 2 or {p['player']['id'] for p in owned} != OWNERS:
            raise ValueError('Expected exactly two owned league champions')
        for row in owned:
            player, version = row['player']['id'], row['policy_version']['id']
            if version not in state['versions'][player]: state['versions'][player].append(version)
        write(ROOT / 'champions-latest.json', owned)
        rounds = page_all(c, f'/v2/rounds?division_id={DIVISION}&limit=20', plan['started_at'])
        # One page may include older history; save only the bounded observation window.
        rounds = [r for r in rounds if r['created_at'] >= plan['started_at'] or
                  set((r.get('round_config') or {}).get('entrant_policy_version_ids', [])) &
                  {v for vs in state['versions'].values() for v in vs}]
        for round_ in rounds:
            rid = round_['id']
            previous = state['rounds'].get(rid)
            if previous and previous['status'] == 'completed': continue
            folder = ROOT / 'rounds' / rid; folder.mkdir(parents=True, exist_ok=True)
            write(folder / 'round.json', round_)
            episodes = page_all(c, f'/v2/rounds/{rid}/episodes?limit=1000')
            write(folder / 'episodes.json', episodes)
            for episode in episodes:
                if episode['id'] in state['episodes']: continue
                if episode['status'] != 'completed': continue
                rows = classify(episode, state['versions'])
                if not rows: continue
                for row in rows:
                    row.update(round=rid, round_number=round_['round_number'], observed_at=now.isoformat(),
                               game_version=episode['coworld_version'])
                state['episodes'][episode['id']] = rows
            state['rounds'][rid] = {'number': round_['round_number'], 'status': round_['status'],
                                    'episodes': len(episodes), 'created_at': round_['created_at']}
        leaderboard = get(c, f'/v2/divisions/{DIVISION}/leaderboard')
        write(ROOT / 'leaderboard-latest.json', leaderboard)
        state['positions'] = [r for r in leaderboard if r['player_id'] in OWNERS]
    rows = [r for rr in state['episodes'].values() for r in rr]
    threats = [r for r in rows if r['needs_replay_review']]
    state.update(last_checked_at=now.isoformat(), ends_at=plan['ends_at'],
                 episode_count=len(state['episodes']), team_outcome_count=len(rows),
                 outcomes={o: sum(r['outcome'] == o for r in rows) for o in ('win', 'loss', 'draw')},
                 threat_episode_count=len({r['episode'] for r in threats}))
    write(ROOT / 'state.json', state)
    write(ROOT / 'threats.json', {'updated_at': now.isoformat(), 'rows': threats})
    print({k: state[k] for k in ('last_checked_at', 'episode_count', 'outcomes', 'threat_episode_count')}, flush=True)
    return state


def main(hours=3, once=False):
    ROOT.mkdir(exist_ok=True)
    if not (ROOT / 'plan.json').exists():
        now = datetime.now(timezone.utc)
        write(ROOT / 'plan.json', {'started_at': now.isoformat(), 'ends_at': (now + timedelta(hours=hours)).isoformat(),
              'league': LEAGUE, 'division': DIVISION, 'poll_seconds': 60,
              'authorization': 'Monitor league rounds over the next few hours; if a threat appears, analyze episodes and run an autoresearch loop.',
              'watch_scope': 'Both owned champions from promotion onward; keep policy versions and game releases separate.',
              'research_trigger': 'Every actual defeat against an external opponent becomes a replay-review case; repeated defeats prioritize research. No claim that a single mixed-team loss proves an individual policy counter.'})
    deadline = datetime.fromisoformat(read(ROOT / 'plan.json')['ends_at'])
    while True:
        try:
            state = poll()
        except Exception as error:
            # Keep the watcher alive across transient service errors; retain the error.
            write(ROOT / 'latest-error.json', {'at': datetime.now(timezone.utc).isoformat(), 'type': type(error).__name__, 'message': str(error)})
            print(type(error).__name__, str(error), flush=True)
            if once: raise
        if once or datetime.now(timezone.utc) >= deadline: break
        time.sleep(min(60, max(0, (deadline - datetime.now(timezone.utc)).total_seconds())))
    if not once:
        write(ROOT / 'completed.json', {'completed_at': datetime.now(timezone.utc).isoformat(), 'state': str(ROOT / 'state.json')})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hours', type=float, default=3)
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args(); main(args.hours, args.once)
