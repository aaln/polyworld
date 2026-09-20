"""Run the locally qualified isolated response against the exact mixed roster."""
import os,time,sys
from policy_ir import read
from mixed_isolated import STUDY
from mixed_backdoor_hosted import prepare,run
from rush_unblock import STUDY as PRIOR
from rush_unblock_queue import main as insert


if __name__=='__main__':
    if '--blue' in sys.argv:
        from mixed_blue import STUDY
    pid=read(STUDY/'confirmation-process.json')['pid']
    while not (STUDY/'local/comparison.json').exists():
        try:os.kill(pid,0)
        except ProcessLookupError:raise RuntimeError('Local isolated confirmation stopped; inspect preserved failures')
        time.sleep(15)
    if not read(STUDY/'local/comparison.json')['selected']:raise ValueError('No qualified isolated candidate')
    prepare(STUDY)
    while not (PRIOR/'queue-state.json').exists() or read(PRIOR/'queue-state.json')['stage']!='original_sweep_resumed':
        time.sleep(15)
    insert(lambda _:prepare(STUDY),lambda _:run(STUDY),'mixed_isolated160',STUDY/'local',STUDY)
