"""Separate 80-game draft-isolation cycle after the 400-game screen closes."""
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import importlib.util
import json
from pathlib import Path
import time
from environment import h, panel, STUDY

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('balance_hosted_followup', HERE / 'hosted.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
OUT = STUDY / 'draft-isolation'


def prepare(c):
    h.CYCLE = 'interactive-crossbow-draft-isolation-20260922'
    prior = h.read(STUDY / 'hosted/result.json')
    assert prior['complete'] and sum(x['games'] for x in prior['cells']) == 400
    assert all(x['invalid'] == 0 for x in prior['cells'][:2])
    assert h.read(STUDY / 'crossbow-draft-native.json')['passed']
    assert h.read(STUDY / 'crossbow-draft-scenarios.json')['passed']
    assert h.read(STUDY / 'crossbow-draft-practice.json')['passed']
    h.live(c)
    path = OUT / 'plan.json'
    if path.exists():
        return h.read(path)
    version, source = b.upload(c, 'crossbow_draft')
    original = h.read(STUDY / 'hosted/plan.json')
    arms = []
    for control in original['arms'][:2]:
        side = control['side']
        arm = {**control, 'name': 'crossbow_draft', 'version': version, 'source_sha256': source,
               'roster': list(control['roster'])}
        arm['roster'][side*5] = version
        body = h.read(STUDY / 'hosted/control' / str(side) / 'request.json')
        body.update(idempotency_key='gota-draft-isolation0922-' + str(side) + '-' + source[:12],
                    roster=[{'slot': i, 'player': {'policy_ref': v}} for i, v in enumerate(arm['roster'])],
                    notes='Prospective follow-up after completed 400-game hero study: change only Crossbowman public draft priority, preserve deployed post-draft controller. Same exact current-engine roster/config; reuse frozen 80-game controls, later time window. Full source/VM/replay/integer-score audit. No automatic selection.')
        folder = OUT / str(side)
        h.freeze(folder / 'arm.json', arm)
        h.freeze(folder / 'request.json', body)
        h.create(c, body, folder / 'batch', dry_run=True)
        arms.append(arm)
    plan = {'game_version': h.VERSION, 'engine_commit': h.COMMIT, 'cycle': h.CYCLE, 'games': 80,
            'arms': arms, 'control_plan_sha256': h.sha((STUDY / 'hosted/plan.json').read_bytes()),
            'control_result_sha256': h.sha((STUDY / 'hosted/result.json').read_bytes()),
            'rule': 'All clean; strict >=10% aggregate score gain and >=95% per-color preservation versus same frozen controls. Descriptive follow-up, no fresh concurrent controls or independent confirmation.'}
    h.freeze(path, plan)
    return plan


def run(plan):
    with h.research.lock(STUDY / 'hosted.lock', blocking=False), h.client() as c:
        for index, arm in enumerate(plan['arms']):
            folder = OUT / str(arm['side'])
            if (folder / 'result.json').exists():
                continue
            receipt = folder / 'batch/created.json'
            ident = h.read(receipt)['id'] if receipt.exists() else panel.reserve(c, h.read(folder / 'request.json'), folder / 'batch')
            print(json.dumps({'side': arm['side'], 'request': ident}), flush=True)
            while True:
                eps = h.episodes(c, ident)
                h.write(folder / 'episodes.json', eps)
                done = [x for x in eps if x['status'] in ('completed', 'failed', 'cancelled', 'error')]
                if len(done) == 40 and index == 0:
                    next_folder = OUT / '1'
                    if not (next_folder / 'batch/created.json').exists():
                        panel.reserve(c, h.read(next_folder / 'request.json'), next_folder / 'batch')
                with ThreadPoolExecutor(8) as pool:
                    rows = list(pool.map(lambda ep: b.collect(c, arm, folder, ep), done))
                h.write(folder / 'progress.json', {'audited': len(rows), 'total': len(eps), 'rows': rows})
                print(json.dumps({'side': arm['side'], 'audited': len(rows)}), flush=True)
                if len(rows) == 40:
                    break
                time.sleep(10)
            cell = {'name': 'crossbow_draft', 'side': arm['side'], 'games': 40,
                    'invalid': sum(not r['valid'] for r in rows),
                    'score': sum(r.get('score', 0) for r in rows)/40,
                    'deaths': sum(r.get('deaths', 0) for r in rows)/40,
                    'xp': sum(r.get('xp', 0) for r in rows)/40,
                    'picks': dict(Counter(r.get('class') for r in rows)),
                    'distinct_streams': len({r.get('canonical_commands_sha1') for r in rows}), 'rows': rows}
            h.write(folder / 'result.json', cell)
            print(json.dumps({k:v for k,v in cell.items() if k!='rows'}), flush=True)
        cells = [h.read(OUT / str(side) / 'result.json') for side in (0,1)]
        controls = h.read(STUDY / 'hosted/result.json')['cells'][:2]
        own, old = sum(c['score'] for c in cells), sum(c['score'] for c in controls)
        passed = all(c['invalid']==0 for c in cells+controls) and own > old and own >= 1.1*old and all(c['score'] >= .95*b['score'] for c,b in zip(cells,controls))
        result = {'complete': True, 'passed': passed, 'score': own/2, 'control_score': old/2,
                  'uplift_percent': 100*(own/old-1), 'cells': cells,
                  'control_reuse': 'Earlier exact-engine/configuration/version/seat cohort; no concurrent fresh control or independent confirmation.'}
        h.write(OUT / 'result.json', result)
        print(json.dumps({k:v for k,v in result.items() if k!='cells'}), flush=True)


if __name__ == '__main__':
    with h.client() as client:
        plan = prepare(client)
    run(plan)
