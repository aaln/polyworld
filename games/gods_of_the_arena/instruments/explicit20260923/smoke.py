"""Four complete current-engine runtime checks; no rival or candidate claim."""
from concurrent.futures import ThreadPoolExecutor
import json
import subprocess
from check import RAW, ENGINE, POLICY, sha


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    game = json.loads((RAW / 'game.json').read_text())
    config = {k: v for k, v in game['manifest']['variants'][0]['game_config'].items() if k not in ['players', 'tokens', 'seed']}
    write(RAW / 'game-config.json', config)
    reference = ENGINE / 'examples/gods_of_the_arena/players/base.bas'
    cases = [{'side': side, 'ordinal': ordinal, 'seed': 9230600} for side in range(2) for ordinal in [0, 3]]
    plan = {'cases': cases, 'own_source_sha256': sha(POLICY), 'upstream_source_sha256': sha(reference), 'scope': 'One incumbent subject and nine responsive updated upstream VMs; four complete runtime/parity checks, not a competitive comparison.'}
    path = RAW / 'smoke-plan.json'
    if path.exists():
        assert json.loads(path.read_text()) == plan
    else:
        write(path, plan)

    def run(case):
        slot = case['side'] * 5 + case['ordinal']
        out = RAW / 'smoke' / f"side{case['side']}-seat{case['ordinal']}"
        out.mkdir(parents=True, exist_ok=True)
        roster = [POLICY if i == slot else reference for i in range(10)]
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
    write(RAW / 'smoke.json', {'passed': True, 'games': 4, 'rows': rows, 'scope': plan['scope'], 'new_hosted_games': 0})


if __name__ == '__main__':
    main()
