"""Paired responsive reference games, both colors and first/final team seats."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import hashlib
ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT.parent / 'polyworld/tmp/gota-harvest-value61-20260923'
ENGINE = ROOT.parent / 'polyworld-gota-control61-20260923'
POLICY = ROOT / 'examples/gods_of_the_arena/players/ir/forks/druid-lane20260923-hosted/druid-lane/policy.bas'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    game = json.loads((RAW / 'game.json').read_text())
    config = {k: v for k, v in game['manifest']['variants'][0]['game_config'].items() if k not in ['players', 'tokens', 'seed']}
    write(RAW / 'game-config.json', config)
    reference = ENGINE / 'examples/gods_of_the_arena/players/base.bas'
    cases = [{'name': name, 'side': side, 'ordinal': ordinal, 'seed': seed} for name in ['baseline', 'harvest-value'] for side in range(2) for ordinal in [2, 4] for seed in [9230630, 9230631]]
    plan = {'cases': cases, 'own_source_sha256': sha(POLICY), 'candidate_source_sha256': sha(RAW / 'harvest-value/policy.bas'), 'upstream_source_sha256': sha(reference), 'scope': 'Sixteen paired observations: eight previously captured exact-seed baseline controls plus eight new native harvest candidate games, one subject and nine current reference VMs. Matched seed/roster/slot/config with nine responsive current reference VMs; runtime evidence, not league qualification.'}
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
        subject = POLICY if case['name'] == 'baseline' else RAW / 'harvest-value/policy.bas'
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
    write(RAW / 'native-result.json', {'passed': True, 'games': 16, 'rows': rows, 'scope': plan['scope'], 'new_hosted_games': 0})


if __name__ == '__main__':
    main()
