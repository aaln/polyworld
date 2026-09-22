"""Build the exact live god-XP patch in its own worktree and record provenance."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
STUDY=ROOT.parent/'polyworld/tmp/gota-score-20260922'
ENGINE=ROOT.parent/'polyworld-gota-engine-score-20260922'
COMMIT='1b70894436b7ffdcd0d421b6b32c2415c9c8bfde'
NIM=Path('/Users/aaln/.nimby/nim-2.2.10/bin/nim')
DEPS=ROOT.parent/'polyworld/tmp/gota-week-20260921/deps'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def command(args,cwd=ENGINE):
    return subprocess.check_output(list(map(str,args)),cwd=cwd,text=True).strip()


def main():
    assert command(['git','rev-parse','HEAD'])==COMMIT
    assert not command(['git','diff',COMMIT,'--','src','examples/gods_of_the_arena','coworld/dependencies.lock'])
    revisions={}
    for line in (ENGINE/'coworld/dependencies.lock').read_text().splitlines():
        name,_,url,revision=line.split()
        assert command(['git','-C',DEPS/name,'rev-parse','HEAD'])==revision
        assert not command(['git','-C',DEPS/name,'status','--porcelain'])
        revisions[name]=revision
    sources={'episode-v2':HERE.parent/'balance20260922/episode.nim',
             'practice':HERE/'practice.nim',
             'portals':HERE.parent/'portals20260922/practice.nim',
             'scenarios':HERE.parent/'targets20260922/scenarios.nim',
             'economy':HERE.parent/'portals20260922/economy.nim',
             'command-hash':HERE.parent/'week20260921/command_hash.nim'}
    bins=STUDY/'bin58';bins.mkdir(exist_ok=True)
    def build(item):
        name,source=item
        dest=ENGINE/'examples/gods_of_the_arena/tools'/('score_'+name.replace('-','_')+'.nim')
        shutil.copy2(source,dest)
        p=subprocess.run([str(NIM),'c','-d:headless','-d:release','-d:replayEvents','--hints:off','--out:'+str(bins/name),str(dest)],cwd=ENGINE,env=dict(os.environ,POLYWORLD_DEPS=str(DEPS)),capture_output=True,text=True)
        (STUDY/('build-'+name+'.log')).write_text(p.stdout+p.stderr)
        assert p.returncode==0,p.stderr
        print(name+' built',flush=True)
    with ThreadPoolExecutor(2) as pool:list(pool.map(build,sources.items()))
    proof={'engine_commit':COMMIT,'replay_version':58,'nim':command([NIM,'--version']),'dependencies':revisions,'sources':{str(p.relative_to(ROOT)):sha(p) for p in sources.values()},'binaries':{p.name:sha(p) for p in bins.iterdir()},'engine_files':{n:sha(ENGINE/n) for n in ['coworld/dependencies.lock','examples/gods_of_the_arena/sim.nim','examples/gods_of_the_arena/content.nim','examples/gods_of_the_arena/bots.nim','examples/gods_of_the_arena/replays.nim','examples/gods_of_the_arena/scores.nim']}}
    out=STUDY/'bootstrap58.json'
    assert not out.exists()
    out.write_text(json.dumps(proof,indent=2)+'\n')


if __name__=='__main__':main()
