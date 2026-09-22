"""Offline verification of semantic/source parity and evidence scope."""
from pathlib import Path
import hashlib
import json
import runpy
import sys

pair=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(pair/'manifest.json')
for name,digest in m['artifacts'].items():assert sha(pair/name)==digest,name
sys.path.insert(0,str(pair/'tooling/portals20260922'))
import portal_binding
portal_binding.configure();ir=portal_binding.ir
p=runpy.run_path(str(pair/'policy.py'))['POLICY']
assert p==read(pair/'policy.ir.json')==read(pair/'extracted.ir.json')
assert ir.compile_policy(p)==(pair/'policy.bas').read_text()
assert ir.extract((pair/'policy.bas').read_text(),p)==p
assert ir.digest(p)==m['ir_sha256'] and sha(pair/'policy.bas')==m['source_sha256']
checks=read(pair/'evidence/candidate-r3-practice-v4.json')
assert len(checks['rows'])==checks['checks']==84 and all(r['passed'] for r in checks['rows'])
assert checks['max_instructions']<=19000 and checks['max_work']<=50000
assert read(pair/'evidence/candidate-r3-scenarios.json')['passed']
n=read(pair/'evidence/native-result.json');assert n['passed'] and len(n['rows'])==8 and all(r['valid'] for r in n['rows'])
if m['hosted_complete']:
    r=read(pair/'evidence/hosted/result.json');assert r['complete']
    assert sum(c['games'] for c in r['cells'])==160
    old,new=r['cells'][:2],r['cells'][2:]
    passed=all(c['invalid']==0 for c in r['cells']) and r['score']>r['control_score'] and r['score']>=1.1*r['control_score'] and all(c['score']>=.95*b['score'] for c,b in zip(new,old))
    assert passed==r['passed']==m['score_gate_passed']
else:
    assert m['score_gate_passed'] is None
    assert p['belief']['claims']['CompetitiveGain']['status']=='requires_review'
print(json.dumps({'verified':True,'source_sha256':m['source_sha256'],'ir_sha256':m['ir_sha256'],'portal_checks':84,'native_games':8,'hosted_complete':m['hosted_complete'],'score_gate_passed':m['score_gate_passed'],'hashed_artifacts':len(m['artifacts'])}))
