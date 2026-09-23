from pathlib import Path
import hashlib,json,sys
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'tooling/richard17420260923'))
import pressure_binding as b
b.configure();ir=b.ir
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(P/'manifest.json');p=read(P/'policy.ir.json');s=(P/'policy.bas').read_text()
assert ir.compile_policy(p)==s and ir.extract(s,p)==p
assert ir.digest(p)==m['ir_sha256'] and sha(P/'policy.bas')==m['source_sha256']
for path,digest in m['artifacts'].items():assert sha(P/path)==digest,path
for name in ['practice','recovery','openings','buyback','portals']:assert all(r['passed'] for r in read(P/'evidence'/(name+'.json'))['rows'])
assert read(P/'evidence/scenarios.json')['passed'] and read(P/'evidence/native-result.json')['passed']
print(json.dumps({'verified':True,'source_sha256':m['source_sha256'],'ir_sha256':m['ir_sha256'],'hosted_complete':m['hosted_complete'],'deployment_qualified':m['deployment_qualified']}))
