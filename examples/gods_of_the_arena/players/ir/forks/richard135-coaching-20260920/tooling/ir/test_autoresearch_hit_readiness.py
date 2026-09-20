"""Isolated readiness scope, target arbitration parity, equipment and VM budgets."""
from pathlib import Path
import unittest
import test_policy_ir as f
from test_autoresearch_target_geometry import scene
from hero_binding import class_id
from policy_ir import read,write,compile_policy,extract
from autoresearch_hit_readiness import STUDY,VARIANTS,make
D=Path('/Users/aaln/experiments/softmax/gota-autoresearch/cycles/20260920T033342Z-b4ca5b')

class HitTests(unittest.TestCase):
 vm=D/'scenario-vm-public-target'
 run_vm=f.RealVmTests.run_vm
 captures=[]
 @classmethod
 def tearDownClass(cls):write(STUDY/'native-captures.json',cls.captures)
 def play(self,name,cc):
  memory=('bestId','motionActive','defActive')+(() if name=='parent' else ('denseSteps',))
  rr=self.run_vm(STUDY/'candidates'/name/'policy.bas',cc,memory)
  self.captures.append(dict(name=name,inputs=cc,outputs=rr));return rr
 def cases(self,team=0,slot=0,hits=(7,8,8),level=1,kind=2,count=240,direction='away'):
  cc=[scene(team,slot,100+i,h,direction=direction,kind=kind,count=count) for i,h in enumerate(hits)]
  for c in cc:c['self'].update(selfLevel=level,selfTarget=200)
  return cc
 def test_boundary_both_colors_all_classes(self):
  for team in (0,1):
   for slot in range(5):
    for last in (7,8,15,16):
     cc=self.cases(team,slot,hits=(last-1,last,last))
     for name in ('hits8','hits16'):
      eligible=last>=int(name[4:]) and class_id(team,slot) in (0,1,4,5,6)
      rr=self.play(name,cc)
      self.assertEqual([r['memory']['motionActive'] for r in rr],[0,int(eligible),0])
      self.assertEqual(rr[-1]['actions'][0]['command'],'attackTarget')
 def test_level2_sparse_nohit_and_excluded_preserve_reference(self):
  for team in (0,1):
   for slot in range(5):
    for mode in ('level2','sparse','no_hit','before_threshold'):
     cc=self.cases(team,slot,hits=(7,7,7) if mode=='no_hit' else (0,1,1) if mode=='before_threshold' else (15,16,16),level=2 if mode=='level2' else 1,count=30 if mode=='sparse' else 240)
     expected=[r['actions'] for r in self.play('suppression_reference',cc)]
     for name in ('hits8','hits16'):self.assertEqual([r['actions'] for r in self.play(name,cc)],expected)
 def test_geometry_guard_and_target_handoff_unchanged(self):
  for name in ('hits8','hits16'):
   for team in (0,1):
    for kind in (2,3,4):
     cc=self.cases(team,1,hits=(15,16,16),direction='toward',kind=kind)
     for c in cc:c['self']['selfTarget']=199
     rr=self.play(name,cc)
     self.assertEqual(rr[1]['memory']['motionActive'],int(kind==4))
 def test_gaps_cooldown_blocked_failed_preserve_safety(self):
  for name in ('hits8','hits16'):
   for mode in ('gap','same_tick','no_cooldown','blocked','failed'):
    cc=self.cases(slot=1,hits=(15,16,16))[:2]
    if mode=='gap':cc[1]['self']['worldTick']=103
    if mode=='same_tick':cc[1]['self']['worldTick']=100
    if mode=='no_cooldown':cc[1]['self']['selfAttackCooldown']=0
    if mode=='blocked':cc[1]['blocked']=[[100,14]]
    if mode=='failed':cc[1]['returns']={'walkTo':0}
    r=self.play(name,cc)[1];self.assertEqual(r['memory']['motionActive'],0)
    self.assertTrue(any(a['command']=='attackTarget' for a in r['actions']))
 def test_native_limits_gear_all_classes_both_colors(self):
  rows=[]
  for name in ('hits8','hits16'):
   for team in (0,1):
    for slot in range(5):
     for active in (False,True):
      cc=[scene(team,slot,t,h,direction='away',active=active) for t,h in ((100,15),(101,16))]
      for c in cc:
       c['self'].update(selfTarget=199,selfLevel=1)
       if not active:
        e=c['objects'].pop(2);e['objectKind']=3;c['objects'].append(e)
      rows+=self.play(name,cc)
  for r in rows:self.assertTrue(any(a['command']=='buyItem' and a['arguments'][0]>4 for a in r['actions']))
  self.assertLessEqual(max(r['instructions'] for r in rows),20000);self.assertLessEqual(max(r['work'] for r in rows),50000)
  write(STUDY/'vm-budget.json',dict(decisions=len(rows),max_work=max(r['work'] for r in rows),max_instructions=max(r['instructions'] for r in rows),limits=dict(globals=256,source_bytes=65536,instructions=20000,work=50000),native_compile_enforces=True))
 def test_compile_reverse_and_old_binding_preserved(self):
  self.assertTrue((Path(__file__).parent/'binding.py').read_bytes().startswith((STUDY/'binding-before.py').read_bytes()))
  for name in VARIANTS:
   p=make(name);source=compile_policy(p);self.assertEqual(extract(source,p),p);self.assertEqual(source,(STUDY/'candidates'/name/'policy.bas').read_text())

if __name__=='__main__':unittest.main()
