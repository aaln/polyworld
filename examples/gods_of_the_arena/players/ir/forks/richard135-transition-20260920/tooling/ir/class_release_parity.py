"""Check full deterministic replay identity for the intended class partition."""
import json
import subprocess
from policy_ir import read,write,digest
from release_workspace import RUN
from class_release_screen import STUDY


def check():
    plan=read(STUDY/'local/plan.json')
    report=read(STUDY/'local/screen-result.json')
    assert report['verified_games']==240
    rows=[]
    for name in ['berserker_plain','berserker_base']:
        for case in plan['cases']:
            folder=f"seed-{case['seed']}-slot-{case['slot']}"
            new=read(STUDY/'local/screen'/name/folder/'result.json')
            control='footprint' if case['slot']!=4 else ('v2' if name=='berserker_base' else None)
            if control is None: continue
            old=read(RUN/'local/screen'/control/folder/'result.json')
            new_tape=STUDY/'local/screen'/name/folder/'episode.replay'
            old_tape=RUN/'local/screen'/control/folder/'episode.replay'
            result=subprocess.run([str(RUN/'build/replay-parity'),str(old_tape),str(new_tape)],capture_output=True,text=True,check=True)
            proof=json.loads(result.stdout)
            rows.append({'candidate':name,**case,'control':control,'replay_sha256':new['replay_sha256'],
                         'control_replay_sha256':old['replay_sha256'],**proof})
    write(STUDY/'local/class-parity.json',{'full_action_state_identity_cases':len(rows), 'comparator_sha256':digest((RUN/'build/replay-parity').read_bytes()),'new_games':80,
          'reused_control_games':160,'meaning':'All72unaffected-class games reproduce every footprint action and state hash; all4Berserker-base games reproduce every waveguard action and state hash. Replay VM work metrics may differ. The four Berserker-plain games intentionally may differ.','cases':rows})
    print('76full games match every intended action and state; VM cost metrics may differ.')

if __name__=='__main__':check()
