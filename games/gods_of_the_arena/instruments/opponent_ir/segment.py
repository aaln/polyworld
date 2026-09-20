"""Annotate every sustained visible motif start, with preselection affordances."""
import argparse,gzip,json,hashlib
from collections import Counter
from pathlib import Path
from semantics import *

def analyze(row,folder):
 segments=[];active={};last_view={};last_tick=None;previous_labels={};visible_ticks=0;residual=0;ownteam=row['observer_slot']//5;fort=None;header=None
 def close(hero_id,reason):
  nonlocal residual
  s=active.pop(hero_id);n=s['end_tick']-s['tick']+1
  if n<PARAMETERS['minimum_segment_ticks']:
   residual+=n;return
  target=s.pop('_target_start');ending=s.pop('_target_end');start=s.pop('_first');end=s.pop('_last')
  s.update({'duration_ticks':n,'termination':reason,'outcome':{'hp_change':end[HP]-start[HP],
    'displacement_tiles':round(distance(start,end),3),'distance_to_our_god_change':round(distance(end,fort)-distance(start,fort),3),
    'target_hp_change':ending[HP]-target[HP] if target and ending else None,
    'target_hp_attribution':'aggregate visible HP change; not attributed to this hero; null if endpoint target not visible',
    'terminal_event':'visibility loss is censored, never inferred death'},'concurrent_movement':dict(s['concurrent_movement'])})
  s['id']=f"{row['id']}.h{hero_id}.t{s['tick']}"
  s['preference_eligible']=s['predictor_tick'] is not None and s['selected'] in s['affordances'] and len(s['affordances'])>=2
  s['exclusion']=None if s['preference_eligible'] else 'left_censored' if s['predictor_tick'] is None else 'selected_skill_not_established_by_prior_affordances'
  segments.append(s)
 with gzip.open(folder/'observer.jsonl.gz','rt') as f:
  for line in f:
   data=json.loads(line)
   if data['type']=='header':header=data;continue
   if data['type']!='view':continue
   tick=data['tick'];objects={o[I]:o for o in data['objects']};opponents={i:o for i,o in objects.items() if o[K]==2 and o[T]!=ownteam and o[ALIVE] and o[HP]>0}
   fort=next((o for o in objects.values() if o[K]==1 and o[T]==ownteam),fort)
   if fort is None:continue
   visible_ticks+=len(opponents)
   for hid in list(active):
    if hid not in opponents:close(hid,'observer_dead' if not data['available'] else 'visibility_lost_or_not_alive')
   for hid,o in opponents.items():
    selected,target_id,movement=classify(o,objects,fort);key=(selected,target_id)
    if hid in active and active[hid]['motif_key']!=list(key):close(hid,'visible_target_change' if active[hid]['target_id']!=target_id else 'movement_character_change')
    if hid not in active:
     before=last_view.get(hid);continuous=before is not None and before[ALIVE] and before[HP]>0 and last_tick==tick-1
     prior=before if continuous else o;view=last_view if continuous else objects
     fs,aff,basis=features(prior,view,fort,header['terrain'],previous_labels.get(hid) if continuous else None)
     active[hid]={'episode':row['id'],'opponent_version':row['opponent_version'],'level':'individual' if row['split']!='population' else 'population',
      'split':row['split'],'observer_slot':row['observer_slot'],'opponent_hero_id':hid,'tick':tick,'end_tick':tick,'predictor_tick':tick-1 if continuous else None,
      'visibility':{'opponent_visible':True,'observer_alive':True,'left_censored':not continuous,'visible_object_ids':list(objects),'perspective':'single policy instance predecision snapshot'},
      'situation':fs,'affordances':aff,'affordance_evidence':basis,'selected':selected,'target_id':target_id,'motif_key':list(key),
      '_first':o,'_last':o,'_target_start':objects.get(target_id),'_target_end':objects.get(target_id),'concurrent_movement':Counter(),
      'unglossed':['estimated_opponent_affordances','visible_target_not_attack','concurrent_target_and_motion','absolute_low_hp','observer_relative_advance']}
    s=active[hid];s['end_tick']=tick;s['_last']=o;s['_target_end']=objects.get(target_id);s['concurrent_movement'][movement]+=1
   previous_labels={hid:classify(o,objects,fort)[0] for hid,o in opponents.items()};last_view=objects;last_tick=tick
 for hid in list(active):close(hid,'episode_end')
 segments.sort(key=lambda r:(r['tick'],r['opponent_hero_id']))
 summary={'episode':row['id'],'split':row['split'],'visible_hero_ticks':visible_ticks,'residual_ticks':residual,'residual_fraction':residual/visible_ticks if visible_ticks else None,
  'segments':len(segments),'eligible':sum(r['preference_eligible'] for r in segments),'exclusions':dict(Counter(r['exclusion'] for r in segments if r['exclusion']))}
 assert residual+sum(r['duration_ticks'] for r in segments)==visible_ticks
 return segments,summary

def main():
 p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--heldout',action='store_true');a=p.parse_args();d=a.directory
 if a.heldout and not (d/'model-freeze.json').exists():raise SystemExit('Model must be frozen first')
 rows=json.loads((d/'study-plan.json').read_text())['episodes'];stats=[]
 for row in rows:
  if (row['split']=='heldout')!=a.heldout:continue
  folder=d/'artifacts'/row['id'];segments,summary=analyze(row,folder)
  with gzip.open(folder/'observations.jsonl.gz','wt') as f:
   for s in segments:f.write(json.dumps(s,separators=(',',':'))+'\n')
  (folder/'segmentation.json').write_text(json.dumps(summary,indent=2)+'\n');stats.append(summary)
  print(row['split'],row['id'],summary['segments'],summary['eligible'],round(summary['residual_fraction'],3),flush=True)
 (d/('heldout-segmentation.json' if a.heldout else 'training-segmentation.json')).write_text(json.dumps(stats,indent=2)+'\n')
if __name__=='__main__':main()
