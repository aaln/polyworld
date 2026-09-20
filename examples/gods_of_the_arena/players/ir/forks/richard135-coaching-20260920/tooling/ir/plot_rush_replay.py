"""Draw sampled replay positions without confusing shared vision with ground truth."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


def plot(path, output, own_team=0, title='Five-hero rush: positions from the verified replay',
         opponent='khors', sample_seconds=(40,80)):
    with path.open() as stream:
        header = json.loads(next(stream))
        frames = [r for line in stream if (r := json.loads(line))['type'] == 'frame']
    chosen = [min(frames, key=lambda r: abs(r['tick']-t)) for t in [*(24*s for s in sample_seconds), frames[-1]['tick']]]
    terrain = [[c == '.' for c in row] for row in header['terrain']]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.7), facecolor='#101821')
    colors = ['#ff7474', '#6bb9ff']
    for ax, frame in zip(axes, chosen):
        ax.imshow(terrain, cmap=ListedColormap(['#172029', '#33443b']), interpolation='nearest')
        for b in frame['buildings']:
            x, y = b['position']
            alive = b['hp'] > 0
            god = b['kind'] == 'Fort'
            ax.scatter(x, y, marker='*' if god else '^', s=180 if god else 32,
                       c=colors[b['team']] if alive else '#687078', alpha=1 if alive else .6,
                       edgecolors='#101821', linewidths=.5)
            if god:
                ax.text(x-4, y+7 if y < 58 else y-7, f'God {max(0,b["hp"])} HP',
                        ha='right' if x > 58 else 'left', color=colors[b['team']], fontsize=8)
        for h in frame['heroes']:
            team, slot = h['team'], h['slot']
            points = [next(x['position'] for x in prior['heroes'] if x['slot'] == slot)
                      for prior in frames if prior['tick'] <= frame['tick']]
            ax.plot([p[0] for p in points], [p[1] for p in points], c=colors[team], alpha=.4, lw=1)
            ax.scatter(*h['position'], marker='o' if team == own_team else 's', s=60,
                       c=colors[team], edgecolors='#101821', linewidths=.8)
        secs = frame['tick']/24
        ax.set_title(f'{int(secs)//60}:{secs%60:04.1f}', color='white', pad=10)
        ax.set(xlim=(-1, 117), ylim=(117, -1), xticks=[], yticks=[])
        for spine in ax.spines.values(): spine.set_visible(False)
    fig.suptitle(title, color='white', fontsize=16, y=.99)
    own_color,enemy_color = ('Red','Blue') if own_team == 0 else ('Blue','Red')
    fig.text(.5, .065, f'{own_color} circles: our heroes   •   {enemy_color} squares: {opponent} heroes   •   Triangles: structures   •   Stars: gods',
             ha='center', color='#e0e7ed', fontsize=10)
    fig.text(.5, .025, 'Verified full replay; positions sampled every 5 seconds plus the final tick. Paths include respawns. Enemy positions shown are ground truth.',
             ha='center', color='#b6c5cf', fontsize=9)
    fig.subplots_adjust(left=.025, right=.975, top=.89, bottom=.13, wspace=.06)
    fig.savefig(output, dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('replay', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    plot(args.replay, args.output)
