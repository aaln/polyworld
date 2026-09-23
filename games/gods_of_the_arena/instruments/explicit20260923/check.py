"""Run bounded new-contract checks on the isolated published replay60 engine."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RAW = ROOT.parent / 'polyworld/tmp/gota-explicit60-20260923'
ENGINE = ROOT.parent / 'polyworld-gota-explicit60-20260923'
COMMIT = 'fd315c8fa30f8923c7a7709a577c40ac071b1c2a'
NIM = '/Users/aaln/.nimby/nim-2.2.10/bin/nim'
DEPS = RAW / 'deps'
POLICY = ROOT / 'examples/gods_of_the_arena/players/ir/forks/druid-lane20260923-hosted/druid-lane/policy.bas'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ENGINE, text=True).strip() == COMMIT
    assert not subprocess.check_output(['git', 'diff', COMMIT, '--', 'src', 'examples/gods_of_the_arena', 'coworld/dependencies.lock'], cwd=ENGINE, text=True)
    deps = {}
    for line in (ENGINE / 'coworld/dependencies.lock').read_text().splitlines():
        name, _, url, rev = line.split()
        assert subprocess.check_output(['git', '-C', str(DEPS / name), 'rev-parse', 'HEAD'], text=True).strip() == rev
        deps[name] = rev
    assert sha(POLICY) == '29f6d7e67252a9cc32521e5a906ec33222a5e7e3b5e59b168db5c6b20c9c9e36'
    probe = ENGINE / 'examples/gods_of_the_arena/tools/explicit60_healing_probe.nim'
    probe.parent.mkdir(exist_ok=True)
    shutil.copyfile(HERE / 'healing_probe.nim', probe)
    episode = ENGINE / 'examples/gods_of_the_arena/tools/explicit60_episode.nim'
    shutil.copyfile(HERE.parent / 'productive20260923/episode59.nim', episode)
    sources = {name: ENGINE / 'tests' / (name + '.nim') for name in ['test_gota_attacks', 'test_gota_spells', 'test_gota_base']}
    sources.update(healing_probe=probe, episode=episode)
    (RAW / 'bin').mkdir(exist_ok=True)

    def run(item):
        name, source = item
        binary = RAW / 'bin' / name
        env = dict(os.environ, POLYWORLD_DEPS=str(DEPS), AUDIT_POLICY=str(POLICY))
        proc = subprocess.run([NIM, 'c', '-d:headless', '-d:release', '-d:replayEvents', '--hints:off', '--out:' + str(binary), str(source)], cwd=ENGINE, env=env, capture_output=True, text=True)
        (RAW / (name + '-build.log')).write_text(proc.stdout + proc.stderr)
        assert proc.returncode == 0, (name, proc.stderr[-2200:])
        if name != 'episode':
            proc = subprocess.run([str(binary)], cwd=ENGINE, env=env, capture_output=True, text=True, timeout=180)
            (RAW / (name + '-run.log')).write_text(proc.stdout + proc.stderr)
            assert proc.returncode == 0, (name, proc.stdout[-1800:], proc.stderr[-1800:])
            if name == 'healing_probe':
                (RAW / 'healing-probe.json').write_text(json.dumps(json.loads(proc.stdout.splitlines()[-1]), indent=2) + '\n')
        print(name + ' passed', flush=True)
        return {'name': name, 'source': str(source), 'source_sha256': sha(source), 'binary_sha256': sha(binary), 'executed': name != 'episode', 'passed': True}

    with ThreadPoolExecutor(2) as pool:
        rows = list(pool.map(run, sources.items()))
    proof = {'engine_commit': COMMIT, 'replay_version': 60, 'dependencies': deps, 'source_sha256': sha(POLICY), 'checks': rows, 'new_hosted_games': 0}
    (RAW / 'checks.json').write_text(json.dumps(proof, indent=2) + '\n')


if __name__ == '__main__':
    main()
