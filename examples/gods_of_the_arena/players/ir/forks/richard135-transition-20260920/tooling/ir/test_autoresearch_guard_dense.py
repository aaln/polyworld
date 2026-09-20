"""Native context scope plus inherited recruitment and integration checks."""
from copy import deepcopy
import unittest
import test_policy_ir as f
import test_rush_unblock as u
import test_autoresearch_role_raid as rr
import test_autoresearch_role_dense as rd
from test_autoresearch_dense_cadence import case
from policy_ir import write
from autoresearch_guard_dense import make,STUDY
class GuardDenseTests(unittest.TestCase):
    factory=staticmethod(lambda n:make('role_guard_dense' if n in ('role64','role_dense') else n))
    run_vm=f.RealVmTests.run_vm
    play=u.UnblockTests.play
    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)
    test_small_alarm_scope=rr.RoleRaidTests.test_small_alarm_keeps_attack_roles_on_parent_commands
    test_rank=rr.RoleRaidTests.test_all_ally_rank_and_dead_allies_are_respected
    test_committed_holds=rr.RoleRaidTests.test_group_defense_and_remembered_scoped_hold_survive
    test_response_recovery=rd.RoleDenseTests.test_response_and_recovery_compose
    test_stale_hit=rd.RoleDenseTests.test_gap_cannot_reuse_dense_hit
    def test_inactive_dense_is_exact_role64_commands_after_new_hits(self):
        for team in (0,1):
            for slot in range(5):
                cc=[case(team,slot,t,h) for t,h in [(100,0),(101,1),(102,1)]]
                for c in cc:
                    for o in c['objects']:
                        if o['objectKind']==2:o['objectTarget']=0
                new=self.play('role_guard_dense',cc,('defActive','motionActive','denseSteps'))
                self.assertEqual([r['memory']['defActive'] for r in new],[0,0,0])
                self.assertEqual([r['memory']['denseSteps'] for r in new],[0,0,0])
                self.assertEqual([r['actions'] for r in new],[r['actions'] for r in self.play('role64_reference',cc)])
    def test_active_dense_retains_unscoped_commands_equipment_and_limits(self):
        rows=[]
        for team in (0,1):
            for slot in range(5):
                cc=[case(team,slot,t,h,240,True) for t,h in [(100,0),(101,1),(102,1)]]
                new=self.play('role_guard_dense',cc,('defActive','motionActive','denseSteps'));rows+=new
                self.assertTrue(all(r['memory']['defActive'] for r in new))
                self.assertEqual([r['actions'] for r in new],[r['actions'] for r in self.play('role_dense_reference',cc)])
                self.assertTrue(all(any(a['command']=='buyItem' and a['arguments'][0]>4 for a in r['actions']) for r in new))
        self.assertLessEqual(max(r['instructions'] for r in rows),20000);self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(STUDY/'vm-budget.json',{'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),'max_work':max(r['work'] for r in rows),'native_compile_enforces':{'globals':256,'source_bytes':65536,'instructions':20000,'work':50000}})
if __name__=='__main__':unittest.main()
