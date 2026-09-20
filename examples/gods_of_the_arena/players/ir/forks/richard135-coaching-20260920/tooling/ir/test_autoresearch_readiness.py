"""Native level-transition arbitration, exclusions, fallback, gear and limits."""
from pathlib import Path
import tempfile
import unittest
import test_policy_ir as f
from test_autoresearch_dense_cadence import case
from hero_binding import class_id
from policy_ir import compile_policy, write
from autoresearch_readiness import make, STUDY


def fixture(team, slot, tick, hits, level=1, active=True, count=240):
    c = case(team, slot, tick, hits, count, active)
    c['self']['selfLevel'] = level
    if not active:
        c['self'].update(selfX=58, selfY=58)
        for obj in c['objects']:
            if obj['objectKind'] == 2: obj.update(objectX=60, objectY=58, objectTarget=0)
    return c


class ReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): f.RealVmTests.setUpClass.__func__(cls)
    run_vm = f.RealVmTests.run_vm

    def play(self, name, cases):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'policy.bas';p.write_text(compile_policy(make(name)))
            memory = ('bestId','motionActive','defActive','defCount')
            if name != 'parent': memory += ('denseSteps',)
            return self.run_vm(p, cases, memory)

    def test_level1_active_alarm_exact_parent_all_classes(self):
        for name in ('first_level','first_level_defense'):
            for team in (0,1):
                for slot in range(5):
                    cc = [fixture(team,slot,t,h) for t,h in [(100,0),(101,1),(102,2)]]
                    rr = self.play(name,cc)
                    self.assertTrue(all(r['memory']['defActive'] for r in rr))
                    self.assertEqual([r['actions'] for r in rr],[r['actions'] for r in self.play('parent',cc)])

    def test_no_alarm_level1_scopes_differ(self):
        for team in (0,1):
            for slot in range(5):
                cc = [fixture(team,slot,t,h,active=False) for t,h in [(100,0),(101,1)]]
                rr = self.play('first_level_defense',cc)
                self.assertTrue(all(r['memory']['defActive']==0 for r in rr))
                self.assertEqual(rr[-1]['memory']['motionActive'],int(class_id(team,slot) in (0,1,4,5,6)))
                self.assertEqual([r['actions'] for r in rr],[r['actions'] for r in self.play('weapon_reference',cc)])
                self.assertEqual([r['actions'] for r in self.play('first_level',cc)],[r['actions'] for r in self.play('parent',cc)])

    def test_first_level_transition_then_resume(self):
        for name in ('first_level','first_level_defense'):
            for team in (0,1):
                for slot in range(5):
                    cc = [fixture(team,slot,t,h,l) for t,h,l in [(100,0,1),(101,1,1),(102,2,2),(103,2,2)]]
                    rr = self.play(name,cc);eligible=class_id(team,slot) in (0,1,4,5,6)
                    self.assertEqual([r['memory']['motionActive'] for r in rr],[0,0,int(eligible),0])
                    self.assertEqual(rr[-1]['actions'][0]['command'],'attackTarget')

    def test_level2_and_sparse_exact_reference(self):
        for name in ('first_level','first_level_defense'):
            for team in (0,1):
                for slot in range(5):
                    for active,level,count in [(True,2,240),(False,2,240),(True,1,30),(False,1,30)]:
                        cc=[fixture(team,slot,t,h,level,active,count) for t,h in [(100,0),(101,1),(102,1)]]
                        self.assertEqual([r['actions'] for r in self.play(name,cc)],[r['actions'] for r in self.play('weapon_reference',cc)])

    def test_gaps_failed_movement_and_cooldown(self):
        for name in ('first_level','first_level_defense'):
            for mode in ('gap','same_tick','no_cooldown','blocked','failed'):
                cc=[fixture(0,1,100,0,2),fixture(0,1,101,1,2)]
                if mode=='gap':cc[1]['self']['worldTick']=103
                elif mode=='same_tick':cc[1]['self']['worldTick']=100
                elif mode=='no_cooldown':cc[1]['self']['selfAttackCooldown']=0
                elif mode=='blocked':cc[1]['blocked']=[[100,14]]
                else:cc[1]['returns']={'walkTo':0}
                rr=self.play(name,cc)[-1];self.assertEqual(rr['memory']['motionActive'],0)
                self.assertTrue(any(a['command']=='attackTarget' for a in rr['actions']))

    def test_equipment_and_native_limits(self):
        rows=[]
        for name in ('first_level','first_level_defense'):
            for team in (0,1):
                for slot in range(5):
                    for level in (1,2):
                        for active in (False,True):
                            rows+=self.play(name,[fixture(team,slot,t,h,level,active) for t,h in [(100,0),(101,1)]])
        for r in rows:
            self.assertLessEqual(r['instructions'],20000);self.assertLessEqual(r['work'],50000)
            self.assertTrue(any(a['command']=='buyItem' and a['arguments'][0]>4 for a in r['actions']))
        write(STUDY/'vm-budget.json',{'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),'max_work':max(r['work'] for r in rows),'native_compile_enforces':{'globals':256,'source_bytes':65536,'instructions':20000,'work':50000}})


if __name__=='__main__': unittest.main()
