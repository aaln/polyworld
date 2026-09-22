"""Offline verification; installed at the root of the preserved policy pair."""
from pathlib import Path
import hashlib
import json
import runpy
import sys

pair = Path(__file__).resolve().parent
sys.path.insert(0, str(pair / 'tooling/targets20260922'))
import practiced
practiced.configure('potions')
ir = practiced.ir
read = lambda p: json.loads(p.read_text())
manifest = read(pair / 'manifest.json')
p = read(pair / 'policy.ir.json')
assert runpy.run_path(str(pair / 'policy.py'))['POLICY'] == p
source = (pair / 'policy.bas').read_bytes()
assert ir.compile_policy(p).encode() == source
assert ir.extract(source.decode(), p) == p == read(pair / 'extracted.ir.json')
assert ir.grounded(p) == read(pair / 'semantics.json')
assert ir.digest(p) == manifest['ir_sha256']
assert hashlib.sha256(source).hexdigest() == manifest['source_sha256']
for name, digest in manifest['artifacts'].items():
    assert hashlib.sha256((pair / name).read_bytes()).hexdigest() == digest, name
e = pair / 'evidence'
assert read(e / 'uploads/practiced/upload-request.json')['content_hash'] == manifest['source_sha256']
for label in ('baseline', 'practiced'):
    plan = read(e / label / 'plan.json')
    result = read(e / label / 'result.json')
    assert result['complete'] and sum(c['games'] for c in result['results']) == 240
    if label == 'practiced':
        assert plan['source_sha256'] == manifest['source_sha256']
    for c in result['results']:
        assert len(c['rows']) == c['games'] == 40
        assert sum(not r['valid'] for r in c['rows']) == c['invalid']
        for metric, key in [('wins', 'win'), ('losses', 'loss'), ('draws', 'draw')]:
            assert sum(r.get(key, 0) for r in c['rows']) == c[metric]
        assert abs(sum(r.get('score', 0) for r in c['rows']) / 40 - c['own_score']) < 1e-7
        assert abs(sum(r.get('opponent_score', 0) for r in c['rows']) / 40 - c['opponent_score']) < 1e-7
        assert c['fort_passed'] == (c['invalid'] == 0 and c['wins'] >= 30)
        assert c['score_passed'] == (c['invalid'] == 0 and c['own_score'] > c['opponent_score'] and c['own_score'] >= 1.1 * c['opponent_score'])
        assert all(r['all_hashes_equal'] for r in c['rows'] if r['valid'])
    assert result['fort_passed'] == all(c['fort_passed'] for c in result['results'])
    assert result['score_passed'] == all(c['score_passed'] for c in result['results'])
assert read(e / 'practiced-scenarios-r2.json')['passed']
assert all(r['valid'] and r['runtime_margin'] for r in read(e / 'practiced-local-result.json')['rows'])
print(json.dumps({'verified': True, 'source_sha256': manifest['source_sha256'],
                  'ir_sha256': manifest['ir_sha256'], 'artifacts': len(manifest['artifacts'])}))
