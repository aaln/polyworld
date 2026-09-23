"""Build source reconstruction and draft-prefix probes on exact replay59 engine."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib, json, os, shutil, subprocess
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[3]
RAW=ROOT.parent/'polyworld/tmp/gota-relh169-audit-20260923'
ENGINE=ROOT.parent/'polyworld-gota-engine-20260923'
DEPS=ROOT.parent/'polyworld/tmp/gota-week-20260921/deps'
NIM='/Users/aaln/.nimby/nim-2.2.10/bin/nim'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*map(str,args)],text=True).strip()
assert git('-C',ENGINE,'rev-parse','HEAD')=='d6827a4bd3a55a46cf86f88e921f147137709c64'
assert not git('-C',ENGINE,'diff','--','src','examples/gods_of_the_arena','coworld/dependencies.lock')
dependencies={}
for line in (ENGINE/'coworld/dependencies.lock').read_text().splitlines():
 name,_,url,revision=line.split()
 assert git('-C',DEPS/name,'rev-parse','HEAD')==revision
 assert not git('-C',DEPS/name,'status','--porcelain')
 dependencies[name]=revision
def build(name):
 source=HERE/(name+'.nim');dest=ENGINE/'examples/gods_of_the_arena/tools'/('relh169_'+name+'.nim')
 shutil.copy2(source,dest)
 p=subprocess.run([NIM,'c','-d:headless','-d:release','-d:replayEvents','--hints:off','--out:'+str(RAW/name),str(dest)],cwd=ENGINE,env=dict(os.environ,POLYWORLD_DEPS=str(DEPS)),capture_output=True,text=True)
 (RAW/('build-'+name+'.log')).write_text(p.stdout+p.stderr)
 assert p.returncode==0,p.stderr[-3000:]
 return {'source':str(source.relative_to(ROOT)),'source_sha256':sha(source),'binary_sha256':sha(RAW/name)}
with ThreadPoolExecutor(2) as pool:rows=list(pool.map(build,['source_probe','drafts']))
proof={'engine_commit':git('-C',ENGINE,'rev-parse','HEAD'),'dependencies':dependencies,'instruments':rows,'reused_runtime_provenance':'../gota-productive-return59-20260923/runtime-provenance.json'}
(RAW/'runtime-provenance.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof))
