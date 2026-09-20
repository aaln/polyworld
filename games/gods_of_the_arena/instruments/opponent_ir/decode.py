"""Decode existing tapes into observer-only, hash-verified gzip JSONL."""
import argparse,concurrent.futures,gzip,hashlib,json,os,subprocess
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--heldout',action='store_true');a=p.parse_args();d=a.directory.resolve()
 if a.heldout and not (d/'model-freeze.json').exists():raise SystemExit('Freeze the training model before decoding heldout behavior')
 plan=json.loads((d/'study-plan.json').read_text());rows=[r for r in plan['episodes'] if (r['split']=='heldout')==a.heldout]
 def decode(r):
  folder=d/'artifacts'/r['id'];out=folder/'observer.jsonl.gz';proof=folder/'observer-validation.json'
  if proof.exists() and out.exists():return
  env=dict(os.environ,OBSERVER_SLOT=str(r['observer_slot']));h=hashlib.sha256();validation=None
  with (folder/'observer.stderr').open('w') as err:
   proc=subprocess.Popen([str(d/'observer-probe'),'--replay',str(folder/'replay.bin')],env=env,stdout=subprocess.PIPE,stderr=err)
   with gzip.open(str(out)+'.tmp','wb',compresslevel=4) as f:
    for line in proc.stdout:
     f.write(line)
     if line.startswith(b'{"type":"view"'):h.update(line)
     if line.startswith(b'{"type":"validation"'):validation=json.loads(line)
   if proc.wait()!=0 or not validation:raise RuntimeError(f'Replay verification failed: {r["id"]}')
  Path(str(out)+'.tmp').replace(out);validation['observable_sha256']=h.hexdigest();proof.write_text(json.dumps(validation,indent=2)+'\n')
  print(r['split'],r['id'],validation['ticks'],'verified',flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(decode,rows))
if __name__=='__main__':main()
