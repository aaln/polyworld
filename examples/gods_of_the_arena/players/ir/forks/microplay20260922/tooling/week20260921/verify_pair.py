"""Offline verification of the self-contained new-week IR/policy evidence bundle."""
import hashlib
import json
from pathlib import Path
import runpy
import sys

pair=Path(__file__).resolve().parent
sys.path.insert(0,str(pair/'tooling'))
import contracts
contracts.register()
from policy_ir import compile_policy,extract,digest

p=json.loads((pair/'policy.ir.json').read_text())
assert runpy.run_path(str(pair/'policy.py'))['POLICY']==p
source=(pair/'policy.bas').read_bytes()
assert compile_policy(p).encode()==source
assert extract(source.decode(),p)==p
manifest=json.loads((pair/'manifest.json').read_text())
for name,h in manifest['artifacts'].items():
    assert hashlib.sha256((pair/name).read_bytes()).hexdigest()==h,name
assert manifest['source_sha256']==hashlib.sha256(source).hexdigest()
assert manifest['ir_sha256']==digest(p)
evidence=pair/'evidence'
plan=json.loads((evidence/'hosted-plan.json').read_text())
assert plan['source_sha256']==manifest['source_sha256']
uploaded=json.loads((evidence/'uploads/lane/upload-request.json').read_text())
assert uploaded['content_hash']==manifest['source_sha256']
hosted=json.loads((evidence/'hosted-result.json').read_text())
assert hosted['complete'] and sum(r['games'] for r in hosted['results'])==160
cells={}
for r in hosted['results']:
    assert len(r['rows'])==r['games']==40
    assert abs(sum(x.get('score',0) for x in r['rows'])/40-r['mean_score'])<1e-8
    assert sum(not x['valid'] for x in r['rows'])==r['invalid']
    assert all(x.get('all_hashes_equal') for x in r['rows'])
    cells[r['arm']['name'],r['arm']['side']]=r
candidate=[cells['candidate',s]['mean_score'] for s in (0,1)]
control=[cells['incumbent',s]['mean_score'] for s in (0,1)]
passed=all(r['invalid']==0 for r in cells.values()) and all(candidate[s]>=1.1*control[s] for s in (0,1)) and sum(candidate)>=1.2*sum(control)
assert passed==hosted['passed']==manifest['hosted_gate_passed']
field_path=evidence/'field-result.json'
if field_path.exists():
    field=json.loads(field_path.read_text())
    assert field['complete'] and sum(r['games'] for r in field['results'])==160
    cells={}
    for r in field['results']:
        assert len(r['rows'])==r['games']==40
        clean=[x for x in r['rows'] if x['valid']]
        assert len(clean)==r['clean_games']
        assert abs(sum(x['score'] for x in clean)/max(1,len(clean))-r['mean_score_clean'])<1e-8
        assert sum(not x.get('subject_valid',False) for x in r['rows'])==r['subject_invalid']
        assert all(x.get('all_hashes_equal') for x in r['rows'])
        cells[r['arm']['name'],r['arm']['side']]=r
    candidate=[cells['candidate',s]['mean_score_clean'] for s in (0,1)]
    control=[cells['incumbent',s]['mean_score_clean'] for s in (0,1)]
    passed=all(r['subject_invalid']==0 and r['clean_games']>=30 for r in cells.values()) and all(candidate[s]>=control[s] for s in (0,1)) and sum(candidate)>=1.2*sum(control)
    assert passed==field['passed']==manifest['mixed_team_gate_passed']
print(json.dumps({'verified':True,'source_sha256':manifest['source_sha256'],
  'ir_sha256':manifest['ir_sha256'],'artifacts':len(manifest['artifacts'])}))
