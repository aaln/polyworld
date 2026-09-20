"""Native arbitration boundaries, inherited commitments, equipment and VM budgets."""
import unittest
import test_policy_ir as f
import test_rush_unblock as u
from test_autoresearch_nearraids import bounded_case
from test_rush_defense import scene
from hero_binding import class_id
from policy_ir import write
from autoresearch_role_raid import make, STUDY

MEMORY = ('defActive', 'defUntil', 'pairedRush', 'raidSelfD', 'raidNearer', 'raidScoped')


class RoleRaidTests(unittest.TestCase):
    factory = staticmethod(make)
    run_vm = f.RealVmTests.run_vm
    play = u.UnblockTests.play

    @classmethod
    def setUpClass(cls):
        f.RealVmTests.setUpClass.__func__(cls)

    def test_small_alarm_keeps_attack_roles_on_parent_commands(self):
        for slot in range(5):
            for distance in (20, 64, 65):
                case = bounded_case(slot, distance)
                row = self.play('role64', [case], MEMORY)[0]
                self.assertEqual(row['memory']['defActive'], int(slot in (0, 2, 3) and distance <= 64))
                if slot in (1, 4):
                    self.assertEqual(row['actions'], self.play('parent', [case])[0]['actions'])

    def test_all_ally_rank_and_dead_allies_are_respected(self):
        case = bounded_case(2, 20)
        # Two nearer attack allies exhaust recruitment rank; no guaranteed sentry.
        for o in case['objects']:
            if o['objectId'] in (101, 104):
                o.update(objectX=67, objectY=43)
            if o['objectId'] == 103:
                o.update(objectX=116, objectY=115)
        self.assertEqual(self.play('role64', [case], MEMORY)[0]['memory']['defActive'], 0)
        for o in case['objects']:
            if o['objectId'] == 104:
                o.update(objectHp=0, objectAlive=0)
        self.assertEqual(self.play('role64', [case], MEMORY)[0]['memory']['defActive'], 1)

    def test_group_defense_and_remembered_scoped_hold_survive(self):
        for slot in range(5):
            case = bounded_case(slot, 70, count=4)
            row = self.play('role64', [case], MEMORY)[0]
            self.assertEqual(row['memory']['defActive'], 1)
            self.assertEqual(row['actions'], self.play('parent', [case])[0]['actions'])
        for slot in (0, 2, 3):
            rows = self.play('role64', [bounded_case(slot, 20), bounded_case(slot, 70, tick=101)], MEMORY)
            self.assertEqual(rows[0]['memory']['defUntil'], 820)
            self.assertEqual(rows[1]['memory']['pairedRush'], 0)
            self.assertEqual(rows[1]['memory']['defActive'], 1)
            rows = self.play('role64', [bounded_case(slot, 20), bounded_case(slot, 20, count=4, tick=101)], MEMORY)
            self.assertEqual(rows[-1]['memory']['raidScoped'], 0)
            self.assertEqual(rows[-1]['memory']['defUntil'], 7301)

    def test_blue_parity_equipment_and_dense_budgets_all_classes(self):
        rows = []
        for team in (0, 1):
            for slot in range(5):
                case = bounded_case(slot, 20) if team == 0 else scene(1, count=5, worldTick=100, selfGold=150)
                case['self']['selfClass'] = class_id(team, slot)
                case['objects'] += [f.obj(1000+i, kind=3, team=i%2, x=i%116, y=i*7%116) for i in range(220)]
                row = self.play('role64', [case], MEMORY)[0]
                rows.append(row)
                if team == 1:
                    self.assertEqual(row['actions'], self.play('parent', [case])[0]['actions'])
                self.assertTrue(any(a['command'] == 'buyItem' and a['accepted'] for a in row['actions']))
        self.assertLessEqual(max(r['instructions'] for r in rows), 20000)
        self.assertLessEqual(max(r['work'] for r in rows), 50000)
        write(STUDY/'vm-budget.json', {'decisions':len(rows),
              'max_instructions':max(r['instructions'] for r in rows),
              'max_work':max(r['work'] for r in rows)})


if __name__ == '__main__':
    unittest.main()
