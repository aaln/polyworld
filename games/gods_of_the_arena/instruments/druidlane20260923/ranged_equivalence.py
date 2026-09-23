"""Complete exact-source Ranger and Crossbowman equivalence on both sides."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json, subprocess, hashlib
import native
ROOT,STUDY,ENGINE=native.ROOT,native.STUDY,native.ENGINE
read=native.read
sha=native.sha
write=native.write
PARENT=ROOT/'examples/gods_of_the_arena/players/ir/forks/blue-center20260923-hosted/blue-center/policy.bas'
def run(case):
    label,side=case
    out=STUDY/'ranged-equivalence'/label/str(side);out.mkdir(parents=True,exist_ok=True)
    source=PARENT if label=='baseline' else STUDY/'druid-lane/policy.bas'
    tape=out/'replay.bin';binary=STUDY/'bin/episode-v2'
    roster=[str(source) if i==side*5 else str(PARENT) for i in range(10)]
    cmd=[str(binary),'--config',str(STUDY/'game-config.json'),'--seed','923050','--record',str(tape)]+['--bot:'+p+':1' for p in roster]
    write(out/'command.json',cmd)
    q=subprocess.run(cmd,capture_output=True,text=True,cwd=ENGINE,timeout=900)
    (out/'stderr.log').write_text(q.stderr);assert q.returncode==0,q.stderr[-1600:]
    live=json.loads(q.stdout.splitlines()[-1]);write(out/'live.json',live)
    q=subprocess.run([str(binary),'--replay',str(tape)],capture_output=True,text=True,cwd=ENGINE,timeout=900)
    assert q.returncode==0,q.stderr[-1600:]
    audit=json.loads(q.stdout.splitlines()[-1]);write(out/'audit.json',audit)
    assert audit['hash_mismatches']==0
    for k in ['ticks','state_hash','actions','winner','fort_hp','commands']:assert audit[k]==live[k],k
    q=subprocess.run([str(STUDY/'bin/command-hash'),str(tape)],capture_output=True,text=True,check=True)
    hashes=json.loads(q.stdout.splitlines()[-1]);write(out/'command-hash.json',hashes)
    result={'label':label,'side':side,'class':live['heroes'][side*5]['class'],'source_sha256':sha(source),'replay_sha256':sha(tape),'hashes':hashes,'valid':True}
    write(out/'result.json',result);return result
if __name__=='__main__':
    cases=[(n,s) for n in ['baseline','druid-lane'] for s in [0,1]]
    write(STUDY/'ranged-equivalence-plan.json',{'cases':cases,'seed':923050,'other_nine_policy_sha256':sha(PARENT),'scope':'Deterministic local behavior equivalence, not competitive rival evaluation.'})
    with ThreadPoolExecutor(2) as pool:rows=list(pool.map(run,cases))
    for side in [0,1]:
        control=STUDY/'ranged-equivalence/baseline'/str(side)
        candidate=STUDY/'ranged-equivalence/druid-lane'/str(side)
        assert read(control/'command-hash.json')==read(candidate/'command-hash.json')
        old,new=read(control/'live.json'),read(candidate/'live.json')
        for k in ['ticks','state_hash','actions','winner','fort_hp','commands']:assert old[k]==new[k],(side,k)
    assert {r['class'] for r in rows}=={1,6},rows
    write(STUDY/'ranged-equivalence.json',{'passed':True,'rows':rows,'scope':'Ranger and Crossbowman actual commands and complete world terminal state equal under both source variants; four full local games, normal draft.'})
    print(json.dumps({'passed':True,'games':4,'classes':[r['class'] for r in rows]}))
