"""Fresh80Jordan test after exact per-color gameplay preservation checks."""
import os,time,shutil
import jordan_root_hosted as hosted
from jordan_lineup import STUDY,PRIOR
from policy_ir import read,write
from rush_sentries import STUDY as BASE
from rush_unblock_queue import main

if __name__=='__main__':
    while not (STUDY/'local/comparison.json').exists():
        pid=read(STUDY/'local-process.json')['pid']
        try:os.kill(pid,0)
        except ProcessLookupError:raise RuntimeError('Local parity stopped')
        time.sleep(15)
    candidate=STUDY/'local/candidates/blue_repair'
    if not candidate.exists():shutil.copytree(STUDY/'candidate',candidate)
    # The existing priority queue owns remote pacing until it drains/resumes.
    while read(PRIOR/'queue-state.json')['stage']!='original_sweep_resumed':
        pid=read(PRIOR/'xp-process.json')['pid']
        try:os.kill(pid,0)
        except ProcessLookupError:raise RuntimeError('Prior queue stopped without safe resume')
        time.sleep(15)
    hosted.STUDY=STUDY
    write(STUDY/'hosted-plan.json',{'new_games':80,'episodes_per_color':40,'red_minimum':38,'blue_minimum':30,'reference':'Exact deployed red and release20blue; fresh hosted outcome, no inference from concatenating historical wins.'})
    if (BASE/'league-sweep/completed.json').exists():hosted.run_candidates('blue_repair')
    else:main(hosted.prepare,hosted.run_candidates,'jordan_lineup80',STUDY/'local',STUDY)
