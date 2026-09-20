"""Evaluate a frozen model and assemble counted evidence, without refitting."""
import argparse,gzip,hashlib,json,random,statistics
from collections import Counter,defaultdict
from pathlib import Path
from semantics import SKILLS,context,predict

def rate(a,n):return a/n if n else None

def score(rows,models):
 preds=[]
 for r in rows:
  if not r['preference_eligible']:continue
  pred,probs,key=predict(models['train'],r['situation'],r['affordances']);base,bprobs,_=predict(models['population'],r['situation'],r['affordances']);actual=r['selected']
  preds.append({'observation':r['id'],'episode':r['episode'],'context':key,'actual':actual,'prediction':pred,'probabilities':probs,'population':base,'population_probabilities':bprobs,
   'correct':pred==actual,'population_correct':base==actual,'persistence_correct':r['situation']['previous_skill']==actual,'uniform_probability':1/len(r['affordances'])})
 return preds

def metrics(preds):
 n=len(preds);correct=sum(p['correct'] for p in preds);base=sum(p['population_correct'] for p in preds)
 return {'n':n,'correct':correct,'accuracy':rate(correct,n),'population_correct':base,'population_accuracy':rate(base,n),
  'persistence_accuracy':rate(sum(p['persistence_correct'] for p in preds),n),'uniform_expected_accuracy':rate(sum(p['uniform_probability'] for p in preds),n)}

def confidence_interval(preds,episode_group):
 groups=defaultdict(list)
 for p in preds:groups[episode_group[p['episode']]].append(p)
 # Cluster by exact observer trajectory; repeated tapes inside a group counted once.
 unique=[]
 for rs in groups.values():
  ep=rs[0]['episode'];unique.append([p for p in rs if p['episode']==ep])
 if len(unique)<2:return {'clusters':len(unique),'lift_95pct':None,'note':'Too few distinct observable trajectories'}
 rng=random.Random(192026);samples=[]
 for _ in range(2000):
  sample=[p for g in rng.choices(unique,k=len(unique)) for p in g];samples.append(sum(int(p['correct'])-int(p['population_correct']) for p in sample)/len(sample))
 samples.sort();return {'clusters':len(unique),'lift_95pct':[samples[49],samples[1949]],'method':'2000 bootstrap resamples of distinct full observer trajectories; descriptive with few clusters'}

