"""Verify the reviewed semantic pair against its frozen executable and evidence."""
from pathlib import Path
import hashlib
import json
import runpy
import sys

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P / 'tooling/khors18020260924'))
import recovery_binding as b
b.configure()
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
m = read(P / 'manifest.json')
p = read(P / 'policy.ir.json')
s = (P / 'policy.bas').read_text()
assert runpy.run_path(str(P / 'policy.py'))['POLICY'] == p
assert b.ir.compile_policy(p) == s and b.ir.extract(s, p) == p
assert read(P / 'extracted.ir.json') == p
assert read(P / 'semantics.json') == b.ir.grounded(p)
assert b.ir.digest(p) == m['ir_sha256'] and sha(P / 'policy.bas') == m['source_sha256']
for path, digest in m['artifacts'].items():
    assert sha(P / path) == digest, path
frozen = read(P / 'evidence/frozen-input.ir.json')
assert b.ir.digest(frozen) == m['frozen_ir_sha256']
assert b.ir.compile_policy(frozen) == s
assert read(P / 'evidence/practice-comparison.json')['passed']
assert read(P / 'evidence/native-comparison.json')['passed']
camp = read(P / 'evidence/camp-income.json')
assert camp['passed'] and len(camp['rows']) == 20
assert all(r['neutral_kills'] >= 1 for r in camp['rows'])
study = read(P / 'evidence/statistics.json')
assert study['complete'] and study['games'] == 180
a = study['contrasts']['weak-neutral']['overall']
assert m['score_gate_passed'] == (a['mean_delta'] > 0 and a['delta975'][0] > 0)
assert m['hosted_complete'] and not m['deployment_qualified']
print(json.dumps({'verified': True, 'source_sha256': m['source_sha256'],
                  'ir_sha256': m['ir_sha256'], 'score_gate_passed': m['score_gate_passed']}))
