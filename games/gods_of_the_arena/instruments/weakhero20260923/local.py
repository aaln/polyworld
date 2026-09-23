"""Compile exact60 tools and exercise both frozen policy sources."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT.parent / 'polyworld/tmp/gota-weakhero60-20260923'
PARENT = ROOT / 'examples/gods_of_the_arena/players/ir/forks/druid-lane20260923-hosted/druid-lane'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')

ENGINE = ROOT.parent / 'polyworld-gota-explicit60-20260923'
DEPS = ROOT.parent / 'polyworld/tmp/gota-explicit60-20260923/deps'
COMMIT = 'fd315c8fa30f8923c7a7709a577c40ac071b1c2a'
HERE = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ENGINE, text=True).strip() == COMMIT
    assert not subprocess.check_output(['git', 'diff', COMMIT, '--', 'src', 'examples/gods_of_the_arena', 'coworld/dependencies.lock'], cwd=ENGINE, text=True)
    deps = {}
    for line in (ENGINE / 'coworld/dependencies.lock').read_text().splitlines():
        name, _, _, rev = line.split()
        assert subprocess.check_output(['git', '-C', str(DEPS / name), 'rev-parse', 'HEAD'], text=True).strip() == rev
        assert not subprocess.check_output(['git', '-C', str(DEPS / name), 'status', '--porcelain'], text=True)
        deps[name] = rev
    sources = {'practice': HERE / 'practice.nim', 'economy': HERE.parent / 'portals20260922/economy.nim', 'command-hash': HERE.parent / 'week20260921/command_hash.nim', 'episode-v2': HERE.parent / 'productive20260923/episode59.nim'}
    (RAW / 'bin').mkdir(exist_ok=True)

    def build(entry):
        name, source = entry
        dest = ENGINE / 'examples/gods_of_the_arena/tools' / ('weak60_' + name.replace('-', '_') + '.nim')
        shutil.copyfile(source, dest)
        proc = subprocess.run(['/Users/aaln/.nimby/nim-2.2.10/bin/nim', 'c', '-d:headless', '-d:release', '-d:replayEvents', '--hints:off', '--out:' + str(RAW / 'bin' / name), str(dest)], cwd=ENGINE, env=dict(os.environ, POLYWORLD_DEPS=str(DEPS)), capture_output=True, text=True)
        (RAW / (name + '-build.log')).write_text(proc.stdout + proc.stderr)
        assert proc.returncode == 0, proc.stderr[-2000:]
        print(name + ' built', flush=True)

    with ThreadPoolExecutor(2) as pool:
        list(pool.map(build, sources.items()))
    for label, policy in [('baseline', PARENT / 'policy.bas'), ('explicit-sustain', RAW / 'explicit-sustain/policy.bas')]:
        proc = subprocess.run([str(RAW / 'bin/practice')], cwd=ENGINE, env=dict(os.environ, AUDIT_POLICY=str(policy)), capture_output=True, text=True, timeout=300)
        (RAW / (label + '-practice.log')).write_text(proc.stdout + proc.stderr)
        assert proc.returncode == 0, proc.stderr[-2000:]
        write(RAW / (label + '-practice.json'), json.loads(proc.stdout.splitlines()[-1]))
        print(label + ' practice finished', flush=True)
    pair = RAW / 'explicit-sustain'
    for mode in ['compile', 'extract']:
        out = RAW / 'conversion-check' / mode
        if not out.exists():
            args = [sys.executable, str(pair / 'convert.py'), mode, '--out', str(out)]
            if mode == 'extract':
                args += ['--source', str(pair / 'policy.bas')]
            subprocess.run(args, check=True, capture_output=True, text=True)
        assert (out / 'policy.bas').read_bytes() == (pair / 'policy.bas').read_bytes()
        assert json.loads((out / 'policy.ir.json').read_text()) == json.loads((pair / 'policy.ir.json').read_text())
    write(RAW / 'runtime-provenance.json', {'engine_commit': COMMIT, 'dependencies': deps, 'sources': {str(p.relative_to(ROOT)): sha(p) for p in sources.values()}, 'binaries': {p.name: sha(p) for p in (RAW / 'bin').iterdir()}, 'compile_extract_equal': True})


if __name__ == '__main__':
    main()
