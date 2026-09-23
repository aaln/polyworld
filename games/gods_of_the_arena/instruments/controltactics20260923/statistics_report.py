"""Audit all paired games and aggregate score, time budgets and XP-flow graphs."""
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from statistics import mean
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT.parent / 'polyworld/tmp/gota-control-tactics61-20260923'
sys.path.insert(0,str(ROOT/'tools/gota_autoresearch'))
from score_statistics import accounting, paired_summary


def read(path): return json.loads(path.read_text())
def write(path,data): path.write_text(json.dumps(data,indent=2)+'\n')


def decode(folder):
    out=folder/'telemetry.json'
    if out.exists(): return
    p=subprocess.run([str(RAW/'bin/telemetry'),'--replay',str(folder/'replay.bin')],capture_output=True,text=True,timeout=900)
    (folder/'telemetry-stderr.log').write_text(p.stderr)
    assert p.returncode==0,p.stderr[-2000:]
    d=json.loads(p.stdout.splitlines()[-1]); assert d['hash_mismatches']==0
    write(out,d)


def audit_pair(r,plan):
    specs=[]
    for label in ['baseline','candidate']:
        own=r[label];folder=RAW/'artifacts'/own['episode']
        a,t,s,v,res=[read(folder/n) for n in ['audit.json','telemetry.json','spec.json','player-status.json','results.json']]
        assert len(v['players'])==10 and sorted(x['slot'] for x in v['players'])==list(range(10))
        assert all(x['exit_code']==0 for x in v['players']) and len(s['players'])==10
        assert len(a['heroes'])==len(t['heroes'])==len(res['scores'])==10
        for i in range(10):
            assert t['heroes'][i]['total_xp']==a['heroes'][i]['xp']==res['total_xp'][i]
            assert accounting(a['heroes'][i]['xp'],a['ticks'])['score']==res['scores'][i]
            assert sum(t['heroes'][i]['time_ticks'].values())==a['ticks']
            assert sum(t['heroes'][i]['xp_by_pre_tick_state'].values())==a['heroes'][i]['xp']
        assert s['players'][own['slot']]['content_hash']==plan['source_hashes'][label]
        specs.append(s)
    left,right=specs
    assert left['manifest']==right['manifest'] and left['coworld_manifest_hash']==right['coworld_manifest_hash']
    # Baseline API stores a placeholder config seed; actual runtime seed is in replay/results.
    configs=[dict(s['game_config'],seed=r['baseline']['seed']) for s in specs]
    assert configs[0]==configs[1]
    assert r['baseline']['seed']==r['candidate']['seed']==r['pair']['seed']
    assert r['baseline']['hero']['class']==r['candidate']['hero']['class']
    assert r['baseline']['slot']==r['candidate']['slot']


