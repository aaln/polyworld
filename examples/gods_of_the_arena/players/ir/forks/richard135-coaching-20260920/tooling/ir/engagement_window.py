"""Measure per-hero attack ordering in a selected decoded replay window.

Usage: python engagement_window.py decoded.jsonl output-prefix --start 5520 --end 5760
Actions are exact recorded orders, not hits. HP is the first available world
snapshot in the window; snapshot cadence may be coarser than the action clock.
"""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main(path, output, start, end, team):
    slots = range(team*5, team*5+5)
    attacks = {s: [] for s in slots}
    snapshot = None
    for line in path.open():
        r = json.loads(line)
        if not start <= r.get('tick', -1) <= end: continue
        if r.get('type') == 'frame' and snapshot is None: snapshot = r
        if r.get('type') == 'action' and r.get('kind') == 2 and r.get('slot') in slots:
            attacks[r['slot']].append({'tick': r['tick'], 'target': r['first']})
    if snapshot is None: raise ValueError('No world snapshot in this window')
    heroes = {r['slot']: r for r in snapshot['heroes']}
    result = {'source': str(path), 'start': start, 'end': end,
              'hp_snapshot_tick': snapshot['tick'], 'heroes': {s: {
                  'class': heroes[s]['class'], 'hp': heroes[s]['hp'], 'max_hp': heroes[s]['max_hp'],
                  'position': heroes[s]['position'], 'attack_orders': attacks[s]} for s in slots}}
    output.with_suffix('.json').write_text(json.dumps(result, indent=2)+'\n')
    fig, ax = plt.subplots(figsize=(11, 3.8))
    for y, slot in enumerate(slots):
        a = attacks[slot]
        if a:
            ax.scatter([v['tick'] for v in a], [y]*len(a), marker='|', s=90, color='#377d86')
            ax.annotate(str(a[0]['tick']), (a[0]['tick'], y), xytext=(0, 10),
                        textcoords='offset points', fontsize=9)
    ax.set_yticks(range(5), [f"{heroes[s]['class']}  ({heroes[s]['hp']}/{heroes[s]['max_hp']} HP)" for s in slots])
    ax.set_ylim(4.6, -.8); ax.set_xlim(start, end)
    ax.set_title('Defenders start attacking at different times', loc='left')
    ax.set_xlabel('Replay tick (24 ticks per second)')
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='x', alpha=.2)
    fig.text(.01, .01, f'Each mark is an attack-target order, not a landed hit. HP shown at tick {snapshot["tick"]}.', fontsize=9)
    fig.tight_layout(rect=[0, .05, 1, 1])
    fig.savefig(output.with_suffix('.png'), dpi=160)
    plt.close(fig)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('decoded', type=Path); p.add_argument('output', type=Path)
    p.add_argument('--start', type=int, required=True); p.add_argument('--end', type=int, required=True)
    p.add_argument('--team', type=int, default=0, choices=(0, 1))
    a = p.parse_args(); main(a.decoded, a.output, a.start, a.end, a.team)
