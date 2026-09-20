"""Reconstruct g002 red failures and successful comparison games on one clock."""
from concurrent.futures import ThreadPoolExecutor
import json
import subprocess

from league_threat_review import run_native
from policy_ir import read, write, digest
from release_workspace import RUN, ROOT
from threat_coverage_hosted import control
from win_replay_review import plot

STUDY = RUN / 'coached-lanes/r5-g002-coordination'
H = RUN / 'coached-lanes/r5-anchored-support'
A = RUN / 'coached-lanes/r5-ally-assist'
G = RUN / 'coached-lanes/r5-jordan-lineup'


def rows(root):
    return next(iter(read(root / 'result.json')['rivals'].values()))['rows']


def tape(root, row):
    key = read(root / 'plan.json')['rival_key']
    p = root / key / row['color'] / 'artifacts' / row['episode'] / 'replay.bin'
    if digest(p.read_bytes()) != row['replay_sha256']:
        raise ValueError('Replay changed')
    return p


def order(path):
    out = subprocess.run([str(RUN / 'r5/initial-turn-probe'), '--replay', str(path)],
                         cwd=ROOT, text=True, capture_output=True, check=True)
    return json.loads(out.stdout)['initial_vm_slot']


def main():
    out = STUDY / 'review'; out.mkdir(parents=True, exist_ok=True)
    head = H / 'hosted/anchor/g002'
    losses = sorted((r for r in rows(head) if r['color'] == 'red' and r['loss']),
                    key=lambda r: (r['ticks'], r['episode']))
    first = losses[0]; target_order = order(tape(head, first))
    cases = [('anchor-fast-loss', head, first, H / 'local/candidates/anchor/policy.bas'),
             ('anchor-median-loss', head, losses[len(losses)//2], H / 'local/candidates/anchor/policy.bas')]
    for label, root, source in (
            ('all-role-assist-win', A / 'hosted/assist22/preservation/g002', A / 'local/candidates/assist22/policy.bas'),
            ('deployed-win', control('gota-g002:v1'), G / 'candidate/policy.bas')):
        wins = sorted((r for r in rows(root) if r['color'] == 'red' and r['win']), key=lambda r:r['episode'])
        matching = [r for r in wins if order(tape(root, r)) == target_order]
        cases.append((label, root, (matching or wins)[0], source))
    selection = []
    for label, root, row, source in cases:
        selection.append({'name': label, 'root': str(root), 'row': row,
            'tape': str(tape(root, row)), 'initial_vm_slot': order(tape(root, row)),
            'source': str(source), 'source_sha256': digest(source.read_bytes())})
    write(out / 'selection.json', {'cases': selection,
        'selection': 'Fastest and median-duration anchor red loss; first lexicographic red wins from all-role assistance and deployed controls, preferring the fastest-loss initial VM order when available.',
        'scope': 'Actual complete replay comparisons. Matching initial order is not a matched full RNG stream. No counterfactual winner or causal effect inferred.'})

    def one(case):
        from pathlib import Path
        folder = out / case['name']; folder.mkdir(exist_ok=True)
        replay = Path(case['tape'])
        decoded = folder / 'decoded.jsonl'
        summary = run_native('macro-replay-v5', replay, decoded)
        binary = 'replay-assist-context-probe' if 'aaCommitted' in Path(case['source']).read_text() else 'replay-slots-probe'
        proof = run_native(binary, replay, folder / 'decisions.jsonl',
                           {'PROBE_POLICY': case['source'], 'PROBE_SLOTS': '0,1,2,3,4'})
        if summary['hash_mismatches'] or not proof['all_state_hashes_equal'] or not proof['all_actions_consumed']:
            raise ValueError('Incomplete replay')
        write(folder / 'proof.json', proof)
        frames = []; header = None
        for line in decoded.open():
            r = json.loads(line)
            if r['type'] == 'header': header = r
            elif r['type'] == 'frame':
                for hero in r['heroes']: hero.pop('visible_post_tick', None)
                frames.append(r)
        view = case | {'header': header, 'frames': frames, 'summary': summary}
        write(folder / 'view.json', view)
        print(case['name'], case['row']['episode'], proof['ticks'], 'all commands verified', flush=True)
        return view

    with ThreadPoolExecutor(2) as pool:
        views = list(pool.map(one, selection))
    plot(views, out / 'g002-recorded-positions.png',
         'gota-g002 red-side review — actual recorded positions',
         'Red: our heroes. Blue: g002. Each row is a different game; initial-order matching is not matched RNG.')


if __name__ == '__main__':
    main()
