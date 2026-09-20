"""Native mechanism/arbitration, exclusion, equipment and budget checks."""
from pathlib import Path
import tempfile
import unittest
import test_policy_ir as f
from test_autoresearch_dense_cadence import case
from hero_binding import class_id
from policy_ir import compile_policy, write
from autoresearch_defense_phase import make, STUDY


class DefensePhaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        f.RealVmTests.setUpClass.__func__(cls)

    run_vm = f.RealVmTests.run_vm

    def play(self, name, cases):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / 'policy.bas'
            source.write_text(compile_policy(make(name)))
            memory = ('bestId', 'motionActive', 'defActive', 'defCount')
            if name != 'parent':
                memory += ('denseSteps',)
            return self.run_vm(source, cases, memory)

    def test_mass_alarm_exact_parent_actions_all_classes(self):
        for name in ('push_only', 'small_defense'):
            for team in (0, 1):
                for slot in range(5):
                    cc = [case(team, slot, t, h, 240, True) for t, h in [(100, 0), (101, 1), (102, 2)]]
                    rr = self.play(name, cc)
                    self.assertTrue(all(r['memory']['defActive'] and r['memory']['defCount'] >= 4 for r in rr))
                    self.assertEqual([r['actions'] for r in rr], [r['actions'] for r in self.play('parent', cc)])

    def test_weak_persistent_alarm_distinguishes_scopes(self):
        for team in (0, 1):
            for slot in range(5):
                eligible = class_id(team, slot) in (0, 1, 4, 5, 6)
                cc = [case(team, slot, 100, 0, 240, True), case(team, slot, 101, 1, 240, False)]
                push = self.play('push_only', cc)
                small = self.play('small_defense', cc)
                self.assertTrue(small[-1]['memory']['defActive'])
                self.assertEqual(small[-1]['memory']['defCount'], 1)
                self.assertEqual(small[-1]['memory']['motionActive'], int(eligible))
                self.assertEqual(push[-1]['actions'], self.play('parent', cc)[-1]['actions'])

    def test_no_alarm_and_sparse_exact_reference_actions(self):
        for name in ('push_only', 'small_defense'):
            for team in (0, 1):
                for slot in range(5):
                    for count in (30, 240):
                        cc = [case(team, slot, t, h, count, False) for t, h in [(100, 0), (101, 1), (102, 1)]]
                        for fixture in cc:
                            fixture['self'].update(selfX=58, selfY=58)
                            for obj in fixture['objects']:
                                if obj['objectKind'] == 2:
                                    obj.update(objectX=60, objectY=58, objectTarget=0)
                        rr = self.play(name, cc)
                        self.assertTrue(all(r['memory']['defActive'] == 0 for r in rr))
                        self.assertEqual([r['actions'] for r in rr], [r['actions'] for r in self.play('weapon_reference', cc)])

    def test_gaps_cooldown_and_failed_movement_fallback(self):
        for name in ('push_only', 'small_defense'):
            for mode in ('gap', 'same_tick', 'no_cooldown', 'blocked', 'failed'):
                first = case(team=0, slot=1)
                second = case(team=0, slot=1, tick=101, hits=1)
                if mode == 'gap': second['self']['worldTick'] = 103
                elif mode == 'same_tick': second['self']['worldTick'] = 100
                elif mode == 'no_cooldown': second['self']['selfAttackCooldown'] = 0
                elif mode == 'blocked': second['blocked'] = [[100, 14]]
                elif mode == 'failed': second['returns'] = {'walkTo': 0}
                row = self.play(name, [first, second])[-1]
                self.assertEqual(row['memory']['motionActive'], 0)
                self.assertTrue(any(a['command'] == 'attackTarget' for a in row['actions']))

    def test_equipment_and_all_native_limits(self):
        rows = []
        for name in ('push_only', 'small_defense'):
            for team in (0, 1):
                for slot in range(5):
                    for active in (False, True):
                        rows += self.play(name, [case(team, slot, t, h, 240, active) for t, h in [(100, 0), (101, 1)]])
        for r in rows:
            self.assertLessEqual(r['instructions'], 20000)
            self.assertLessEqual(r['work'], 50000)
            self.assertTrue(any(a['command'] == 'buyItem' and a['arguments'][0] > 4 for a in r['actions']))
        write(STUDY / 'vm-budget.json', {'decisions': len(rows),
            'max_instructions': max(r['instructions'] for r in rows),
            'max_work': max(r['work'] for r in rows),
            'native_compile_enforces': {'globals': 256, 'source_bytes': 65536, 'instructions': 20000, 'work': 50000}})


if __name__ == '__main__':
    unittest.main()
