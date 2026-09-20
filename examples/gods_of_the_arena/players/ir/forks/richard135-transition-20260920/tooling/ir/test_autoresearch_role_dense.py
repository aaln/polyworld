"""Native composition tests for response arbitration and dense recovery."""
from copy import deepcopy
import unittest
import test_policy_ir as f
import test_rush_unblock as u
import test_autoresearch_role_raid as rr
from test_autoresearch_nearraids import bounded_case
from test_autoresearch_dense_cadence import case
from hero_binding import class_id
from policy_ir import write
from autoresearch_role_dense import make,STUDY
class RoleDenseTests(unittest.TestCase):
    factory=staticmethod(lambda n:make('role_dense' if n=='role64' else n))
    run_vm=f.RealVmTests.run_vm
    play=u.UnblockTests.play
    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)
    test_small_alarm_scope=rr.RoleRaidTests.test_small_alarm_keeps_attack_roles_on_parent_commands
    test_rank=rr.RoleRaidTests.test_all_ally_rank_and_dead_allies_are_respected
    test_committed_holds=rr.RoleRaidTests.test_group_defense_and_remembered_scoped_hold_survive
    def test_response_and_recovery_compose(self):
        for slot in (0,2,3):
            a=bounded_case(slot,6);a['self'].update(selfAttacksLanded=0,selfAttackCooldown=12)
            a['objects'] += [f.obj(3000+i,kind=3,team=0,x=40+i%9,y=40+i%8) for i in range(220)]
            b=deepcopy(a);b['self'].update(worldTick=101,selfAttacksLanded=1)
            c=deepcopy(b);c['self']['worldTick']=102
            rows=self.play('role_dense',[a,b,c],('bestId','defActive','motionActive','denseSteps','raidScoped'))
            self.assertEqual([r['memory']['defActive'] for r in rows],[1,1,1])
            self.assertEqual([r['memory']['motionActive'] for r in rows],[0,1,0])
            self.assertEqual(rows[1]['actions'][0]['command'],'walkTo')
            self.assertEqual(rows[2]['actions'][0]['command'],'attackTarget')
    def test_class_and_blue_dense_parity_equipment_limits(self):
        rows=[]
        for team in (0,1):
            for slot in range(5):
                for active in (False,True):
                    cases=[case(team,slot,t,h,240,active) for t,h in [(100,0),(101,1)]]
                    new=self.play('role_dense',cases);rows+=new
                    if team==1:self.assertEqual([r['actions'] for r in new],[r['actions'] for r in self.play('dense_reference',cases)])
                    for row in new:self.assertTrue(any(a['command']=='buyItem' and a['arguments'][0]>4 for a in row['actions']))
        self.assertLessEqual(max(r['instructions'] for r in rows),20000);self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(STUDY/'vm-budget.json',{'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),'max_work':max(r['work'] for r in rows),'native_compile_enforces':{'globals':256,'source_bytes':65536,'instructions':20000,'work':50000}})
    def test_gap_cannot_reuse_dense_hit(self):
        a=case();b=case(tick=500,hits=3)
        rows=self.play('role_dense',[a,b],('motionActive','denseSteps'))
        self.assertEqual([r['memory']['denseSteps'] for r in rows],[0,0])
if __name__=='__main__':unittest.main()
