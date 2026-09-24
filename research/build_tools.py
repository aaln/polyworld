"""Build pinned-current-engine research tools without touching captured binaries."""
import argparse
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
TOOLS = {
    'episode': 'recovery_episode',
    'telemetry': 'recovery_telemetry',
    'own-probe': 'recovery_own_probe',
    'camp-income': 'recovery_camp_income',
    'practice': 'weak_neutral_practice',
}


def main():
    config = json.loads((ROOT / 'research/environment.json').read_text())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tool', choices=[*TOOLS, 'all'])
    parser.add_argument('--nim', default=config['nim'])
    parser.add_argument('--deps', default=os.environ.get('POLYWORLD_DEPS', config['dependency_root']))
    parser.add_argument('--out', type=Path, default=ROOT / 'research/.build')
    args = parser.parse_args()
    args.out = args.out.resolve()
    args.out.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, POLYWORLD_DEPS=str(Path(args.deps).resolve()))
    for name in TOOLS if args.tool == 'all' else [args.tool]:
        source = ROOT / 'examples/gods_of_the_arena/tools' / (TOOLS[name] + '.nim')
        subprocess.run([args.nim, 'c', '-d:headless', '-d:release', '-d:replayEvents',
                        '--hints:off', '--nimcache:' + str(args.out / ('cache-' + name)),
                        '--out:' + str(args.out / name), str(source)],
                       cwd=ROOT, env=env, check=True)
        print(args.out / name, flush=True)


if __name__ == '__main__':
    main()
