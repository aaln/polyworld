"""Observer-only opponent semantics. This module never reads tape commands or truth."""
from collections import Counter
import math
SKILLS=('target_hero','target_creep','target_structure','advance','withdraw','lateral','hold')
PARAMETERS={'minimum_segment_ticks':6,'opportunity_radius_tiles':12,'low_hp_absolute':100,'motion_min_world_units':1000,'radial_cosine_threshold':0.35,'local_route_check_tiles':2}
I,K,T,C,X,Y,HP,ALIVE,TARGET,VX,VY,LEVEL,MANA,ITEMS,COUNTS=range(15)
KIND_SKILL={1:'target_structure',2:'target_hero',3:'target_creep',4:'target_structure',5:'target_structure'}
BIT={'target_hero':1,'target_creep':2,'target_structure':4}

def distance(a,b):return math.hypot(a[X]-b[X],a[Y]-b[Y])

def motion(o,fort):
 vx,vy=o[VX],o[VY];speed=math.hypot(vx,vy)
 if speed<PARAMETERS['motion_min_world_units']:return 'hold'
 dx,dy=fort[X]-o[X],fort[Y]-o[Y];denom=math.hypot(dx,dy)*speed
 cosine=(dx*vx+dy*vy)/denom if denom else 0
 return 'advance' if cosine>PARAMETERS['radial_cosine_threshold'] else 'withdraw' if cosine<-PARAMETERS['radial_cosine_threshold'] else 'lateral'

def classify(o,objects,fort):
 target=objects.get(o[TARGET]);movement=motion(o,fort)
 if target and target[T]!=o[T] and target[HP]>0 and target[ALIVE]:return KIND_SKILL[target[K]],o[TARGET],movement
 return movement,0,movement

def walkable(terrain,x,y):return 0<=int(y)<len(terrain) and 0<=int(x)<len(terrain[0]) and terrain[int(y)][int(x)]=='.'

def features(o,objects,fort,terrain,previous_skill):
 hostiles=[q for q in objects.values() if q[T]!=o[T] and q[HP]>0 and q[ALIVE]]
 nearby=[q for q in hostiles if distance(o,q)<=PARAMETERS['opportunity_radius_tiles']]
 kinds=sorted(set(KIND_SKILL[q[K]] for q in nearby));mask=sum(BIT[s] for s in kinds)
 # An estimate of local movement opportunity, never a claim of accepted/reachable path.
 dx,dy=fort[X]-o[X],fort[Y]-o[Y];denom=math.hypot(dx,dy) or 1;ux,uy=dx/denom,dy/denom
 dirs={'advance':[(ux,uy)],'withdraw':[(-ux,-uy)],'lateral':[(-uy,ux),(uy,-ux)]}
 movement=[s for s,ds in dirs.items() if any(all(walkable(terrain,o[X]+vx*t,o[Y]+vy*t) for t in (1,2)) for vx,vy in ds)]
 pressure=[q[I] for q in nearby if q[TARGET]==o[I]]
 allies=[q[I] for q in objects.values() if q[K]==2 and q[T]==o[T] and q[I]!=o[I] and q[ALIVE] and distance(o,q)<=12]
 us=[q[I] for q in nearby if q[K]==2]
 feats={'opportunity_mask':mask,'low_hp':o[HP]<=PARAMETERS['low_hp_absolute'],'hp':o[HP],'class':o[C],
   'position':[o[X],o[Y]],'distance_to_our_god':round(distance(o,fort),3),'previous_skill':previous_skill,
   'visible_pressure_ids':pressure,'nearby_our_hero_ids':us,'nearby_opponent_ally_ids':allies,
   'visible_target':o[TARGET],'mana':o[MANA],'inventory':o[ITEMS]}
 affordable=sorted(set(['hold',*kinds,*movement]))
 return feats,affordable,{'nearby_hostile_ids':[q[I] for q in nearby],
  'basis':'Visible living/exposed hostile within 12 integer tiles permits estimated target/pursuit opportunity; movement has two locally walkable terrain samples. Enemy sight, dynamic collision, cooldowns and private intent are unknown.',
  'certainty':'estimated_not_proven_executable','cooldown_dependent_skills_excluded':True}

def context(feats):return f"mask_{feats['opportunity_mask']}_low_{int(feats['low_hp'])}"

def distribution(counts,affordances):
 total=sum(counts.get(s,0)+1 for s in affordances)
 return {s:(counts.get(s,0)+1)/total for s in affordances}

def predict(model,features,affordances):
 key=context(features);counts=model['contexts'].get(key,model['global'])
 if sum(counts.values())<8:counts=model['global']
 probs=distribution(counts,affordances)
 return max(probs,key=lambda s:(probs[s],s)),probs,key

def fit(rows):
 contexts={};totals=Counter()
 for r in rows:
  if not r['preference_eligible']:continue
  key=context(r['situation']);contexts.setdefault(key,Counter())[r['selected']]+=1;totals[r['selected']]+=1
 return {'contexts':{k:dict(v) for k,v in sorted(contexts.items())},'global':dict(totals),'smoothing':'Laplace +1 over estimated available skills; context backs off globally if n<8'}
