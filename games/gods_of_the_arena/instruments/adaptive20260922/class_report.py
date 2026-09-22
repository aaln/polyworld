"""All-source, full-replay XP decomposition and prospective multi-arm score decisions."""
import argparse,json,random,statistics,subprocess,time
from concurrent.futures import ThreadPoolExecutor
import class_hosted as study
h,STUDY=study.h,study.STUDY
RIVALS={'khors:v114':'145c01e0-0cbf-4e1e-8120-11b437175b91','Richard:v167':'e811221e-c419-4f7b-9629-01f8722ab9f7','Jordan:v411':'a15665be-4edf-4857-b23b-2888b4b49868'}
mean=statistics.mean

def ci(values,seed=922617,repeats=10000):
    rng=random.Random(seed);draws=sorted(mean(rng.choices(values,k=len(values))) for _ in range(repeats));return [draws[repeats//40],draws[repeats*39//40]]
def decode(path):
    dest=path.parent/'economy.json'
    if dest.exists():return
    p=subprocess.run([str(STUDY/'bin/economy'),'--replay',str(path.parent/'replay.bin')],capture_output=True,text=True,timeout=900)
    (path.parent/'economy-stderr.log').write_text(p.stderr);assert p.returncode==0,p.stderr[-1600:]
    d=json.loads(p.stdout.splitlines()[-1]);assert d['hash_mismatches']==0;h.write(dest,d)

def build(stage):
    out=STUDY/stage;plan=h.read(out/'plan.json');verdict=h.read(out/'result.json')
    hashes={r['version']:r['source_sha256'] for r in h.read(STUDY/'preflight.json')['rows']}
    hashes.update({a['version']:a['source_sha256'] for a in plan['arms']})
    cells=[]
    for arm,cell in zip(plan['arms'],verdict['cells']):
        assert len(cell['rows'])==40
        rows=[];own=arm['own_slots'][0];folder=out/arm['name']/str(arm['side'])
        for row in cell['rows']:
            p=folder/'artifacts'/row['episode'];spec=h.read(p/'spec.json')
            for slot,version in enumerate(arm['roster']):assert spec['players'][slot]['content_hash']==hashes[version],(row['episode'],slot)
            economy=h.read(p/'economy.json');hero=economy['heroes'][own];audit=h.read(p/'audit.json')
            assert hero['total_xp']==row['xp'] and audit['hash_mismatches']==0
            god=500 if audit['fort_hp'][1-arm['side']]<=0 else 0;xp=hero['xp_sources'];building=xp.get('structure_or_other',0)-god;assert building>=0
            detail={**row,'hero_xp':xp.get('hero',0),'creep_xp':xp.get('creep',0),'building_xp':building,'god_xp':god,'kills':hero['hero_kills'],'creep_last_hits':hero['creep_last_hits'],'spells':hero['spells'],'minutes':row['ticks']/1440,'out_of_range':hero['rejected'].get('ActionOutOfRange',0)}
            assert sum(detail[k] for k in ['hero_xp','creep_xp','building_xp','god_xp'])==row['xp'];rows.append(detail)
        comparisons=[]
        for label,version in RIVALS.items():
            slot=arm['roster'].index(version);assert slot//5!=arm['side']
            deltas=[r['score']-r['scores'][slot] for r in rows]
            comparisons.append({'label':label,'version':version,'slot':slot,'score':mean(r['scores'][slot] for r in rows),'own_minus_rival':mean(deltas),'difference_ci95':ci(deltas),'individual_outscores':sum(d>0 for d in deltas),'ties':sum(d==0 for d in deltas)})
        unique={}
        for r in rows:unique.setdefault(r['canonical_commands_sha1'],[]).append(r['episode'])
        keys=['score','xp','hero_xp','creep_xp','building_xp','god_xp','kills','deaths','level','creep_last_hits','minutes','spells','out_of_range']
        result={'name':arm['name'],'side':arm['side'],'games':40,'invalid':sum(not r['valid'] for r in rows),'distinct_streams':len(unique),'duplicate_groups':[v for v in unique.values() if len(v)>1],'means':{k:mean(r[k] for r in rows) for k in keys},'score_ci95':ci([r['score'] for r in rows]),'by_class':{str(cls):{'n':sum(r['class']==cls for r in rows),**{k:mean(r[k] for r in rows if r['class']==cls) for k in keys}} for cls in sorted({r['class'] for r in rows})},'pooled_xp_per_minute':sum(r['xp'] for r in rows)/sum(r['minutes'] for r in rows),'team_wins':sum(r['win'] for r in rows),'opponents':comparisons,'rows':rows}
        h.write(folder/'review.json',result);cells.append(result)
    by={n:[c for c in cells if c['name']==n] for n in dict.fromkeys(c['name'] for c in cells)}
    before=by['baseline'];base=mean(c['means']['score'] for c in before);candidates=[]
    for name,after in by.items():
        if name=='baseline':continue
        new=mean(c['means']['score'] for c in after);rng=random.Random(922618);gains=[]
        for _ in range(10000):
            draw=[mean(rng.choices([r['score'] for r in c['rows']],k=40)) for c in before+after]
            b,n=mean(draw[:2]),mean(draw[2:]);gains.append((n/b-1)*100 if b else 0)
        gains.sort()
        passed=all(c['invalid']==0 for c in before+after) and new>base and new>=1.1*base and all(n['means']['score']>=.95*b['means']['score'] for b,n in zip(before,after))
        candidates.append({'name':name,'source_sha256':h.sha(study.source(name).read_bytes()),'score_gate_passed':passed,'baseline_score':base,'candidate_score':new,'aggregate_gain_percent':(new/base-1)*100,'gain_ci95_percent':[gains[250],gains[9750]],'per_color_gain_percent':[(n['means']['score']/b['means']['score']-1)*100 for b,n in zip(before,after)]})
    qualified=sorted([r for r in candidates if r['score_gate_passed']],key=lambda r:(-r['candidate_score'],r['name']))
    selected=qualified[0]['name'] if qualified else None
    changes=h.read(out/'field-changes.json')
    result={'complete':True,'stage':stage,'games':plan['games'],'engine_commit':plan['engine_commit'],'game_version':plan['game_version'],'selected':selected,'candidates':candidates,'cells':[{k:v for k,v in c.items() if k!='rows'} for c in cells],'field_changes':changes,'deployment_qualified':stage=='confirmation' and selected is not None and not changes['game_changed'] and not changes['champion_changes'],'evidence_scope':'Fresh controls and unmatched random seeds, one subject, fixed mixed roster;10 source hashes/VM exits, full replay hashes, XP sources and integer scores checked. Side-stratified independent whole-game bootstrap; duplicate streams disclosed. Screen is selection, not independent confirmation. No universal rank or per-component causality.'}
    h.write(out/'report.json',result);print(json.dumps({k:v for k,v in result.items() if k!='cells'}),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['screen','confirmation'],default='screen');p.add_argument('--watch',action='store_true');a=p.parse_args();out=STUDY/a.stage;total=h.read(out/'plan.json')['games']
    while True:
        files=list(out.glob('*/*/artifacts/*/result.json'));todo=[p for p in files if not (p.parent/'economy.json').exists()]
        with ThreadPoolExecutor(3) as pool:list(pool.map(decode,todo))
        count=len(list(out.glob('*/*/artifacts/*/economy.json')));h.write(out/'economy-progress.json',{'decoded':count,'total':total})
        if (out/'result.json').exists() and (out/'field-changes.json').exists() and count==total:build(a.stage);break
        if not a.watch:raise SystemExit('Incomplete. --watch streams complete replay decodes.')
        time.sleep(10)
