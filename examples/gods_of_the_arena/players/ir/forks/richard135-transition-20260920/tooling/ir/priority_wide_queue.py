"""Hand off a serial hosted queue only after created cohorts finish auditing."""
from contextlib import contextmanager
import os
import signal
import subprocess
import sys
import time
from jordan_lineup_wide import ROOT as WIDE
from policy_ir import HERE, digest, read, write
from ranger_guard_queue import alive


@contextmanager
def drained_wide(study):
    runner = read(WIDE/'process.json')['pid']; paused = terminated = False
    if alive(runner):
        cmd = subprocess.check_output(['ps','-p',str(runner),'-o','command='],text=True)
        if 'jordan_lineup_wide.py run' not in cmd: raise ValueError('Unexpected broad controller')
        os.kill(runner,signal.SIGSTOP); paused = True
    elif not (WIDE/'result.json').exists(): raise RuntimeError('Reconcile stopped broad controller')
    try:
        write(study/'queue-state.json',{'stage':'draining_wide','runner':runner})
        while True:
            pending = []
            for receipt in WIDE.glob('**/batch/created.json'):
                folder = receipt.parent.parent; n = read(receipt.with_name('request.json'))['num_episodes']
                if not (folder/'audit-progress.json').exists() or read(folder/'audit-progress.json').get('verified') != n:
                    pending.append(str(folder))
            write(study/'queue-drain.json',{'pending':pending})
            if not pending: break
            time.sleep(15)
        if paused:
            os.kill(runner,signal.SIGKILL); paused = False; terminated = True
        yield
    finally:
        if paused: os.kill(runner,signal.SIGCONT)
        elif terminated:
            with (WIDE/'run.log').open('a') as f:
                p = subprocess.Popen([sys.executable,'-u','jordan_lineup_wide.py','run'],cwd=HERE,
                    stdin=subprocess.DEVNULL,stdout=f,stderr=f,start_new_session=True)
            write(WIDE/'process.json',{'pid':p.pid,'command':'jordan_lineup_wide.py run',
                'plan_sha256':digest((WIDE/'plan.json').read_bytes()),'reason':'Resume unchanged broad suite after '+study.name})
            write(study/'queue-state.json',{'stage':'wide_resumed','runner':p.pid})
            print('Broad suite resumed',p.pid,flush=True)
