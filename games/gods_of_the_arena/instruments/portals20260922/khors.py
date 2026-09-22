"""Prospective revision before spending: portal A/B against khors:v114."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
import time
import study

h, panel, audit = study.h, study.panel, study.audit
OUT = study.STUDY / 'hosted-khors114'
KHORS = '145c01e0-0cbf-4e1e-8120-11b437175b91'


def prepare():
    assert not list((study.STUDY / 'hosted').rglob('created.json'))
    assert h.read(study.STUDY / 'khors-discovery/preflight.json')['passed']
    assert h.sha(study.SOURCE.read_bytes()) == study.HASH
    assert all(r['passed'] for r in h.read(study.STUDY / 'candidate-r3-practice-v4.json')['rows'])
    assert h.read(study.STUDY / 'native-result.json')['passed']
    candidate = h.read(study.STUDY / 'upload/version.json')['id']
    old = h.read(study.STUDY / 'hosted/plan.json')
    # Team membership and within-team draft seats rotate together. Both subject
    # and priority rival are their team's first pick in both colors.
    template = list(old['arms'][0]['roster'])
    template[1] = KHORS
    template[1], template[5] = template[5], template[1]
    arms = []
    with h.client() as c:
        h.live(c)
        for label, version, source in [('baseline', study.BASELINE, old['arms'][0]['source_sha256']),
                                       ('candidate', candidate, study.HASH)]:
            for side in (0, 1):
                roster = list(template)
                roster[0] = version
                if side:
                    roster = roster[5:] + roster[:5]
                slot, rival = side * 5, (1 - side) * 5
                assert roster[rival] == KHORS and roster[slot] == version
                arm = {'name': label, 'side': side, 'version': version,
                       'source_sha256': source, 'own_slots': [slot],
                       'rival_slot': rival, 'roster': roster, 'games': 40}
                original = h.read(study.STUDY / 'hosted' / label / str(side) / 'request.json')
                body = {**original,
                        'idempotency_key': f'gota-portals0922-khors114-{label}-{side}-{study.HASH[:10]}',
                        'roster': [{'slot': i, 'player': {'policy_ref': v}} for i, v in enumerate(roster)],
                        'notes': 'Pre-result user revision: exact khors:v114 opposing first-pick seat both colors; half-turn roster swap. Fresh portal/control A/B, 40 each color/source. Original unlaunched plan preserved. Full source/VM/replay/XP/integer-score audit. Score gate >=10% aggregate gain and >=95% each color; khors superiority separate (>=10% per-color score lead and positive bootstrap lower bound). No automatic league selection.'}
                folder = OUT / label / str(side)
                h.freeze(folder / 'arm.json', arm)
                h.freeze(folder / 'request.json', body)
                h.create(c, body, folder / 'batch', dry_run=True)
                arms.append(arm)
        plan = {**old, 'arms': arms, 'prepared_at': h.research.now(),
                'revision': 'User named khors:v114 before any new requests or outcome observation; old plan remains unlaunched.',
                'khors_version': KHORS,
                'khors_source_sha256': h.read(study.STUDY / 'khors-discovery/preflight.json')['rows'][0]['source_sha256'],
                'rule': 'No invalid games; strict aggregate gain >=10% and each color >=95% fresh control. Separate khors claim requires >=10% individual mean-score lead on each color and positive 95% bootstrap lower bound of within-game score difference. Team wins diagnostic. Fixed first-pick mixed roster; no general league rank claim.',
                'mechanism_plan': 'Decode all 160 replays for portal starts/completions/interruptions, keep-to-home waste and low-health ready-scroll time. Report all, never select by outcomes.'}
        path = OUT / 'plan.json'
        if path.exists():
            plan['prepared_at'] = h.read(path)['prepared_at']
        h.freeze(path, plan)
        print(json.dumps({'prepared': True, 'games': 160, 'khors': KHORS, 'created': 0}), flush=True)


def collect(c, arm, folder, ep):
    row = audit.collect(c, arm, folder, ep)
    if 'score' in row:
        spec = h.read(folder / 'artifacts' / ep['id'] / 'spec.json')
        assert spec['players'][arm['rival_slot']]['content_hash'] == h.read(OUT / 'plan.json')['khors_source_sha256']
        row['khors_score'] = row['scores'][arm['rival_slot']]
        row['khors_score_delta'] = row['score'] - row['khors_score']
    return row


def run():
    plan = h.read(OUT / 'plan.json')
    assert plan['source_sha256'] == h.sha(study.SOURCE.read_bytes()) == study.HASH
    with h.research.lock(study.STUDY / 'hosted.lock', blocking=False), h.client() as c:
        for index, arm in enumerate(plan['arms']):
            folder = OUT / arm['name'] / str(arm['side'])
            if (folder / 'result.json').exists():
                continue
            receipt = folder / 'batch/created.json'
            ident = h.read(receipt)['id'] if receipt.exists() else panel.reserve(c, h.read(folder / 'request.json'), folder / 'batch')
            print(json.dumps({'name': arm['name'], 'side': arm['side'], 'request': ident}), flush=True)
            while True:
                eps = h.episodes(c, ident)
                h.write(folder / 'episodes.json', eps)
                done = [e for e in eps if e['status'] in ('completed', 'failed', 'cancelled', 'error')]
                if len(done) == arm['games'] and index + 1 < len(plan['arms']):
                    next_arm = plan['arms'][index + 1]
                    nf = OUT / next_arm['name'] / str(next_arm['side'])
                    if not (nf / 'batch/created.json').exists():
                        next_id = panel.reserve(c, h.read(nf / 'request.json'), nf / 'batch')
                        print(json.dumps({'queued_after_drain': next_arm['name'], 'side': next_arm['side'], 'request': next_id}), flush=True)
                with ThreadPoolExecutor(8) as pool:
                    rows = list(pool.map(lambda ep: collect(c, arm, folder, ep), done))
                h.write(folder / 'progress.json', {'audited': len(rows), 'total': arm['games'], 'rows': rows})
                if len(rows) == arm['games']:
                    break
                print(json.dumps({'arm': arm['name'], 'side': arm['side'], 'audited': len(rows)}), flush=True)
                time.sleep(10)
            n = len(rows)
            cell = {'name': arm['name'], 'side': arm['side'], 'games': n,
                    'invalid': sum(not r['valid'] for r in rows),
                    **{k: sum(r.get(k, 0) for r in rows) / n for k in ('score', 'xp', 'deaths', 'khors_score', 'khors_score_delta')},
                    'picks': dict(Counter(r.get('class') for r in rows)),
                    'distinct_streams': len({r.get('canonical_commands_sha1') for r in rows}),
                    'individual_score_wins': sum(r.get('khors_score_delta', 0) > 0 for r in rows),
                    'team_wins': sum(r.get('win', 0) for r in rows), 'rows': rows}
            h.write(folder / 'result.json', cell)
            print(json.dumps({k: v for k, v in cell.items() if k != 'rows'}), flush=True)
        cells = [h.read(OUT / a['name'] / str(a['side']) / 'result.json') for a in plan['arms']]
        old, new = cells[:2], cells[2:]
        control, score = sum(c['score'] for c in old) / 2, sum(c['score'] for c in new) / 2
        passed = (all(c['invalid'] == 0 for c in cells) and score > control and score >= 1.1 * control
                  and all(c['score'] >= .95 * b['score'] for c, b in zip(new, old)))
        result = {'complete': True, 'passed': passed, 'score': score, 'control_score': control, 'cells': cells}
        h.write(OUT / 'result.json', result)
        print(json.dumps({k: v for k, v in result.items() if k != 'cells'}), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--prepare', action='store_true')
    args = p.parse_args()
    if args.prepare:
        prepare()
    else:
        run()
