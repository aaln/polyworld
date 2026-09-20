"""Reconcile accepted spending and kill income at fixed early horizons."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import gzip
import json
import subprocess
from study import ROOT, STUDY, read, write, digest

BINARY = ROOT / 'tmp/gota-ir/richard-v135-source-audit-20260920/economy/economy-probe'
EXPECTED = 'cc15542cbff1a62b70ac367c9a20d2856f45e2076e97e78a8eb5f99255663e9d'


def one(path):
    result = read(path / 'result.json')
    assert result['valid']
    output = path / 'economy.json.gz'
    if output.exists():
        with gzip.open(output, 'rt') as f: record = json.load(f)
    else:
        p = subprocess.run([str(BINARY), str(path / 'replay.bin')], capture_output=True, text=True, check=True, timeout=600)
        record = json.loads(p.stdout.splitlines()[-1])
        with gzip.open(output, 'wt') as f: json.dump(record, f)
    assert record['all_state_hashes_equal'] and record['all_actions_consumed']
    assert record['ticks'] == result['ticks']
    initial = {x['hero']['id']: x['hero'] for x in record['samples'] if x['tick'] == 0}
    for hid, start in initial.items():
        end = [x['hero'] for x in record['samples'] if x['tick'] == result['ticks'] and x['hero']['id'] == hid][0]
        rewards = [x for x in record['rewards'] if x['hero'] == hid]
        purchases = [x for x in record['purchases'] if x['hero'] == hid]
        assert sum(x['xp'] for x in rewards) == end['total_xp'] - start['total_xp']
        assert start['gold'] + sum(x['gold'] for x in rewards) - sum(x['cost'] for x in purchases) == end['gold']
        level, xp = 1, end['total_xp']
        while level < 20 and xp >= 100 + (level-1)*75:
            xp -= 100 + (level-1)*75; level += 1
        assert (level, xp) == (end['level'], end['xp'])
    horizons = []
    for requested in (2000, 4000, result['ticks']):
        at = min(requested, result['ticks'])
        actors = []
        for hid, start in initial.items():
            sample = next(x['hero'] for x in record['samples'] if x['tick'] == at and x['hero']['id'] == hid)
            rewards = [x for x in record['rewards'] if x['hero'] == hid and x['tick'] <= at]
            buys = [x for x in record['purchases'] if x['hero'] == hid and x['tick'] <= at]
            hits = [x for x in record['basic_hits'] if x['hero'] == hid and x['tick'] <= at]
            actors.append({'id': hid, 'class': start['class'], 'team': start['team'],
                'level': sample['level'], 'xp': sample['total_xp'], 'gold': sample['gold'],
                'damage': sample['damage'], 'max_hp': sample['max_hp'],
                'deaths': sum(x['alive_changed'] and x['hero']['hp'] <= 0 for x in record['transitions'] if x['hero']['id'] == hid and x['tick'] <= at),
                'hits': len(hits), 'hit_targets': dict(Counter(x['kind'] for x in hits)),
                'reward_kinds': dict(Counter(x['kind'] for x in rewards)),
                'purchases': buys, 'healing_spend': sum(x['cost'] for x in buys if x['item_id'] in (1, 2)),
                'equipment_spend': sum(x['cost'] for x in buys if x['item_id'] > 4)})
        teams = []
        for side in (0, 1):
            ours = [x for x in actors if x['team'] == side]
            teams.append({'side': side, **{k: sum(x[k] for x in ours) for k in ('xp', 'deaths', 'hits', 'healing_spend', 'equipment_spend')},
                'mean_level': sum(x['level'] for x in ours)/5})
        horizons.append({'requested_tick': requested, 'observed_tick': at, 'already_terminated': at < requested,
                         'actors': actors, 'teams': teams})
    receipt = {'name': result['name'], 'seed': result['seed'], 'side': result['side'],
        'win': result['win'], 'ticks': result['ticks'], 'all_ten_accounts_reconcile': True,
        'all_replay_states_equal': True, 'binary_sha256': digest(BINARY.read_bytes()),
        'replay_sha256': result['replay_sha256'], 'raw_sha256': digest(output.read_bytes()), 'horizons': horizons}
    write(path / 'economy-summary.json', receipt)
    return receipt


def main():
    assert digest(BINARY.read_bytes()) == EXPECTED
    matches = sorted((STUDY / 'local').glob('*/*/result.json'))
    with ThreadPoolExecutor(2) as pool: rows = list(pool.map(lambda p: one(p.parent), matches))
    write(STUDY / 'economy-results.json', {'matches': len(rows), 'rows': rows,
        'scope': 'Fixed early horizons and terminal truth. Accepted purchases, kill rewards and all ten accounts reconcile; samples are not public policy inputs.'})
    for row in rows:
        print(json.dumps({'name': row['name'], 'side': row['side'], 'win': row['win'],
            'horizons': [{'tick': h['observed_tick'], **h['teams'][row['side']]} for h in row['horizons']]}), flush=True)


if __name__ == '__main__': main()
