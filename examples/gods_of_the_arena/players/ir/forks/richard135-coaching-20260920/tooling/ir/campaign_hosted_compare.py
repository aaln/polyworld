"""Independent-cohort hosted comparison for a frozen local campaign qualifier.

Input layout: DIRECTORY/{control,candidate}/{plan.json,collection.json,audit,artifacts/}.
Every artifact is rechecked before computing the predeclared 100-per-arm verdict.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from math import comb
from pathlib import Path

from hosted_wave_audit import verify
from policy_ir import digest, read, write


def fisher_greater(candidate_wins, candidate_n, control_wins, control_n):
    wins = candidate_wins + control_wins
    total = candidate_n + control_n
    return sum(comb(wins, x) * comb(total - wins, candidate_n - x)
               for x in range(candidate_wins, min(candidate_n, wins) + 1)
               if 0 <= candidate_n - x <= total - wins) / comb(total, candidate_n)


def verify_rotated_roster(actual, expected, subject):
    """A fixed roster must preserve teammate/opponent placement, not just membership."""
    if (len(actual) != 10 or len(expected) != 10 or Counter(actual) != Counter(expected) or
            actual.count(subject) != 1 or expected.count(subject) != 1):
        raise ValueError('Frozen roster membership changed')
    shift = (actual.index(subject) - expected.index(subject)) % 10
    rotated = expected[-shift:] + expected[:-shift] if shift else expected
    if actual != rotated:
        raise ValueError('Opponent order changed within a rotated subject seat')


def cohort(directory, workers):
    plan = read(directory / 'plan.json')
    body = read(directory / 'batch/request.json')
    collection = read(directory / 'collection.json')
    count = body['num_episodes']
    if count != 100 or collection['episodes'] != count or collection['request_count'] != 1:
        raise ValueError('This verdict requires one complete 100-episode request per arm')
    folders = sorted(p.parent for p in (directory / 'artifacts').glob('*/.done'))
    if len(folders) != count:
        raise ValueError('Incomplete artifact collection')
    binary = directory / 'audit'
    binary_hash = digest(binary.read_bytes())
    with ThreadPoolExecutor(workers) as pool:
        list(pool.map(lambda folder: verify(folder, binary, binary_hash), folders))
    expected_roster = Counter(row['player']['policy_ref'] for row in body['roster'])
    rows = []
    for folder in folders:
        ep, result, audit = [read(folder / n) for n in ['episode.json', 'results.json', 'audit.json']]
        if (Counter(ep['policy_version_ids']) != expected_roster or
                ep['coworld_id'] != plan['target']['coworld_id'] or ep['coworld_version'] != plan['game_version']):
            raise ValueError('Frozen roster or game release changed')
        config = {k: v for k, v in ep['game_config'].items() if k not in {'seed', 'tokens', 'players'}}
        if config != plan['config']:
            raise ValueError('Frozen configuration changed')
        slot = ep['policy_version_ids'].index(plan['policy_version'])
        verify_rotated_roster(ep['policy_version_ids'],
                              [r['player']['policy_ref'] for r in body['roster']], plan['policy_version'])
        hero = audit['heroes'][slot]
        if [h['total_xp'] for h in audit['heroes']] != result['total_xp']:
            raise ValueError('Lifetime XP disagrees with hosted output')
        rows.append({'episode': ep['id'], 'seed': result['seed'], 'slot': slot, 'class': hero['class'],
                     'win': hero['score'], 'deaths': hero['deaths'], 'alive_ticks': hero['alive_ticks'],
                     'ticks': result['ticks'], 'xp': hero['total_xp'], 'first_gear_tick': hero['first_gear_tick'],
                     'glory': hero['score'] * (hero['total_xp'] - 100 * result['ticks'] / 1440),
                     'timeout': result['outcome'] == 'time_limit',
                     'replay_sha256': audit['replay_sha256']})
    if len({r['seed'] for r in rows}) != count or Counter(r['slot'] for r in rows) != Counter({s: 10 for s in range(10)}):
        raise ValueError('Repeated seeds or wrong seat coverage')
    return {'games': count, 'wins': sum(r['win'] for r in rows),
            'death_rate': sum(r['deaths'] for r in rows) * 1440 / sum(r['alive_ticks'] for r in rows),
            'deaths': sum(r['deaths'] for r in rows), 'xp': sum(r['xp'] for r in rows),
            'mean_glory': sum(r['glory'] for r in rows) / count,
            'timeouts': sum(r['timeout'] for r in rows),
            'bought_equipment': sum(r['first_gear_tick'] >= 0 for r in rows),
            'policy_version': plan['policy_version'], 'rows': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    directory = args.directory.resolve()
    plans = {arm: read(directory / arm / 'plan.json') for arm in ['control', 'candidate']}
    for key in ['target', 'game_version', 'config', 'opponents']:
        if plans['control'][key] != plans['candidate'][key]:
            raise ValueError('The two arms do not share a frozen ' + key)
    arms = {arm: cohort(directory / arm, args.workers) for arm in plans}
    control, candidate = arms['control'], arms['candidate']
    p = fisher_greater(candidate['wins'], 100, control['wins'], 100)
    gain = (candidate['wins'] - control['wins']) / 100
    # Survival/XP thresholds are frozen in the hosted plan before launching either arm.
    preregistered = read(directory / 'plan.json')
    gates = preregistered['gates']
    checks = {'win_gain': gain >= gates['minimum_win_gain'], 'win_p': p < gates['maximum_win_p'],
              'survival': candidate['death_rate'] <= gates['maximum_death_rate_ratio'] * control['death_rate'],
              'xp': candidate['xp'] >= gates['minimum_xp_ratio'] * control['xp'],
              'equipment': candidate['bought_equipment'] == 100}
    report = {'design': 'Independent seed cohorts, identical pinned roster and balanced seats',
              'arms': arms, 'win_gain': gain, 'one_sided_fisher_p': p, 'checks': checks,
              'passed': all(checks.values()), 'field_guardrail': 'pending; no league promotion yet'}
    write(directory / 'comparison.json', report)
    print({k: v for k, v in report.items() if k != 'arms'})


if __name__ == '__main__':
    main()
