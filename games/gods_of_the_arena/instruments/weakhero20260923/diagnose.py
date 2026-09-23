"""Apply the predeclared outcome-blind32game downtime sample."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import statistics
import subprocess
from local import RAW, HERE, sha, write


def main():
    read = lambda p: json.loads(p.read_text())
    plan = read(RAW / 'trial/plan.json')
    rows = []
    for arm in plan['arms']:
        folder = RAW / 'trial' / arm['name'] / arm['cell']
        eps = read(folder / 'episodes.json')
        assert len(eps) == 50 and all(e['status'] == 'completed' for e in eps)
        selection = sorted(eps, key=lambda e: hashlib.sha256(e['id'].encode()).hexdigest())[:4]
        rows.extend({'name': arm['name'], 'cell': arm['cell'], 'slot': arm['own_slots'][0], 'episode': e['id']} for e in selection)
    path = RAW / 'diagnostic-selection.json'
    if path.exists():
        assert read(path) == rows
    else:
        write(path, rows)

    def run(row):
        folder = RAW / 'trial' / row['name'] / row['cell'] / 'artifacts' / row['episode']
        dest = folder / 'downtime.json'
        if not dest.exists():
            proc = subprocess.run([str(RAW / 'bin/downtime'), '--replay', str(folder / 'replay.bin')], capture_output=True, text=True, timeout=300)
            (folder / 'downtime-stderr.log').write_text(proc.stderr)
            assert proc.returncode == 0, proc.stderr[-2000:]
            write(dest, json.loads(proc.stdout.splitlines()[-1]))
        data = read(dest)
        assert data['hash_mismatches'] == 0 and data['all_actions_consumed']
        hero = data['heroes'][row['slot']]
        t = hero['totals']
        scores = read(folder / 'result.json')
        return {**row, 'class': hero['class'], 'score': scores['score'], 'xp': scores['xp'], 'deaths': scores['deaths'], 'totals': t, 'dead_fraction': t.get('dead_ticks', 0) / t['battle_ticks'], 'keep_fraction': t.get('keep_ticks', 0) / t['battle_ticks'], 'field_xp_drought_fraction': t.get('field_after30s_without_xp_ticks', 0) / t['battle_ticks'], 'near_creep_fraction_of_alive_samples': t.get('within_creep_xp_range_samples', 0) / max(1, t.get('alive_position_samples', 0)), 'self_healing': t.get('ability_self_healing', 0), 'mana_restored': t.get('ability_mana_restored', 0), 'audit_sha256': sha(dest)}

    with ThreadPoolExecutor(3) as pool:
        results = list(pool.map(run, rows))
    summary = {}
    keys = ['score', 'xp', 'deaths', 'dead_fraction', 'keep_fraction', 'field_xp_drought_fraction', 'near_creep_fraction_of_alive_samples', 'self_healing', 'mana_restored']
    for label in ['baseline', 'explicit-sustain']:
        summary[label] = {}
        for group in ['lead', 'late']:
            rs = [r for r in results if r['name'] == label and r['cell'].endswith(group)]
            summary[label][group] = {'games': len(rs), **{k: statistics.mean(r[k] for r in rs) for k in keys}}
    write(RAW / 'diagnostic-summary.json', {'plan': read(RAW / 'diagnostic-plan.json'), 'games': len(results), 'summary': summary, 'rows': results, 'source_sha256': sha(HERE / 'downtime.nim'), 'binary_sha256': sha(RAW / 'bin/downtime')})
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
