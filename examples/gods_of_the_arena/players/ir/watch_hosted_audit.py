"""Verify full hosted tapes as their core artifacts finish downloading."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import time

from hosted_wave_audit import verify
from policy_ir import digest, read, write


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    directory = args.directory.resolve()
    count = read(directory / 'batch/request.json')['num_episodes']
    binary = directory / 'audit'
    binary_hash = digest(binary.read_bytes())
    attempted, verified, pending = set(), set(), {}
    with ThreadPoolExecutor(args.workers) as pool:
        while len(verified) < count:
            for future, folder in list(pending.items()):
                if future.done():
                    verified.add(future.result())
                    del pending[future]
                    write(directory / 'audit-progress.json', {'expected': count, 'verified': len(verified),
                                                            'binary_sha256': binary_hash})
                    print(f'Full replay audits: {len(verified)}/{count}', flush=True)
            for marker in sorted((directory / 'artifacts').glob('*/.done')):
                folder = marker.parent
                if folder in attempted or len(pending) >= args.workers:
                    continue
                attempted.add(folder)
                pending[pool.submit(verify, folder, binary, binary_hash)] = folder
            time.sleep(1)


if __name__ == '__main__':
    main()
