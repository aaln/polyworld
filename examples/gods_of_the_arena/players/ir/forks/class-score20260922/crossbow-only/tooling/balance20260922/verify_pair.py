"""Offline verification of every IR pair and the complete frozen decision."""
from pathlib import Path
import hashlib
import json
import runpy
import sys

pair = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = read(pair / 'manifest.json')
for name, digest in manifest['artifacts'].items():
    assert sha(pair / name) == digest, name
sys.path.insert(0, str(pair / 'tooling/balance20260922'))
import build

for name in ('control', 'ranger', 'crossbow', 'warlock', 'arcanist'):
    build.configure_control() if name == 'control' else build.configure()
    ir = build.ir
    p = runpy.run_path(str(pair / name / 'policy.py'))['POLICY']
    assert p == read(pair / name / 'policy.ir.json') == read(pair / name / 'extracted.ir.json')
    source = (pair / name / 'policy.bas').read_text()
    assert ir.compile_policy(p) == source
    assert ir.extract(source, p) == p
    m = read(pair / name / 'manifest.json')
    assert m['source_sha256'] == sha(pair / name / 'policy.bas')
    assert m['ir_sha256'] == ir.digest(p)
    assert p['execution']['game_version'] == manifest['game_version'] == '2026.9.22.2'

plan, result = [read(pair / 'evidence' / name) for name in ('plan.json', 'result.json')]
assert plan['games'] == manifest['games'] == 400
assert result['complete'] and len(result['cells']) == len(plan['arms']) == 10
for arm, cell in zip(plan['arms'], result['cells']):
    assert (arm['name'], arm['side']) == (cell['name'], cell['side'])
    assert len(cell['rows']) == cell['games'] == arm['games'] == 40
    assert arm['source_sha256'] == sha(pair / arm['name'] / 'policy.bas')
    assert cell['score'] == sum(r.get('score', 0) for r in cell['rows']) / 40
    assert cell['invalid'] == sum(not r['valid'] for r in cell['rows'])
    assert all(r.get('all_hashes_equal') for r in cell['rows'] if 'score' in r)
controls = result['cells'][:2]
for comparison in result['comparisons']:
    cells = [c for c in result['cells'] if c['name'] == comparison['name']]
    score, control = sum(c['score'] for c in cells), sum(c['score'] for c in controls)
    assert comparison['passed'] == (all(c['invalid'] == 0 for c in cells + controls)
        and all(c['score'] >= .95*b['score'] for c,b in zip(cells,controls))
        and score > control and score >= 1.1*control)
eligible = [c for c in result['comparisons'] if c['passed']]
selected = max(eligible, key=lambda c: c['score'])['name'] if eligible else 'control'
assert selected == manifest['selected'] == result['selected']
print(json.dumps({'verified': True, 'pairs': 5, 'games': 400, 'selected': selected,
                  'hashed_artifacts': len(manifest['artifacts'])}))
