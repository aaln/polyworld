from pathlib import Path
import json, hashlib, sys
P = Path(__file__).resolve().parent
sys.path.insert(0, str(P / 'tooling/weakhero20260923'))
import weak_binding as b
b.configure()
read = lambda p: json.loads(p.read_text())
m, p = read(P/'manifest.json'), read(P/'policy.ir.json')
s = (P/'policy.bas').read_text()
assert b.ir.compile_policy(p) == s and b.ir.extract(s, p) == p
assert b.ir.digest(p) == m['ir_sha256']
for name, digest in m['artifacts'].items():
    assert hashlib.sha256((P/name).read_bytes()).hexdigest() == digest, name
assert read(P/'evidence/local-summary.json')['passed']
assert read(P/'evidence/trial-report.json')['complete']
print(json.dumps({'verified': True, 'source_sha256': m['source_sha256'], 'ir_sha256': m['ir_sha256'], 'deployment_qualified': m['deployment_qualified']}))
