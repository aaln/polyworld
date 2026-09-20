"""Native VM mechanism, scope, reset, fallback, equipment and limit checks."""
from copy import deepcopy
from pathlib import Path
import tempfile,unittest
import test_policy_ir as f
from hero_binding import class_id
from policy_ir import compile_policy,extract,write
from autoresearch_dense_cadence import make,STUDY,VARIANTS

def case(team=0,slot=0,tick=100,hits=0,n=240,active=False):
    x,y=(99,15) if team==0 else (15,99)
    objects=[f.obj(1,kind=1,team=0,x=105,y=11,hp=400,alive=0),f.obj(2,kind=1,team=1,x=11,y=105,hp=400,alive=0)]
    enemy=f.obj(200,kind=2,team=1-team,x=x+2,y=y,hp=400);enemy['objectTarget']=1 if team==0 else 2
    objects.append(enemy)
    if active:
        for i in range(3):
            e=f.obj(201+i,kind=2,team=1-team,x=x+2,y=y+i%2,hp=400);e['objectTarget']=enemy['objectTarget'];objects.append(e)
    for i in range(n-len(objects)):objects.append(f.obj(1000+i,kind=3,team=team,x=40+i%8,y=40+i%9,hp=60))
    return f.fixture(objects,selfId=100+5*team+slot,selfTeam=team,selfClass=class_id(team,slot),selfX=x,selfY=y,worldTick=tick,selfAttacksLanded=hits,selfAttackCooldown=12,selfGold=150,selfAttackRange=330000)

class DenseCadenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)
    run_vm=f.RealVmTests.run_vm
    def play(self,name,cases,memory=('bestId','motionActive','denseSteps')):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'policy.bas';p.write_text(compile_policy(make(name)));return self.run_vm(p,cases,memory)
    def test_new_hit_step_then_resume_all_eligible_classes_both_colors(self):
        for name in ('dense_all','dense_ranged'):
            for team in (0,1):
                for slot in range(5):
                    cls=class_id(team,slot);eligible=cls!=9 and (name=='dense_all' or cls in (1,2,3,6,7,8))
                    rows=self.play(name,[case(team,slot,t,h) for t,h in [(100,0),(101,1),(102,1)]])
                    self.assertEqual([r['memory']['motionActive'] for r in rows],[0,int(eligible),0])
                    if eligible:
                        self.assertEqual(rows[1]['actions'][0]['command'],'walkTo')
                        self.assertEqual(rows[1]['actions'][0]['arguments'],[100,14] if team==0 else [14,100])
                    self.assertEqual(rows[-1]['actions'][0]['command'],'attackTarget')
    def test_gap_and_same_tick_do_not_reuse_hit_and_cooldown_required(self):
        for tick in (100,102,600):
            rows=self.play('dense_all',[case(tick=100),case(tick=tick,hits=1)])
            self.assertEqual(rows[-1]['memory']['motionActive'],0)
        no_cd=case(tick=101,hits=1);no_cd['self']['selfAttackCooldown']=0
        self.assertEqual(self.play('dense_all',[case(),no_cd])[-1]['memory']['motionActive'],0)
    def test_failed_or_blocked_step_reissues_original_attack(self):
        for mode in ('blocked','failed','home'):
            c=case(tick=101,hits=1)
            if mode=='blocked':c['blocked']=[[100,14]]
            elif mode=='failed':c['returns']={'walkTo':0}
            else:c['self'].update(selfX=105,selfY=11)
            row=self.play('dense_all',[case(),c])[-1]
            self.assertEqual(row['memory']['motionActive'],0)
            self.assertTrue(any(a['command']=='attackTarget' for a in row['actions']))
    def test_sparse_actions_and_no_hit_dense_actions_exact_parent_parity(self):
        for name in ('dense_all','dense_ranged'):
            for team in (0,1):
                for slot in range(5):
                    for n in (30,240):
                        cc=[case(team,slot,t,h,n) for t,h in [(100,0),(101,0),(102,0)]]
                        self.assertEqual([r['actions'] for r in self.play(name,cc)],[r['actions'] for r in self.play('parent',cc,('bestId','motionActive'))])
    def test_native_global_source_instruction_work_and_equipment_limits(self):
        rows=[]
        for name in ('dense_all','dense_ranged'):
            for team in (0,1):
                for slot in range(5):
                    for active in (False,True):
                        rr=self.play(name,[case(team,slot,t,h,240,active) for t,h in [(100,0),(101,1)]])
                        rows.extend(rr)
                        for row in rr:self.assertTrue(any(a['command']=='buyItem' and a['arguments'][0]>4 for a in row['actions']))
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(STUDY/'vm-budget.json',{'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),'max_work':max(r['work'] for r in rows),'limits':{'globals':256,'source_bytes':65536,'instructions':20000,'work':50000},'native_compile_enforces_globals_and_source':True})
    def test_exact_compile_full_reverse(self):
        for name in VARIANTS:
            p=make(name);self.assertEqual(extract(compile_policy(p),p),p)

if __name__=='__main__':unittest.main()
