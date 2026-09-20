"""Watch the red fixed-lineup Codex loss and bounded-pursuit successor win."""
import json
from pathlib import Path
import subprocess
from policy_ir import read,write,digest
from release_workspace import ROOT,RUN
from win_screen import STUDY
from win_replay_review import plot

def main():
    out=STUDY/'review';cases=[]
    for label,study in [('Lich',RUN/'lich-followup'),('bounded',STUDY)]:
        result=read(study/'rival-matchups/result.json')
        row=sorted((r for r in result['rivals']['codex_lanes']['rows'] if r['color']=='red'),key=lambda r:r['episode'])[0]
        replay=study/'rival-matchups/codex_lanes/red/artifacts'/row['episode']/'replay.bin'
        if digest(replay.read_bytes())!=row['replay_sha256']:raise ValueError('Replay changed')
        tape=out/(label.lower()+'-codex-red.jsonl')
        binary=RUN/'r3/macro-replay-v2'
        with tape.open('w') as f:subprocess.run([str(binary),'--replay',str(replay)],cwd=ROOT,stdout=f,check=True)
        header=None;frames=[];summary=None
        with tape.open() as f:
            for line in f:
                obj=json.loads(line)
                if obj['type']=='header':header=obj
                elif obj['type']=='frame':
                    for h in obj['heroes']:h.pop('visible_post_tick',None)
                    frames.append(obj)
                elif obj['type']=='summary':summary=obj
        if not summary or summary['hash_mismatches']:raise ValueError('Replay not verified')
        cases.append({'name':label,'row':row,'header':header,'frames':frames,'summary':summary})
    write(out/'codex-red-comparison.json',{'cases':cases,'decoder_sha256':digest(binary.read_bytes()),
        'selection':'First lexicographic red episode for each completed policy probe; five policy copies per team. Different seeds; source-matched full replays. Old release .2 simulation equivalence to .3 established separately.',
        'source_equivalence':str(RUN/'r3/source-parity.json')})
    plot(cases,out/'codex-red-comparison.png','Codex fixed-lineup comparison — recorded replay positions',
         'Red: our five heroes. Blue: Codex objective-lanes v1. Squares: living buildings. Rows use different seeds and different durations.')

if __name__=='__main__':main()
