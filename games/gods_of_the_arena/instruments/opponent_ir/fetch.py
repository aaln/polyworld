"""Freeze a chronological opponent study, then download existing artifacts (GET only)."""
import argparse, concurrent.futures, datetime, gzip, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'examples/gods_of_the_arena/players/ir'))
from hosted_wave import client

def write(p,data): p.write_text(json.dumps(data,indent=2)+'\n')
def main():
 p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args();d=a.directory
 if not (d/'study-plan.json').exists():
  source=json.loads((d/'eligible.json').read_text())
  jordan=sorted(source['jordan'],key=lambda r:(r['episode']['created_at'],r['episode']['id']))
  cutoff=jordan[-4]['episode']['created_at']; groups={}
  for r in sorted(source['population'],key=lambda r:(r['episode']['created_at'],r['episode']['id'])):
   e=r['episode'];slot=5-r['observer_slot']
   if e['created_at']<cutoff: groups.setdefault((e['policy_version_ids'][slot],r['observer_slot']),r)
  rows=[]
  for split,rs in [('train',jordan[:-4]),('heldout',jordan[-4:]),('population',list(groups.values()))]:
   for r in rs:
    e=r['episode'];other=e['participants'][5-r['observer_slot']]
    rows.append({'id':e['id'],'created_at':e['created_at'],'observer_slot':r['observer_slot'],'split':split,'opponent_version':other['policy_version_id'],'opponent_label':other['policy_name']+':v'+str(other['version']),'version':e['coworld_version']})
  plan={'schema':'gota-opponent-study/1','frozen_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'target_version':'207ffaf9-0d1e-4d92-a15d-4352f1bddec2','selection':'All exact-version Jordan vs our two pinned policy versions in latest 20 completed rounds; outcomes ignored. Population: earliest episode per non-Jordan opponent-version and observer side before heldout cutoff.','holdout':'Chronologically last 4/20 Jordan episodes; no behavioral inspection until feature/model freeze.','observation':'One real policy instance (slot 0 or 5); predecision visibility only; no pooling teammate sensor views. Enemy VM commands excluded.','validation':'Skill starts inferred from visible targets/velocity; lagged preselection features. Report censored selections, residual, per-statement n and heldout accuracy vs conditional population and persistence. n<8 or heldout accuracy <= population => provisional. Duplicate observable trajectories are not independent evidence. Proxy unusable without rollout validation.','episodes':rows}
  write(d/'study-plan.json',plan)
 plan=json.loads((d/'study-plan.json').read_text());source=json.loads((d/'eligible.json').read_text());meta={r['episode']['id']:r['episode'] for rs in source.values() for r in rs}
 def fetch(row):
  folder=d/'artifacts'/row['id'];folder.mkdir(parents=True,exist_ok=True);write(folder/'episode.json',meta[row['id']])
  with client() as c:
   for kind,name in [('results','results.json'),('replay','replay.bin'),('logs','game.log')]:
    path=folder/name
    if path.exists():continue
    response=c.get(f"/v2/episode-requests/{row['id']}/artifacts/{kind}");response.raise_for_status();body=response.content
    if kind=='replay' and body.startswith(b'\x1f\x8b'):body=gzip.decompress(body)
    path.write_bytes(body)
  write(folder/'checksums.json',{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir() if p.is_file() and p.name!='checksums.json'})
  print(row['split'],row['id'],'downloaded',flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(fetch,plan['episodes']))
 print('Complete',len(plan['episodes']))
if __name__=='__main__':main()
