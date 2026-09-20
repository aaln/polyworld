"""Plot decision ownership and evidence timing from a generated episode IR."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


def main(directory):
    doc = json.loads((directory / 'episode.ir.json').read_text())
    trace = Path(doc['provenance']['sources'][0]['path'])
    ticks, deadline, hp, tower_ticks, tower_counts = [], [], [], [], []
    for line in trace.open():
        row = json.loads(line)
        if row['type'] == 'decision':
            # NaNs break curves over ticks at which no policy observation exists.
            if ticks and row['tick'] / 1440 - ticks[-1] > 1.5 / 1440:
                ticks.append(float('nan')); deadline.append(float('nan'))
            ticks.append(row['tick'] / 1440)
            deadline.append(max(0, row['memory']['defUntil'] - row['tick']) / 24)
        elif row['type'] == 'ground_truth':
            tower_ticks.append(row['tick'] / 1440)
            hp.append(next(x['hp'] for x in row['structures'] if x['kind'] == 1 and x['team'] == 0))
            tower_counts.append(sum(x['kind'] == 4 and x['team'] == 0 and x['hp'] > 0 for x in row['structures']))
    colors = {'wave': '#367b59', 'rally': '#c78e29', 'attack': '#b9524b'}
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.spines.top': False,
                         'axes.spines.right': False})
    fig, axes = plt.subplots(3, 1, figsize=(12, 7.4), sharex=True,
                             gridspec_kw={'height_ratios': [0.9, 1.3, 1.5]})
    axes[0].set_facecolor('#eeeeee')
    for s in doc['decision_points']:
        mode = 'attack' if s['rule'] == 'R2' else 'rally' if s['defense_active'] else 'wave'
        axes[0].broken_barh([((s['start_tick']-1)/1440, (s['end_tick']-s['start_tick']+1)/1440)],
                            (0, 1), facecolors=colors[mode], edgecolors='white', linewidth=0.3)
    axes[0].set_yticks([])
    axes[0].set_ylim(0, 1)
    axes[0].set_title('Primary perspective: DeathKnight, slot 0 · 43 decision points', loc='left', pad=12)
    axes[0].legend(handles=[Patch(color=colors[k], label=t) for k, t in
                          [('wave','R4 opening wave route'), ('rally','R4 defense rally'), ('attack','R2 attack')]] +
                   [Patch(color='#eeeeee', label='No policy invocation (death)')],
                   loc='upper left', bbox_to_anchor=(0, -0.08), ncol=4, frameon=False, fontsize=9)
    axes[1].plot(ticks, deadline, color='#756044', linewidth=1)
    axes[1].set_ylabel('Defense time\nremaining (seconds)')
    axes[1].set_title('Reconstructed policy memory: deadline renews, with no release after first activation', loc='left')
    axes[1].set_ylim(-5, 320)
    axes[1].axvline(838/1440, linestyle=':', color='#555', linewidth=1)
    axes[1].annotate('dp02 · first defense', xy=(838/1440, 300), xytext=(1.3, 180),
                     arrowprops={'arrowstyle': '->', 'color':'#666'}, fontsize=9)
    axes[1].scatter([8150/1440], [300], s=24, color='#333', zorder=5)
    axes[1].annotate('dp18 · one enemy renews 300 s', xy=(8150/1440, 300), xytext=(4.25, 180),
                     arrowprops={'arrowstyle': '->', 'color':'#666'}, fontsize=9)
    axes[2].plot(tower_ticks, hp, color='#394f7e', linewidth=1.5, label='Red god HP')
    axes[2].set_ylabel('Red god HP')
    axes[2].set_ylim(-5, 420)
    right = axes[2].twinx()
    right.step(tower_ticks, tower_counts, where='post', color='#7c7570', linewidth=1, label='Red standing towers')
    right.set_ylabel('Red standing towers')
    right.set_ylim(-0.2, 11.5)
    right.spines['top'].set_visible(False)
    axes[2].set_title('Retrospective full-state assessment · temporal association, not causal attribution', loc='left')
    axes[2].legend(loc='lower left', frameon=False)
    right.legend(loc='upper right', frameon=False)
    for ax in axes:
        ax.set_xlim(0, doc['outcome']['ticks']/1440)
        ax.grid(axis='x', alpha=0.15)
    axes[2].set_xlabel('Game time (minutes, 24 ticks per second)')
    fig.suptitle('Episode 0806a449 · Red loss at 09:24.88', x=0.08, ha='left', fontsize=16, fontweight='bold')
    fig.text(0.08, 0.015, 'Output-equivalent reconstruction. No counterfactual rollouts or decision-quality verdicts.', fontsize=9, color='#555')
    fig.subplots_adjust(left=0.08, right=0.92, top=0.88, bottom=0.09, hspace=0.8)
    fig.savefig(directory/'decision-timeline.png', dpi=160)
    fig.savefig(directory/'decision-timeline.svg')
    plt.close(fig)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory', type=Path)
    main(p.parse_args().directory)
