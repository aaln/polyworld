#!/usr/bin/env python3
"""Portable, read-only bootstrap and monitoring for the Devin GotA handoff."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

REPO = Path(__file__).resolve().parents[2]
ASSETS = Path(__file__).resolve().parent / 'portable'
SEED = REPO / 'docs/handoff/gota-20260920'
ENGINE = 'f2ab9598d8f8001b6beae3e66404e341770c803f'
IR = Path('examples/gods_of_the_arena/players/ir')


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2) + '\n')
    temp.replace(path)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(*args, **kwargs):
    return subprocess.check_output([str(a) for a in args], text=True, **kwargs).strip()


def check_engine(work):
    if command('git', '-C', work, 'rev-parse', 'HEAD') != ENGINE:
        raise ValueError('Engine commit changed; use a new pinned runtime.')
    if command('git', '-C', work, 'status', '--porcelain', '--untracked-files=no'):
        raise ValueError('Tracked engine files changed; do not claim league parity.')


def init(root):
    if (root / 'config.json').exists():
        raise ValueError('State already initialized; preserving existing configuration and research.')
    work = root / 'engine'
    root.mkdir(parents=True, exist_ok=True)
    if not work.exists():
        command('git', '-C', REPO, 'worktree', 'add', '--detach', work, ENGINE)
    check_engine(work)
    manifest = read(ASSETS / 'runtime-manifest.json')
    archive = ASSETS / 'runtime-ir.zip'
    if sha(archive) != manifest['archive_sha256']:
        raise ValueError('Runtime archive hash mismatch')
    tooling = work / IR
    tooling.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        if set(z.namelist()) != set(manifest['files']):
            raise ValueError('Runtime archive inventory changed')
        for name, expected in manifest['files'].items():
            if Path(name).name != name:
                raise ValueError('Archive entry must be a flat source filename')
            data = z.read(name)
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError('Runtime source hash mismatch: ' + name)
            (tooling / name).write_bytes(data)
    # Portability adapters are explicit overlays; original archive stays immutable.
    overlays = {
        'hosted_wave.py': REPO / IR / 'hosted_wave.py',
        'remote_episode.nim': ASSETS / 'remote_episode.nim',
        'replay_opponent_observer.nim': REPO / 'games/gods_of_the_arena/instruments/opponent_ir/replay_observer.nim',
    }
    for name, source in overlays.items():
        shutil.copy2(source, tooling / name)
    cfg = read(SEED / 'config.json')
    cfg.update(workspace=str(work), tooling=str(tooling), python=sys.executable,
               dependencies=str(root / 'deps'), auditor=str(root / 'bin/audit-hosted'),
               league_auto_deploy=False, remote_mode='observe',
               daily_episode_limit=1600, cycle_episode_limit=400)
    for name in ('codex', 'auditor_sha256', 'daily_episode_limit_override',
                 'league_deployment_authorization'):
        cfg.pop(name, None)
    write(root / 'config.json', cfg)
    write(root / 'runtime-overlay.json', {n: sha(tooling / n) for n in overlays})
    (root / 'FOCUS.md').write_text(
        '# Remote startup\n\nObserver mode. Read docs/guides/devin-gota-autoresearch.md in the fork.\n'
        'The archived campaign is provenance, not an active remote ledger or a completed transfer.\n')
    print(json.dumps({'initialized': str(root), 'mode': 'observe', 'engine': ENGINE}))


def build(root, nim, existing_deps):
    cfg = read(root / 'config.json')
    work = Path(cfg['workspace'])
    check_engine(work)
    deps = existing_deps.resolve() if existing_deps else Path(cfg['dependencies'])
    deps.mkdir(parents=True, exist_ok=True)
    revisions = {}
    for line in (work / 'coworld/dependencies.lock').read_text().splitlines():
        if not line.strip():
            continue
        name, _, url, revision = line.split()
        path = deps / name
        if not path.exists():
            command('git', 'clone', '--filter=blob:none', '--no-checkout', url, path)
            command('git', '-C', path, 'fetch', '--depth=1', 'origin', revision)
            command('git', '-C', path, 'checkout', '--detach', revision)
        if command('git', '-C', path, 'rev-parse', 'HEAD') != revision:
            raise ValueError('Dependency revision differs: ' + name)
        if command('git', '-C', path, 'status', '--porcelain'):
            raise ValueError('Dependency has local changes: ' + name)
        revisions[name] = revision
    out = root / 'bin'
    out.mkdir(exist_ok=True)
    env = dict(os.environ, POLYWORLD_DEPS=str(deps))
    sources = {'episode': 'remote_episode.nim', 'audit-hosted': 'audit_hosted_release.nim',
               'scenario-vm': 'scenario_vm.nim', 'observer-probe': 'replay_opponent_observer.nim'}
    for name, source in sources.items():
        subprocess.run([nim, 'c', '-d:headless', '-d:release', '--hints:off',
                        '-o:' + str(out / name), str(work / IR / source)],
                       cwd=work, env=env, check=True)
    check_engine(work)
    receipt = {'at': datetime.now(timezone.utc).isoformat(), 'engine': ENGINE,
               'nim': command(nim, '--version'), 'dependencies': revisions,
               'dependency_lock_sha256': sha(work / 'coworld/dependencies.lock'),
               'sources': {n: sha(work / IR / s) for n, s in sources.items()},
               'binaries': {n: sha(out / n) for n in sources}}
    write(root / 'build.json', receipt)
    cfg.update(dependencies=str(deps), auditor_sha256=receipt['binaries']['audit-hosted'])
    write(root / 'config.json', cfg)
    write(root / 'game-config.json', cfg['game_config'])
    print(json.dumps({'built': list(sources), 'receipt': str(root / 'build.json')}))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=REPO / '.gota')
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('init')
    b = sub.add_parser('build')
    b.add_argument('--nim', default='nim')
    b.add_argument('--existing-deps', type=Path)
    sub.add_parser('monitor')
    sub.add_parser('verify')
    args = p.parse_args()
    root = args.root.resolve()
    if args.command == 'init':
        init(root)
    elif args.command == 'build':
        build(root, args.nim, args.existing_deps)
    elif args.command == 'monitor':
        env = dict(os.environ, GOTA_RESEARCH_ROOT=str(root))
        subprocess.run([sys.executable, str(Path(__file__).with_name('league_watch.py'))],
                       env=env, check=True)
    else:
        for script in (REPO / IR / 'forks/jordan268/verify.py',
                       REPO / IR / 'forks/richard135-coaching-20260920/reproduce.py',
                       REPO / IR / 'forks/richard135-transition-20260920/reproduce.py'):
            subprocess.run([sys.executable, str(script)], cwd=REPO, check=True)
        subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s',
                        'games/gods_of_the_arena/instruments/opponent_ir', '-p', 'test_*.py'],
                       cwd=REPO, check=True)


if __name__ == '__main__':
    main()
