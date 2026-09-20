"""Pace the exact ten-player A/B after the current fixed-policy repair suite."""
import os,time
from policy_ir import read
from mixed_backdoor import STUDY
from mixed_backdoor_hosted import prepare,run
from rush_unblock import STUDY as PRIOR
from rush_unblock_queue import main as insert


if __name__=='__main__':
    pid=read(STUDY/'confirmation-process.json')['pid']
    while not (STUDY/'local/comparison.json').exists():
        try:os.kill(pid,0)
        except ProcessLookupError:raise RuntimeError('Mixed local confirmation stopped; inspect logs before launching')
        time.sleep(15)
    if not read(STUDY/'local/comparison.json')['selected']:
        raise ValueError('No local mixed-backdoor qualifier')
    prepare()  # Inert registration and dry-run only; no concurrent XP launch.
    while not (PRIOR/'queue-state.json').exists() or read(PRIOR/'queue-state.json')['stage']!='original_sweep_resumed':
        time.sleep(15)
    insert(lambda _:prepare(),lambda _:run(),'mixed_backdoor160',STUDY/'local',STUDY)
