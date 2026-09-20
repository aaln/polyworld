"""Native tests for coordinated defense and resource behavior; no old proof edits."""
import unittest
import test_policy_ir as f
import test_rush_unblock as u
import test_autoresearch_role_raid as role_tests
from test_rush_defense import scene
from hero_binding import class_id
from policy_ir import write
from autoresearch_role_mana import make,STUDY

class RoleManaTests(unittest.TestCase):
    factory=staticmethod(lambda name:make('rolebuy40' if name=='role64' else name))
    run_vm=f.RealVmTests.run_vm
    play=u.UnblockTests.play
    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)
    test_role_and_radius=role_tests.RoleRaidTests.test_small_alarm_keeps_attack_roles_on_parent_commands
    test_rank_and_liveness=role_tests.RoleRaidTests.test_all_ally_rank_and_dead_allies_are_respected
    test_commitments=role_tests.RoleRaidTests.test_group_defense_and_remembered_scoped_hold_survive

    def test_mana_boundary_and_emergency_healing(self):
        for team in (0,1):
            for slot in range(5):
                for mana in (39,40,49,50):
                    case=f.fixture(selfTeam=team,selfClass=class_id(team,slot),selfMana=mana,selfGold=150,selfHp=20)
                    row=self.play('rolebuy40',[case],())[0]
                    self.assertEqual(any(a['command']=='buyItem' and a['arguments']==[3] for a in row['actions']),mana<40)
                    old=self.play('role64_reference',[case],())[0]
                    heal=lambda r:[a for a in r['actions'] if a['command']=='buyItem' and a['arguments'][0] in (1,2)]
                    self.assertEqual(heal(row),heal(old))

    def test_dense_budget_and_equipment_all_classes(self):
        rows=[]
        for team in (0,1):
            for slot in range(5):
                case=scene(team,count=5,worldTick=100,selfGold=150)
                case['self'].update(selfClass=class_id(team,slot),selfMana=45,selfMaxMana=100)
                case['objects'] += [f.obj(1000+i,kind=3,team=i%2,x=i%116,y=i*7%116) for i in range(220)]
                row=self.play('rolebuy40',[case])[0];rows.append(row)
                self.assertTrue(any(a['command']=='buyItem' and a['arguments'][0]>4 for a in row['actions']))
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(STUDY/'vm-budget.json',{'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),'max_work':max(r['work'] for r in rows),'scope':'Native BASIC VM with scripted command acceptance; complete games verify live inventory and survival.'})

if __name__=='__main__':unittest.main()
