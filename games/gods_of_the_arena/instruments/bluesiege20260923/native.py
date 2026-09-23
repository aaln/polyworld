"""Complete ten-VM native matches: runtime/mechanism evidence, not league strength."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import subprocess
ROOT=Path(__file__).resolve().parents[4]
STUDY=ROOT.parent/'polyworld/tmp/gota-blue-druid-siege-20260923'
ENGINE=ROOT.parent/'polyworld-gota-engine-score-20260922'

read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')


def run(case):
    label,context,side,ordinal,seed=case
    out=STUDY/'native'/label/context/str(seed);out.mkdir(parents=True,exist_ok=True)
    if (out/'result.json').exists():return read(out/'result.json')
    source=ROOT/'examples/gods_of_the_arena/players/ir/forks/druid-lane20260923-hosted/druid-lane/policy.bas' if label=='baseline' else STUDY/label/'policy.bas'
    binary=STUDY/'bin/episode-v2';tape=out/'replay.bin'
    ref=STUDY/'reference-defer-druid.bas'
    roster=[str(source) if i==side*5+ordinal else str(ref) for i in range(10)]
    if ordinal==3:
        for teammate in [0,2]:roster[side*5+teammate]=str(ROOT/'examples/gods_of_the_arena/players/ir/forks/druid-lane20260923-hosted/druid-lane/policy.bas')
    if context.endswith('-druid'):roster[side*5+2]=str(ref)
    roster[(1-side)*5+2]=str(STUDY/'richard-v174.bas')
    cmd=[str(binary),'--config',str(STUDY/'game-config.json'),'--seed',str(seed),'--record',str(tape)]+['--bot:'+p+':1' for p in roster]
    write(out/'command.json',cmd)
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,cwd=ENGINE,timeout=900)
        (out/'stdout.log').write_text(p.stdout);(out/'stderr.log').write_text(p.stderr)
        assert p.returncode==0,p.stderr[-1800:]
        live=json.loads(p.stdout.splitlines()[-1]);write(out/'live.json',live)
        p=subprocess.run([str(binary),'--replay',str(tape)],capture_output=True,text=True,cwd=ENGINE,timeout=900)
        (out/'audit-stderr.log').write_text(p.stderr);assert p.returncode==0,p.stderr[-1800:]
        audit=json.loads(p.stdout.splitlines()[-1]);write(out/'audit.json',audit)
        for k in ['ticks','state_hash','actions','winner','fort_hp','commands']:
            assert live[k]==audit[k],k
        assert audit['hash_mismatches']==0
        assert all(h['max_instructions']<=19000 and h['max_work']<=50000 for h in live['heroes'])
        assert len({h['class'] for h in live['heroes']})==10
        hero=live['heroes'][side*5+ordinal]
        assert hero['score']==max(0,hero['xp']*1440-200*live['ticks'])//1440
        q=subprocess.run([str(STUDY/'bin/economy'),'--replay',str(tape)],capture_output=True,text=True,cwd=ENGINE,timeout=900)
        (out/'economy-stderr.log').write_text(q.stderr);assert q.returncode==0,q.stderr[-1800:]
        economy=json.loads(q.stdout.splitlines()[-1]);write(out/'economy.json',economy)
        result={'name':label,'context':context,'side':side,'ordinal':ordinal,'seed':seed,'valid':True,'source_sha256':sha(source),'replay_sha256':sha(tape),'ticks':live['ticks'],'hero':hero,'all_hashes_equal':True}
    except Exception as exc:result={'name':label,'context':context,'side':side,'ordinal':ordinal,'seed':seed,'valid':False,'error':repr(exc)}
    write(out/'result.json',result);print(json.dumps(result),flush=True);return result


def main():
    cases=[(n,context,s,ordinal,k) for n in ['baseline','blue-druid-siege'] for context,s,ordinal in [('red-lead',0,0),('blue-lead',1,0),('red-late',0,3),('blue-late',1,3)] for k in [923080,923081]]
    plan={'cases':cases,'engine':'1b70894436b7ffdcd0d421b6b32c2415c9c8bfde','authentic_richard174':sha(STUDY/'richard-v174.bas'),'reference':sha(STUDY/'reference-defer-druid.bas'),'candidates':{n:sha(STUDY/n/'policy.bas') for n in ['blue-druid-siege']},'config':sha(STUDY/'game-config.json'),'scope':'One subject, authentic Richard174 at opposing team position2 and six or eight native reference VMs with Druid draft weight reduced by1000 to leave it available to the subject, and two fixed baseline teammates for later drafts. Mechanism/runtime, not league-strength evidence.'}
    path=STUDY/'native-plan.json'
    if path.exists():assert read(path)==json.loads(json.dumps(plan))
    else:write(path,plan)
    with ThreadPoolExecutor(2) as pool:rows=list(pool.map(run,cases))
    write(STUDY/'native-result.json',{'passed':all(r['valid'] for r in rows),'rows':rows,'scope':plan['scope']})


if __name__=='__main__':main()
