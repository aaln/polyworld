"""Export model comparison and observed response windows from the archived evidence."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'docs/opponents/richard-alex-20260920'
OUT.mkdir(parents=True, exist_ok=True)


def read(path):
    return json.loads(path.read_text())


fig, axes = plt.subplots(1, 2, figsize=(13, 6.4), gridspec_kw={'width_ratios': [1, 1.5]})
fig.subplots_adjust(left=.09, right=.98, top=.82, bottom=.37, wspace=.36)
fig.suptitle('Opponent models and the missed defense window', x=.09, ha='left', fontsize=19)
fig.text(.09, .9, 'Exact Richard v135 and Alex gota-g002:v1 · current Aaron / Coach executable', fontsize=11, color='#525b65')

labels = ['Richard v135', 'Alex g002:v1']
slugs = ['richard-v135', 'alex-g002-v1']
for i, slug in enumerate(slugs):
    h = read(ROOT / 'docs/opponents' / slug / 'evidence.json')['heldout']
    for offset, key, color in [(-.18, 'population_accuracy', '#abb8c4'), (.18, 'accuracy', '#166f9b')]:
        value = 100 * h[key]
        axes[0].barh(i + offset, value, height=.3, color=color)
        axes[0].text(value + 1.3, i + offset, f'{value:.1f}%', va='center', fontsize=10)
axes[0].set(yticks=range(2), yticklabels=labels, xlim=(0, 95), xlabel='Correct held-out motif predictions (%)')
axes[0].invert_yaxis()
axes[0].set_title('Predictive evidence', loc='left', fontsize=13, pad=15)
axes[0].legend(handles=[Line2D([0], [0], color='#abb8c4', lw=8, label='Field baseline'),
                        Line2D([0], [0], color='#166f9b', lw=8, label='Opponent IR')],
               loc='upper left', bbox_to_anchor=(0, -.23), frameon=False, fontsize=10)

cases = [('alex-g002-v1', 'red', 'Alex / our red'),
         ('alex-g002-v1', 'blue', 'Alex / our blue'),
         ('richard-v135', 'blue', 'Richard / our blue')]
for i, (slug, color, label) in enumerate(cases):
    folder = ROOT / 'docs/opponents' / slug
    case = next(c for c in read(folder / 'own-decision-analysis.json')['cases'] if c['own_color'] == color)
    macro = next(r for r in read(folder / 'macro-observations.json')['rows'] if r['episode'] == case['episode'])
    results = next(r for r in read(folder / 'runtime-checks.json')['target_outcomes'] if r['id'] == case['episode'])
    pair = macro['first_visible_pair_near_own_god']['24']['tick'] / 24
    damage = macro['first_observed_god_damage']['tick'] / 24
    end = results['ticks'] / 24
    axes[1].hlines(i, pair, end, color='#adb5bd', lw=3)
    axes[1].scatter([pair], [i], marker='o', color='#c88c19', s=65, zorder=3)
    axes[1].scatter([damage], [i], marker='|', color='#bd463c', s=180, zorder=4)
    axes[1].scatter([end], [i], marker='x', color='#20272d', s=55, zorder=4)
    axes[1].annotate(f'{pair:.1f}s', (pair, i), xytext=(0, -19), textcoords='offset points', ha='center', fontsize=9)
    axes[1].annotate(f'{end-damage:.2f}s from damage to defeat', (damage, i), xytext=(-2, 16),
                     textcoords='offset points', ha='right', fontsize=9, color='#91392f')
axes[1].set(yticks=range(3), yticklabels=[c[2] for c in cases], xlim=(55, 252), ylim=(2.6, -.65), xlabel='Episode time (seconds)')
axes[1].set_title('Representative games: respond before core damage', loc='left', fontsize=13, pad=15)
axes[1].legend(handles=[Line2D([0], [0], marker='o', color='#c88c19', linestyle='', label='Visible enemy pair within 24 tiles'),
                        Line2D([0], [0], marker='|', color='#bd463c', markersize=12, linestyle='', label='First observed god damage'),
                        Line2D([0], [0], marker='x', color='#20272d', linestyle='', label='Defeat')],
               loc='upper left', bbox_to_anchor=(0, -.23), frameon=False, fontsize=10)
for ax in axes:
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='x', alpha=.16)
    ax.set_axisbelow(True)
fig.text(.09, .045, '20 games per target; 16 training / 4 held out. Alex held-out streams all repeat training streams.\nTiming is descriptive discovery evidence, not a validated counterfactual. Motif prediction does not establish a winning policy.', fontsize=9, color='#525b65')
fig.savefig(OUT / 'comparison.png', dpi=170)
fig.savefig(OUT / 'comparison.pdf')
print(OUT / 'comparison.png')
