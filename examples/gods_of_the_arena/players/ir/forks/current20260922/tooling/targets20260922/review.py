"""Keep exact outcomes, growth diagnostics and trajectory correlation separate."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
import subprocess
from panel import h, STUDY


def commands(path):
    out = path.parent / 'command-hash.json'
    if not out.exists():
        p = subprocess.run([str(STUDY / 'bin/command-hash'), str(path.parent / 'replay.bin')],
                           capture_output=True, text=True, check=True)
        h.write(out, json.loads(p.stdout))
    return path.parent.name, h.read(out)


def main():
    cells = []
    for label in ('baseline', 'practiced'):
        for target in ('relh', 'jordan', 'richard'):
            for side in (0, 1):
                folder = STUDY / label / target / str(side)
                if not (folder / 'result.json').exists():
                    continue
                result = h.read(folder / 'result.json')
                with ThreadPoolExecutor(4) as pool:
                    hashes = dict(pool.map(commands, folder.glob('artifacts/*/result.json')))
                counts = Counter(x['canonical_commands_sha1'] for x in hashes.values())
                h.write(folder / 'trajectory-correlation.json', {
                    'streams': hashes, 'counts': dict(counts), 'distinct': len(counts),
                    'games': len(hashes), 'limits': 'Distinct streams are not necessarily independent.'})
                subjects = []
                for path in folder.glob('artifacts/*/audit.json'):
                    audit = h.read(path)
                    subjects.extend(audit['heroes'][side * 5:side * 5 + 5])
                cells.append({
                    'label': label, 'target': target, 'side': side,
                    **{k: result[k] for k in ('games', 'wins', 'losses', 'draws', 'invalid',
                                              'own_score', 'opponent_score', 'fort_passed', 'score_passed')},
                    'distinct_command_streams': len(counts),
                    'hero_games': len(subjects),
                    'classes': dict(Counter(x['class'] for x in subjects)),
                    'mean_terminal': {k: sum(x[k] for x in subjects) / max(1, len(subjects))
                                      for k in ('xp', 'level', 'deaths', 'gold')},
                    'heroes_with_upgrades': sum(sum(x['ranks']) > 0 for x in subjects)})
    before = {(c['target'], c['side']): c for c in cells if c['label'] == 'baseline'}
    for c in cells:
        if c['label'] == 'practiced':
            b = before[c['target'], c['side']]
            c['score_delta'] = c['own_score'] - b['own_score']
            c['win_delta'] = c['wins'] - b['wins']
    h.write(STUDY / 'review.json', {
        'complete': len(cells) == 12, 'cells': cells,
        'limits': 'Uniform five-copy teams, one fixed map, unpaired generated seeds, correlated command streams. Separate XP score and fort outcomes; no mixed-team/rank claim.'})
    print(json.dumps(cells, indent=2))


if __name__ == '__main__':
    main()
