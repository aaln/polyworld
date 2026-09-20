"""Insert qualified repair probes at a drained boundary, then resume full sweep.

Never cancel remote games. Freeze only the known parent orchestrator while its
collectors finish. Exact original receipts/rosters remain resumable.
"""
import os
import signal
import subprocess
import sys
import time

from policy_ir import HERE,read,write
from release_workspace import RUN
from rush_sentries import STUDY as SWEEP
from rush_unblock import STUDY
LOCAL=STUDY/'local-safe'
from rush_unblock_hosted import prepare,run


def launch(argv,log):
    with log.open('a') as stream:
        return subprocess.Popen([sys.executable,'-u',*argv],cwd=HERE,
                                stdin=subprocess.DEVNULL,stdout=stream,stderr=stream,start_new_session=True)


def main(prepare_fn=prepare,run_fn=run,phase='repair320',local_dir=LOCAL,study=STUDY):
    comparison=read(local_dir/'comparison.json')
    name=comparison['selected']
    if not name:raise ValueError('No qualified local repair')
    prepare_fn(name)
    current=read(SWEEP/'priority-resume.json')
    runner,finalizer=current['runner'],current['finalizer']
    command=subprocess.check_output(['ps','-p',str(runner),'-o','command='],text=True)
    if 'rush_league_sweep.py' not in command or str(SWEEP) not in command:
        raise ValueError('Refusing to pause an unexpected process')
    os.kill(runner,signal.SIGSTOP)
    paused=True; terminated=False
    write(study/'queue-state.json',{'stage':'draining_existing_sweep','runner':runner,'candidate':name})
    print('Holding new sweep submissions; existing games/collectors continue.',flush=True)
    try:
        while True:
            pending=[]
            for receipt in SWEEP.glob('**/batch/created.json'):
                folder=receipt.parent.parent
                n=read(receipt.with_name('request.json'))['num_episodes']
                path=folder/'audit-progress.json'
                if not path.exists() or read(path).get('verified')!=n:pending.append(str(folder))
            write(study/'queue-drain.json',{'pending':pending})
            if not pending:break
            print('Draining',len(pending),'active cohort(s)',flush=True)
            time.sleep(15)
        # No remote work is interrupted. The stopped process owns no unfinished
        # collector work; restart later from its idempotent request receipts.
        os.kill(finalizer,signal.SIGTERM)
        os.kill(runner,signal.SIGKILL)
        terminated=True;paused=False
        write(study/'queue-state.json',{'stage':phase,'prior_runner':runner,'candidate':name})
        run_fn(name)
    finally:
        if paused:
            os.kill(runner,signal.SIGCONT)
        elif terminated:
            resumed=launch(['rush_league_sweep.py',str(SWEEP),'long_three'],SWEEP/'xp-sweep.log')
            fin=launch(['rush_sweep_finalize.py',str(SWEEP),'--runner-pid',str(resumed.pid)],SWEEP/'finalize.log')
            info={'runner':resumed.pid,'finalizer':fin.pid,'reason':'Resume unchanged fullsuite after priority replay-repair probes'}
            write(SWEEP/'priority-resume.json',info)
            write(study/'queue-state.json',info|{'stage':'original_sweep_resumed','candidate':name})
            state=read(RUN/'active-state.json')
            state.update(hosted_runner_pid=resumed.pid,hosted_finalizer_pid=fin.pid)
            write(RUN/'active-state.json',state)
            print('Original frozen fullsuite resumed:',info,flush=True)


if __name__=='__main__':
    if '--wait-local' in sys.argv:
        pid=read(STUDY/'confirmation-process.json')['pid']
        while not (LOCAL/'comparison.json').exists():
            try:os.kill(pid,0)
            except ProcessLookupError:raise RuntimeError('Local confirmation stopped before its comparison')
            time.sleep(15)
    main()
