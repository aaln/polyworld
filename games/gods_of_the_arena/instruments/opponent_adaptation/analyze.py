"""Freeze a grouped split, extract causal prefixes, and evaluate detection."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import sys

from detect import HORIZONS, UNKNOWN, fit, predict

ROOT = Path('/Users/aaln/experiments/softmax/polyworld')
OUT = Path('/Users/aaln/experiments/softmax/gota-autoresearch/adaptive-opponent-20260920/detection')
STUDIES = ['opponent-richard-v135-20260920', 'opponent-alex-g002-v1-20260920', 'opponent-jordan-v268-20260919']
LABELS = {'7c370daf-3c5f-42f8-870b-54b79c495a44': 'richard135',
          'a30542cb-54de-4109-92e6-bcabca7db4d8': 'alex_g002',
          '207ffaf9-0d1e-4d92-a15d-4352f1bddec2': 'jordan268'}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare():
    records = {}
    for study in STUDIES:
        root = ROOT/'tmp/gota-ir'/study
        plan = json.loads((root/'study-plan.json').read_text())
        for row in plan['episodes']:
            folder = root/'artifacts'/row['id']
            proof = json.loads((folder/'observer-validation.json').read_text())
            assert proof['all_state_hashes_equal']
            identity = (row['id'], row['observer_slot'])
            if identity in records:
                assert records[identity]['stream'] == proof['observable_sha256']
                continue
            records[identity] = {'episode': row['id'], 'observer_slot': row['observer_slot'],
                'label': LABELS.get(row['opponent_version'], UNKNOWN),
                'opponent_version': row['opponent_version'], 'opponent_label': row.get('opponent_label'),
                'own_version': row.get('own_version'), 'created_at': row.get('created_at'),
                'stream': proof['observable_sha256'], 'observer': str(folder/'observer.jsonl.gz'),
                'validation': str(folder/'observer-validation.json'), 'validation_sha256': sha(folder/'observer-validation.json')}
    groups = defaultdict(list)
    for row in records.values():
        groups[(row['label'], row['observer_slot']//5, row['stream'])].append(row)
    strata = defaultdict(list)
    for (label, color, stream), rows in groups.items():
        strata[(label, color)].append((stream, rows))
    selected = []
    for key, entries in strata.items():
        entries.sort()
        for index, (stream, rows) in enumerate(entries):
            representative = sorted(rows, key=lambda row: row['episode'])[0]
            selected.append({**representative, 'split': 'heldout' if index % 3 == 2 else 'train',
                             'duplicate_episode_count': len(rows)})
    plan = {'at': datetime.now(timezone.utc).isoformat(), 'scope': 'Retrospective classifier feasibility; not causal exploit proof or fresh-game validation.',
            'features': 'First visible living enemy inventory per class, within first1800ticks, sampled every24ticks; no future durations, outcomes, identity metadata or allied policy features.',
            'split_rule': 'Deduplicate by exact full observer stream within label/color; sorted stream hash, every third whole group held out. Inputs and split frozen before inventory extraction.',
            'rule': 'At least2 supporting training groups; class-conditional signature rate>=0.5 and>=4x next label; all known label class comparison groups>=2; at least2 distinct agreeing enemy heroes, otherwise unknown.',
            'horizons': HORIZONS, 'records': selected, 'raw_unique_episode_observers': len(records),
            'limits': 'Jordan uses a different own policy context and earlier date. Unknown population is small. Existing studies were previously analyzed for different questions. Report heldout prefix overlap explicitly; do not call repeats generalization. Further fresh same-controller heldout required.',
            'source_sha256': {str(p): sha(p) for p in [Path(__file__), Path(__file__).with_name('detect.py')]}}
    path = OUT/'study-plan.json'
    if path.exists():
        old = json.loads(path.read_text())
        assert old['records'] == selected and old['source_sha256'] == plan['source_sha256']
        return old
    write(path, plan)
    return plan


def extract(row):
    path = OUT/'prefixes'/(row['episode'] + '.json')
    if path.exists():
        return json.loads(path.read_text())
    our_team = row['observer_slot']//5
    first = {}
    prefixes = {}
    canonical = hashlib.sha256()
    first_enemy_tick = None
    final_tick = 0
    with gzip.open(row['observer'], 'rt') as handle:
        header = json.loads(next(handle))
        assert header['columns'] == ['id','kind','team','class','x','y','hp','alive','target','vx','vy','level','mana','items','item_counts']
        for line in handle:
            # Decode only 1Hz predecision snapshots. Snapshot availability is
            # preserved; no between-sample decision timing is claimed.
            marker = line.find('"tick":')
            if marker < 0:
                continue
            tick = int(line[marker+7:].split(',',1)[0])
            if tick > max(HORIZONS):
                break
            if tick % 24:
                continue
            view = json.loads(line)
            if view.get('type') != 'view':
                continue
            final_tick = tick
            enemies = [o for o in view.get('objects',[]) if o[1] == 2 and o[2] != our_team and o[7] and o[6] > 0] if view['available'] else []
            observed = [(o[3],o[4],o[5],o[6],o[8],o[13]) for o in enemies]
            canonical.update(json.dumps([tick,view['available'],observed],separators=(',',':')).encode())
            if enemies and first_enemy_tick is None:
                first_enemy_tick = tick
            if tick <= 1800:
                for obj in enemies:
                    first.setdefault(obj[0], {'id': obj[0], 'class': obj[3], 'tick': tick, 'items': obj[13]})
            if tick in HORIZONS:
                prefixes[str(tick)] = canonical.hexdigest()
    result = {**row, 'first_inventory': list(first.values()), 'first_enemy_tick': first_enemy_tick,
              'final_sampled_tick': final_tick, 'prefix_hashes': prefixes}
    write(path, result)
    return result


def main():
    plan = prepare()
    records = []
    for index, row in enumerate(plan['records']):
        records.append(extract(row))
        if (index+1)%5 == 0:
            print('Extracted',index+1,'/',len(plan['records']),flush=True)
    training = [r for r in records if r['split'] == 'train']
    heldout = [r for r in records if r['split'] == 'heldout']
    rules = fit(training)
    serial_rules = [{'class': key[0], 'items': list(key[1]), **value} for key,value in sorted(rules.items())]
    write(OUT/'frozen-rules.json', {'rules': serial_rules, 'training': [r['episode'] for r in training],
                                  'at': datetime.now(timezone.utc).isoformat()})
    evaluations = []
    for tick in HORIZONS:
        training_prefixes = {r['prefix_hashes'].get(str(tick)) for r in training} - {None}
        rows = []
        for record in heldout:
            result = predict(record['first_inventory'], rules, tick)
            rows.append({'episode':record['episode'], 'truth':record['label'],
                         'color':'red' if record['observer_slot']<5 else 'blue',
                         'prediction':result['label'], 'evidence':result['evidence'],
                         'prefix_shared_with_training':record['prefix_hashes'].get(str(tick)) in training_prefixes,
                         'observed_to_horizon':record['final_sampled_tick']>=tick})
        cells = []
        for label in sorted({r['truth'] for r in rows}):
            for color in ['red','blue']:
                selected = [r for r in rows if r['truth']==label and r['color']==color]
                cells.append({'label':label,'color':color,'n':len(selected),
                    'correct':sum(r['prediction']==label for r in selected),
                    'abstained':sum(r['prediction']==UNKNOWN for r in selected),
                    'wrong_named':sum(r['prediction'] not in [label,UNKNOWN] for r in selected),
                    'shared_prefixes':sum(r['prefix_shared_with_training'] for r in selected)})
        evaluations.append({'tick':tick,'seconds':tick/24,'cells':cells,'rows':rows})
    profiles = defaultdict(Counter)
    for record in records:
        for hero in record['first_inventory']:
            profiles[(record['label'],hero['class'])][tuple(hero['items'])] += 1
    output = {'records':len(records),'training_groups':len(training),'heldout_groups':len(heldout),
              'eligible_rules':sum(r['eligible'] for r in rules.values()),
              'evaluations':evaluations,'profile_discovery_not_fit':[{'label':k[0],'class':k[1],
                'inventories':[{'items':list(i),'count':n} for i,n in v.most_common()]} for k,v in sorted(profiles.items())],
              'scope':plan['scope'],'limits':plan['limits']}
    write(OUT/'result.json',output)
    print(json.dumps({k:output[k] for k in ['records','training_groups','heldout_groups','eligible_rules']}),flush=True)
    print(json.dumps(evaluations[2]['cells']),flush=True)


if __name__ == '__main__':
    main()
