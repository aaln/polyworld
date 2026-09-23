"""Manual coaching verification using all200 existing baseline games; no new hosted spend."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,subprocess,hashlib,statistics
ROOT=Path(__file__).resolve().parents[4];RAW=ROOT.parent/'polyworld/tmp/gota-manual-score20260923';OLD=ROOT.parent/'polyworld/tmp/gota-unit-farming59-20260923';BIN=RAW/'manual-economy';OUT=ROOT/'docs/coaching/2026-09-23-manual-score/evidence'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
report=read(OLD/'trial/report.json');assert report['complete'] and report['games']==400
rivals={'Andre khors180':'564e4650-5efb-4b66-b9d4-a49070e1e68e','Richard195':'19d5c60e-b0d4-4382-b253-fabcfd03f896'}
cases=[]
for arm in read(OLD/'trial/plan.json')['arms']:
 if arm['name']!='baseline':continue
 folder=OLD/'trial'/arm['name']/arm['cell'];rows=read(folder/'review.json')['rows']
 for r in rows:
  assert r['valid'] and not r['failed_slots']
  cases.append({'episode':r['episode'],'context':arm['cell'],'own_slot':arm['own_slots'][0],'rival_slots':{k:arm['roster'].index(v) for k,v in rivals.items()},'folder':str(folder/'artifacts'/r['episode']),'replay_sha256':r['replay_sha256'],'own_score':r['score']})
plan={'selection':'All200baseline controls from completed unit-farming trial; none selected by resource outcome. User screenshots motivate hypotheses only. Same episode comparisons retain class/side/draft confounds.','cases':cases,'engine_commit':'d6827a4bd3a55a46cf86f88e921f147137709c64','binary_sha256':sha(BIN),'source_sha256':sha(Path(__file__).with_name('manual_economy.nim')),'new_hosted_games':0}
assert len(cases)==200
if (RAW/'plan.json').exists():assert read(RAW/'plan.json')==plan
else:write(RAW/'plan.json',plan)
def decode(src,dst):
 if not dst.exists():
  p=subprocess.run([str(BIN),'--replay',str(src)],capture_output=True,text=True,timeout=900)
  dst.parent.mkdir(parents=True,exist_ok=True);dst.with_suffix('.stderr').write_text(p.stderr);assert p.returncode==0,p.stderr;write(dst,json.loads(p.stdout.splitlines()[-1]))
 d=read(dst);assert d['hash_mismatches']==0 and d['all_actions_consumed'];return d
# Calibration against an independently decoded full episode before aggregate use.
cal=ROOT.parent/'polyworld/tmp/gota-khors179-audit-20260923/episodes/ereq_e3471c64-b38e-4bfc-927e-e0e3f3076d9d'
d=decode(cal/'replay.bin',RAW/'calibration/audit.json');gold=read(cal/'combat-audit.json');econ=read(cal/'economy.json')
for i in range(10):
 assert d['heroes'][i]['xp']==econ['heroes'][i]['total_xp']
 assert d['heroes'][i]['counts'].get('gold_spent',0)==gold['heroes'][i]['totals'].get('gold_spent',0)
 assert d['heroes'][i]['counts'].get('hero_kills',0)==econ['heroes'][i]['hero_kills']
write(RAW/'calibration-proof.json',{'passed':True,'episode':cal.name,'all10_xp_gold_kills_equal':True,'all_state_hashes_equal':True})
def one(c):
 src=Path(c['folder']);assert sha(src/'replay.bin')==c['replay_sha256']
 d=decode(src/'replay.bin',RAW/'episodes'/c['episode']/'audit.json');eco=read(src/'economy.json');result=read(src/'results.json');ps=read(src/'player-status.json')
 assert len(ps['players'])==10 and all(p['exit_code']==0 for p in ps['players'])
 rows=[]
 for label,slot in {'ours':c['own_slot'],**c['rival_slots']}.items():
  h=d['heroes'][slot];e=eco['heroes'][slot];counts=h['counts'];xp=counts.get('xp_creep_at_last_hit',0)+counts.get('xp_creep_shared',0)
  assert h['xp']==e['total_xp'] and xp==e['xp_sources'].get('creep',0)
  assert counts.get('hero_kills',0)==e['hero_kills'] and counts.get('creep_last_hits',0)==e['creep_last_hits']
  assert counts.get('rejected',0)==sum(e['rejected'].values())
  assert result['scores'][slot]==max(0,h['xp']*1440-200*d['ticks'])//1440
  rows.append({'label':label,'episode':c['episode'],'context':c['context'],'slot':slot,'class':h['class'],'score':result['scores'][slot],'xp':h['xp'],'minutes':d['ticks']/1440,'gold_end':h['gold_end'],'deaths':h['deaths'],'counts':counts,'replay_sha256':c['replay_sha256']})
 return rows
with ThreadPoolExecutor(3) as pool:groups=list(pool.map(one,cases))
rows=[r for g in groups for r in g]
def aggregate(rs):
 keys=sorted({k for r in rs for k in r['counts']})
 return {'n':len(rs),'means':{k:statistics.mean(r['counts'].get(k,0) for r in rs) for k in keys},'mean_score':statistics.mean(r['score'] for r in rs),'mean_gold_end':statistics.mean(r['gold_end'] for r in rs),'mean_minutes':statistics.mean(r['minutes'] for r in rs),'mean_rejected_share':statistics.mean(r['counts'].get('rejected',0)/max(1,r['counts'].get('orders',0)) for r in rs),'pooled_hero_kills_per_field_minute':sum(r['counts'].get('hero_kills',0) for r in rs)/max(1,sum(r['counts'].get('field_ticks',0) for r in rs)/1440),'pooled_creep_xp_per_field_minute':sum(r['counts'].get('xp_creep_at_last_hit',0)+r['counts'].get('xp_creep_shared',0) for r in rs)/max(1,sum(r['counts'].get('field_ticks',0) for r in rs)/1440),'class_counts':{cl:sum(r['class']==cl for r in rs) for cl in sorted({r['class'] for r in rs})}}
summary={}
for label in ['ours',*rivals]:
 rs=[r for r in rows if r['label']==label]
 summary[label]={'overall':aggregate(rs),'contexts':{c:aggregate([r for r in rs if r['context']==c]) for c in sorted({r['context'] for r in rs})},'classes':{c:aggregate([r for r in rs if r['class']==c]) for c in sorted({r['class'] for r in rs})}}
result={'complete':True,'games':200,'rows':rows,'summary':summary,'scope':'Existing exact-engine baseline cohort, all10VMs healthy. Same episode does not equal same class, role, team or opportunity. Source/score/XP identities and typed resource counters reconciled; spending effects remain untested.','new_hosted_games':0}
write(RAW/'analysis.json',result);write(OUT/'current-engine-analysis.json',result);write(OUT/'audit-plan.json',plan);write(OUT/'calibration-proof.json',read(RAW/'calibration-proof.json'))
print(json.dumps({k:v['overall'] for k,v in summary.items()}),flush=True)
