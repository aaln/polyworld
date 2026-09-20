"""Source-matched review of the user-selected macromackie v4 league loss."""
from pathlib import Path
from collections import Counter
import json
from policy_ir import read,write
from release_workspace import RUN
ROOT=RUN/'coached-lanes/r5-macromackie-v4'
EPISODE='ereq_fbb5fabf-5c5c-4b11-8740-4954f719341f'

def main():
 p=ROOT/'artifacts'/EPISODE
 frames=[];actions=[]
 for line in (p/'decoded.jsonl').open():
  r=json.loads(line)
  if r['type']=='frame':frames.append(r)
  elif r['type']=='action':actions.append(r)
 decisions=[json.loads(x) for x in (p/'decisions.jsonl').open()]
 last={};events=[]
 for f in frames:
  for b in f['buildings']:
   if b['id'] in last and last[b['id']]['hp']>0 and b['hp']<=0:events.append({'tick_at_or_before':f['tick'],'after_tick':f['tick']-120,**b})
   last[b['id']]=b
 counts=[]
 for start in range(0,9600,960):
  rr=[r for r in decisions if r.get('type')=='decision' and start<=r['tick']<start+960]
  counts.append({'start':start,'end':start+960,'slots':{str(s):dict(Counter((str(r['memory'].get('defActive'))+':target'+str(bool(r['memory'].get('bestId')))) for r in rr if r['slot']==s)) for s in range(5)}})
 selected={}
 for t in (1800,2400,2880,3600,4800,5520,6720,8640,9000,9120,9240,9360,9480):
  fr=min(frames,key=lambda f:abs(f['tick']-t))
  ds=[r for r in decisions if r.get('type')=='decision' and r['tick']==fr['tick']]
  selected[str(fr['tick'])]={'heroes':[{k:h[k] for k in ('slot','class','position','hp','target','hits','inventory')} for h in fr['heroes']], 'decisions':ds,'standing_red':[{k:b[k] for k in ('id','kind','hp')} for b in fr['buildings'] if b['team']==0 and b['hp']>0]}
 write(ROOT/'timeline.json',{'episode':EPISODE,'structure_losses':events,'defense_samples':counts,'checkpoints':selected,'scope':'Sampled frames every120ticks; structure loss lieswithinpreceding120tickwindow. Nativeownedcommands fullymatched; observed associations not isolatedcausal effects.'})
 print('Structure losses',[(r['tick_at_or_before'],r['id'],r['team'],r['kind']) for r in events])
 for t in ('2400','2880','5520','6720','9000','9240','9480'):
  q=selected[t]
  print('TICK',t,'REDSTRUCTURES',q['standing_red'])
  for r in q['decisions']:
   print(r['slot'],{k:r['memory'].get(k) for k in ('bestId','defActive','defUntil','defFront','defCount','defAnchor','defPointX','defPointY','aaReady','aaCommitted')},r['actions'])
if __name__=='__main__':main()
