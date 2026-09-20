"""Native VM evidence for observation, release, routing, and retained emergencies."""
from copy import deepcopy
import unittest
import test_policy_ir as f
import test_rush_unblock as u
import test_coach_assembled as a
from test_rush_defense import scene
from hero_binding import class_id
from binding import CONTRACTS
from policy_ir import compile_policy, extract, write
from autoresearch_wave_study import make, STUDY, VARIANTS

MEMORY = ('bestId', 'defActive', 'cpAdvance', 'cpMode', 'cpLane', 'cpRearNeeded', 'cpWaveUntil')


class WaveTests(unittest.TestCase):
    factory = staticmethod(make)
    run_vm = f.RealVmTests.run_vm
    sequence = a.AssembledTests.sequence

    def play(self, name, cases, memory=('bestId', 'defActive', 'defPointX', 'defPointY')):
        if name != 'outer_converge':
            memory = tuple(k for k in memory if k != 'cpLane')
        return u.UnblockTests.play(self, name, cases, memory)

    @classmethod
    def setUpClass(cls):
        f.RealVmTests.setUpClass.__func__(cls)

    def test_exact_roundtrip_and_unchanged_blue_branch(self):
        old = make('parent')
        for name in VARIANTS[1:]:
            p = make(name)
            self.assertEqual(extract(compile_policy(p), p), p)
            for key, s in p['skill'].items():
                prior = old['skill'][key]
                if prior != s:
                    self.assertEqual(CONTRACTS[s['operator']].source(s['parameters']).split('\nelse\n', 1)[1],
                                     CONTRACTS[prior['operator']].source(prior['parameters']).split('\nelse\n', 1)[1])

    def test_initial_alarm_commands_match_parent(self):
        for name in VARIANTS[1:]:
            for slot in range(5):
                cases = self.sequence(slot)[:2]
                self.assertEqual([r['actions'] for r in self.play(name, cases)],
                                 [r['actions'] for r in self.play('parent', cases)])

    def test_wave_release_does_not_discard_outer_tower(self):
        cases = self.sequence(1)[:3]
        for case in cases:
            case['objects'][3]['objectId'] = 13
        row = self.play('wave_release', cases, MEMORY)[-1]
        self.assertEqual(row['memory']['cpAdvance'], 1)
        self.assertEqual(row['memory']['bestId'], 13)
        self.assertTrue(any(x['command'] == 'attackTarget' and x['arguments'] == [13] for x in row['actions']))

    def test_outer_route_uses_observed_advanced_ally(self):
        for x, y, lane, target in ((25, 12, 0, 13), (100, 90, 2, 25)):
            cases = self.sequence(1)[:3]
            for case in cases:
                case['objects'][3]['objectId'] = target
                # Four allies remain assembled; one is progressing along a flank.
                for obj in case['objects']:
                    if obj['objectId'] == 104:
                        obj['objectX'], obj['objectY'] = x, y
            row = self.play('outer_converge', cases, MEMORY)[-1]
            self.assertEqual(row['memory']['cpAdvance'], 1)
            self.assertEqual(row['memory']['cpLane'], lane)
            self.assertEqual(row['memory']['bestId'], target)

    def test_actual_rear_pressure_and_returning_group(self):
        for name in VARIANTS[1:]:
            for slot in range(5):
                cases = self.sequence(slot)[:3]
                for case in cases[1:]:
                    case['objects'].append(f.obj(888, kind=2, team=1, x=83, y=22))
                row = self.play(name, cases, MEMORY)[-1]
                self.assertEqual(row['memory']['defActive'], int(slot in (2, 3)))
                cases = self.sequence(slot)[:3]
                new = deepcopy(cases[-1]); new['self']['worldTick'] = 461
                new['objects'] += [f.obj(105+i, kind=2, team=1, x=70+i*7, y=50-i*4) for i in range(3)]
                cases.append(new)
                self.assertEqual(self.play(name, cases, MEMORY)[-1]['memory']['defActive'], 1)

    def test_dense_runtime_all_classes_and_creep_alarm(self):
        rows = []
        for name in VARIANTS[1:]:
            for team in (0, 1):
                for slot in range(5):
                    case = scene(team, count=5, worldTick=100, selfGold=150)
                    case['self']['selfClass'] = class_id(team, slot)
                    case['objects'] += [f.obj(1000+i, kind=3, team=i%2, x=i%116, y=i*7%116) for i in range(220)]
                    rows += self.play(name, [case], ('bestId', 'defActive'))
            for slot in (1, 2, 3):
                cases = self.sequence(slot)[:3]
                for tick in range(461, 471):
                    case = deepcopy(cases[2]); case['self']['worldTick'] = tick
                    case['objects'].append(f.obj(888, kind=3, team=1, x=104, y=12))
                    cases.append(case)
                result = self.play(name, cases, MEMORY)
                rows += result
                self.assertGreater(result[-1]['memory']['cpWaveUntil'], 470)
                self.assertEqual(result[-1]['memory']['defActive'], int(slot in (2, 3)))
        self.assertLessEqual(max(r['instructions'] for r in rows), 20000)
        self.assertLessEqual(max(r['work'] for r in rows), 50000)
        write(STUDY / 'vm-budget.json', {'decisions': len(rows),
              'max_instructions': max(r['instructions'] for r in rows),
              'max_work': max(r['work'] for r in rows)})


if __name__ == '__main__':
    unittest.main()
