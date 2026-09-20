"""Boundary/visibility safety and IR evidence gates, not game-winning claims."""
import copy,gzip,json,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE));sys.path.insert(0,str(ROOT/'examples/gods_of_the_arena/players/ir'))
from semantics import classify,features,PARAMETERS
from segment import analyze
import opponent_ir

def obj(id,kind,team,x=10,y=10,hp=200,alive=1,target=0,vx=0,vy=0):
 return [id,kind,team,0,x,y,hp,alive,target,vx,vy,1,0,[],[]]

class ObserverModelTests(unittest.TestCase):
 def test_hidden_target_is_not_filled(self):
  hero=obj(105,2,1,target=999);fort=obj(1,1,0,x=30)
  self.assertEqual(classify(hero,{105:hero,1:fort},fort),('hold',0,'hold'))
 def test_shielded_structure_not_target_opportunity(self):
  hero=obj(105,2,1);fort=obj(1,1,0,x=30);shielded=obj(2,4,0,x=11,hp=400,alive=0)
  f,aff,_=features(hero,{105:hero,1:fort,2:shielded},fort,['.'*50]*50,None)
  self.assertNotIn('target_structure',aff);self.assertEqual(f['opportunity_mask'],0)
 def test_target_and_motion_are_concurrent(self):
  hero=obj(105,2,1,target=100,vx=-6000);enemy=obj(100,2,0,x=12);fort=obj(1,1,0,x=30)
  self.assertEqual(classify(hero,{105:hero,100:enemy,1:fort},fort),('target_hero',100,'withdraw'))
 def test_segmentation_uses_prior_tick_and_excludes_appearance(self):
  with tempfile.TemporaryDirectory() as tmp:
   folder=Path(tmp);header={'type':'header','terrain':['.'*50]*50}
   with gzip.open(folder/'observer.jsonl.gz','wt') as out:
    out.write(json.dumps(header)+'\n')
    # A target becomes visible at tick 8: cannot be put into tick 7 affordances.
    for t in range(1,15):
     visible=t!=1;hero=obj(105,2,1,target=100 if t>=8 else 0);fort=obj(1,1,0,x=30)
     objects=[fort]+([hero] if visible else [])+([obj(100,2,0,x=11)] if t>=8 else [])
     out.write(json.dumps({'type':'view','tick':t,'available':True,'objects':objects})+'\n')
   row={'id':'fixture','opponent_version':'fixture','split':'train','observer_slot':0};segments,stats=analyze(row,folder)
   self.assertEqual(len(segments),2)
   self.assertIsNone(segments[0]['predictor_tick']);self.assertFalse(segments[0]['preference_eligible'])
   s=segments[1];self.assertEqual(s['tick'],8);self.assertEqual(s['predictor_tick'],7);self.assertNotIn('target_hero',s['affordances']);self.assertFalse(s['preference_eligible'])
   self.assertEqual(stats['visible_hero_ticks'],13)
 def test_native_model_and_promotion_gate(self):
  model=opponent_ir.load(ROOT/'examples/gods_of_the_arena/players/ir/opponents/jordan_v268.py')
  supported=next(c for c in model['belief']['claims'].values() if c['status']=='supported')
  supported['evidence'][0]['n']=7
  with self.assertRaises(ValueError):opponent_ir.validate(model)
 def test_unvalidated_proxy_cannot_be_enabled(self):
  model=opponent_ir.load(ROOT/'examples/gods_of_the_arena/players/ir/opponents/jordan_v268.py');model['belief']['grounded']['proxy']['usable']=True
  with self.assertRaises(ValueError):opponent_ir.validate(model)
 def test_prediction_masks_unavailable_skills(self):
  model=opponent_ir.load(ROOT/'examples/gods_of_the_arena/players/ir/opponents/jordan_v268.py')
  result=opponent_ir.predict(model,{'opportunity_mask':7,'low_hp':False},['hold','withdraw'])
  self.assertIn(result['skill'],['hold','withdraw']);self.assertAlmostEqual(sum(result['probabilities'].values()),1);self.assertFalse(result['usable_for_rollout'])
 def test_belief_patch_cannot_mutate_model(self):
  model=opponent_ir.load(ROOT/'examples/gods_of_the_arena/players/ir/opponents/jordan_v268.py');patch=opponent_ir.belief_patch(model);patch.clear();self.assertTrue(model['belief']['claims'])

if __name__=='__main__':unittest.main()
