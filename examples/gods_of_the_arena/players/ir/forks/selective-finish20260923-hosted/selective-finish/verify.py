from pathlib import Path
import json,hashlib,sys
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'tooling/productive20260923'))
import finish_binding as b
b.configure();ir=b.ir
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(P/'manifest.json');p=read(P/'policy.ir.json');source=(P/'policy.bas').read_text()
assert ir.compile_policy(p)==source and ir.extract(source,p)==p
assert ir.digest(p)==m['ir_sha256'] and sha(P/'policy.bas')==m['source_sha256']
for n,d in m['artifacts'].items():assert sha(P/n)==d,n
assert read(P/'evidence/local-summary.json')['passed']
assert read(P/'evidence/trial-report.json')['complete']
print(json.dumps({'verified':True,'source_sha256':m['source_sha256'],'ir_sha256':m['ir_sha256'],'deployment_qualified':m['deployment_qualified']}))
