"""Verify exact portable semantic/source pair and frozen artifact hashes."""
from pathlib import Path
import hashlib,json,sys
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'tooling/adaptive20260922'))
import class_binding as b
b.configure();ir=b.ir
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(P/'manifest.json');p=read(P/'policy.ir.json');source=(P/'policy.bas').read_text()
assert ir.compile_policy(p)==source and ir.extract(source,p)==p
assert m['ir_sha256']==ir.digest(p) and m['source_sha256']==sha(P/'policy.bas')
assert read(P/'extracted.ir.json')==p and read(P/'semantics.json')==ir.grounded(p)
for path,digest in m['artifacts'].items():assert sha(P/path)==digest,path
assert all(r['passed'] for r in read(P/'evidence/practice.json')['rows'])
assert all(r['passed'] for r in read(P/'evidence/portals.json')['rows'])
assert read(P/'evidence/scenarios.json')['passed']
print(json.dumps({'verified':True,'source_sha256':m['source_sha256'],'ir_sha256':m['ir_sha256'],'screen_passed':m['screen_passed'],'confirmation_passed':m['confirmation_passed']}))
