"""Offline source/IR and complete 80-game follow-up gate verification."""
from pathlib import Path
import hashlib
import json
import runpy
import sys

pair = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
m = read(pair / 'manifest.json')
for name, digest in m['artifacts'].items():
    assert sha(pair / name) == digest, name
sys.path.insert(0, str(pair / 'tooling/balance20260922'))
import draft_only
draft_only.configure()
ir = draft_only.build.ir
p = runpy.run_path(str(pair / 'policy.py'))['POLICY']
assert p == read(pair / 'policy.ir.json') == read(pair / 'extracted.ir.json')
assert ir.compile_policy(p) == (pair / 'policy.bas').read_text()
assert ir.extract((pair / 'policy.bas').read_text(), p) == p
assert m['source_sha256'] == sha(pair / 'policy.bas')
assert m['ir_sha256'] == ir.digest(p)
plan, result, controls = [read(pair / 'evidence' / name) for name in ('plan.json', 'result.json', 'controls.json')]
assert result['complete'] and plan['games'] == 80
assert plan['game_version'] == m['game_version'] == p['execution']['game_version'] == '2026.9.22.2'
for arm, cell, control in zip(plan['arms'], result['cells'], controls):
    assert arm['source_sha256'] == m['source_sha256']
    assert cell['side'] == control['side'] == arm['side']
    assert cell['games'] == len(cell['rows']) == control['games'] == len(control['rows']) == 40
    assert cell['score'] == sum(r.get('score', 0) for r in cell['rows'])/40
    assert cell['invalid'] == sum(not r['valid'] for r in cell['rows'])
    assert all(r.get('all_hashes_equal') for r in cell['rows'] if 'score' in r)
own, old = sum(c['score'] for c in result['cells']), sum(c['score'] for c in controls)
passed = all(c['invalid']==0 for c in result['cells']+controls) and own > old and own >= 1.1*old and all(c['score'] >= .95*b['score'] for c,b in zip(result['cells'],controls))
assert passed == result['passed'] == m['score_gate_passed']
print(json.dumps({'verified': True, 'games': 80, 'score_gate_passed': passed,
                  'source_sha256': m['source_sha256'], 'artifacts': len(m['artifacts'])}))
