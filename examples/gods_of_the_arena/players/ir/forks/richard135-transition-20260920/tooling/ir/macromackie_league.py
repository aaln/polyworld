"""Gather comparable full-team league episodes across a pinned round snapshot."""
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from hosted_wave import client
from league_threat_watch import page_all
from policy_ir import read,write
from macromackie_review import ROOT

def one(x):
 path=ROOT/'recent-rounds'/x['id']/'episodes.json';path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():rows=read(path)
 else:
  with client() as c:rows=page_all(c,f'/v2/rounds/{x["id"]}/episodes?limit=1000')
  write(path,rows)
 out=[]
 for e in rows:
  pp={p['position']:p for p in e['participants']};scores={p['position']:p['score'] for p in e['participant_scores']}
  for v,label in [('9cedf3ff-c7ce-4cff-897f-d48b44e049ad','anchor'),('b64f1ccb-02e1-4ad5-b75b-f374222e9e9a','blue_repair')]:
   ss={s for s,p in pp.items() if p['policy_version_id']==v}
   if ss not in (set(range(5)),set(range(5,10))):continue
   others={p['policy_version_id'] for s,p in pp.items() if s not in ss}
   if others!={'1a78a3f9-8112-4c2c-831a-f0ffee8dbacc'}:continue
   out.append({'episode':e['id'],'round':x['id'],'policy':label,'color':'red' if 0 in ss else 'blue','score':scores.get(min(ss)),'status':e['status'],'version':v})
 return out
if __name__=='__main__':
 with ThreadPoolExecutor(4) as p:matches=[y for z in p.map(one,read(ROOT/'recent-rounds.json')) for y in z]
 write(ROOT/'recent-league-matched.json',matches)
 print(Counter((x['policy'],x['color'],x['score']) for x in matches));print(matches)
