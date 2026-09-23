"""Complete ten-VM native matches: runtime/mechanism evidence, not league strength."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import subprocess
ROOT=Path(__file__).resolve().parents[4]
STUDY=ROOT.parent/'polyworld/tmp/gota-selective-finish59-20260923'
ENGINE=ROOT.parent/'polyworld-gota-engine-20260923'

read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')


def run(case):
    label,context,side,ordinal,seed=case
    out=STUDY/'native'/label/context/str(seed);out.mkdir(parents=True,exist_ok=True)
    if (out/'result.json').exists():return read(out/'result.json')
    source=ROOT/'examples/gods_of_the_arena/players/ir/forks/druid-lane20260923-hosted/druid-lane/policy.bas' if label=='baseline' else STUDY/label/'policy.bas'
    binary=STUDY/'bin/episode-v2';tape=out/'replay.bin'
    ref=ENGINE/'examples/gods_of_the_arena/players/base.bas'
    roster=[str(source) if i==side*5+ordinal else str(ref) for i in range(10)]
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
    cases=[(n,context,s,ordinal,k) for n in ['baseline','selective-finish'] for context,s,ordinal in [('red-lead',0,0),('blue-lead',1,0),('red-late',0,4),('blue-late',1,4)] for k in [923060,923061]]
    plan={'cases':cases,'engine':'d6827a4bd3a55a46cf86f88e921f147137709c64','authentic_richard174':sha(STUDY/'richard-v174.bas'),'reference':sha(ENGINE/'examples/gods_of_the_arena/players/base.bas'),'candidates':{n:sha(STUDY/n/'policy.bas') for n in ['selective-finish']},'config':sha(STUDY/'game-config.json'),'scope':'One subject, authentic Richard174 at opposing team position2 and eight responsive native reference VMs. Mechanism/runtime, not league-strength evidence.'}
    path=STUDY/'native-plan.json'
    if path.exists():assert read(path)==json.loads(json.dumps(plan))
    else:write(path,plan)
    with ThreadPoolExecutor(2) as pool:rows=list(pool.map(run,cases))
    write(STUDY/'native-result.json',{'passed':all(r['valid'] for r in rows),'rows':rows,'scope':plan['scope']})


if __name__=='__main__':main()
