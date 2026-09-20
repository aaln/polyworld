"""Export completed discovery cases and render recorded positions for review.

Uses the source-matched full replay decoder. Five-second sampled frames are
ground truth, not the policy decision snapshot; command counts are not damage.
"""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess

from policy_ir import digest, read, write
from release_workspace import ROOT, RUN
from win_screen import STUDY


def export():
    results = read(STUDY / 'hosted-discovery/result.json')
    out = STUDY / 'review'
    out.mkdir(exist_ok=True)
    selections = []
    for arm, cls, win in [('bounded', 'DruidWarden', 0), ('lanes', 'DruidWarden', 1)]:
        row = sorted((r for r in results['arms'][arm]['rows'] if r['class'] == cls and r['win'] == win), key=lambda r:r['episode'])[0]
        selections.append((arm, row))
    binary = RUN / 'r3/macro-replay-v2'
    def one(selection):
        arm, row = selection
        replay = STUDY / 'hosted-discovery' / arm / 'artifacts' / row['episode'] / 'replay.bin'
        if digest(replay.read_bytes()) != row['replay_sha256']:
            raise ValueError('Replay content changed')
        target = out / (arm + '-druid.jsonl')
        with target.open('w') as f:
            subprocess.run([str(binary), '--replay', str(replay)], cwd=ROOT, stdout=f, check=True)
        header, frames, summary = None, [], None
        with target.open() as f:
            for line in f:
                obj = json.loads(line)
                if obj['type'] == 'header': header = obj
                elif obj['type'] == 'frame':
                    for hero in obj['heroes']: hero.pop('visible_post_tick', None)
                    frames.append(obj)
                elif obj['type'] == 'summary': summary = obj
        if not summary or summary['hash_mismatches'] or summary['ticks'] != row['ticks']:
            raise ValueError('Replay audit incomplete')
        data = {'name':arm, 'row':row, 'header':header, 'frames':frames, 'summary':summary}
        write(out / (arm + '-druid-view.json'), data)
        return data
    with ThreadPoolExecutor(2) as pool:
        cases = list(pool.map(one, selections))
    write(out / 'druid-review-manifest.json', {
        'selection':'First lexicographic bounded Druid loss and lane Druid win in completed discovery. Different seeds; anecdotal mechanism review, not a paired effect estimate.',
        'decoder_sha256':digest(binary.read_bytes()), 'source_sha256':digest(Path(__file__).read_bytes()),
        'cases':[{'arm':c['name'], **c['row']} for c in cases]})
    return cases


def plot(cases, output=None, title=None, note=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    fig, axes = plt.subplots(len(cases), 5, figsize=(19, 8), squeeze=False)
    for axes_row, case in zip(axes, cases):
        terrain = np.array([[v == '.' for v in row] for row in case['header']['terrain']])
        for ax, fraction in zip(axes_row, [0, .25, .5, .75, 1]):
            f = case['frames'][round(fraction * (len(case['frames']) - 1))]
            ax.imshow(terrain, origin='lower', cmap='Greys', alpha=.18, extent=(0,116,0,116))
            for b in f['buildings']:
                if b['hp'] > 0:
                    ax.scatter(*b['position'], c=['#cd3838','#287ace'][b['team']], marker='s', s=35 if b['kind'] == 'Fort' else 10)
            for h in f['heroes']:
                if h['hp'] > 0:
                    ax.scatter(*h['position'], c=['#cd3838','#287ace'][h['team']], s=40)
                    ax.annotate(str(h['slot']), h['position'], xytext=(3,3), textcoords='offset points', fontsize=8)
                    if h['slot'] == case['row'].get('slot', -1):
                        ax.scatter(*h['position'], facecolors='none', edgecolors='#d69500', s=190, linewidths=2)
            ax.set(xlim=(0,116), ylim=(0,116), title=f"{case['name']} · {f['tick']/1440:.2f} min", aspect='equal')
    fig.suptitle((title or 'Druid discovery review — actual recorded positions every 5 seconds')+'\n'+
        (note or 'Gold ring: subject hero. Red/blue: teams. Squares: living buildings. Rows use different seeds.'), fontsize=14)
    fig.tight_layout(rect=(0,0,1,.93), h_pad=2)
    fig.savefig(output or STUDY / 'review/druid-movement.png', dpi=150)
    plt.close(fig)


if __name__ == '__main__':
    plot(export())
