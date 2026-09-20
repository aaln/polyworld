"""Backfill equivalent structured VM evidence for captured-log failures only."""
from pathlib import Path
import sys

from hosted_wave import client, get
from hosted_wave_audit import verify_vm_validity
from policy_ir import write


def main(directory):
    count = 0
    with client() as c:
        for path in sorted(directory.glob('**/artifacts/*/game.log')):
            if not path.read_text().startswith('Pod logs were not captured:'):
                continue
            folder = path.parent
            if not (folder / 'player-status.json').exists():
                write(folder / 'player-status.json', get(c,
                      f'/v2/episode-requests/{folder.name}/artifacts/player-status'))
            verify_vm_validity(folder)
            count += 1
    print(f'{count} captured-log failures have verified structured VM evidence; original logs retained.')


if __name__ == '__main__':
    main(Path(sys.argv[1]).resolve())
