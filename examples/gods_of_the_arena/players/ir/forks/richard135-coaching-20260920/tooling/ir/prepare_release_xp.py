"""Freeze current incumbent versions; local selection must be complete first."""
from datetime import datetime, timezone
import shutil

from economy_feedback import record
from policy_ir import HERE, digest, read, write
from release_workspace import RUN, SOURCE, VERSION, verify


def prepare():
    verify()
    from release_feedback import local as feedback
    feedback()
    local = RUN / 'local'
    screen, frozen = read(local / 'screen-result.json'), read(local / 'plan.json')
    if screen['verified_games'] != 280:
        raise ValueError('Complete the local screen first')
    root = RUN / 'hosted-discovery'
    root.mkdir(exist_ok=True)
    if (root / 'plan.json').exists():
        return
    snapshot = RUN / 'live-before'
    league, game, champions = [read(snapshot / (n + '.json')) for n in ['league', 'coworld', 'champions']]
    board = read(next(snapshot.glob('leaderboard-*')))
    own = {'ply_594ec24d-d7f3-4370-a000-468354ec41c9', 'ply_630a768f-d623-44b2-80fa-36968d6fa75a'}
    by_player = {r['player']['id']: r for r in champions if r['is_champion'] and r['status'] == 'competing' and r['substatus'] == 'active'}
    opponents = []
    for row in board:
        player = row['player_id']
        if player in own or player not in by_player:
            continue
        pv = by_player[player]['policy_version']
        opponents.append({'id': pv['id'], 'label': pv['label'], 'player_id': player, 'rank': row['rank']})
        if len(opponents) == 9:
            break
    cfg = next(v['game_config'] for v in game['manifest']['variants'] if v['id'] == 'competition')
    cfg = {k:v for k,v in cfg.items() if k not in {'seed', 'players', 'tokens'}}
    plan = {'created_at': datetime.now(timezone.utc).isoformat(), 'game_version': VERSION,
            'game_source': game['manifest']['game']['runnable']['source_url'],
            'target': {'coworld_id': league['game']['coworld_id'], 'variant_id': 'competition'},
            'config': cfg, 'opponents': opponents, 'episodes_per_arm': 100,
            'controls': {'v2': '6d0ff780-652f-47a8-82b3-336cb7a10a56', 'cadence': 'c5711f9d-6248-4843-ae39-bc13a4911b79'},
            'local_plan_sha256': digest((local / 'plan.json').read_bytes()),
            'confirmation_rule': frozen['rule'], 'previous_outcomes_excluded': True}
    write(root / 'plan.json', plan)
    for name, version in plan['controls'].items():
        folder = root / name
        folder.mkdir()
        arm = {k:plan[k] for k in ['game_version', 'game_source', 'target', 'config', 'opponents']}
        arm.update(policy_version=version, run_id='release-20260916-' + name + '-' + digest(plan)[:10],
                   notes='100episode latest-release fixed-incumbent baseline: both deployed policies, rotated seats, independent request-derived seeds. Full clean-source replay audits; no old-release pooling.')
        write(folder / 'plan.json', arm)
        shutil.copy2(RUN / 'build/audit-hosted', folder / 'audit')
    print('Prepared controls and selected candidates:', screen['selected'])


if __name__ == '__main__':
    prepare()
