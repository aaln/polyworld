"""Preregistered32-game diagnostic subset; full400-game score verdict stays separate."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,subprocess,hashlib,statistics,time
ROOT=Path(__file__).resolve().parents[4];RAW=ROOT.parent/'polyworld/tmp/gota-unit-farming59-20260923';OUT=RAW/'trial';BIN=ROOT.parent/'polyworld/tmp/gota-khors179-audit-20260923/opportunity-audit'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
while not (OUT/'result.json').exists():time.sleep(10)
plan=read(OUT/'plan.json');cases=[]
for arm in plan['arms']:
 folder=OUT/arm['name']/arm['cell']
 for r in sorted(read(folder/'result.json')['rows'],key=lambda r:r['episode'])[:4]:
  cases.append({'name':arm['name'],'cell':arm['cell'],'slot':arm['own_slots'][0],'episode':r['episode']})
definition={'selection':'First4lexical episode UUIDs per cell; rule preregistered before hosted outcomes. Diagnostic subset only.','cases':cases,'binary_sha256':sha(BIN),'source_sha256':sha(Path(__file__).with_name('opportunity_audit.nim'))}
if (OUT/'effects-plan.json').exists():assert read(OUT/'effects-plan.json')==definition
else:write(OUT/'effects-plan.json',definition)
def one(case):
 f=OUT/case['name']/case['cell']/'artifacts'/case['episode'];dst=OUT/'effects'/case['episode']/'audit.json'
 if not dst.exists():
  p=subprocess.run([str(BIN),'--replay',str(f/'replay.bin')],capture_output=True,text=True,timeout=900);assert p.returncode==0,p.stderr;write(dst,json.loads(p.stdout.splitlines()[-1]))
 d=read(dst);assert d['hash_mismatches']==0;a=d['heroes'][case['slot']]['counts']
 b=sum(a.get('attack_target_'+k,0) for k in ['TowerBuilding','BarracksBuilding','god'])
 return {**case,'building_attack_commands':b,'unit_attack_commands':a.get('attack_target_hero',0)+a.get('attack_target_creep',0),'hero':d['heroes'][case['slot']],'audit_sha256':sha(dst)}
with ThreadPoolExecutor(3) as pool:rows=list(pool.map(one,cases))
summary={'plan':definition,'rows':rows,'totals':{n:{'games':sum(r['name']==n for r in rows),'building_attack_commands':sum(r['building_attack_commands'] for r in rows if r['name']==n),'unit_attack_commands':sum(r['unit_attack_commands'] for r in rows if r['name']==n)} for n in ['baseline','unit-farming']},'scope':'Actual submitted commands,32preselected games; not an independent competitive sample or source reconstruction.'}
write(OUT/'effects-summary.json',summary);print(json.dumps(summary['totals']))
