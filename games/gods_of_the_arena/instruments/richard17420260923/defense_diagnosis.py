"""Retrospective diagnostic of redundant home navigation, never a score gate."""
import os,json,subprocess,hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import siege_hosted as s
read=s.h.read;write=s.h.write;S=s.STUDY
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cases=[]
for cell,slot in [('red-late',3),('blue-late',8)]:
 d=read(S/'trial/baseline'/cell/'result.json')
 for row in sorted(d['rows'],key=lambda r:r['episode'])[:4]:cases.append({'cell':cell,'slot':slot,'episode':row['episode']})
plan={'cases':cases,'selection':'First4 lexical baseline episode IDs in each late-draft context, same subset as frozen main mechanism audit. Added retrospectively after red-late transfer failed; diagnosis only.','source_sha256':sha(s.source('baseline')),'instrument_sha256':sha(Path(__file__).with_name('defense_probe.nim')),'binary_sha256':sha(S/'defense-probe')}
s.h.freeze(S/'defense-diagnosis-plan.json',plan)
def run(c):
 out=S/'defense-diagnosis'/c['episode'];replay=S/'trial/baseline'/c['cell']/'artifacts'/c['episode']/'replay.bin'
 if not (out/'result.json').exists():
  out.mkdir(parents=True,exist_ok=True);env={**os.environ,'AUDIT_KIND':'ours','AUDIT_TRANSFER':'0','AUDIT_POLICY':str(s.source('baseline')),'AUDIT_SLOTS':str(c['slot'])}
  q=subprocess.run([str(S/'defense-probe'),'--replay',str(replay)],env=env,text=True,capture_output=True,timeout=900)
  (out/'stdout.log').write_text(q.stdout);(out/'stderr.log').write_text(q.stderr);assert q.returncode==0,q.stderr[-1000:]
  write(out/'result.json',json.loads(q.stdout.splitlines()[-1]))
 d=read(out/'result.json');assert d['all_state_hashes_equal'] and d['all_actions_consumed'];print(json.dumps({**c,'counts':d['counts']}),flush=True);return {**c,**d}
with ThreadPoolExecutor(2) as pool:rows=list(pool.map(run,cases))
write(S/'defense-diagnosis.json',{'plan':plan,'rows':rows,'scope':'Eight current-baseline replays; redundant navigation is descriptive and may be useful team cover. No assumed causal point gain.'})
