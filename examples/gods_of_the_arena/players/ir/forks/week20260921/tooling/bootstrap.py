"""Build the exact new-week simulator in an isolated checkout, never main."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[4]
COMMIT='f776d5e55d439706a8d49878d17d7ba1f6a1f7ce'

def run(*args,**kw):
    return subprocess.check_output(list(map(str,args)),text=True,**kw).strip()

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--engine',type=Path,default=ROOT.parent/'polyworld-gota-week-20260921')
    p.add_argument('--runtime',type=Path,default=ROOT/'tmp/gota-week-20260921')
    p.add_argument('--nim',default='nim');args=p.parse_args()
    engine=args.engine.resolve();runtime=args.runtime.resolve()
    if not engine.exists():
        available=subprocess.run(['git','cat-file','-e',COMMIT+'^{commit}'],cwd=ROOT,capture_output=True).returncode==0
        if not available:run('git','fetch','https://github.com/Metta-AI/polyworld.git',COMMIT,cwd=ROOT)
        run('git','worktree','add','--detach',engine,COMMIT,cwd=ROOT)
    assert run('git','rev-parse','HEAD',cwd=engine)==COMMIT
    assert not run('git','diff',COMMIT,'--', 'examples/gods_of_the_arena','src','coworld/dependencies.lock',cwd=engine)
    nim=run(args.nim,'--version');assert 'Version 2.2.10' in nim,nim
    deps=runtime/'deps';deps.mkdir(parents=True,exist_ok=True)
    def sync(line):
        name,_,url,sha=line.split();dest=deps/name
        if not dest.exists():
            run('git','clone','--filter=blob:none','--no-checkout',url,dest)
            run('git','-C',dest,'fetch','--depth=1','origin',sha)
            run('git','-C',dest,'checkout','--detach',sha)
        assert run('git','-C',dest,'rev-parse','HEAD')==sha
        assert not run('git','-C',dest,'status','--porcelain')
        return name,sha
    with ThreadPoolExecutor(4) as pool:
        revisions=dict(pool.map(sync,(engine/'coworld/dependencies.lock').read_text().splitlines()))
    out=runtime/'bin';out.mkdir(exist_ok=True)
    for name,source in [('episode','episode.nim'),('scenarios','scenarios.nim'),('command-hash','command_hash.nim')]:
        src=Path(__file__).parent/source
        dest=engine/'examples/gods_of_the_arena/tools'/('week_'+source)
        shutil.copyfile(src,dest)
        run(args.nim,'c','-d:headless','-d:release','--hints:off','--out:'+str(out/name),dest,
            cwd=engine,env=dict(os.environ,POLYWORLD_DEPS=str(deps)))
    receipt={'commit':COMMIT,'nim':nim,'dependencies':revisions,
        'binaries':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()}}
    (runtime/'bootstrap-proof.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
