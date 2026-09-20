"""Inspect prospectively selected median losses in the failed tournament guards."""
from concurrent.futures import ThreadPoolExecutor
import json

from league_threat_review import run_native
from macromackie_middle_rush import STUDY
from policy_ir import digest, read, write
from ranger_guard_hosted import freeze
from win_replay_review import plot

ROOT = STUDY / 'guard-review'


def prepare():
    ROOT.mkdir(exist_ok=True)
    cohorts = read(STUDY / 'tournament-guards/result.json')['results']
    cases = []
    for key, color in [('relh154', 'blue'), ('jordan228', 'red')]:
        rows = sorted((r for r in cohorts[key]['result']['rows']
                       if r['color'] == color and r['loss']),
                      key=lambda r: (r['ticks'], r['episode']))
        row = rows[len(rows)//2]
        cases.append(row | {'key': key, 'name': key + ' ' + color + ' loss'})
    freeze(ROOT / 'selection.json', {'selection': 'Median duration loss in each failed color, chosen before replay reconstruction.', 'cases': cases})

    def decode(case):
        folder = STUDY / 'tournament-guards' / case['key'] / 'named' / case['color'] / 'artifacts' / case['episode']
        proof = run_native('macro-replay-v5', folder/'replay.bin', folder/'decoded.jsonl')
        assert proof['hash_mismatches'] == 0
        items = [json.loads(line) for line in (folder/'decoded.jsonl').open()]
        return {'name': case['name'], 'row': case,
                'header': next(r for r in items if r['type'] == 'header'),
                'frames': [r for r in items if r['type'] == 'frame']}

    with ThreadPoolExecutor(2) as pool:
        views = list(pool.map(decode, cases))
    plot(views, ROOT/'positions.png', 'Tournament guard losses: actual replay positions',
         'Owned slots5–9 against relh; slots0–4 against Jordan. Standing structures shown as squares.')
    print(ROOT/'positions.png', flush=True)


def decisions():
    source = STUDY/'local/candidates/blue_three/policy.bas'
    records = []
    for case in read(ROOT/'selection.json')['cases']:
        folder = STUDY/'tournament-guards'/case['key']/'named'/case['color']/'artifacts'/case['episode']
        slots = list(range(5)) if case['color']=='red' else list(range(5,10))
        output = folder/'middle-decisions.jsonl'
        proof = run_native('replay-middle-rush-probe', folder/'replay.bin', output,
                           {'PROBE_POLICY': str(source), 'PROBE_SLOTS': ','.join(map(str,slots)), 'PROBE_SAMPLE_EVERY':'1'})
        assert proof['all_actions_consumed'] and proof['all_state_hashes_equal']
        first, counts = {}, {}
        for line in output.open():
            row = json.loads(line)
            if row['type'] != 'decision':
                continue
            m = row['memory']; slot = row['slot']
            c = counts.setdefault(str(slot), {'decisions':0,'active':0,'middle':0,'no_target_active':0})
            c['decisions'] += 1
            c['active'] += bool(m['defActive'])
            c['middle'] += bool(m.get('middleRush',0))
            c['no_target_active'] += bool(m['defActive'] and not m['bestId'])
            if m['defActive'] and slot not in first:
                first[slot] = {'tick':row['tick'],'memory':m}
        records.append(case | {'proof':proof,'first_recalls':first,'decision_counts':counts})
    write(ROOT/'decisions.json', {'source_sha256':digest(source.read_bytes()),'cases':records})
    print(json.dumps([{'name':r['name'],'first':{k:v['tick'] for k,v in r['first_recalls'].items()},'decisions':r['decision_counts']} for r in records]),flush=True)


if __name__=='__main__':
    import sys
    prepare() if sys.argv[1]=='prepare' else decisions()
