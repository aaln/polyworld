"""Verify the current pair, historical evidence and additional score/draft tests."""
from pathlib import Path
import hashlib
import json
import runpy

pair = Path(__file__).resolve().parent
runpy.run_path(str(pair / 'verify_base.py'))
read = lambda p: json.loads(p.read_text())
e = pair / 'evidence/current'
manifest = read(pair / 'manifest.json')
plan, result = read(e / 'field/plan.json'), read(e / 'field/result.json')
assert plan['candidate_source_sha256'] == manifest['source_sha256']
assert plan['evaluator_sha256'] == hashlib.sha256((e / 'instruments/current_score.py').read_bytes()).hexdigest()
assert plan['games'] == 160 and result['complete']
assert read(e / 'draft-practice.json')['passed']
assert not read(e / 'attention-confirm-decision.json')['admitted']
assert read(e / 'user-episode/summary.json')['all_hashes_equal']
assert read(e / 'user-episode/summary.json')['failed_slots'] == [6, 7, 8]
cells = result['cells']
assert len(cells) == 4
for c in cells:
    rows = c['rows']
    assert c['games'] == len(rows) == 40
    assert c['invalid'] == sum(not r['valid'] for r in rows)
    assert c['all_hashes_equal'] == all(r.get('all_hashes_equal', False) for r in rows)
    assert abs(c['own_score'] - sum(r.get('score', 0) for r in rows) / 40) < 1e-7
    assert abs(c['opponent_score'] - sum(r.get('opponent_score', 0) for r in rows) / 40) < 1e-7
    for metric, key in [('wins', 'win'), ('losses', 'loss'), ('draws', 'draw')]:
        assert c[metric] == sum(r.get(key, 0) for r in rows)
candidate, control = cells[:2], cells[2:]
for a, b in zip(candidate, control):
    assert (a['opponent'], a['side'], a['game_version'], a['engine_commit']) == (b['opponent'], b['side'], b['game_version'], b['engine_commit'])
valid = all(c['invalid'] == 0 and c['all_hashes_equal'] for c in cells)
preserved = all(a['own_score'] >= .95 * b['own_score'] for a, b in zip(candidate, control))
new_score, old_score = [sum(c['own_score'] for c in group) for group in (candidate, control)]
passed = valid and preserved and new_score > old_score and new_score >= 1.10 * old_score
assert result['research_improved'] == manifest['current_field_gate_passed'] == passed
assert result['beats_each_target_color_by_score'] == (valid and all(c['own_score'] > c['opponent_score'] for c in candidate))
assert result['fort_outcomes_gate_progress'] is False
print(json.dumps({'current_pair_verified': True, 'field_games': 160,
                  'field_gate_passed': passed, 'unchanged_source_sha256': manifest['source_sha256']}))

middle_plan, middle = read(e / 'middle-field/plan.json'), read(e / 'middle-field/result.json')
assert middle_plan['candidate_source_sha256'] == manifest['source_sha256']
assert middle_plan['games'] == 160 and middle['complete']
cells = middle['cells']
assert len(cells) == 4
for c in cells:
    rows = c['rows']
    assert c['games'] == len(rows) == 40
    assert c['invalid'] == sum(not r['valid'] for r in rows)
    assert c['all_hashes_equal'] == all(r.get('all_hashes_equal', False) for r in rows)
    assert abs(c['own_score'] - sum(r.get('score', 0) for r in rows) / 40) < 1e-7
    assert abs(c['opponent_score'] - sum(r.get('opponent_score', 0) for r in rows) / 40) < 1e-7
    for metric, key in [('wins', 'win'), ('losses', 'loss'), ('draws', 'draw')]:
        assert c[metric] == sum(r.get(key, 0) for r in rows)
candidate, control = cells[:2], cells[2:]
for a, b in zip(candidate, control):
    assert (a['opponent'], a['side'], a['game_version'], a['engine_commit']) == (b['opponent'], b['side'], b['game_version'], b['engine_commit'])
valid = all(c['invalid'] == 0 and c['all_hashes_equal'] for c in cells)
preserved = all(a['own_score'] >= .95 * b['own_score'] for a, b in zip(candidate, control))
new_score, old_score = [sum(c['own_score'] for c in group) for group in (candidate, control)]
passed = valid and preserved and new_score > old_score and new_score >= 1.10 * old_score
assert middle['research_improved'] == manifest['later_draft_gate_passed'] == passed
assert middle['fort_outcomes_gate_progress'] is False
proof = read(e / 'runnable-proof.json')
assert proof['passed'] and len(proof['rows']) == 8
assert all(r['verified'] and r['runnable']['content_hash'] for r in proof['rows'])
assert all(r['runnable']['content_hash'] == manifest['source_sha256'] for r in proof['rows'] if r['label'] == 'candidate')
print(json.dumps({'later_draft_verified': True, 'total_followup_games': 320,
                  'later_draft_gate_passed': passed}))