def metrics(rows,arm):
    values=[];edges=defaultdict(int);buckets=defaultdict(list)
    for r in rows:
        own=r[arm]; folder=RAW/'artifacts'/own['episode'];t=read(folder/'telemetry.json')
        hero=t['heroes'][own['slot']]; a=read(folder/'audit.json')
        minutes=own['ticks']/1440
        d=dict(score=own['score'],xp=hero['total_xp'],minutes=minutes,
               kills=hero['hero_kills'],deaths=hero['deaths'],creep_last_hits=hero['creep_last_hits'],
               spells=hero['spells'],rejected=sum(hero['rejected'].values()),
               gold_spent=hero['gold_spent'],buyback_gold=hero['buyback_gold'],
               consumables=sum(hero['items_consumed'].values()),
               hero_control_impacts=sum(hero['hero_control_hits'].values()),
               hero_xp=hero['xp_sources'].get('hero',0),creep_xp=hero['xp_sources'].get('creep',0),
               structure_or_other_xp=hero['xp_sources'].get('structure_or_other',0),
               alive_drought_ge30_seconds=hero['alive_xp_drought_ge30_ticks']/24)
        d.update({k+'_seconds':v/24 for k,v in hero['time_ticks'].items()})
        d['issued_commands']=sum(a['commands'][own['slot']])
        values.append(d)
        # Directed victim -> recipient XP graph, using public version identities.
        roster=list(r['baseline']['roster']);roster[own['slot']]=arm
        for i,h in enumerate(t['heroes']):
            for victim,xp in enumerate(h['hero_xp_by_victim_slot']):
                if xp:edges[(roster[victim],roster[i])]+=xp
            key=(roster[i],h['class'],i//5,i%5)
            buckets[key].append(dict(score=a['heroes'][i]['score'],xp=h['total_xp'],deaths=h['deaths'],minutes=minutes))
    sums={k:sum(v[k] for v in values) for k in values[0]}
    return dict(n=len(values),means={k:mean(v[k] for v in values) for k in values[0]},
                pooled_xp_per_minute=sums['xp']/sums['minutes'],
                pooled_deaths_per_minute=sums['deaths']/sums['minutes'],
                pooled_rejected_share=sums['rejected']/sums['issued_commands'] if sums['issued_commands'] else None,
                hero_xp_flow=[dict(victim=k[0],recipient=k[1],xp=v) for k,v in sorted(edges.items())],
                player_class_side_seat=[dict(policy=k[0],hero_class=k[1],side=k[2],seat=k[3],n=len(v),
                    mean_score=mean(x['score'] for x in v),mean_xp=mean(x['xp'] for x in v),
                    deaths_per_minute=sum(x['deaths'] for x in v)/sum(x['minutes'] for x in v)) for k,v in sorted(buckets.items())])


def main():
    folders=[p.parent for p in (RAW/'artifacts').glob('*/audit-result.json')]
    with ThreadPoolExecutor(4) as pool:list(pool.map(decode,folders))
    p=RAW/'paired-results.json'
    if not p.exists() or not read(p)['complete']:
        print(json.dumps({'decoded':len(folders),'paired_complete':False}));return
    rows=read(p)['pairs'];plan=read(RAW/'hosted-plan.json')
    assert len(rows)==plan['pairs']==80
    assert len({r['baseline']['episode'] for r in rows})==len({r['candidate']['episode'] for r in rows})==80
    # The harvester can finish while the initial directory snapshot is decoding.
    # Drain the complete frozen pair list before consuming every telemetry file.
    folders=[RAW/'artifacts'/r[arm]['episode'] for r in rows for arm in ['baseline','candidate']]
    with ThreadPoolExecutor(4) as pool:list(pool.map(decode,folders))
    for r in rows:audit_pair(r,plan)
    overall=paired_summary(rows)
    subsets={'by_color':lambda r:str(r['baseline']['slot']//5),
             'by_context':lambda r:r['baseline']['cell'],
             'by_class':lambda r:str(r['baseline']['hero']['class'])}
    result=dict(overall=overall,all_160_games_10_vms_valid=True,full_hash_xp_score_config_pair_audits=True)
    for key,func in subsets.items():
        result[key]={v:paired_summary([r for r in rows if func(r)==v]) for v in sorted({func(r) for r in rows})}
    result['telemetry']={arm:metrics(rows,arm) for arm in ['baseline','candidate']}
    result['class_telemetry']={v:{arm:metrics([r for r in rows if str(r['baseline']['hero']['class'])==v],arm) for arm in ['baseline','candidate']} for v in result['by_class']}
    result['streams']={}
    for arm in ['baseline','candidate']:
        groups=defaultdict(list)
        for r in rows:
            own=r[arm];sha=read(RAW/'artifacts'/own['episode']/'telemetry.json')['canonical_commands_sha1']
            groups[sha].append(own['episode'])
        result['streams'][arm]=dict(unique=len(groups),duplicates=[v for v in groups.values() if len(v)>1])
    result['pilot_advance']=all([
        overall['mean_delta']>0,overall['delta95'][0]>=0,
        overall['candidate']['nonzero_rate']>=overall['baseline']['nonzero_rate'],
        overall['candidate']['productive_rate']>=overall['baseline']['productive_rate'],
        all(v['candidate']['mean']>=.95*v['baseline']['mean'] for v in result['by_color'].values())])
    result['deployment_qualified']=False
    result['scope']='Directional pilot, 80 paired seeds across four fixed contexts. Frozen gate unchanged. Extra telemetry requested during run is exploratory; not an added selection gate. No established verdict sample floor. Other player comparisons confounded by draft/seat; no causal superiority claim.'
    write(RAW/'statistics.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['telemetry','class_telemetry','streams']},indent=2))


if __name__=='__main__':main()
