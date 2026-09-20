"""Account for accepted purchases, XP and Ranger cadence on the frozen corpus."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import json
import subprocess

from source_audit import OUT, RUN, STUDY, VERSION, read, sha, write


def one(row):
    folder = STUDY / 'artifacts' / row['id']
    episode = read(folder / 'episode.json')
    slots = [p['position'] for p in episode['participants'] if p['policy_version_id'] == VERSION]
    binary = RUN / 'economy/economy-probe'
    tape = folder / 'replay.bin'
    raw = RUN / 'economy/episodes' / (row['id'] + '.json.gz')
    identity = {'binary_sha256': sha(binary), 'replay_sha256': sha(tape)}
    if raw.exists():
        with gzip.open(raw, 'rt') as f:
            record = json.load(f)
        assert record['identity'] == identity
    else:
        p = subprocess.run([str(binary), str(tape)], text=True, capture_output=True, check=True, timeout=600)
        record = json.loads(p.stdout.splitlines()[-1])
        record['identity'] = identity
        raw.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(raw, 'wt') as f:
            json.dump(record, f)
    assert record['all_state_hashes_equal'] and record['all_actions_consumed']
    assert record['ticks'] == read(folder / 'results.json')['ticks']
    heroes = []
    for slot in range(10):
        # Initial snapshot retains the engine's actor ordering; no inferred role IDs.
        initial = record['samples'][slot]['hero']
        hid = initial['id']
        samples = [s for s in record['samples'] if s['hero']['id'] == hid]
        final = samples[-1]['hero']
        rewards = [r for r in record['rewards'] if r['hero'] == hid]
        purchases = [r for r in record['purchases'] if r['hero'] == hid]
        hits = [r for r in record['basic_hits'] if r['hero'] == hid]
        assert sum(r['xp'] for r in rewards) == final['total_xp'] - initial['total_xp']
        assert initial['gold'] + sum(r['gold'] for r in rewards) - sum(p['cost'] for p in purchases) == final['gold']
        level = 1
        xp = final['total_xp']
        while level < 20 and xp >= 100 + (level - 1) * 75:
            xp -= 100 + (level - 1) * 75
            level += 1
        assert (level, xp) == (final['level'], final['xp'])
        hero_hits = [r for r in hits if r['kind'] == 'hero']
        intervals = Counter(b['tick'] - a['tick'] for a, b in zip(hero_hits, hero_hits[1:])
                            if a['target'] == b['target'])
        item_first = {}
        for p in purchases:
            item_first.setdefault(p['item'], p['tick'])
        h = {'slot': slot, 'id': hid, 'class': initial['class'], 'team': initial['team'],
             'policy': 'richard_v135' if slot in slots else 'our_archived_control',
             'initial': initial, 'final': final, 'samples': samples,
             'reward_counts': dict(Counter(r['kind'] for r in rewards)),
             'first_reward_tick': rewards[0]['tick'] if rewards else None,
             'accepted_purchases': purchases, 'first_item_ticks': item_first,
             'level_changes': [t for t in record['transitions'] if t['hero']['id'] == hid and t['level_changed']],
             'deaths': sum(t['hero']['hp'] <= 0 for t in record['transitions'] if t['hero']['id'] == hid and t['alive_changed']),
             'basic_hit_counts': dict(Counter(r['kind'] for r in hits)),
             'same_target_hero_hit_interval_counts': dict(sorted(intervals.items())),
             'xp_gold_and_level_accounting_equal': True}
        if initial['class'] == 'Ranger':
            h['reward_ledger'] = rewards
            h['hero_basic_hit_ledger'] = hero_hits
        heroes.append(h)
    print(row['id'], 'economy audit complete', flush=True)
    return {'episode': row['id'], 'split': row['split'], 'ticks': record['ticks'],
        'raw_receipt': str(raw.relative_to(STUDY.parents[2])), 'raw_sha256': sha(raw),
        'replay_sha256': identity['replay_sha256'],
        'all_state_hashes_equal': True, 'all_actions_consumed': True,
        'trajectory_signature': hashlib.sha256(json.dumps({k: record[k] for k in ['samples', 'rewards', 'purchases', 'basic_hits']}, sort_keys=True).encode()).hexdigest(),
        'heroes': heroes}


def main():
    rows = [r for r in read(STUDY / 'study-plan.json')['episodes'] if r['split'] != 'population']
    with ThreadPoolExecutor(max_workers=3) as pool:
        receipts = list(pool.map(one, rows))
    write(OUT / 'economy-audit.ir.json', {'schema': 'gota-source-reveal-economy-audit/1',
        'game_commit': 'f2ab9598d8f8001b6beae3e66404e341770c803f', 'episodes': len(receipts),
        'all_state_hashes_equal': True, 'all_200_hero_xp_gold_level_accounts_equal': True,
        'binary_sha256': sha(RUN / 'economy/economy-probe'),
        'overlay': read(RUN / 'economy/overlay-manifest.json'),
        'scope': 'Retrospective source-reveal truth. Purchases are accepted calls; rewards belong to the killing hero. Cadence counts condition on consecutive hero-target basics with the same target, not continuous-range eligibility.',
        'rows': receipts})
    rangers = [h for r in receipts for h in r['heroes'] if h['class'] == 'Ranger' and h['policy'] == 'richard_v135']
    print(json.dumps({'richard_ranger_games': len(rangers), 'rangers': [
        {k: h[k] for k in ['first_reward_tick', 'first_item_ticks', 'reward_counts', 'final', 'same_target_hero_hit_interval_counts']}
        for h in rangers]}, indent=2))


if __name__ == '__main__':
    main()
