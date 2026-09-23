"""Verify frozen source, replay audit evidence and semantic claim boundaries.

Default uses repository artifacts. --inputs additionally rehashes original local
replays and validates raw draft/source-probe records. Neither mode sends requests.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputs', action='store_true')
    args = parser.parse_args()
    manifest = read(HERE / 'artifact-manifest.json')
    for row in manifest:
        assert sha(HERE / row['path']) == row['sha256'], row['path']
    source = HERE / 'source/relh-v169.bas'
    assert sha(source) == '6791bc8cab237d88225356efa03713e2dbbd875c2c42bb718f1cfc926b02f9ca'
    comparison = read(HERE / 'battle-body-comparison.json')
    old = HERE / comparison['richard_source']
    marker = b'if drafting then'
    assert source.read_bytes().split(marker, 1)[1] == old.read_bytes().split(marker, 1)[1]
    assert sha(old) == comparison['richard174_source_sha256']
    assert hashlib.sha256(marker + source.read_bytes().split(marker, 1)[1]).hexdigest() == comparison['body_sha256']
    for path in ['relh_v169.source.ir.json', 'transfer-hypotheses.ir.json']:
        ir = read(HERE / path)
        assert {'situation', 'belief', 'goal', 'skill', 'strategy', 'execution', 'update'} <= ir.keys()
        if path.startswith('relh'):
            assert ir['execution']['proxy_usable'] is False
            assert ir['execution']['authentic_source_replay_verified'] is True
        else:
            assert ir['execution']['executable'] is False
            assert ir['execution']['deployed'] is False

    plan = read(HERE / 'plan.json')
    a = read(HERE / 'evidence/analysis.json')
    assert a['complete'] and a['games'] == len(plan['cases']) == 200
    assert len({r['episode'] for r in plan['cases']}) == 200
    assert len({r['replay_sha256'] for r in plan['cases']}) == 200
    assert Counter(r['context'] for r in plan['cases']) == {x: 50 for x in ['red-lead', 'blue-lead', 'red-late', 'blue-late']}
    assert len(a['rows']) == 400 and len(a['drafts']) == 400
    by_case = {(r['episode'], r['label']): r for r in a['rows']}
    assert len(by_case) == 400
    for row in a['rows']:
        assert sum(row['xp_sources'].values()) == row['xp']
        ticks = round(row['minutes'] * 1440)
        assert row['score'] == max(0, row['xp'] * 1440 - 200 * ticks) // 1440
    for label, summary in a['summary'].items():
        rows = [r for r in a['rows'] if r['label'] == label]
        nonzero = [r['score'] for r in rows if r['score'] > 0]
        assert summary['overall']['score'] == statistics.mean(r['score'] for r in rows)
        assert summary['overall']['nonzero_rate'] == len(nonzero) / 200
        assert summary['overall']['nonzero_mean'] == statistics.mean(nonzero)
    for row in a['drafts']:
        expected = row['relh_choice'] if row['label'] == 'relh169' else row['our_choice']
        assert row['choice'] == expected and row['legal'][expected]
        if row['label'] == 'ours' and 'late' in row['context']:
            assert {i for i, legal in enumerate(row['legal']) if legal} <= {0, 4, 5, 9}
    changes = Counter((r['choice'], r['relh_choice']) for r in a['drafts'] if r['label'] == 'ours')
    assert changes == {(6, 6): 49, (1, 1): 51, (5, 5): 56, (5, 0): 30, (0, 0): 14}
    probe = a['source_probe']
    assert probe['episodes'] == len(probe['rows']) == 8
    assert sum(p['commands_matched'] for p in probe['rows']) == probe['commands_matched'] == 142715
    assert all(p['all_state_hashes_equal'] and p['all_actions_consumed'] for p in probe['rows'])
    assert {p['episode'] for p in probe['rows']} == {p['episode'] for p in plan['source_reconstruction']}
    assert a['new_hosted_games'] == plan['new_hosted_games'] == 0
    inputs_verified = 0
    if args.inputs:
        for row in read(HERE / 'evidence/input-manifest.json'):
            p = Path(row['path'])
            assert sha(p) == row['sha256'], str(p)
            inputs_verified += 1
        raw = Path(read(HERE / 'provenance.json')['raw_root'])
        for case in plan['cases']:
            folder = Path(case['folder'])
            assert read(raw / 'episodes' / case['episode'] / 'drafts.json')['prefix_hashes_equal']
            resource = read(raw.parent / 'gota-manual-score20260923/episodes' / case['episode'] / 'audit.json')
            assert resource['hash_mismatches'] == 0 and resource['all_actions_consumed']
            status = read(folder / 'player-status.json')['players']
            assert len(status) == 10 and all(p['exit_code'] == 0 for p in status)
            spec = read(folder / 'spec.json')
            assert spec['players'][case['slot']]['content_hash'] == sha(source)
    print(json.dumps({'passed': True, 'repository_artifacts': len(manifest), 'original_inputs': inputs_verified, 'current_engine_games': 200, 'draft_choices_checked': 400, 'full_reconstructions': 8, 'source_commands_matched': 142715, 'new_hosted_games': 0}))


if __name__ == '__main__':
    main()
