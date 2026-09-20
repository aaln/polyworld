"""Wait for recall diagnostic, then run pressure probes at a drained boundary."""
import os
import signal
import subprocess
import sys
import time
from jordan_lineup_wide import ROOT as WIDE
from policy_ir import HERE, digest, read, write
from ranger_guard import STUDY as RECALL
from ranger_guard_queue import alive
from ranger_guard_hosted import freeze
from red_pressure import STUDY
from red_pressure_hosted import control_path, prepare, run


def main():
    plan = {'maximum_candidates': 2, 'rules': {'black_kite_red_gain': 20, 'black_kite_red_absolute': 20,
            'black_kite_maximum_blue_loss': 2, 'black_kite_maximum_new_losses': 2, 'jordan_minimum_each_color': 38},
            'design': 'Wait for local nonregression and complete recall diagnostic. Reuse the80already-planned blue_repair black-kite13 games as control. '
            'Test the first locally qualified pressure variant80; if black-kite fails, try second80. If black-kite passes, require80Jordan with38wins/color. '
            'Stop after one passes both. Maximum320newcandidate games plus80already-budgeted broad control games. No automatic deployment; field tests remain necessary.'}
    freeze(STUDY / 'hosted-prospective-plan.json', plan)
    while not (STUDY / 'local/comparison.json').exists():
        if not alive(read(STUDY / 'local-process.json')['pid']): raise RuntimeError('Pressure local study stopped without verdict')
        time.sleep(15)
    choices = read(STUDY / 'local/comparison.json')['qualified'][:2]
    if not choices:
        print('No pressure local qualifier; no hosted requests.', flush=True); return
    while alive(read(RECALL / 'diagnostic-hosted-process.json')['pid']): time.sleep(15)
    if not (RECALL / 'hosted-comparison.json').exists(): raise RuntimeError('Recall controller stopped without reconciled completion')
    freeze(STUDY / 'hosted-selection.json', {'choices': choices, 'local_sha256': digest((STUDY / 'local/comparison.json').read_bytes()),
                                          'reused_control': str(control_path())})
    prepare(choices[0])
    runner = read(WIDE / 'process.json')['pid']; paused = terminated = False
    if alive(runner):
        cmd = subprocess.check_output(['ps', '-p', str(runner), '-o', 'command='], text=True)
        if 'jordan_lineup_wide.py run' not in cmd: raise ValueError('Unexpected broad controller')
        os.kill(runner, signal.SIGSTOP); paused = True
    elif not (WIDE / 'result.json').exists(): raise RuntimeError('Broad controller requires reconciliation')
    try:
        write(STUDY / 'queue-state.json', {'stage': 'draining_wide', 'runner': runner})
        while True:
            pending = []
            for receipt in WIDE.glob('**/batch/created.json'):
                folder = receipt.parent.parent; n = read(receipt.with_name('request.json'))['num_episodes']
                if not (folder / 'audit-progress.json').exists() or read(folder / 'audit-progress.json').get('verified') != n:
                    pending.append(str(folder))
            write(STUDY / 'queue-drain.json', {'pending': pending})
            if not pending: break
            time.sleep(15)
        if paused:
            os.kill(runner, signal.SIGKILL); paused = False; terminated = True
        results = {}; selected = None
        for name in choices:
            write(STUDY / 'queue-state.json', {'stage': 'hosted_pressure', 'candidate': name})
            r = run(name); results[name] = {'black_kite_passed': r['passed'], 'checks': r['checks']}
            jp = STUDY / 'hosted' / name / 'jordan-result.json'
            if jp.exists(): results[name]['jordan_passed'] = read(jp)['passed']
            if r['passed'] and jp.exists() and read(jp)['passed']:
                selected = name; break
        write(STUDY / 'hosted-comparison.json', {'selected': selected, 'results': results,
                'scope': 'Targeted black-kite/Jordan evidence only; broad field required before promotion.'})
    finally:
        if paused: os.kill(runner, signal.SIGCONT)
        elif terminated:
            with (WIDE / 'run.log').open('a') as f:
                p = subprocess.Popen([sys.executable, '-u', 'jordan_lineup_wide.py', 'run'], cwd=HERE,
                    stdin=subprocess.DEVNULL, stdout=f, stderr=f, start_new_session=True)
            write(WIDE / 'process.json', {'pid': p.pid, 'command': 'jordan_lineup_wide.py run',
                  'plan_sha256': digest((WIDE / 'plan.json').read_bytes()), 'reason': 'Resume unchanged broad suite after pressure challenge'})
            write(STUDY / 'queue-state.json', {'stage': 'wide_resumed', 'runner': p.pid})
            print('Broad suite resumed', p.pid, flush=True)


if __name__ == '__main__': main()
