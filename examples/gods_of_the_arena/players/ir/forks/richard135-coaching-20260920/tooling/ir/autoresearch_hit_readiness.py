"""Accepted-parent coherent IR siblings for late level-one recovery."""
from copy import deepcopy
from pathlib import Path
from policy_ir import read,digest,refresh_grounding,bundle
C=Path('/Users/aaln/experiments/softmax/gota-autoresearch')
STUDY=C/'forks/fork_20260920_045449_29b23b/hit_readiness'
REFERENCE=C/'forks/fork_20260919_212453_e79df8/target_geometry/candidates/suppress_toward'
VARIANTS=('parent','suppression_reference','hits8','hits16')

def make(name):
 parent=read(C/'snapshots/0000-b2693715459d/policy.ir.json')
 if name=='parent':return parent
 reference=read(REFERENCE/'policy.ir.json')
 if name=='suppression_reference':return reference
 assert name in VARIANTS
 p=deepcopy(parent);plan=read(STUDY/'prospective.json');evidence=dict(artifact=str(STUDY/'prospective.json'),sha256=digest((STUDY/'prospective.json').read_bytes()))
 p['id']='autoresearch_20260920_isolated_'+name
 p['situation']['notes']='Published2026.9.16.5. Basic hits are public lifetime counts and persist across deaths; hero level may remain1 despite many hits. Target-direction suppression is unchanged. No nonhero handoff override, hidden state or opponent/seed branches.'
 for claim in p['belief']['claims'].values():claim['claim']='Inherited ancestor evidence, not a measurement of '+name+'. '+claim['claim']
 p['belief']['claims']['B_hit_readiness']=dict(status='untested',claim=plan['hypothesis'],evidence=[evidence])
 p['goal']['G_cadence']['preference']='Test recovery timing for an XP-starved level1 physical hero after '+name[4:]+' observed lifetime hits. Keep suppression geometry and original target ordering. Activation alone is not fort-conversion benefit.'
 p['goal']['G_survival']['preference']='Retain both parent and deployed-suppression survival bounds, all classes and equipment. Lifetime hits are an empirical readiness heuristic, not a claim of safer movement.'
 p['goal']['G_fort']['preference']=plan['screen']['decision_rule']+' '+plan['confirmation']['decision_rule']
 p['skill']['attack']=dict(operator='target_hit_readiness_v1',parameters=reference['skill']['attack']['parameters']|{'verified_hits':int(name[4:])})
 for rule in p['strategy']:
  if rule['id']=='R2':rule['for']=['G_fort','G_cadence','G_survival','G_defense']
 p['execution']=dict(binding='gota-basic/1',game_version='2026.9.16.5',language='BASIC')
 p['update'].update(parent=digest(parent),revision=parent['update']['revision']+1,change='Accepted-parent physical recovery with isolated verified-hit readiness: '+name,evidence=p['update']['evidence']+[evidence],needs_review=['belief/B_hit_readiness','goal/G_cadence','goal/G_survival','goal/G_fort'])
 refresh_grounding(p);return p

if __name__=='__main__':
 for name in VARIANTS:
  bundle(make(name),STUDY/'candidates'/name);print(name,'full IR compile and reverse parity complete',flush=True)
