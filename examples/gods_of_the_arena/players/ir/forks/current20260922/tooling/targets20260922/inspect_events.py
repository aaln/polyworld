"""Outcome-stratified median-score diagnostic replays, explicitly retrospective."""
from concurrent.futures import ThreadPoolExecutor
import json
import subprocess
from panel import h, STUDY


def run(case):
    folder = STUDY / case['label'] / case['target'] / str(case['side']) / 'artifacts' / case['episode']
    path = folder / 'micro-events.json'
    if not path.exists():
        p = subprocess.run([str(STUDY / 'bin/events'), '--replay', str(folder / 'replay.bin')],
                           capture_output=True, text=True, check=True, timeout=300)
        (folder / 'micro-events.log').write_text(p.stdout + p.stderr)
        data = json.loads(p.stdout.splitlines()[-1])
        assert data['hash_mismatches'] == 0
        h.write(path, data)
    return {**case, 'events': h.read(path)}


def main():
    cases = []
    for label in ('baseline', 'practiced'):
        for target in ('relh', 'jordan', 'richard'):
            for side in (0, 1):
                p = STUDY / label / target / str(side) / 'result.json'
                if not p.exists():
                    continue
                for outcome in ('win', 'loss', 'draw'):
                    rows = [r for r in h.read(p)['rows'] if r['valid'] and r[outcome]]
                    if rows:
                        rows.sort(key=lambda r: (r['score'], r['episode']))
                        row = rows[len(rows) // 2]
                        cases.append({'label': label, 'target': target, 'side': side,
                                      'outcome': outcome, 'episode': row['episode']})
    with ThreadPoolExecutor(2) as pool:
        rows = list(pool.map(run, cases))
    h.write(STUDY / 'events-review.json', {
        'selection': 'Median own score within each observed W/L/D group per completed cell; tie by episode ID. Retrospective diagnosis, never independent validation.',
        'cases': rows})
    print(json.dumps({'audited': len(rows)}))


if __name__ == '__main__':
    main()
