"""Audit median blue outcomes and close the bounded early-middle experiment."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

from economy_feedback import record
from league_threat_review import run_native
from macromackie_middle_rush import STUDY
from macromackie_color_review import trace
from policy_ir import read, write, digest
from win_replay_review import plot


def prepare():
    result = read(STUDY/'result.json')
    cohort = result['candidate']
    assert cohort['games'] == 80 and cohort['all_full_audits_passed']
    cases = []
    for win in (False, True):
        subset = sorted((r for r in cohort['rows'] if r['color'] == 'blue' and bool(r['win']) == win),
                        key=lambda r: (r['ticks'], r['episode']))
        if subset:
            cases.append(subset[len(subset)//2])
    write(STUDY/'review-selection.json', {'selection': 'Median duration blue win/loss for every outcome present, selected before reconstruction.', 'cases': cases})

    def one(case):
        d = STUDY/'hosted/blue_three/macromackie-v4/macromackie_v4/blue/artifacts'/case['episode']
        proof = run_native('macro-replay-v5', d/'replay.bin', d/'decoded.jsonl')
        assert proof['hash_mismatches'] == 0
        items = [json.loads(line) for line in (d/'decoded.jsonl').open()]
        return {'name': 'New blue '+('win' if case['win'] else 'loss'), 'row': case,
                'header': next(x for x in items if x['type']=='header'),
                'frames': [x for x in items if x['type']=='frame']}
    with ThreadPoolExecutor(2) as pool:
        views = list(pool.map(one, cases))
    plot(views, STUDY/'review-positions.png', 'Early middle response against macromackie v4',
         'Blue slots5–9 are ours. Actual reconstructed positions; squares are standing structures.')
    print(STUDY/'review-positions.png')


def finish():
    source = STUDY/'local/candidates/blue_three/policy.bas'
    cases = read(STUDY/'review-selection.json')['cases']
    output = []
    for case in cases:
        d = STUDY/'hosted/blue_three/macromackie-v4/macromackie_v4/blue/artifacts'/case['episode']
        proof = run_native('replay-middle-rush-probe', d/'replay.bin', d/'middle-decisions.jsonl',
            {'PROBE_POLICY': str(source), 'PROBE_SLOTS': '5,6,7,8,9', 'PROBE_SAMPLE_EVERY': '1'})
        inspected = trace(d/'middle-decisions.jsonl')
        first = {}
        for line in (d/'middle-decisions.jsonl').open():
            r = json.loads(line)
            if r['type'] == 'decision' and r['memory']['defActive'] and r['slot'] not in first:
                first[r['slot']] = {'tick': r['tick'], 'memory': r['memory']}
        output.append(case | inspected | {'first_decisions': first})
    result = read(STUDY/'result.json')
    mechanism = bool(output) and all(
        len(r['first_decisions']) == 5 and all(x['tick'] < 1558 and x['memory']['middleRush'] == 1
        and x['memory']['defCount'] == 3 for x in r['first_decisions'].values()) for r in output)
    report = result | {'source_sha256': digest(source.read_bytes()), 'reviewed_cases': output,
                       'mechanism_verified': mechanism, 'targeted_pass': result['passed'] and mechanism,
                       'promotion_performed': False}
    write(STUDY/'review-result.json', report)
    root = STUDY/'hosted/blue_three'
    if not (root/'reviewed-feedback').exists():
        record(root/'evaluated-feedback/policy.ir.json', source,
            f'Complete macromackie-v4 comparison: candidate{result["candidate"]["colors"]}, '
            f'deployed control{result["control"]["colors"]}. Source-verified earlier '
            f'three-visible middle recall={mechanism}; targeted pass={report["targeted_pass"]}. '
            'No opponent label exposed in BASIC. Broad matchups remain untested; no league promotion. '
            'Local candidate deaths151 versus100 despite equal11/12 wins; preserve this risk.',
            STUDY/'review-result.json', root/'reviewed-feedback')
    print(json.dumps({'colors': result['candidate']['colors'], 'mechanism_verified': mechanism,
                      'targeted_pass': report['targeted_pass'],
                      'first_recalls': [{k:v['tick'] for k,v in r['first_decisions'].items()} for r in output]}))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['prepare', 'finish'])
    args = parser.parse_args()
    prepare() if args.stage == 'prepare' else finish()
