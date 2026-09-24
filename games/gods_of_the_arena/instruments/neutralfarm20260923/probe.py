"""Reconstruct the candidate's full decisions without changing captured games."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT.parent / 'polyworld/tmp/gota-lane-neutral62-20260923'
read = lambda p: json.loads(p.read_text())


def run(folder):
    out = RAW / 'source-audits' / folder.name
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'result.json').exists(): return read(out / 'result.json')
    row = read(folder / 'audit-result.json')
    assert row['valid']
    command = [str(RAW / 'bin/source-probe'), '--replay', str(folder / 'replay.bin')]
    proc = subprocess.run(command, capture_output=True, text=True, timeout=300,
        env=dict(os.environ, AUDIT_SLOT=str(row['slot']), AUDIT_POLICY=str(RAW/'lane-neutral/policy.bas')))
    (out / 'run.log').write_text(proc.stdout + proc.stderr)
    assert proc.returncode == 0, proc.stderr[-2000:]
    result = json.loads(proc.stdout.splitlines()[-1])
    assert result['valid'] and result['first_choice'] is not None
    assert result['prefix_ticks'] == row['ticks']
    assert result['max_instructions'] <= 19000 and result['max_work'] <= 50000
    result.update(episode=folder.name, hero_class=row['hero']['class'], slot=row['slot'])
    (out / 'result.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def main():
    seen = {}
    with ThreadPoolExecutor(2) as pool:
        while len(seen) < 40:
            pairs = read(RAW/'counterfactual/lane-neutral/paired-results.json')['pairs'] if (RAW/'counterfactual/lane-neutral/paired-results.json').exists() else []
            folders = [RAW/'artifacts'/r['candidate']['episode'] for r in pairs if r['candidate']['episode'] not in seen]
            for r in pool.map(run, folders): seen[r['episode']] = r
            print(json.dumps({'full_sources_reconstructed': len(seen)}), flush=True)
            if len(seen) < 40: time.sleep(10)
    rows = list(seen.values())
    result = {'complete': True, 'games': 40, 'rows': rows,
        'changed_lane_games': sum(r['first_choice']['laneChanged'] == 1 for r in rows),
        'matched_commands': sum(r['matched_commands'] for r in rows),
        'games_with_neutral_targets':sum(r['neutral_target_decisions']>0 for r in rows),
        'games_with_pulls':sum(r['pull_starts']>0 for r in rows),
        'pull_starts':sum(r['pull_starts'] for r in rows),
        'scope': 'Exact own-source complete reconstruction, not responsive counterfactual evaluation. No outcome-selected exclusions.'}
    (RAW/'source-audit.json').write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__': main()
