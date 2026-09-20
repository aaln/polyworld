"""Measure repeated rally orders near stationary heroes in verified replay JSONL.

Uses actual commands plus post-tick position samples. It cannot identify VM
memory or prove physical collision. Twenty-second windows require >=75% of
ticks ordering the same walk destination, sampled displacement <=2 tiles,
and a living hero with no new basic hits. Run on losses AND wins.
"""
import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path

from policy_ir import digest, write


def inspect(path, team=0):
    windows = defaultdict(lambda: defaultdict(Counter))
    frames = defaultdict(list)
    header = summary = None
    for line in path.open():
        row = json.loads(line)
        if row['type'] == 'header': header = row
        elif row['type'] == 'summary': summary = row
        elif row['type'] == 'frame': frames[row['tick']//480].append(row)
        elif row['type'] == 'action' and row['kind'] == 1 and row['slot']//5 == team:
            windows[row['tick']//480][row['slot']][(row['first'],row['second'])] += 1
    if not summary or summary['hash_mismatches']:
        raise ValueError('A complete source-matched replay is required')
    stalls = []
    for window, slots in windows.items():
        sample = frames.get(window, [])
        if len(sample) < 3: continue
        for slot, counts in slots.items():
            destination, count = counts.most_common(1)[0]
            if count < 360: continue
            heroes = [next(h for h in f['heroes'] if h['slot'] == slot) for f in sample]
            if any(h['hp'] <= 0 for h in heroes): continue
            spread = max(math.dist(a['position'],b['position']) for a in heroes for b in heroes)
            if spread > 2 or heroes[-1]['hits'] != heroes[0]['hits']: continue
            stalls.append({'start_seconds':window*20,'end_seconds':(window+1)*20,
                           'slot':slot,'walk_destination':list(destination),'repeat_orders':count,
                           'sampled_position_diameter_tiles':spread,
                           'visible_enemy_heroes_at_first_sample':sum(o['kind']==2 and o['team']!=team and o['hp']>0
                                                                    for o in heroes[0]['visible_post_tick'])})
    shared = []
    for window in sorted({r['start_seconds'] for r in stalls}):
        points = defaultdict(list)
        for row in stalls:
            if row['start_seconds']==window: points[tuple(row['walk_destination'])].append(row['slot'])
        for point, slots in points.items():
            if len(slots) >= 2:
                shared.append({'start_seconds':window,'destination':list(point),'slots':slots})
    return {'source':header['source'],'version':header['version'],
            'input_sha256':digest(path.read_bytes()),'ticks':summary['ticks'],'winner':summary['winner'],
            'own_team':team,'stationary_repeated_order_windows':stalls,'shared_destination_windows':shared,
            'interpretation':__doc__}


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('replay',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--team',type=int,choices=[0,1],default=0)
    a=p.parse_args();r=inspect(a.replay,a.team);write(a.output,r)
    print(len(r['stationary_repeated_order_windows']),'stationary hero windows;',
          len(r['shared_destination_windows']),'shared-destination windows')
