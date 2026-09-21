"""Responsive local screen: candidate (5 heroes) vs rival (5 heroes), both colours, fixed seeds.

usage: local_screen.py OUT_DIR CANDIDATE.bas RIVAL_NAME=RIVAL.bas [...] [--seeds 54,101,202] [--jobs 3]
Writes OUT_DIR/<rival>-<color>-<seed>.{json,replay,log} and OUT_DIR/plan.json; prints a W/L/D/INVALID table.
Red = slots 0-4, blue = slots 5-9. Never edits policies; hashes everything it runs.
"""
import argparse, hashlib, json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / '.gota'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run(out, tag, ours, rival, color, seed):
    cmd = [str(ROOT/'bin/episode'), '--config', str(ROOT/'game-config.json'), '--seed', str(seed),
           '--record', str(out/f'{tag}.replay')]
    order = [ours]*5 + [rival]*5 if color == 'red' else [rival]*5 + [ours]*5
    cmd += ['--bot:' + str(p) for p in order]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    (out/f'{tag}.log').write_text(r.stdout + '\n--- stderr ---\n' + r.stderr)
    line = next((l for l in reversed(r.stdout.splitlines()) if l.startswith('{')), None)
    if r.returncode != 0 or line is None:
        return tag, {'res': 'INVALID', 'error': (r.stderr.strip().splitlines() or ['no json'])[-1][:200]}
    j = json.loads(line)
    (out/f'{tag}.json').write_text(line)
    team = 0 if color == 'red' else 1
    hs = j['heroes']; our = [h for h in hs if h['team'] == team]; th = [h for h in hs if h['team'] != team]
    if any(h.get('vm_failed') for h in hs):
        res = 'INVALID'
    else:
        res = 'W' if j['winner'] == team else ('L' if j['winner'] in (0, 1) else 'D')
    return tag, {'res': res, 'ticks': j['ticks'], 'timeout': j.get('timeout'),
                 'our_deaths': sum(h['deaths'] for h in our), 'their_deaths': sum(h['deaths'] for h in th),
                 'our_lvl': sum(h['level'] for h in our), 'their_lvl': sum(h['level'] for h in th),
                 'max_instr': max(h['max_instructions'] for h in our),
                 'vmfail': [h.get('slot', i) for i, h in enumerate(hs) if h.get('vm_failed')],
                 'hash': j['state_hash']}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out'); ap.add_argument('candidate'); ap.add_argument('rivals', nargs='+')
    ap.add_argument('--seeds', default='54,101,202'); ap.add_argument('--jobs', type=int, default=3)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    cand = Path(a.candidate).resolve()
    rivals = {r.split('=')[0]: Path(r.split('=')[1]).resolve() for r in a.rivals}
    seeds = [int(s) for s in a.seeds.split(',')]
    plan = {'candidate': sha(cand), 'candidate_path': str(cand.relative_to(REPO)),
            'rivals': {k: {'sha256': sha(v), 'path': str(v)} for k, v in rivals.items()},
            'seeds': seeds, 'colors': ['red', 'blue'], 'engine': json.loads((ROOT/'build.json').read_text()),
            'frozen_at': datetime.now(timezone.utc).isoformat()}
    (out/'plan.json').write_text(json.dumps(plan, indent=1))
    jobs = [(f'{name}-{color}-{seed}', cand, path, color, seed)
            for name, path in rivals.items() for color in ('red', 'blue') for seed in seeds]
    results = {}
    with ThreadPoolExecutor(a.jobs) as ex:
        for tag, r in ex.map(lambda j: run(out, *j), jobs):
            results[tag] = r; print(tag, json.dumps(r), flush=True)
    (out/'results.json').write_text(json.dumps(results, indent=1))
    for name in rivals:
        for color in ('red', 'blue'):
            rs = [results[f'{name}-{color}-{s}'] for s in seeds]
            tally = {k: sum(r['res'] == k for r in rs) for k in ('W', 'L', 'D', 'INVALID')}
            streams = len({r.get('hash') for r in rs})
            mi = max((r.get('max_instr', 0) for r in rs), default=0)
            print(f'{name:>8} {color:>4} W{tally["W"]} L{tally["L"]} D{tally["D"]} INV{tally["INVALID"]} streams={streams} max_instr={mi}')


if __name__ == '__main__':
    main()
