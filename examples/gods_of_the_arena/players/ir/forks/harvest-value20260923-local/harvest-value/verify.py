from pathlib import Path
import hashlib,json,runpy,sys
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'tooling/controltactics20260923'))
import harvest_binding as b
b.configure();ir=b.ir
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(P/'manifest.json');p=read(P/'policy.ir.json');s=(P/'policy.bas').read_text()
assert runpy.run_path(str(P/'policy.py'))['POLICY']==p
assert ir.compile_policy(p)==s and ir.extract(s,p)==p
assert read(P/'extracted.ir.json')==p and read(P/'semantics.json')==ir.grounded(p)
assert ir.digest(p)==m['ir_sha256'] and sha(P/'policy.bas')==m['source_sha256']
for path,digest in m['artifacts'].items():assert sha(P/path)==digest,path
assert read(P/'evidence/native-comparison.json')['runtime_valid']
assert not m['deployment_qualified'] and not m['hosted_complete']
print(json.dumps({'verified':True,'source_sha256':m['source_sha256'],'ir_sha256':m['ir_sha256']}))