def main():
 p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args();d=a.directory;plan=json.loads((d/'study-plan.json').read_text());frozen=json.loads((d/'model-freeze.json').read_text())
 for name in ['semantics.py','segment.py']:
  assert hashlib.sha256((Path(__file__).parent/name).read_bytes()).hexdigest()==frozen['source_sha256'][name],f'Frozen source changed: {name}'
 data={};proofs={};stats={};metadata={};groups={};results={}
 for row in plan['episodes']:
  folder=d/'artifacts'/row['id'];metadata[row['id']]=row
  with gzip.open(folder/'observations.jsonl.gz','rt') as f:data[row['id']]=[json.loads(l) for l in f]
  proof=json.loads((folder/'observer-validation.json').read_text());proofs[row['id']]=proof;groups[row['id']]=proof['observable_sha256']
  stats[row['id']]=json.loads((folder/'segmentation.json').read_text());results[row['id']]=json.loads((folder/'results.json').read_text())
 train_ids=[i for i in frozen['training_episode_ids'] if metadata[i]['split']=='train'];pop_ids=[i for i in frozen['training_episode_ids'] if metadata[i]['split']=='population'];hold_ids=[r['id'] for r in plan['episodes'] if r['split']=='heldout'];train_hash={groups[i] for i in train_ids};novel=[i for i in hold_ids if groups[i] not in train_hash]
 train=[r for i in train_ids for r in data[i]];pop=[r for i in pop_ids for r in data[i]];held=[r for i in hold_ids for r in data[i]]
 predictions=score(held,frozen['models']);summary=metrics(predictions);summary['cluster_uncertainty']=confidence_interval(predictions,groups)
 summary['novel_trajectories']=metrics([p for p in predictions if p['episode'] in novel]);summary['novel_episode_ids']=novel
 robust={}
 for label in ['class','side']:
  counts=defaultdict(Counter)
  for r in pop:
   if r['preference_eligible']:counts[(context(r['situation']),r['situation']['class'] if label=='class' else r['observer_slot'])][r['selected']]+=1
  scored=[]
  for r in held:
   if not r['preference_eligible']:continue
   key=context(r['situation']);c=counts[(key,r['situation']['class'] if label=='class' else r['observer_slot'])]
   if sum(c.values())<8:c=frozen['models']['population']['contexts'].get(key,frozen['models']['population']['global'])
   selected=max(r['affordances'],key=lambda skill:(c.get(skill,0)+1,skill));scored.append({'context':key,'correct':selected==r['selected']})
  robust[label]={'correct':sum(s['correct'] for s in scored),'n':len(scored),'accuracy':sum(s['correct'] for s in scored)/len(scored),'by_context':{key:{'correct':sum(s['correct'] for s in scored if s['context']==key),'n':sum(s['context']==key for s in scored)} for key in {s['context'] for s in scored}}}
 summary['robustness_baselines']=robust
 summary['by_episode']={i:metrics([p for p in predictions if p['episode']==i]) for i in hold_ids}
 summary['by_observer_side']={str(side):metrics([p for p in predictions if metadata[p['episode']]['observer_slot']==side]) for side in [0,5]}
 preferences=[]
 for key,counts in sorted(frozen['models']['train']['contexts'].items()):
  candidates=[r for r in train if r['preference_eligible'] and context(r['situation'])==key];n=len(candidates);chosen=max(counts,key=lambda s:(counts[s],s));success=counts[chosen];other=Counter(s for r in candidates for s in r['affordances'] if s!=chosen)
  # For a preference X OVER Y, count only observations where BOTH X and Y were available.
  pop_counts=frozen['models']['population']['contexts'].get(key,{})
  alternatives=[s for s in other if s!=chosen]
  alternative=max(alternatives,key=lambda s:(pop_counts.get(s,0),counts.get(s,0),other[s],s));paired=[r for r in candidates if chosen in r['affordances'] and alternative in r['affordances']]
  pop_pair=[r for r in pop if r['preference_eligible'] and context(r['situation'])==key and chosen in r['affordances'] and alternative in r['affordances']]
  held_pair=[r for r in held if r['preference_eligible'] and context(r['situation'])==key and chosen in r['affordances'] and alternative in r['affordances']]
  pair_ids={r['id'] for r in held_pair};pp=[p for p in predictions if p['observation'] in pair_ids]
  statement=metrics(pp);assert all(p['prediction']==chosen for p in pp) or n<8
  count=sum(r['selected']==chosen for r in paired);status='supported' if len(paired)>=8 and statement['n'] and statement['accuracy']>statement['population_accuracy'] and chosen!='hold' else 'provisional'
  mask=int(key.split('_')[1]);low=int(key.split('_')[-1]);pid=f'Jordan268_I_O{mask*2+low+1:02d}'
  preferences.append({'id':pid,'when':key,'skill':chosen,'over':alternative,'n':len(paired),'chosen_count':count,'rate':rate(count,len(paired)),
   'context_n':n,'confidence':(count+1)/(len(paired)+2),'confidence_meaning':'Laplace-smoothed observed selection probability, not probability of hidden intent; correlated segments',
   'base_rate':{'source':'21-episode population prior, same context and paired affordances','n':len(pop_pair),'chosen_count':sum(r['selected']==chosen for r in pop_pair),'rate':rate(sum(r['selected']==chosen for r in pop_pair),len(pop_pair))},
   'status':status,'level':'individual','opponent':plan['target_version'],'last_observed':max(candidates,key=lambda r:(metadata[r['episode']]['created_at'],r['tick']))['id'],
   'predictions':statement,'prediction_interval':confidence_interval(pp,groups),'supporting_episodes':len({r['episode'] for r in paired}),'examples':[r['id'] for r in paired[:3]],
   'unresolved_constraints':'Enemy cooldowns/private memory and full route execution unavailable. Hold can be turning/collision; always provisional.',
   'counterstrategy_status':'proposed_test_only; no exploitation attempt or validated rollout proxy'})
 skill_stats={}
 for skill in SKILLS:
  rows=[r for r in train if r['selected']==skill];actual=[p for p in predictions if p['actual']==skill];pred=[p for p in predictions if p['prediction']==skill]
  skill_stats[skill]={'n':len(rows),'episodes':len({r['episode'] for r in rows}),'ticks':sum(r['duration_ticks'] for r in rows),'initiation_contexts':dict(Counter(context(r['situation']) for r in rows)),
   'termination':dict(Counter(r['termination'] for r in rows)),'left_censored':sum(r['predictor_tick'] is None for r in rows),'median_duration_ticks':statistics.median(r['duration_ticks'] for r in rows),
   'outcome_hp_change_median':statistics.median(r['outcome']['hp_change'] for r in rows),'concurrent_movement_ticks':dict(sum((Counter(r['concurrent_movement']) for r in rows),Counter())),
   'prediction':{'actual_n':len(actual),'predicted_n':len(pred),'recall':rate(sum(p['correct'] for p in actual),len(actual)),'precision':rate(sum(p['correct'] for p in pred),len(pred))},'example':rows[0]['id']}
 # Compare the SAME contexts within halves and chronologically. Changes are descriptive, not causal adaptation.
 adaptation=[]
 half_time={i:proofs[i]['ticks']/2 for i in train_ids};half_epi=len(train_ids)//2
 for pref in preferences:
  rows=[r for r in train if r['preference_eligible'] and context(r['situation'])==pref['when'] and pref['skill'] in r['affordances'] and pref['over'] in r['affordances']]
  def pair(rs):return {'n':len(rs),'selected':sum(r['selected']==pref['skill'] for r in rs),'rate':rate(sum(r['selected']==pref['skill'] for r in rs),len(rs))}
  adaptation.append({'preference':pref['id'],'within_early':pair([r for r in rows if r['tick']<half_time[r['episode']]]),'within_late':pair([r for r in rows if r['tick']>=half_time[r['episode']]]),
   'chronological_early':pair([r for r in rows if r['episode'] in train_ids[:half_epi]]),'chronological_late':pair([r for r in rows if r['episode'] in train_ids[half_epi:]]),
   'our_pressure_present':pair([r for r in rows if r['situation']['visible_pressure_ids']]),'our_pressure_absent':pair([r for r in rows if not r['situation']['visible_pressure_ids']]),'causal_adaptation_established':False})
 jordan_ids=train_ids+hold_ids;all_jordan=[r['id'] for r in plan['episodes'] if r['split']!='population'];visibility={}
 for label,ids in [('all_jordan',all_jordan),('distinct_train',train_ids),('heldout',hold_ids),('population',pop_ids)]:
  live=sum(proofs[i]['truth_live_opponent_ticks'] for i in ids);seen=sum(proofs[i]['visible_live_opponent_ticks'] for i in ids);ticks=sum(proofs[i]['ticks'] for i in ids)
  visibility[label]={'episodes':len(ids),'ticks':ticks,'living_opponent_ticks':live,'visible_living_opponent_ticks':seen,'fraction':seen/live,'all_scheduled_hero_tick_fraction':seen/(5*ticks),'observer_dead_fraction':sum(proofs[i]['observer_dead_ticks'] for i in ids)/ticks,
   'residual_fraction':sum(stats[i]['residual_ticks'] for i in ids)/seen,'segments':sum(stats[i]['segments'] for i in ids),'eligible':sum(stats[i]['eligible'] for i in ids),
   'exclusions':dict(sum((Counter(stats[i]['exclusions']) for i in ids),Counter()))}
 win_counts=Counter()
 for i in all_jordan:
  us=metadata[i]['observer_slot'];scores=results[i]['scores'];win_counts['jordan_win' if scores[5-us]>scores[us] else 'our_win' if scores[us]>scores[5-us] else 'draw']+=1
 report={'schema':'gota-opponent-validation/1','model_freeze_sha256':hashlib.sha256((d/'model-freeze.json').read_bytes()).hexdigest(),'all_replays_verified':all(p['all_state_hashes_equal'] for p in proofs.values()),
  'models':frozen['models'],'training_episode_ids':train_ids,'population_episode_ids':pop_ids,'heldout_episode_ids':hold_ids,'unique_training_trajectories':len(train_ids),'unique_heldout_trajectories':len({groups[i] for i in hold_ids}),
  'heldout_matches_training':{i:[j for j in train_ids if groups[j]==groups[i]] for i in hold_ids},'observability':visibility,'outcomes':dict(win_counts),'heldout':summary,'preferences':preferences,'skills':skill_stats,'adaptation':adaptation,
  'proxy':{'usable':False,'rollouts':0,'divergence':None,'reason':'No executable skill controller or rollout validation. Boundary-conditional prediction alone cannot qualify a proxy.',
   'proposed_gate':{'skill_frequency_total_variation_max':0.10,'position_histogram_total_variation_max':0.15,'win_rate_absolute_gap_max':0.10,'note':'Proposed future gate on novel seeds, both sides; not tested or a certification.'}}}
 (d/'evaluation.json').write_text(json.dumps(report,indent=2)+'\n')
 with gzip.open(d/'heldout-predictions.jsonl.gz','wt') as f:
  for pred in predictions:f.write(json.dumps(pred)+'\n')
 print(json.dumps({'heldout':summary,'observability':visibility,'outcomes':dict(win_counts),'preferences':[{k:r[k] for k in ['id','skill','over','n','rate','status','predictions']} for r in preferences]},indent=2))
if __name__=='__main__':main()
