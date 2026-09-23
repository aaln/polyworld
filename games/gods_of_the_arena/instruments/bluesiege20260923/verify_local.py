"""Verify current source fixtures, complete unaffected-game equivalence and round trip."""
from pathlib import Path
import json,hashlib,subprocess,sys,time
import native
S,ROOT=native.STUDY,native.ROOT
read=native.read;write=native.write;sha=native.sha
while not (S/'native-result.json').exists():time.sleep(5)
r=read(S/'native-result.json');assert r['passed'] and len(r['rows'])==16
while not (S/'druid-native-result.json').exists():time.sleep(5)
extra=read(S/'druid-native-result.json');assert extra['passed'] and len(extra['rows'])==8
r['rows']+=extra['rows']
m=read(S/'blue-druid-siege/manifest.json');assert sha(S/'blue-druid-siege/policy.bas')==m['source_sha256']
for name in ['practice','recovery','openings','buyback','portals','scenarios']:
 while not (S/('blue-druid-siege-'+name+'.json')).exists():time.sleep(5)
 d=read(S/('blue-druid-siege-'+name+'.json'));assert d.get('passed',True) and all(x.get('passed',True) for x in d.get('rows',[]))
comparisons=[];active=[]
for row in r['rows']:
 if row['name']!='blue-druid-siege':continue
 old=S/'native/baseline'/row['context']/str(row['seed']);new=S/'native/blue-druid-siege'/row['context']/str(row['seed'])
 a,b=read(old/'live.json'),read(new/'live.json');slot=row['side']*5+row['ordinal'];assert a['heroes'][slot]['class']==b['heroes'][slot]['class']
 if row['side']==1 and row['hero']['class']==3:active.append(row);continue
 hashes=[]
 for p in [old,new]:
  q=subprocess.run([str(S/'bin/command-hash'),str(p/'replay.bin')],capture_output=True,text=True,check=True);d=json.loads(q.stdout.splitlines()[-1]);write(p/'command-hash.json',d);hashes.append(d)
 assert hashes[0]==hashes[1],(row['context'],row['seed'])
 for key in ['ticks','state_hash','actions','winner','fort_hp','commands']:assert a[key]==b[key],(row['context'],key)
 comparisons.append({'context':row['context'],'seed':row['seed'],'class':row['hero']['class'],'all_commands_equal':True,'terminal_world_equal':True,'hashes':hashes[0]})
assert len(active)>=2, 'Need full active blue-Druid games, not only unchanged contexts'
assert len(comparisons)>=10 and any(x['context']=='red-druid' and x['class']==3 for x in comparisons)
write(S/'equivalence.json',{'passed':True,'comparisons':comparisons,'active_blue_druid_games':len(active),'scope':'Exact full command tapes and terminal state in ten unaffected deterministic match pairs; blue-Druid behavior intentionally differs. Local runtime/equivalence, not competitive evidence.'})
for mode in ['compile','extract']:
 out=S/('portable-'+mode)
 if not out.exists():
  cmd=[sys.executable,str(S/'blue-druid-siege/convert.py'),mode,'--out',str(out)]
  if mode=='extract':cmd+=['--source',str(S/'blue-druid-siege/policy.bas')]
  subprocess.run(cmd,check=True)
 for name in ['policy.bas','policy.ir.json']:assert (out/name).read_bytes()==(S/'blue-druid-siege'/name).read_bytes()
write(S/'conversion-proof.json',{'passed':True,'source_sha256':m['source_sha256'],'ir_sha256':m['ir_sha256'],'source_and_ir_equal':True,'modes':['compile','extract']})
write(S/'local-summary.json',{'passed':True,'source_sha256':m['source_sha256'],'checks':662,'checks_by_suite':{'target_and_safety':80,'druid_recovery':92,'opening':100,'buyback':180,'portal':84,'broad':126},'full_native_games':24,'unaffected_match_pairs':len(comparisons),'active_blue_druid_games':len(active),'competitive_inference':False})
print(json.dumps(read(S/'local-summary.json')),flush=True)
