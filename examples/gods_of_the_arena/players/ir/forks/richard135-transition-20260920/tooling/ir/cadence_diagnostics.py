"""Diagnose completed discovery tapes without inspecting confirmation outcomes."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys

from policy_ir import HERE, digest, read, write


def main(directory):
    binary = directory / 'replay-diagnostics'
    report = read(directory / 'hosted-discovery/result.json')
    out = directory / 'cadence-diagnostics'
    out.mkdir(exist_ok=True)
    selected = ['v2', 'motion', 'cadence_all']
    inputs = {'binary_sha256': digest(binary.read_bytes()),
              'source_sha256': digest((HERE / 'replay_diagnostics.nim').read_bytes()),
              'discovery_sha256': digest((directory / 'hosted-discovery/result.json').read_bytes()),
              'meaning': 'Descriptive mechanisms on all already-observed discovery tapes; no new strength test.'}
    if (out / 'inputs.json').exists() and read(out / 'inputs.json') != inputs:
        raise ValueError('Diagnostic provenance changed')
    write(out / 'inputs.json', inputs)

    def diagnose(case):
        name, row = case
        tape = directory / 'hosted-discovery' / name / 'artifacts' / row['episode'] / 'replay.bin'
        dest = out / name / (row['episode'] + '.jsonl')
        dest.parent.mkdir(exist_ok=True)
        if not dest.exists():
            proc = subprocess.run([str(binary), '--replay', str(tape)],
                                  env=os.environ | {'GOTA_SLOT': str(row['slot']), 'GOTA_FRAME_STEP': '0'},
                                  capture_output=True, text=True, timeout=600)
            dest.with_suffix('.stderr').write_text(proc.stderr)
            if proc.returncode:
                raise ValueError('Full diagnostic replay failed: ' + row['episode'])
            dest.write_text(proc.stdout)
        result = json.loads(dest.read_text().splitlines()[-1])
        if (result['type'] != 'summary' or result['hash_mismatches'] or
                result['slot'] != row['slot'] or result['ticks'] != row['ticks'] or
                result['xp'] != row['xp']):
            raise ValueError('Discovery diagnostic mismatch')
        return name, result | {'episode': row['episode'], 'replay_sha256': digest(tape.read_bytes()),
                               'diagnostic_sha256': digest(dest.read_bytes())}

    cases = [(name, row) for name in selected for row in report['arms'][name]['rows']]
    with ThreadPoolExecutor(4) as pool:
        rows = list(pool.map(diagnose, cases))
    write(out / 'rows.json', [{'arm': name, **row} for name, row in rows])
    metrics = {}
    for name in selected:
        cohort = [row for arm, row in rows if arm == name]
        groups = {}
        for cls in sorted({row['class'] for row in cohort}):
            cc = [row for row in cohort if row['class'] == cls]
            intervals = Counter(b['tick'] - a['tick'] for row in cc
                                for a, b in zip(row['hits'], row['hits'][1:])
                                if a['target'] == b['target'] and b['tick'] - a['tick'] <= 96)
            groups[cls] = {'games': len(cc), 'hits': sum(len(row['hits']) for row in cc),
                           'hits_per_alive_minute': sum(len(row['hits']) for row in cc) * 1440 / sum(row['alive_ticks'] for row in cc),
                           'same_target_intervals_le96_most_common': intervals.most_common(8)}
        walks = [w for row in cohort for w in row['walks'] if w['hit_adjacent']]
        metrics[name] = {'games': len(cohort),
                         'hits_per_alive_minute': sum(len(row['hits']) for row in cohort) * 1440 / sum(row['alive_ticks'] for row in cohort),
                         'offense_casts': sum(c['kind'] == 'Strike' for row in cohort for c in row['casts']),
                         'post_hit_walk_bursts': len(walks),
                         'post_hit_moving_ticks': sum(w['moved_ticks'] for w in walks),
                         'post_hit_median_displacement': statistics.median(w['displacement'] for w in walks) if walks else None,
                         'longest_idle_ticks': max(row['longest_idle_ticks'] for row in cohort),
                         'classes': groups}
    write(out / 'result.json', {'inputs': inputs, 'arms': metrics,
          'limits': ['Independent seeds, fixed class/roster coupling; descriptive discovery data.',
                     'Consecutive same-target intervals exclude gaps over96ticks; events within a game are correlated.',
                     'Post-hit walk segments come from commands, not private VM trigger state.',
                     'No competitive inference beyond the separately frozen hosted comparison.']})
    print(json.dumps({name: {k: v for k, v in m.items() if k != 'classes'} for name, m in metrics.items()}, indent=2))


if __name__ == '__main__':
    main(Path(sys.argv[1]).resolve())
