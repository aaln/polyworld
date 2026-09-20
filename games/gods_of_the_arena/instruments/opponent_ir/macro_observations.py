"""Count descriptive visible core pressure; never use these post-fit as predictors."""
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

def scan(row, folder):
    side=row['observer_slot']//5
    first_pair={};first_damage=None;previous_fort=None;previous_tick=None
    first_seen={};visible_target_ticks=Counter();visible_ticks=0
    with gzip.open(folder/'observer.jsonl.gz','rt') as stream:
        for line in stream:
            v=json.loads(line)
            if v['type']!='view' or not v['available']:continue
            objects={o[0]:o for o in v['objects']};fort=next((o for o in objects.values() if o[1]==1 and o[2]==side),None)
            if fort is None:continue
            enemies=[o for o in objects.values() if o[1]==2 and o[2]!=side and o[6]>0 and o[7]]
            allies=[o for o in objects.values() if o[1]==2 and o[2]==side and o[6]>0 and o[7]]
            distance=lambda o:math.hypot(o[4]-fort[4],o[5]-fort[5])
            near=lambda radius:[o[0] for o in enemies if distance(o)<=radius]
            event=lambda:{'tick':v['tick'],'our_god_hp':fort[6],
                'visible_enemy_ids':near(60),'visible_enemies_within40':near(40),'visible_enemies_within24':near(24),
                'friendly_alive_visible':len(allies),'friendly_within28':sum(distance(o)<=28 for o in allies),
                'friendly_farther28':sum(distance(o)>28 for o in allies),
                'friendly_positions':{str(o[0]):o[4:6] for o in allies},
                'visible_enemy_positions':{str(o[0]):o[4:6] for o in enemies}}
            for radius in (60,40,24):
                if str(radius) not in first_pair and len(near(radius))>=2:first_pair[str(radius)]=event()
            if first_damage is None and previous_fort is not None and fort[6]<previous_fort:
                first_damage=event()|{'previous_observed_hp':previous_fort,'previous_observed_tick':previous_tick,
                    'continuous_previous_snapshot':previous_tick==v['tick']-1}
            previous_fort,previous_tick=fort[6],v['tick']
            for o in enemies:
                first_seen.setdefault(str(o[0]),{'tick':v['tick'],'class':o[3],'hp':o[6],
                    'inventory':o[13],'note':'First visible inventory, not first purchase or inferred gold.'})
                target=objects.get(o[8]);visible_ticks+=1
                if target and target[2]!=o[2] and target[6]>0 and target[7]:
                    visible_target_ticks[{1:'god',2:'hero',3:'creep',4:'tower',5:'barracks'}[target[1]]]+=1
                else:visible_target_ticks['no_valid_visible_target']+=1
    return {'episode':row['id'],'observer_slot':row['observer_slot'],'first_visible_pair_near_own_god':first_pair,
        'first_observed_god_damage':first_damage,'first_visible_inventory':first_seen,
        'visible_target_ticks':dict(visible_target_ticks),'visible_opponent_ticks':visible_ticks,
        'source_sha256':hashlib.sha256((folder/'observer.jsonl.gz').read_bytes()).hexdigest()}

def main():
    d=Path(sys.argv[1]);plan=json.loads((d/'study-plan.json').read_text());frozen=json.loads((d/'model-freeze.json').read_text())
    train=set(frozen['training_episode_ids']);rows=[r for r in plan['episodes'] if r['split']=='train' and r['id'] in train]
    records=[scan(r,d/'artifacts'/r['id']) for r in rows]
    evidence={'scope':'Descriptive discovery-only macro counts on distinct training observer streams. Added after the targeting predictor froze; not prediction features or heldout-validated macro rules.',
        'n':len(records),'rows':records,'visible_target_ticks':dict(sum((Counter(r['visible_target_ticks']) for r in records),Counter()))}
    for radius in ('60','40','24'):
        events=[r['first_visible_pair_near_own_god'][radius] for r in records if radius in r['first_visible_pair_near_own_god']]
        evidence['radius'+radius]={'observed_pair_episodes':len(events),
            'zero_friendly_within28':sum(e['friendly_within28']==0 for e in events),
            'all_five_friendly_alive_and_distant':sum(e['friendly_alive_visible']==5 and e['friendly_farther28']==5 for e in events)}
    events=[r['first_observed_god_damage'] for r in records if r['first_observed_god_damage']]
    evidence['first_god_damage']={'observed_episodes':len(events),'zero_friendly_within28':sum(e['friendly_within28']==0 for e in events),
        'continuous_onset_episodes':sum(e['continuous_previous_snapshot'] for e in events)}
    (d/'macro-observations.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps({k:v for k,v in evidence.items() if k!='rows'}))

if __name__=='__main__':main()
