"""Build audit-only probes against the exact published engine, never research main."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
RAW=ROOT.parent/'polyworld/tmp/gota-khors114-audit-20260923';ENGINE=ROOT.parent/'polyworld-gota-engine-score-20260922';DEPS=ROOT.parent/'polyworld/tmp/gota-week-20260921/deps';NIM='/Users/aaln/.nimby/nim-2.2.10/bin/nim';COMMIT='1b70894436b7ffdcd0d421b6b32c2415c9c8bfde'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ENGINE,text=True).strip()==COMMIT
subprocess.run(['git','diff','--exit-code',COMMIT,'--','src','examples/gods_of_the_arena','coworld/dependencies.lock'],cwd=ENGINE,check=True)
for line in (ENGINE/'coworld/dependencies.lock').read_text().splitlines():
    name,_,url,revision=line.split()
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=DEPS/name,text=True).strip()==revision
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=DEPS/name,text=True).strip()
for name,source,module in [('stalls','stalls.nim','khors114_stalls.nim'),('own-source-probe','own_source_probe.nim','khors114_own_source.nim')]:
    src=HERE/source;dest=ENGINE/'examples/gods_of_the_arena/tools'/module;shutil.copy2(src,dest)
    if (RAW/name).exists():
        archive=RAW/'binary-history'/sha(RAW/name);archive.parent.mkdir(exist_ok=True)
        if not archive.exists():shutil.copy2(RAW/name,archive)
    command=[NIM,'c','-d:headless','-d:release','-d:replayEvents','--hints:off','--out:'+str(RAW/name),str(dest)]
    p=subprocess.run(command,cwd=ENGINE,env=dict(os.environ,POLYWORLD_DEPS=str(DEPS)),capture_output=True,text=True)
    (RAW/('rebuild-'+name+'.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    (RAW/('rebuild-'+name+'-provenance.json')).write_text(json.dumps({'engine_commit':COMMIT,'source_sha256':sha(src),'binary_sha256':sha(RAW/name),'command':command},indent=2)+'\n')
    print(name+' built',flush=True)
