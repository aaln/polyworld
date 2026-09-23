"""Rebuild the balance auditor with exact engine and dependency revisions."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from build import COMMIT, ENGINE, ROOT, STUDY, HERE


def run(*args, **kwargs):
    return subprocess.check_output(list(map(str, args)), text=True, **kwargs).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--engine', type=Path, default=ENGINE)
    parser.add_argument('--runtime', type=Path, default=STUDY)
    parser.add_argument('--deps', type=Path, required=True)
    parser.add_argument('--nim', default='nim')
    args = parser.parse_args()
    engine, runtime, deps = args.engine.resolve(), args.runtime.resolve(), args.deps.resolve()
    if not engine.exists():
        run('git', 'worktree', 'add', '--detach', engine, COMMIT, cwd=ROOT)
    assert run('git', 'rev-parse', 'HEAD', cwd=engine) == COMMIT
    assert not run('git', 'diff', COMMIT, '--', 'src', 'examples/gods_of_the_arena', 'coworld/dependencies.lock', cwd=engine)
    nim = run(args.nim, '--version')
    assert 'Version 2.2.10' in nim
    deps.mkdir(parents=True, exist_ok=True)
    revisions = {}
    for line in (engine / 'coworld/dependencies.lock').read_text().splitlines():
        name, _, url, revision = line.split()
        path = deps / name
        if not path.exists():
            run('git', 'clone', '--filter=blob:none', '--no-checkout', url, path)
            run('git', '-C', path, 'fetch', '--depth=1', 'origin', revision)
            run('git', '-C', path, 'checkout', '--detach', revision)
        assert run('git', '-C', path, 'rev-parse', 'HEAD') == revision
        assert not run('git', '-C', path, 'status', '--porcelain')
        revisions[name] = revision
    sources = {'episode-v2': HERE / 'episode.nim',
               'command-hash': HERE.parent / 'week20260921/command_hash.nim',
               'practice': HERE.parent / 'targets20260922/practice.nim',
               'scenarios': HERE.parent / 'targets20260922/scenarios.nim'}
    (runtime / 'bin').mkdir(parents=True, exist_ok=True)
    for name, source in sources.items():
        dest = engine / 'examples/gods_of_the_arena/tools' / ('balance_' + name.replace('-', '_') + '.nim')
        shutil.copyfile(source, dest)
        run(args.nim, 'c', '-d:headless', '-d:release', '--hints:off', '--out:' + str(runtime / 'bin' / name),
            dest, cwd=engine, env=dict(os.environ, POLYWORLD_DEPS=str(deps)))
    dest = engine / 'tests/balance_policy_mirrors.nim'
    shutil.copyfile(HERE / 'mirrors.nim', dest)
    run(args.nim, 'c', '-d:headless', '-d:release', '--hints:off', '--out:' + str(runtime / 'bin/mirrors-memory'),
        dest, cwd=engine, env=dict(os.environ, POLYWORLD_DEPS=str(deps)))
    proof = {'engine_commit': COMMIT, 'nim': nim, 'dependencies': revisions,
             'binaries': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (runtime / 'bin').iterdir()}}
    path = runtime / 'bootstrap-rebuilt.json'
    assert not path.exists(), 'Use a fresh runtime directory for a new provenance capture'
    path.write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
