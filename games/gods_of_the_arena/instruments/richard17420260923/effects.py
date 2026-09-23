"""Exact subject-VM reconstruction on a prospectively selected mechanism subset."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse,json,subprocess,time,hashlib,statistics,os
import siege_hosted as study
ROOT,STUDY=study.ROOT,study.STUDY
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def main():
 p=argparse.ArgumentParser();p.add_argument('--watch',action='store_true');a=p.parse_args();out=STUDY/'trial'
 plan=read(out/'plan.json')
 def select(arm):
  cell=read(out/arm['name']/arm['cell']/'result.json')
  return [{'name':arm['name'],'cell':arm['cell'],'side':arm['side'],'slot':arm['own_slots'][0],'episode':row['episode'],'class':row['class'],'source_sha256':arm['source_sha256']} for row in sorted(cell['rows'],key=lambda r:r['episode'])[:4]]
 def decode(c):
  src=out/c['name']/c['cell']/'artifacts'/c['episode'];dst=out/'effects'/c['episode']/'audit.json';policy=study.source(c['name'])
  assert sha(policy)==c['source_sha256']==read(src/'spec.json')['players'][c['slot']]['content_hash']
  if not dst.exists():
   env={**os.environ,'AUDIT_KIND':'ours','AUDIT_TRANSFER':'1' if c['name']=='guarded-siege' else '0','AUDIT_POLICY':str(policy),'AUDIT_SLOTS':str(c['slot'])}
   cmd=[str(STUDY/'effect-probe-r2'),'--replay',str(src/'replay.bin')]
   write(dst.parent/'command.json',{'command':cmd,'audit_kind':'ours','policy':str(policy),'slot':c['slot'],'replay_sha256':sha(src/'replay.bin')})
   q=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=900)
   (dst.parent/'stdout.log').write_text(q.stdout);(dst.parent/'stderr.log').write_text(q.stderr);assert q.returncode==0,q.stderr[-1200:]
   write(dst,json.loads(q.stdout.splitlines()[-1]))
  d=read(dst);assert d['all_state_hashes_equal'] and d['all_actions_consumed']
  result={**c,**d,'audit_sha256':sha(dst)};print(json.dumps({k:result[k] for k in ['name','cell','episode','commands_matched','counts']}),flush=True);return result
 # Decode already-complete cells while the remaining cells run. The final
 # sample is still the exact prospectively specified first4 per complete cell.
 # Timing changes no source, sample size, ordering, endpoint or score gate.
 rows=[];done=set()
 while len(done)<len(plan['arms']):
  ready=[arm for arm in plan['arms'] if (arm['name'],arm['cell']) not in done and (out/arm['name']/arm['cell']/'result.json').exists()]
  todo=[case for arm in ready for case in select(arm)]
  with ThreadPoolExecutor(2) as pool:rows.extend(pool.map(decode,todo))
  done.update((arm['name'],arm['cell']) for arm in ready)
  if len(done)<len(plan['arms']):
   if not a.watch:raise SystemExit('Incomplete cells; --watch resumes saved decodes')
   time.sleep(10)
 cases=[case for arm in plan['arms'] for case in select(arm)]
 rows_by_id={r['episode']:r for r in rows};rows=[rows_by_id[c['episode']] for c in cases]
 definition={'selection':'First4 lexical episode UUIDs per source/context, chosen in prospective-experiment.md before hosted spend. Retrospective descriptive subset, no independent competitive gate.','cases':cases,'instrument_sha256':sha(Path(__file__).with_name('source_probe.nim')),'binary_sha256':sha(STUDY/'effect-probe-r2'),'execution':'Decode complete cells as available; final sample checked against all complete cells, identical to the frozen selection.','instrument_revision':'r2: query pressureChoice only in the new source; absent baseline global raised a diagnostic error. Failed logs and r1 preserved; no hosted policy bytes changed.'}
 path=out/'effects-plan.json'
 if path.exists():assert read(path)==definition
 else:write(path,definition)
 cells=[]
 for arm in plan['arms']:
  r=[x for x in rows if x['name']==arm['name'] and x['cell']==arm['cell']];keys=sorted({k for x in r for k in x['counts']})
  cells.append({'name':arm['name'],'cell':arm['cell'],'n':len(r),'mean_counts':{k:statistics.mean(x['counts'].get(k,0) for x in r) for k in keys},'classes':[x['class'] for x in r]})
 write(out/'effects-summary.json',{'plan':definition,'cells':cells,'rows':rows,'scope':'32-game descriptive source reconstruction; guards and submitted commands are not landed damage or causal score contribution. Full400-game score qualification remains separate.'})
 print(json.dumps({'completed':len(rows),'cells':cells}),flush=True)
if __name__=='__main__':main()
