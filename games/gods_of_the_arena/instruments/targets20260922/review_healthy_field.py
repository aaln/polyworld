"""Growth and trajectory audit for the frozen current-score mixed rosters."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
import subprocess
from review import commands
from healthy_field import h, OUT


def main():
    result = h.read(OUT / 'result.json')
    assert result['complete']
    cells, selections = [], []
    for label in ('candidate', 'control'):
        for side in (0, 1):
            folder = OUT / label / str(side)
            cell = h.read(folder / 'result.json')
            with ThreadPoolExecutor(4) as pool:
                streams = dict(pool.map(commands, folder.glob('artifacts/*/result.json')))
            counts = Counter(v['canonical_commands_sha1'] for v in streams.values())
            h.write(folder / 'trajectory-correlation.json', {
                'streams': streams, 'counts': dict(counts), 'distinct': len(counts),
                'limits': 'Generated seeds and distinct streams are not independent samples.'})
            rows = cell['rows']
            cells.append({'label': label, 'side': side,
                **{k: cell[k] for k in ('games', 'invalid', 'own_score', 'opponent_score', 'wins', 'losses', 'draws')},
                'distinct_command_streams': len(counts),
                'classes': dict(Counter(r.get('class') for r in rows)),
                'means': {k: sum(r.get(k, 0) for r in rows) / len(rows) for k in ('xp', 'deaths', 'level', 'hits')}})
            # Retrospective mechanism review, not another validation sample.
            for outcome in ('win', 'loss', 'draw'):
                subset = sorted((r for r in rows if r['valid'] and r[outcome]), key=lambda r: (r['score'], r['episode']))
                if not subset:
                    continue
                row = subset[len(subset) // 2]
                path = folder / 'artifacts' / row['episode']
                event_path = path / 'micro-events.json'
                if not event_path.exists():
                    p = subprocess.run([str(h.STUDY / 'bin/events'), '--replay', str(path / 'replay.bin')],
                                       text=True, capture_output=True, check=True, timeout=300)
                    (path / 'micro-events.log').write_text(p.stdout + p.stderr)
                    h.write(event_path, json.loads(p.stdout.splitlines()[-1]))
                events = h.read(event_path)
                assert events['hash_mismatches'] == 0
                selections.append({'label': label, 'side': side, 'outcome': outcome,
                                   'episode': row['episode'], 'events': events})
    h.write(OUT / 'review.json', {'complete': True, 'cells': cells,
             'diagnostic_selection': 'Median subject score within each observed outcome per cell; retrospective.',
             'diagnostic_replays': selections,
             'limits': 'Two fixed mixed-team first-pick rosters, current exact versions, correlated trajectories. No late-draft, universal field or rank conclusion.'})
    print(json.dumps(cells, indent=2))


if __name__ == '__main__':
    main()
