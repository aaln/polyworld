"""Fail closed on engine/dependency drift; build only the published release."""
import os
from pathlib import Path
import subprocess

from policy_ir import HERE, ROOT, digest, read, write

RUN = ROOT.parent / 'gota-research-20260916'
SOURCE = 'f2ab9598d8f8001b6beae3e66404e341770c803f'
VERSION = '2026.9.16.5'


def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], text=True).strip()


def verify():
    if git(ROOT, 'rev-parse', 'HEAD') != SOURCE:
        raise ValueError('Engine commit differs from the published release')
    if git(ROOT, 'status', '--porcelain', '--untracked-files=no'):
        raise ValueError('Tracked engine/config files have local changes')
    unknown = git(ROOT, 'ls-files', '--others', '--exclude-standard').splitlines()
    if any(not p.startswith('examples/gods_of_the_arena/players/ir/') for p in unknown):
        raise ValueError('Unexpected untracked source in clean engine workspace')
    dependencies = {}
    for line in (ROOT / 'coworld/dependencies.lock').read_text().splitlines():
        name, version, url, revision = line.split()
        path = RUN / 'deps' / name
        if git(path, 'rev-parse', 'HEAD') != revision or git(path, 'status', '--porcelain'):
            raise ValueError('Pinned dependency changed: ' + name)
        dependencies[name] = revision
    coworld = read(RUN / 'coached-lanes/live-change.json')
    if coworld['version'] != VERSION or f'/tree/{SOURCE}/' not in coworld['manifest']['game']['runnable']['source_url']:
        raise ValueError('Published game and checkout disagree')
    return {'game_source': SOURCE, 'game_version': VERSION, 'workspace': str(ROOT),
            'engine_clean': True, 'dependencies': dependencies,
            'lock_sha256': digest((ROOT / 'coworld/dependencies.lock').read_bytes()),
            'nim': subprocess.check_output(['nim', '--version'], text=True)}


def build():
    manifest = verify()
    out = RUN / 'r5/build'
    out.mkdir(exist_ok=True)
    env = dict(os.environ, POLYWORLD_DEPS=str(RUN / 'deps'))
    for name, source in [('episode', 'episode_release.nim'), ('audit', 'audit_release.nim')]:
        subprocess.run(['nim', 'c', '-d:headless', '--hints:off', f'-o:{out/name}', str(HERE/source)],
                       cwd=ROOT, env=env, check=True)
    manifest['sources'] = {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in HERE.glob('*.nim')}
    manifest['binaries'] = {name: digest((out/name).read_bytes()) for name in ['episode', 'audit']}
    verify()
    write(out / 'manifest.json', manifest)


if __name__ == '__main__':
    build()
