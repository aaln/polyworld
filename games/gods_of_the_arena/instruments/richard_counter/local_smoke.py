"""Complete and reconcile six native runtime smokes; not matchup validation."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
STUDY = ROOT / 'tmp/gota-ir/richard-counter-20260920'
BIN = ROOT.parent / 'gota-research-20260916/r5/fast'
DEFAULT = ROOT.parent / 'polyworld-gota-clean-20260916-r5/examples/gods_of_the_arena/players/base.bas'

def run(item):
    name, side = item
    folder = STUDY / 'local-runtime' / name / str(side)
    folder.mkdir(parents=True, exist_ok=True)
    source = STUDY / 'candidates' / name / 'policy.bas'
    if not (folder / 'stdout.log').exists():
        command = [str(BIN / 'episode'), '--config', str(STUDY / 'local-config.json'),
            '--seed', '920260', '--record', str(folder / 'replay.bin')]
        command += ['--bot:' + str(source if i//5 == side else DEFAULT) for i in range(10)]
        with (folder / 'stdout.log').open('w') as out, (folder / 'stderr.log').open('w') as err:
            p = subprocess.run(command, stdout=out, stderr=err)
        (folder / 'process.json').write_text(json.dumps({'returncode': p.returncode, 'command': command})+'\n')
        p.check_returncode()
    actual = json.loads((folder / 'stdout.log').read_text().splitlines()[-1])
    audit = folder / 'audit-hosted.json'
    if not audit.exists():
        p = subprocess.run([str(BIN / 'audit-hosted'), '--replay', str(folder / 'replay.bin')], capture_output=True, text=True, check=True)
        audit.write_text(p.stdout)
    proof = json.loads(audit.read_text())
    assert actual['ticks'] == proof['recorded_ticks'] == proof['ticks']
    assert actual['actions'] == proof['recorded_actions'] == proof['actions_consumed']
    assert actual['state_hash'] == proof['state_hash'] and proof['hash_mismatches'] == 0
    assert len(actual['heroes']) == len(proof['heroes']) == 10
    assert [h['score'] for h in actual['heroes']] == [h['score'] for h in proof['heroes']]
    assert all(h['max_instructions'] <= 20000 and h['max_work'] <= 50000 for h in actual['heroes'])
    assert not (folder/'stderr.log').read_text().strip()
    row = {'candidate': name, 'side': side, 'ticks': actual['ticks'], 'winner': actual['winner'],
        'all_replay_hashes_and_actions': True, 'all_ten_vm_budgets': True,
        'max_instructions': max(h['max_instructions'] for h in actual['heroes']),
        'max_work': max(h['max_work'] for h in actual['heroes']),
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'audit_sha256': hashlib.sha256(audit.read_bytes()).hexdigest(),
        'scope': 'One local default-opponent runtime smoke. No Richard/Jordan performance claim.'}
    print(json.dumps(row), flush=True)
    return row

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(run, [(n,s) for n in ('critical40','critical60','weapon') for s in (0,1)]))
    (STUDY/'local-runtime-proof.json').write_text(json.dumps(results,indent=2)+'\n')
