"""Fit once on distinct training trajectories, freeze before opening heldout."""
import argparse,datetime,gzip,hashlib,json
from collections import Counter
from pathlib import Path
from semantics import PARAMETERS,fit

def main():
 p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args();d=a.directory
 if (d/'model-freeze.json').exists():raise SystemExit('Refusing to replace frozen model')
 plan=json.loads((d/'study-plan.json').read_text());data={'train':[],'population':[]};seen=set();used=[]
 for row in plan['episodes']:
  if row['split']=='heldout':continue
  f=d/'artifacts'/row['id'];proof=json.loads((f/'observer-validation.json').read_text());key=(row['split'],proof['observable_sha256'])
  if key in seen:continue
  seen.add(key);used.append(row['id'])
  with gzip.open(f/'observations.jsonl.gz','rt') as stream:data[row['split']].extend(json.loads(l) for l in stream)
 result={'frozen_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'parameters':PARAMETERS,
   'models':{s:fit(rs) for s,rs in data.items()},'training_episode_ids':used,
   'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')},
   'notes':'Heldout has not been decoded. Parameters/segmentation and predictor are frozen. Training and population use one episode per exact observer trajectory. Predictions are conditional on retrospective motif starts, not predictions of event timing.'}
 (d/'model-freeze.json').write_text(json.dumps(result,indent=2)+'\n')
 for split,rows in data.items():
  print(split,'segments',len(rows),'eligible',sum(r['preference_eligible'] for r in rows),'choice',Counter(r['selected'] for r in rows if r['preference_eligible']))
  for key,c in result['models'][split]['contexts'].items():print(key,sum(c.values()),Counter(c).most_common(3))
if __name__=='__main__':main()
