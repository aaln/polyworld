"""Count distinct full per-hero command tapes in a completed hosted cohort.

Different seeds alone do not establish distinct gameplay. Equality is checked
with the native replay reader, comparing every tick and command for all heroes.
This measures command diversity, not independence of RNG or statistical trials.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess

from policy_ir import digest, read, write
from release_workspace import RUN


def inventory(directory):
    result = read(directory / 'result.json')
    binary = RUN / 'r5/rival-trajectory'
    outputs = {}
    for arm, metrics in result.get('arms', result.get('rivals', {})).items():
        tapes = {p.parent.name:p for p in (directory / arm).glob('**/artifacts/*/replay.bin')}
        rows = metrics['rows']
        category = 'class' if 'class' in rows[0] else 'color'
        if set(tapes) != {r['episode'] for r in rows}:
            raise ValueError('Episode inventory incomplete')
        def role(cls):
            groups = []
            for row in sorted((r for r in rows if r[category] == cls), key=lambda r:r['episode']):
                tape = tapes[row['episode']]
                if digest(tape.read_bytes()) != row['replay_sha256']:
                    raise ValueError('Replay changed')
                for group in groups:
                    rep = tapes[group['representative']]
                    proof = json.loads(subprocess.check_output([str(binary), str(rep), str(tape)], text=True))
                    if proof['all_per_hero_tick_commands_equal']:
                        group['members'].append(row['episode'])
                        break
                else:
                    ticks = row['ticks'] if 'ticks' in row else read(tape.parent / 'audit.json')['ticks']
                    groups.append({'representative':row['episode'], 'members':[row['episode']], 'ticks':ticks, 'win':row['win']})
            return cls, {'games':sum(len(g['members']) for g in groups), 'distinct_full_command_tapes':len(groups), 'groups':groups}
        with ThreadPoolExecutor(4) as pool:
            roles = dict(pool.map(role, sorted({r[category] for r in rows})))
        outputs[arm] = {'games':len(rows), 'distinct_full_command_tapes':sum(r['distinct_full_command_tapes'] for r in roles.values()), 'classes' if category == 'class' else 'colors':roles}
        print(arm, outputs[arm]['games'], outputs[arm]['distinct_full_command_tapes'], flush=True)
    write(directory / 'command-diversity.json', {
        'result_sha256':digest((directory / 'result.json').read_bytes()), 'instrument_sha256':digest(Path(__file__).read_bytes()),
        'native_comparator_sha256':digest(binary.read_bytes()), 'arms':outputs,
        'interpretation':'Exact all-hero command equality, grouped within subject class or rival lineup color. Distinct tapes are not necessarily statistically independent. Repeated deterministic lineups limit generalization of episode-level p-values; field evidence remains separate.'})


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory', type=Path)
    inventory(p.parse_args().directory.resolve())
