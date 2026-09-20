"""Mine exact-version GOTA tapes without rerunning policies or changing games.

python replay_review.py RUN --binary RUN/diagnostics --arms v2 long_bare spell_short
Writes complete diagnostic JSONL, immutable input hashes, and per-episode rows.
The 40 cases are an already-observed discovery cohort, not new validation.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ARMS = {
    "v2": "tmp/gota-ir/hit-kite-20260915/screen/parent",
    "default": "tmp/gota-ir/hit-kite-20260915/screen/baseline",
    "long_bare": "tmp/gota-ir/kiting-spells-20260915/long_bare/screen/candidate",
    "spell_short": "tmp/gota-ir/kiting-spells-20260915/spell_short/screen/candidate",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tape(path):
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.startswith('{')]
    if not rows or rows[0].get("type") != "header" or rows[-1].get("type") != "summary":
        raise ValueError(f"Incomplete diagnostic: {path}")
    if rows[-1]["hash_mismatches"]:
        raise ValueError(f"Replay hash mismatch: {path}")
    return rows[0], rows[1:-1], rows[-1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("directory", type=Path)
    p.add_argument("--binary", type=Path, required=True)
    p.add_argument("--arms", nargs="+", choices=ARMS, default=["v2"])
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--frame-step", type=int, default=0)
    args = p.parse_args()
    args.directory.mkdir(exist_ok=True, parents=True)
    binary = args.binary.resolve()
    binary_sha = sha(binary)
    jobs = [(arm, path) for arm in args.arms for path in sorted((ROOT / ARMS[arm]).glob('*/result.json'))]
    if len(jobs) != 40 * len(args.arms):
        raise ValueError("Expected every one of the 40 discovery cases per arm")

    def decode(job):
        arm, result_path = job
        result = json.loads(result_path.read_text())
        slot = result['candidate_slots'][0]
        replay = result_path.parent / 'episode.replay'
        if sha(replay) != result['replay_sha256']:
            raise ValueError("Source replay changed")
        folder = args.directory / arm / result_path.parent.name
        folder.mkdir(exist_ok=True, parents=True)
        manifest = {'binary_sha256': binary_sha, 'replay_sha256': sha(replay), 'slot': slot,
                    'frame_step': args.frame_step, 'result_sha256': sha(result_path),
                    'policy_sha256': result['candidate_sha256'], 'source': str(result_path)}
        output = folder / 'diagnostic.jsonl'
        if (folder / 'inputs.json').exists():
            if json.loads((folder / 'inputs.json').read_text()) != manifest:
                raise ValueError(f"Frozen input changed: {folder}")
        else:
            (folder / 'inputs.json').write_text(json.dumps(manifest, indent=2) + '\n')
        if not output.exists():
            tmp = folder / 'diagnostic.running'
            with tmp.open('w') as stdout, (folder / 'stderr.log').open('w') as stderr:
                subprocess.run([str(binary), '--replay', str(replay)], cwd=ROOT,
                               env={**os.environ, 'GOTA_SLOT': str(slot), 'GOTA_FRAME_STEP': str(args.frame_step)},
                               stdout=stdout, stderr=stderr, check=True, timeout=300)
            tmp.rename(output)
        header, frames, s = read_tape(output)
        if s['ticks'] != result['ticks'] or s['state_hash'] != result['state_hash']:
            raise ValueError("Final state does not match original episode")
        own = result['heroes'][slot]
        if len(s['deaths']) != own['deaths'] or len(s['hits']) != own['basic_hit_events'] or s['xp'] != own['total_xp']:
            raise ValueError("Independent counters disagree with original result")
        row = {'arm': arm, 'case': result_path.parent.name, 'seed': result['seed'],
               'score': own['score'], 'diagnostic': str(output), 'diagnostic_sha256': sha(output),
               **s}
        return row

    rows = []
    with ThreadPoolExecutor(args.workers) as pool:
        for f in as_completed([pool.submit(decode, j) for j in jobs]):
            rows.append(f.result())
            print(f"Verified {len(rows)}/{len(jobs)}", flush=True)
    rows.sort(key=lambda x: (x['arm'], x['seed']))
    (args.directory / 'results.json').write_text(json.dumps(rows, indent=2) + '\n')


if __name__ == '__main__':
    main()
