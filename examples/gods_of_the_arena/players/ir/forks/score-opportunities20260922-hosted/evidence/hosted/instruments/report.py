"""Stream replay58 XP attribution; read the fixed score gate and uncertainty."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import random
import statistics
import subprocess
import time
import hosted_score as study

h,OUT,STUDY=study.h,study.OUT,study.STUDY
RIVALS={'khors:v114':'145c01e0-0cbf-4e1e-8120-11b437175b91',
        'Jordan:v411':'a15665be-4edf-4857-b23b-2888b4b49868',
        'Richard:v167':'e811221e-c419-4f7b-9629-01f8722ab9f7'}


def ci(values,seed=922314,repeats=10000):
    rng=random.Random(seed)
    draws=sorted(statistics.mean(rng.choices(values,k=len(values))) for _ in range(repeats))
    return [draws[int(.025*repeats)],draws[int(.975*repeats)]]


def decode(path):
    dest=path.parent/'economy.json'
    if dest.exists():return
    p=subprocess.run([str(STUDY/'bin58/economy'),'--replay',str(path.parent/'replay.bin')],capture_output=True,text=True,timeout=900)
    (path.parent/'economy-stderr.log').write_text(p.stderr)
    assert p.returncode==0,p.stderr[-1600:]
    data=json.loads(p.stdout.splitlines()[-1]);assert data['hash_mismatches']==0
    h.write(dest,data)


def build():
    plan=h.read(OUT/'plan.json');verdict=h.read(OUT/'result.json')
    hashes={r['version']:r['source_sha256'] for r in h.read(STUDY/'preflight.json')['rows']}
    hashes[h.read(STUDY/'upload/version.json')['id']]=plan['source_sha256']
    cells=[]
    for arm,cell in zip(plan['arms'],verdict['cells']):
        assert len(cell['rows'])==40
        rows=[];own=arm['own_slots'][0]
        folder=OUT/arm['name']/str(arm['side'])
        for row in cell['rows']:
            p=folder/'artifacts'/row['episode']
            spec=h.read(p/'spec.json')
            for slot,version in enumerate(arm['roster']):
                assert spec['players'][slot]['content_hash']==hashes[version],(row['episode'],slot)
            economy=h.read(p/'economy.json');hero=economy['heroes'][own];audit=h.read(p/'audit.json')
            assert hero['total_xp']==row['xp'] and audit['hash_mismatches']==0
            god=500 if audit['fort_hp'][1-arm['side']]<=0 else 0
            xp=hero['xp_sources']
            building=xp.get('structure_or_other',0)-god
            assert building>=0
            detail={**row,'hero_xp':xp.get('hero',0),'creep_xp':xp.get('creep',0),'building_xp':building,'god_xp':god,'kills':hero['hero_kills'],'creep_last_hits':hero['creep_last_hits'],'spells':hero['spells'],'minutes':row['ticks']/1440,'out_of_range':hero['rejected'].get('ActionOutOfRange',0)}
            assert sum(detail[k] for k in ['hero_xp','creep_xp','building_xp','god_xp'])==row['xp']
            rows.append(detail)
        comparisons=[]
        for label,version in RIVALS.items():
            slot=arm['roster'].index(version);assert slot//5!=arm['side']
            deltas=[r['score']-r['scores'][slot] for r in rows]
            comparisons.append({'label':label,'version':version,'slot':slot,'score':statistics.mean(r['scores'][slot] for r in rows),'own_minus_rival':statistics.mean(deltas),'difference_ci95':ci(deltas),'individual_outscores':sum(d>0 for d in deltas),'ties':sum(d==0 for d in deltas)})
        unique={}
        for r in rows:unique.setdefault(r['canonical_commands_sha1'],[]).append(r['episode'])
        result={'name':arm['name'],'side':arm['side'],'games':40,'invalid':sum(not r['valid'] for r in rows),'distinct_streams':len(unique),'duplicate_groups':[v for v in unique.values() if len(v)>1],'means':{k:statistics.mean(r[k] for r in rows) for k in ['score','xp','hero_xp','creep_xp','building_xp','god_xp','kills','deaths','level','creep_last_hits','minutes','spells','out_of_range']},'score_ci95':ci([r['score'] for r in rows]),'pooled_xp_per_minute':sum(r['xp'] for r in rows)/sum(r['minutes'] for r in rows),'team_wins':sum(r['win'] for r in rows),'opponents':comparisons,'rows':rows}
        h.write(folder/'review.json',result);cells.append(result)
    before,after=cells[:2],cells[2:]
    base=statistics.mean(c['means']['score'] for c in before)
    new=statistics.mean(c['means']['score'] for c in after)
    rng=random.Random(922316);gains=[]
    for _ in range(10000):
        draws=[statistics.mean(rng.choices([r['score'] for r in c['rows']],k=40)) for c in cells]
        b=statistics.mean(draws[:2]);n=statistics.mean(draws[2:])
        gains.append((n/b-1)*100 if b else 0)
    gains.sort()
    passed=all(c['invalid']==0 for c in cells) and new>base and new>=1.1*base and all(n['means']['score']>=.95*b['means']['score'] for b,n in zip(before,after))
    assert passed==verdict['passed']
    result={'complete':True,'games':160,'source_sha256':plan['source_sha256'],'engine_commit':plan['engine_commit'],'game_version':plan['game_version'],'score_gate_passed':passed,'baseline_score':base,'candidate_score':new,'aggregate_gain_percent':(new/base-1)*100,'gain_ci95_percent':[gains[250],gains[9750]],'per_color_gain_percent':[(n['means']['score']/b['means']['score']-1)*100 for b,n in zip(before,after)],'cells':[{k:v for k,v in c.items() if k!='rows'} for c in cells],'evidence_scope':'Fresh controls, one subject, fixed first-pick mixed roster. All ten source hashes/VM exits, full replay hashes, XP sources and integer scores checked. Side-stratified independent whole-game bootstrap; duplicates disclosed. No universal rank claim or per-component causal attribution. God500XP separated from remaining structure rewards.'}
    h.write(OUT/'report.json',result)
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--watch',action='store_true');args=p.parse_args()
    while True:
        files=list(OUT.glob('*/*/artifacts/*/result.json'))
        todo=[p for p in files if not (p.parent/'economy.json').exists()]
        with ThreadPoolExecutor(4) as pool:list(pool.map(decode,todo))
        count=len(list(OUT.glob('*/*/artifacts/*/economy.json')))
        h.write(OUT/'economy-progress.json',{'decoded':count,'total':160})
        if (OUT/'result.json').exists() and count==160:
            build();break
        if not args.watch:raise SystemExit('Incomplete; --watch streams all160 full decodes.')
        time.sleep(10)
