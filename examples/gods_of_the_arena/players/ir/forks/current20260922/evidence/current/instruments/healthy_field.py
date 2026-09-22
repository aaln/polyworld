"""Current-score mixed-team comparison after read-only roster VM preflight."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import time
import panel
import current_score

h = panel.h
OUT = h.STUDY / 'healthy-field'
CANDIDATE = 'f3f8baab-d02a-4f7f-8fc9-e1f050f967a7'
NAMES = ['Andre von Auto', 'Games Bond', 'Andre von Houck', 'docxology',
         'relh', 'Jordan', 'richard', 'NanosaurusX', "Aaron's Co-play Coach"]


def preflight(c):
    path = OUT / 'preflight-result.json'
    if path.exists():
        assert h.read(path)['passed']
        return h.read(OUT / 'memberships.json')
    members_path = OUT / 'memberships.json'
    if not members_path.exists():
        members = h.get(c, '/v2/league-policy-memberships?league_id=league_3c60897b-25cf-4b37-9d1a-8554c1198f28&champions_only=true&limit=100')
        by_name = {m['player']['name']: m for m in members}
        h.freeze(members_path, [by_name[n] for n in NAMES])
    members = h.read(members_path)
    assert len({m['player']['id'] for m in members}) == 9
    assert h.PLAYER not in {m['player']['id'] for m in members}
    versions = [(m['player']['name'], m['policy_version']['id']) for m in members]
    versions += [('Aaron control', h.INCUMBENT), ('Aaron candidate', CANDIDATE)]
    def check(item):
        name, version = item
        with h.client() as cc:
            listing_path = OUT / 'preflight' / version / 'episodes.json'
            if listing_path.exists():
                listings = h.read(listing_path)
            else:
                listings = h.get(cc, f'/v2/policy-versions/{version}/episode-requests?limit=20')
                h.write(listing_path, listings)
            counts, failures, selected = [0, 0], [], []
            for ep in listings['entries']:
                if ep['status'] != 'completed' or ep['coworld_id'] != h.GAME:
                    continue
                slots = [i for i, v in enumerate(ep['policy_version_ids']) if v == version]
                if not any(counts[i // 5] < 3 for i in slots):
                    continue
                status_path = OUT / 'preflight' / version / ep['id'] / 'status.json'
                if status_path.exists():
                    status = h.read(status_path)
                else:
                    full = h.get(cc, '/v2/episode-requests/' + ep['id'])
                    assert full['coworld_version'] == h.VERSION
                    status = h.get(cc, '/v2/episode-requests/' + ep['id'] + '/artifacts/player-status')
                    h.write(status_path, status)
                selected.append(ep['id'])
                for side in (0, 1):
                    if any(i // 5 == side for i in slots):
                        counts[side] += 1
                for s in status['players']:
                    if s['slot'] in slots and s.get('exit_code') != 0:
                        failures.append({'episode': ep['id'], **s})
                if min(counts) >= 3:
                    break
            return {'name': name, 'version': version, 'games_by_color': counts,
                    'failures': failures, 'episodes': selected,
                    'passed': min(counts) >= 3 and not failures}
    with ThreadPoolExecutor(4) as pool:
        rows = list(pool.map(check, versions))
    result = {'passed': all(r['passed'] for r in rows), 'rows': rows,
              'scope': 'Recent existing games: roster VM health only, no strength selection.'}
    h.write(path, result)
    print(json.dumps(result), flush=True)
    assert result['passed'], 'Do not spend on a known unhealthy roster'
    return members


def prepare(c):
    h.CYCLE = 'interactive-current-draft-field-20260922'
    path = OUT / 'plan.json'
    if path.exists():
        return h.read(path)
    h.live(c)
    assert h.read(h.STUDY / 'draft-practice.json')['passed']
    pair = h.ROOT / current_score.CONTRACT['reference_pair']
    policy = h.read(pair / 'policy.ir.json')
    current_score.require_current(policy)
    assert h.sha((pair / 'policy.bas').read_bytes()) == current_score.CONTRACT['reference_source_sha256']
    members = preflight(c)
    cfg = {k: v for k, v in h.read(h.STUDY / 'canonical-game.json')['manifest']['variants'][0]['game_config'].items() if k not in ('seed', 'players', 'tokens')}
    arms = []
    for label, version in [('candidate', CANDIDATE), ('control', h.INCUMBENT)]:
        for side in (0, 1):
            subject = side * 5
            pool = iter(m['policy_version']['id'] for m in members)
            roster = [version if i == subject else next(pool) for i in range(10)]
            background = h.sha(json.dumps([None if i == subject else v for i, v in enumerate(roster)]).encode())
            arm = {'name': label, 'target': 'mixed-first-pick', 'opponent': background,
                   'side': side, 'version': version, 'own_slots': [subject],
                   'roster': roster, 'games': 40}
            body = {'idempotency_key': 'gota-current-draft-field0922-' + label + '-' + str(side) + '-' + background[:8],
                    'target': {'coworld_id': h.GAME, 'variant_id': 'competition'},
                    'game_config_overrides': cfg, 'num_episodes': 40,
                    'roster': [{'slot': i, 'player': {'policy_ref': v}} for i, v in enumerate(roster)],
                    'notes': 'Current-release XP-score A/B: practiced policy versus live compat, one first-pick seat, nine distinct frozen healthy-preflight players. Both colors; all VMs, full replay and official scores audited. Fort outcomes diagnostic only. No league selection.'}
            folder = OUT / label / str(side)
            h.freeze(folder / 'arm.json', arm)
            h.freeze(folder / 'request.json', body)
            arms.append(arm)
    plan = {'game_version': h.VERSION, 'engine_commit': h.COMMIT, 'cycle': h.CYCLE,
            'games': 160, 'arms': arms, 'candidate_source_sha256': current_score.CONTRACT['reference_source_sha256'],
            'evaluator_sha256': h.sha((panel.HERE / 'current_score.py').read_bytes()),
            'rule': 'All 40 games/cell clean and hash/score audited. Candidate own XP score >=0.95 control each color, strict aggregate gain >=10%. Fort outcomes not a gate. Rival score superiority reported separately. Two fixed first-pick rosters only; not universal field strength.',
            'reason': 'User episode exposes old compat Vanguard choice and three failed teammates. Strong practiced version retained after further native refinements failed matched score gates. New mixed-roster question; not continuation of the finished target panel.'}
    h.freeze(path, plan)
    return plan


def collect(c, arm, folder, ep):
    row = h.collect(c, arm, folder, ep)
    if 'score' not in row:
        return row
    out = folder / 'artifacts' / ep['id']
    result, audit = h.read(out / 'results.json'), h.read(out / 'audit.json')
    hero = audit['heroes'][arm['own_slots'][0]]
    rival_slots = range((1 - arm['side']) * 5, (1 - arm['side']) * 5 + 5)
    row.update({'opponent_score': sum(result['scores'][s] for s in rival_slots) / 5,
                'class': hero['class'], 'xp': hero['xp'], 'deaths': hero['deaths'],
                'level': hero['level'], 'hits': hero['hits']})
    h.write(out / 'matched-result.json', row)
    return row


def run(plan, initial_queue=3):
    with h.research.lock(h.STUDY / 'hosted.lock', blocking=False), h.client() as c:
        # Three queued requests maximum, shared reservation rechecks the whole journal.
        for arm in plan['arms'][:initial_queue]:
            folder = OUT / arm['name'] / str(arm['side'])
            if not (folder / 'batch/created.json').exists():
                ident = panel.reserve(c, h.read(folder / 'request.json'), folder / 'batch')
                print(json.dumps({'queued': arm['name'], 'side': arm['side'], 'request': ident}), flush=True)
        for arm in plan['arms']:
            folder = OUT / arm['name'] / str(arm['side'])
            if (folder / 'result.json').exists():
                continue
            receipt = folder / 'batch/created.json'
            ident = h.read(receipt)['id'] if receipt.exists() else panel.reserve(c, h.read(folder / 'request.json'), folder / 'batch')
            while True:
                eps = h.episodes(c, ident)
                h.write(folder / 'episodes.json', eps)
                done = [e for e in eps if e['status'] in ('completed', 'failed', 'cancelled', 'error')]
                with ThreadPoolExecutor(4) as pool:
                    rows = list(pool.map(lambda e: collect(c, arm, folder, e), done))
                h.write(folder / 'progress.json', {'audited': len(rows), 'total': len(eps), 'rows': rows})
                if len(rows) == arm['games']:
                    break
                print(json.dumps({'arm': arm['name'], 'side': arm['side'], 'audited': len(rows)}), flush=True)
                time.sleep(10)
            cell = {k: arm[k] for k in ('target', 'opponent', 'side')}
            cell.update({'game_version': h.VERSION, 'engine_commit': h.COMMIT,
                         'games': len(rows), 'invalid': sum(not r['valid'] for r in rows),
                         'all_hashes_equal': all(r.get('all_hashes_equal', False) for r in rows),
                         'own_score': sum(r.get('score', 0) for r in rows) / len(rows),
                         'opponent_score': sum(r.get('opponent_score', 0) for r in rows) / len(rows),
                         'wins': sum(r.get('win', 0) for r in rows),
                         'losses': sum(r.get('loss', 0) for r in rows),
                         'draws': sum(r.get('draw', 0) for r in rows), 'rows': rows})
            h.write(folder / 'result.json', cell)
            print(json.dumps({k: v for k, v in cell.items() if k != 'rows'}), flush=True)
        cells = [h.read(OUT / a['name'] / str(a['side']) / 'result.json') for a in plan['arms']]
        verdict = current_score.compare(cells[:2], cells[2:])
        h.write(OUT / 'result.json', {'complete': True, **verdict, 'cells': cells})
        print(json.dumps(verdict), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    with h.client() as c:
        h.live(c)
        if args.preflight_only:
            preflight(c)
        else:
            plan = prepare(c)
    if not args.preflight_only:
        run(plan)
