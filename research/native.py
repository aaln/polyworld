"""Paired responsive reference games, both colors and first/final team seats."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import hashlib
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT.parent / 'polyworld/tmp/gota-weak-neutral62-20260924'
ENGINE = ROOT
SOURCES = {k:ROOT/'research/policies'/k/'policy.bas' for k in ['deployed','previous','weak-neutral']}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    game = json.loads((RAW / 'game.json').read_text())
    config = {k: v for k, v in game['manifest']['variants'][0]['game_config'].items() if k not in ['players', 'tokens', 'seed']}
    write(RAW / 'game-config.json', config)
    reference = ENGINE / 'examples/gods_of_the_arena/players/base.bas'
    cases = [{'name': name, 'side': side, 'ordinal': ordinal, 'seed': seed} for name in SOURCES for side in range(2) for ordinal in [0, 4] for seed in [9240620]]
    plan = {'cases': cases, 'source_hashes': {k:sha(v) for k,v in SOURCES.items()}, 'upstream_source_sha256': sha(reference), 'scope': 'Twelve fresh replay62 native games; deployed, previous, weak-neutral; one subject, nine responsive current reference VMs; two sides and two seats, one matched seed. Runtime/mechanism screen only.'}
    path = RAW / 'native-plan-with-hashes.json'
    if path.exists():
        assert json.loads(path.read_text()) == plan
    else:
        write(path, plan)

    def run(case):
        slot = case['side'] * 5 + case['ordinal']
        out = RAW / 'native' / case['name'] / f"side{case['side']}-seat{case['ordinal']}-{case['seed']}"
        out.mkdir(parents=True, exist_ok=True)
        if (out / 'result.json').exists():
            return json.loads((out / 'result.json').read_text())
        subject = SOURCES[case['name']]
        roster = [subject if i == slot else reference for i in range(10)]
        binary = RAW / 'bin/episode'
        command = [str(binary), '--config', str(RAW / 'game-config.json'), '--seed', str(case['seed']), '--record', str(out / 'replay.bin')] + ['--bot:' + str(p) + ':1' for p in roster]
        write(out / 'command.json', command)
        proc = subprocess.run(command, cwd=ENGINE, capture_output=True, text=True, timeout=300)
        (out / 'run.log').write_text(proc.stdout + proc.stderr)
        assert proc.returncode == 0, proc.stderr[-2000:]
        live = json.loads(proc.stdout.splitlines()[-1])
        write(out / 'live.json', live)
        proc = subprocess.run([str(binary), '--replay', str(out / 'replay.bin')], cwd=ENGINE, capture_output=True, text=True, timeout=300)
        (out / 'replay.log').write_text(proc.stdout + proc.stderr)
        assert proc.returncode == 0, proc.stderr[-2000:]
        replay = json.loads(proc.stdout.splitlines()[-1])
        write(out / 'replay.json', replay)
        for key in ['ticks', 'state_hash', 'actions', 'commands', 'fort_hp', 'winner']:
            assert live[key] == replay[key], key
        assert replay['hash_mismatches'] == 0
        assert len({h['class'] for h in live['heroes']}) == 10
        for h in live['heroes']:
            assert h['max_instructions'] <= 19000 and h['max_work'] <= 50000
            assert h['score'] == max(0, h['xp'] * 1440 - 200 * live['ticks']) // 1440
        result = {**case, 'valid': True, 'ticks': live['ticks'], 'subject': live['heroes'][slot], 'replay_sha256': sha(out / 'replay.bin'), 'hash_mismatches': 0}
        write(out / 'result.json', result)
        print(json.dumps({**case, 'passed': True, 'ticks': live['ticks']}), flush=True)
        return result

    with ThreadPoolExecutor(2) as pool:
        rows = list(pool.map(run, cases))
    assert all(r['valid'] for r in rows) and len(rows) == 12
    write(RAW / 'native-comparison.json', {'passed':True,'games':12,'source_hashes':plan['source_hashes'],'score_totals':{k:sum(r['subject']['score'] for r in rows if r['name']==k) for k in SOURCES},'scope':plan['scope']})
    write(RAW / 'native-result.json', {'passed': True, 'games': 12, 'rows': rows, 'scope': plan['scope'], 'new_hosted_games': 0})


if __name__ == '__main__':
    main()
