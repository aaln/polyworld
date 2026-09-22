"""Decode every hosted portal trace; report score and rival uncertainty."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import random
import statistics
import subprocess
import time
import khors

h, OUT = khors.h, khors.OUT


def interval(values, seed=922114, repeats=10000):
    rng = random.Random(seed)
    n = len(values)
    samples = sorted(sum(rng.choices(values, k=n)) / n for _ in range(repeats))
    return [samples[int(.025 * repeats)], samples[int(.975 * repeats)]]


def decode(path):
    dest = path.parent / 'portals.json'
    if dest.exists():
        return
    proc = subprocess.run([str(h.STUDY / 'bin/events'), '--replay', str(path.parent / 'replay.bin')],
                          capture_output=True, text=True, timeout=900)
    (path.parent / 'portals.log').write_text(proc.stderr)
    assert proc.returncode == 0, proc.stderr[-2000:]
    data = json.loads(proc.stdout.splitlines()[-1])
    assert data['hash_mismatches'] == 0
    h.write(dest, data)


def build():
    plan = h.read(OUT / 'plan.json')
    verdict = h.read(OUT / 'result.json')
    cells = []
    for arm, cell in zip(plan['arms'], verdict['cells']):
        own, rival = arm['own_slots'][0], arm['rival_slot']
        folder = OUT / arm['name'] / str(arm['side'])
        assert cell['games'] == 40
        portal_rows = [h.read(folder / 'artifacts' / r['episode'] / 'portals.json')['heroes'][own] for r in cell['rows']]
        portal = {k: sum(r[k] for r in portal_rows) for k in
                  ('portals_started', 'completed', 'interrupted', 'home_portals_from_keep', 'low_field_ticks', 'ready_low_field_ticks')}
        deltas = [r['khors_score_delta'] for r in cell['rows']]
        ci = interval(deltas)
        comparisons = []
        for label, ident in [('khors:v114', khors.KHORS),
                             ('Jordan:v411', 'a15665be-4edf-4857-b23b-2888b4b49868'),
                             ('Richard:v153', 'd774f970-7699-4478-acb3-3fb99a6627cb')]:
            slot = arm['roster'].index(ident)
            assert slot // 5 != arm['side']
            scores = [r['scores'][slot] for r in cell['rows']]
            delta = [r['score'] - s for r, s in zip(cell['rows'], scores)]
            comparisons.append({'opponent': label, 'slot': slot, 'mean_score': statistics.mean(scores),
                                'own_minus_opponent': statistics.mean(delta), 'difference_ci95': interval(delta),
                                'individual_score_wins': sum(d > 0 for d in delta), 'ties': sum(d == 0 for d in delta)})
        cells.append({**{k: v for k, v in cell.items() if k != 'rows'}, 'portal': portal,
                      'khors_difference_ci95': ci, 'opponents': comparisons,
                      'khors_superiority_passed': cell['invalid'] == 0 and cell['score'] >= 1.1 * cell['khors_score'] and ci[0] > 0})
    old, new = verdict['cells'][:2], verdict['cells'][2:]
    rng = random.Random(922160)
    gains = []
    for _ in range(10000):
        scores = [sum(rng.choices([r['score'] for r in c['rows']], k=40)) / 40 for c in old + new]
        control = sum(scores[:2]) / 2
        gains.append((sum(scores[2:]) / 2 / control - 1) * 100 if control else 0)
    gains.sort()
    result = {'complete': True, 'source_sha256': khors.study.HASH, 'games': 160,
              'score_gate_passed': verdict['passed'],
              'khors_superiority_passed': all(c['khors_superiority_passed'] for c in cells[2:]),
              'aggregate_gain_percent': (verdict['score'] / verdict['control_score'] - 1) * 100,
              'aggregate_gain_ci95_percent': [gains[250], gains[9750]], 'cells': cells,
              'uncertainty': 'Whole-game bootstrap, side-stratified independent control/candidate draws; within-game rival differences. Fixed rosters/first picks and repeated trajectories limit generalization. Portal counts are descriptive; total low-health time also depends on game duration.',
              'source': str(OUT / 'plan.json')}
    h.write(OUT / 'report.json', result)
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--watch', action='store_true')
    args = p.parse_args()
    while True:
        todo = [p for p in OUT.glob('*/*/artifacts/*/result.json') if not (p.parent / 'portals.json').exists()]
        with ThreadPoolExecutor(4) as pool:
            list(pool.map(decode, todo))
        done = list(OUT.glob('*/*/artifacts/*/portals.json'))
        h.write(OUT / 'portal-progress.json', {'decoded': len(done), 'total': 160})
        if (OUT / 'result.json').exists() and len(done) == 160:
            build()
            break
        if not args.watch:
            raise SystemExit('Comparison not complete; --watch streams all replay decodes.')
        time.sleep(10)
