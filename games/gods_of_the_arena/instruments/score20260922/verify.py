"""Offline semantic/source/evidence verification; no competitive inference."""
from pathlib import Path
import hashlib
import json
import runpy
import sys
pair=Path(__file__).resolve().parent
sys.path.insert(0,str(pair/'tooling/score20260922'))
import score_binding
score_binding.configure();ir=score_binding.ir
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=read(pair/'policy.ir.json');m=read(pair/'manifest.json');source=(pair/'policy.bas').read_text()
assert runpy.run_path(str(pair/'policy.py'))['POLICY']==p
assert ir.compile_policy(p)==source
assert ir.extract(source,p)==read(pair/'extracted.ir.json')==p
assert ir.grounded(p)==read(pair/'semantics.json')
assert sha(pair/'policy.bas')==m['source_sha256']
assert ir.digest(p)==m['ir_sha256']
for f,digest in m['artifacts'].items():assert sha(pair/f)==digest,f
for f in ['practice-r3-v2.json','portals-r3.json']:
    assert all(r['passed'] for r in read(pair/'evidence'/f)['rows'])
assert read(pair/'evidence/scenarios-r3.json')['passed']
assert read(pair/'evidence/native-result.json')['passed']
assert p['belief']['claims']['CompetitiveGain']['status']=='requires_review'
assert m['hosted_complete'] is False
print(json.dumps({'passed':True,'source_sha256':m['source_sha256'],'ir_sha256':m['ir_sha256'],'hosted_complete':False}))
