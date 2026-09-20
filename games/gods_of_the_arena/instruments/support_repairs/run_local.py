"""Run and fully audit the frozen local screen; preserve every failure."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
from prepare import ROOT, STUDY, digest, read, write

BIN = ROOT.parent / 'gota-research-20260916/r5/fast'


def run(item):
    name, case, plan = item
    folder = STUDY / 'local' / name / str(case['seed'])
    folder.mkdir(parents=True, exist_ok=True)
    if (folder / 'result.json').exists():
        return read(folder / 'result.json')
    source = Path(plan['sources'][name])
    other = Path(plan['opponents'][case['opponent']])
    command = [str(BIN / 'episode'), '--config', str(STUDY / 'config.json'),
               '--seed', str(case['seed']), '--record', str(folder / 'replay.bin')]
    command += ['--bot:' + str(source if i // 5 == case['side'] else other) for i in range(10)]
    try:
        if not (folder / 'process.json').exists():
            with (folder / 'stdout.log').open('w') as out, (folder / 'stderr.log').open('w') as err:
                proc = subprocess.run(command, stdout=out, stderr=err, timeout=900)
            write(folder / 'process.json', {'command': command, 'returncode': proc.returncode})
        assert read(folder / 'process.json')['returncode'] == 0
        assert not (folder / 'stderr.log').read_text().strip()
        actual = json.loads((folder / 'stdout.log').read_text().splitlines()[-1])
        if not (folder / 'audit.json').exists():
            proc = subprocess.run([str(BIN / 'audit-hosted'), '--replay', str(folder / 'replay.bin')],
                                  capture_output=True, text=True, check=True, timeout=900)
            write(folder / 'audit.json', json.loads(proc.stdout))
        proof = read(folder / 'audit.json')
        assert actual['ticks'] == proof['recorded_ticks'] == proof['ticks']
        assert actual['actions'] == proof['recorded_actions'] == proof['actions_consumed']
        assert actual['state_hash'] == proof['state_hash'] and proof['hash_mismatches'] == 0
        assert len(actual['heroes']) == len(proof['heroes']) == 10
        assert [h['score'] for h in actual['heroes']] == [h['score'] for h in proof['heroes']]
        assert all(h['max_instructions'] <= 20000 and h['max_work'] <= 50000 for h in actual['heroes'])
        ours = proof['heroes'][case['side'] * 5:case['side'] * 5 + 5]
        scores = {h['score'] for h in ours}
        assert len(scores) == 1 and next(iter(scores)) in (0, 1)
        result = {'candidate': name, **case, 'valid': True, 'win': next(iter(scores)),
                  'ticks': actual['ticks'], 'deaths': sum(h['deaths'] for h in ours),
                  'gear_heroes': sum(h['first_gear_tick'] >= 0 for h in ours),
                  'all_replay_hashes_actions_budgets': True,
                  'max_instructions': max(h['max_instructions'] for h in actual['heroes']),
                  'max_work': max(h['max_work'] for h in actual['heroes']),
                  'source_sha256': digest(source.read_bytes()),
                  'replay_sha256': digest((folder / 'replay.bin').read_bytes()),
                  'audit_sha256': digest((folder / 'audit.json').read_bytes())}
    except Exception as exc:
        result = {'candidate': name, **case, 'valid': False, 'error': repr(exc),
                  'scope': 'Invalid runtime/evidence, not a gameplay loss; all files preserved.'}
    write(folder / 'result.json', result)
    print(json.dumps(result), flush=True)
    return result


def main():
    plan = read(STUDY / 'plan.json')
    assert read(STUDY / 'vm-proof.json')['passed']
    for path, expected in plan['inputs_sha256'].items():
        assert digest(Path(path).read_bytes()) == expected, path
    write(STUDY / 'local-runtime-provenance.json', {
        'started_at': datetime.now(timezone.utc).isoformat(),
        'episode_sha256': digest((BIN / 'episode').read_bytes()),
        'auditor_sha256': digest((BIN / 'audit-hosted').read_bytes())})
    # Keep one native game active so the existing research worker retains capacity.
    with ThreadPoolExecutor(max_workers=1) as pool:
        rows = list(pool.map(run, [(name, case, plan) for case in plan['cases'] for name in plan['sources']]))
    write(STUDY / 'local-results.json', {'rows': rows, 'complete': len(rows) == 24,
                                        'scope': plan['scope']})


if __name__ == '__main__':
    main()
