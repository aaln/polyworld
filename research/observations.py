"""Aggregate version-bound public decision frames and retrospective outcomes."""
from pathlib import Path
from collections import Counter, defaultdict
import gzip, hashlib, json, statistics

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT.parent/'polyworld/tmp/gota-khors180-observations-20260924'
OUT=ROOT/'research/opponents/khors-v180'
KHORS='564e4650-5efb-4b66-b9d4-a49070e1e68e'
read=lambda p:json.loads(p.read_text())

def write(p,d):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')

def one(row):
    folder=RAW/'episodes'/row['id'];out=folder/'tendencies.json'
    if out.exists():return read(out)
    b=json.loads(gzip.decompress((folder/'behavior.json.gz').read_bytes()))
    slots={i for i,v in enumerate(row['versions']) if v==KHORS or row['participants'][i]['player_name'] in ['Aaron',"Aaron's Co-play Coach"]}
    counts={i:Counter() for i in slots};examples={i:{} for i in slots}
    previous={}
    for f in b['frames']:
        i=f['slot']
        if i not in slots:continue
        c=counts[i];c['living_public_frames']+=1
        if not f['commands']:continue
        c['command_frames']+=1
        objects={o['id']:o for o in f['objects']}
        side=i//5
        available=[o for o in objects.values() if o['alive'] and (o['kind']==6 or o['team']!=side)]
        near={k:[o for o in available if o['kind']==k and o['distance']<=f['attack_range']+0.25] for k in [1,2,3,4,5,6]}
        has_hero10=any(o['kind']==2 and o['distance']<=10 for o in available)
        has_creep6=any(o['kind']==3 and o['distance']<=6 for o in available)
        finishable=[o for o in near[3] if o['hp']<=f['attack_damage']]
        for a in f['commands']:
            c['command_'+str(a['kind'])]+=1
            if a['kind']!=2:continue
            o=objects.get(a['first']);k=o['kind'] if o else 'unseen'
            c['attack_'+str(k)]+=1
            if near[2] and near[3]:
                c['both_hero_creep_in_basic_range']+=1;c['both_choose_'+str(k)]+=1
            if finishable:
                c['one_basic_creep_available']+=1
                if a['first'] in {o['id'] for o in finishable}:c['choose_finishable_creep']+=1
            if any(o['kind'] in [1,4,5] and o['distance']<=9 for o in available):
                c['structure_visible_alive_within9']+=1;c['structure_opportunity_choose_'+str(k)]+=1
            if any(o['kind']==6 and not o['returning'] and o['distance']<=10 for o in available) and not has_hero10 and not has_creep6:
                c['neutral_without_nearby_hero_wave']+=1;c['neutral_opportunity_choose_'+str(k)]+=1
                if k==6:examples[i].setdefault('neutral_income',{'tick':f['tick'],'hp':f['hp'],'max_hp':f['max_hp'],'level':f['level'],'target':o})
            if o and o['distance']>8:c['attack_target_farther_than8']+=1
            if o and k==6 and o['returning']:c['attack_returning_neutral']+=1
            if i in previous and previous[i]!=a['first']:c['attack_target_switches']+=1
            previous[i]=a['first']
    result=[]
    for i in slots:
        ev=[e for e in b['events'] if e['actor']==i]
        t=row['heroes'][i]
        result.append({'episode':row['id'],'slot':i,'round':row['round_number'],'version':row['versions'][i],
            'player':row['participants'][i]['player_name'],'class':t['class'],'score':row['scores'][i],
            'minutes':row['ticks']/1440,'all_vm_clean':not row['failed_slots'],'subject_vm_clean':i not in row['failed_slots'],
            'source_sha256':row['source_hashes'][i],'stream':row['stream'],'counts':dict(counts[i]),'examples':examples[i],
            'neutral_kills':sum(e['kind']=='Death' and e['target_kind']==6 for e in ev),
            'portals':dict(Counter(e['kind'] for e in ev if e['kind'].startswith('Portal'))),
            'purchases':[{k:e[k] for k in ['tick','detail','amount']} for e in ev if e['kind']=='ItemPurchased'],
            'telemetry':t})
    write(out,result);print(row['id'],len(result),flush=True);return result

def stats(rows):
    if not rows:return {'n':0}
    return {'n':len(rows),'mean_score':statistics.mean(r['score'] for r in rows),
        'nonzero_mean':statistics.mean(r['score'] for r in rows if r['score']>0) if any(r['score']>0 for r in rows) else 0,
        'zeroes':sum(r['score']==0 for r in rows),'mean_minutes':statistics.mean(r['minutes'] for r in rows),
        'mean_xp':statistics.mean(r['telemetry']['total_xp'] for r in rows),
        'mean_hero_kills':statistics.mean(r['telemetry']['hero_kills'] for r in rows),
        'mean_deaths':statistics.mean(r['telemetry']['deaths'] for r in rows),
        'mean_neutral_kills':statistics.mean(r.get('neutral_kills',0) for r in rows),
        'mean_xp_sources':{k:statistics.mean(r['telemetry']['xp_sources'].get(k,0) for r in rows) for k in ['hero','creep','neutral','structure_or_other']},
        'mean_gold_spent':statistics.mean(r['telemetry']['gold_spent'] for r in rows),
        'mean_buyback_gold':statistics.mean(r['telemetry']['buyback_gold'] for r in rows),
        'mean_time_minutes':{k:statistics.mean(r['telemetry']['time_ticks'].get(k,0)/1440 for r in rows) for k in ['draft','dead','own_keep','moving_field','other_field']},
        'commands':dict(sum((Counter(r.get('counts',{})) for r in rows),Counter())),
        'consumables':dict(sum((Counter(r['telemetry']['items_consumed']) for r in rows),Counter()))}

def main():
    records=read(RAW/'verified.json')['rows']
    rows=[x for r in records for x in one(r)]
    kh=[r for r in rows if r['version']==KHORS]
    assert len({r['source_sha256'] for r in kh})==1
    summary={'khors':stats(kh),'khors_clean_games':stats([r for r in kh if r['all_vm_clean']]),
        'khors_classes':{c:stats([r for r in kh if r['class']==c]) for c in sorted({r['class'] for r in kh})},
        'khors_sides':{str(side):stats([r for r in kh if r['slot']//5==side]) for side in range(2)},
        'own_rounds':{str(n):{name:stats([r for r in rows if r['round']==n and r['player']==name]) for name in ['Aaron',"Aaron's Co-play Coach"]} for n in sorted({r['round'] for r in rows})},
        'scope':'36current-engine natural league games across3rounds;28khors180 appearances. Public predecision objects and retrospective submitted commands, not source/internal beliefs. All typed XP and integer scores reconcile. Failures of other policies retained separately. Descriptive, no holdout forecast or causal claim.',
        'source_sha256':kh[0]['source_sha256'],'khors_distinct_full_game_streams':len({r['stream'] for r in kh})}
    write(OUT/'evidence/actor-rows.json',rows);write(OUT/'evidence/summary.json',summary)
    write(OUT/'evidence/plan.json',read(RAW/'plan.json'))
    write(OUT/'evidence/artifact-index.json',[{'episode':r['id'],'raw':str(RAW/'episodes'/r['id']),'replay_sha256':r['replay_sha256'],'stream':r['stream'],'failed_slots':r['failed_slots']} for r in records])
    print(json.dumps({'summary':summary['khors'],'classes':{k:v['n'] for k,v in summary['khors_classes'].items()}}),flush=True)

if __name__=='__main__':main()
