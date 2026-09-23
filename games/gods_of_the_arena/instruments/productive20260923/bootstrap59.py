"""Build exact published replay59 tools; never mutate archived engine58 evidence."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib,json,os,shutil,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
STUDY=ROOT.parent/'polyworld/tmp/gota-productive-return59-20260923';ENGINE=ROOT.parent/'polyworld-gota-engine-20260923'
COMMIT='d6827a4bd3a55a46cf86f88e921f147137709c64';NIM=Path('/Users/aaln/.nimby/nim-2.2.10/bin/nim');DEPS=ROOT.parent/'polyworld/tmp/gota-week-20260921/deps'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def command(args,cwd=ENGINE):return subprocess.check_output(list(map(str,args)),cwd=cwd,text=True).strip()
def main():
    assert command(['git','rev-parse','HEAD'])==COMMIT
    assert not command(['git','diff',COMMIT,'--','src','examples/gods_of_the_arena','coworld/dependencies.lock'])
    revisions={}
    for line in (ENGINE/'coworld/dependencies.lock').read_text().splitlines():
        name,_,url,revision=line.split();assert command(['git','-C',DEPS/name,'rev-parse','HEAD'])==revision
        assert not command(['git','-C',DEPS/name,'status','--porcelain']);revisions[name]=revision
    sources={'episode-v2':HERE/'episode59.nim','scenarios':HERE.parent/'targets20260922/scenarios.nim','economy':HERE.parent/'portals20260922/economy.nim','command-hash':HERE.parent/'week20260921/command_hash.nim','return-practice':HERE/'practice.nim','recovery-practice':HERE.parent/'druidlane20260923/practice.nim','opening-practice':HERE.parent/'bluekhors20260923/practice.nim','buyback-practice':HERE.parent/'adaptive20260922/buyback_practice.nim','return-probe':HERE/'source_probe.nim','combat-audit':HERE.parent/'adaptive20260922/combat_audit.nim','stalls':HERE.parent/'khors11420260923/stalls.nim'}
    bins=STUDY/'bin';bins.mkdir(exist_ok=True)
    def build(item):
        name,source=item;dest=ENGINE/'examples/gods_of_the_arena/tools'/('productive59_'+name.replace('-','_')+'.nim');shutil.copy2(source,dest)
        p=subprocess.run([str(NIM),'c','-d:headless','-d:release','-d:replayEvents','--hints:off','--out:'+str(bins/name),str(dest)],cwd=ENGINE,env=dict(os.environ,POLYWORLD_DEPS=str(DEPS)),capture_output=True,text=True)
        (STUDY/('build-'+name+'.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr[-2500:];print(name+' built',flush=True)
        if name.endswith('practice') or name=='return-probe':shutil.copy2(bins/name,STUDY/name)
    with ThreadPoolExecutor(2) as pool:list(pool.map(build,sources.items()))
    proof={'reuse_verified':True,'engine_commit':COMMIT,'replay_version':59,'nim':command([NIM,'--version']),'dependencies':revisions,'sources':{str(p.relative_to(ROOT)):sha(p) for p in sources.values()},'binaries':{p.name:sha(p) for p in bins.iterdir()},'engine_files':{n:sha(ENGINE/n) for n in ['coworld/dependencies.lock','src/polyworld/tapes.nim','examples/gods_of_the_arena/sim.nim','examples/gods_of_the_arena/content.nim','examples/gods_of_the_arena/bots.nim','examples/gods_of_the_arena/replays.nim','examples/gods_of_the_arena/scores.nim']}}
    out=STUDY/'runtime-provenance.json';assert not out.exists();out.write_text(json.dumps(proof,indent=2)+'\n')
if __name__=='__main__':main()
