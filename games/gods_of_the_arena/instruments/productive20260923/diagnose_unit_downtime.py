"""Post-verdict descriptive follow-up on the same32 preselected unit-farming games."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json,subprocess,hashlib,statistics
ROOT=Path(__file__).resolve().parents[4];RAW=ROOT.parent/'polyworld/tmp/gota-unit-farming59-20260923';OUT=RAW/'trial';BIN=RAW/'bin/stalls'
read=lambda p:json.loads(p.read_text())
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
cases=read(OUT/'effects-plan.json')['cases']
def one(case):
 src=OUT/case['name']/case['cell']/'artifacts'/case['episode']/'replay.bin';dst=OUT/'downtime'/case['episode']/'audit.json'
 if not dst.exists():
  p=subprocess.run([str(BIN),'--replay',str(src)],capture_output=True,text=True,timeout=900);assert p.returncode==0,p.stderr;write(dst,json.loads(p.stdout.splitlines()[-1]))
 d=read(dst);assert d['hash_mismatches']==0 and d['all_actions_consumed'];h=d['heroes'][case['slot']]
 return {**case,'totals':h['totals'],'max_without_xp_minutes':h['max_without_xp_ticks']/1440,'full_minutes':sum(w['full_minute'] for w in h['windows']),'full_minutes_over200xp':sum(w['full_minute'] and w['values'].get('xp',0)>200 for w in h['windows'])}
with ThreadPoolExecutor(3) as pool:rows=list(pool.map(one,cases))
s={}
for n in ['baseline','unit-farming']:
 rs=[r for r in rows if r['name']==n];keys=sorted({k for r in rs for k in r['totals']})
 s[n]={'games':len(rs),'means':{k:statistics.mean(r['totals'].get(k,0)/(1440 if k.endswith('_ticks') else 1) for r in rs) for k in keys},'mean_max_without_xp_minutes':statistics.mean(r['max_without_xp_minutes'] for r in rs),'full_minutes':sum(r['full_minutes'] for r in rs),'full_minutes_over200xp':sum(r['full_minutes_over200xp'] for r in rs)}
result={'scope':'Post-verdict descriptive follow-up, same32 preselected cases. Not a new qualification metric or independent competitive sample. Full post-tick truth; no target does not prove inactivity. Drought includes preceding dead time.','rows':rows,'summary':s,'binary_sha256':hashlib.sha256(BIN.read_bytes()).hexdigest()};write(OUT/'downtime-summary.json',result);print(json.dumps(s))
