"""Insert qualified recall probes at a drained wide-suite boundary, then resume."""
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from jordan_lineup_wide import ROOT as WIDE
from policy_ir import HERE, digest, read, write
from ranger_guard import STUDY
from ranger_guard_hosted import prepare, run


def alive(pid):
    try: os.kill(pid, 0)
    except ProcessLookupError: return False
    return True


def main(diagnostic=False):
    while not (STUDY / 'local/comparison.json').exists():
        if not alive(read(STUDY / 'local-process.json')['pid']):
            raise RuntimeError('Local recall study stopped without a verdict')
        time.sleep(15)
    comparison = read(STUDY / 'local/comparison.json')
    if not diagnostic and not comparison['selected']:
        print('No qualified local recall variant; no hosted requests.', flush=True)
        return
    names = ['arrival12'] if diagnostic else comparison['qualified']
    conditional = {'ordered_candidates': names,
                   'diagnostic_only': diagnostic,
                   'rule': 'Primary fresh80mixed candidate vs fresh80deployed; if mixed fails, next locally qualified variant reuses the same80control. If mixed passes, require38/40 percolor in80freshJordan games. Stop after one passes both; no automatic deployment. Maximum400newgames for two mixed candidates and two Jordan probes plus sharedcontrol80.'}
    if diagnostic:
        conditional['rule'] = ('Mechanism diagnostic despite explicitly failed original local absolute gate. '
            'One arrival12 candidate: fresh80mixed vs fresh80deployed. Only if mixed passes,80freshJordan. '
            'Maximum240newgames. No second candidate, no automatic deployment, no relabeling of original failed qualification.')
    path = STUDY / ('hosted-diagnostic-conditional-plan.json' if diagnostic else 'hosted-conditional-plan.json')
    if path.exists() and read(path) != conditional: raise ValueError('Conditional plan changed')
    write(path, conditional)
    prepare(names[0], diagnostic=diagnostic)  # Inert uploads and validated dry-runs only.
    runner = read(WIDE / 'process.json')['pid']
    paused = terminated = False
    if alive(runner):
        command = subprocess.check_output(['ps', '-p', str(runner), '-o', 'command='], text=True)
        if 'jordan_lineup_wide.py run' not in command: raise ValueError('Unexpected wide controller')
        os.kill(runner, signal.SIGSTOP); paused = True
    elif not (WIDE / 'result.json').exists():
        raise RuntimeError('Wide controller stopped unexpectedly; reconcile before priority research')
    try:
        write(STUDY / 'queue-state.json', {'stage': 'draining_current_wide_arm', 'prior_runner': runner})
        while True:
            pending = []
            for receipt in WIDE.glob('**/batch/created.json'):
                folder = receipt.parent.parent
                n = read(receipt.with_name('request.json'))['num_episodes']
                if not (folder / 'audit-progress.json').exists() or read(folder / 'audit-progress.json').get('verified') != n:
                    pending.append(str(folder))
            write(STUDY / 'queue-drain.json', {'pending': pending})
            if not pending: break
            time.sleep(15)
        if paused:
            os.kill(runner, signal.SIGKILL); paused = False; terminated = True
        results = {}; selected = None
        for name in names:
            write(STUDY / 'queue-state.json', {'stage': 'hosted_recall', 'candidate': name})
            result = run(name, diagnostic=diagnostic); results[name] = {'mixed': {k: v for k, v in result.items() if k != 'arms'}}
            jordan = STUDY / 'hosted' / name / 'jordan-result.json'
            if jordan.exists(): results[name]['jordan'] = read(jordan)
            if result['passed'] and jordan.exists() and read(jordan)['passed']:
                selected = name; break
        write(STUDY / 'hosted-comparison.json', {'selected': selected, 'results': results, 'diagnostic_only': diagnostic,
              'scope': 'Targeted mixed recall and Jordan preservation only; broad field remains necessary.'})
    finally:
        if paused: os.kill(runner, signal.SIGCONT)
        elif terminated:
            with (WIDE / 'run.log').open('a') as stream:
                resumed = subprocess.Popen([sys.executable, '-u', 'jordan_lineup_wide.py', 'run'], cwd=HERE,
                    stdin=subprocess.DEVNULL, stdout=stream, stderr=stream, start_new_session=True)
            write(WIDE / 'process.json', {'pid': resumed.pid, 'command': 'jordan_lineup_wide.py run',
                  'plan_sha256': digest((WIDE / 'plan.json').read_bytes()), 'reason': 'Resume unchanged broad suite after drained recall probes'})
            write(STUDY / 'queue-state.json', {'stage': 'wide_suite_resumed', 'runner': resumed.pid})
            print('Unchanged broad suite resumed:', resumed.pid, flush=True)


if __name__ == '__main__': main(diagnostic='--diagnostic' in sys.argv[1:])
