import unittest
import test_policy_ir as f
import test_rush_unblock as unblock
from test_rush_defense import scene
from test_mixed_backdoor import intruder
from test_jordan_root import final_approach
from threat_coverage import make, VARIANTS


class CoverageTests(unittest.TestCase):
    factory = staticmethod(make)
    run_vm = f.RealVmTests.run_vm
    play = unblock.UnblockTests.play

    @classmethod
    def setUpClass(cls): f.RealVmTests.setUpClass.__func__(cls)

    def test_three_hero_rush_and_two_hero_core_attack(self):
        for team in (0, 1):
            case = scene(team, count=3, worldTick=100)
            case['self']['selfClass'] = 1 if team == 0 else 6
            self.assertEqual(self.play('deployed', [case])[0]['memory']['defActive'], 0)
            self.assertEqual(self.play('both_coverage', [case])[0]['memory']['defActive'], 1)
        case = intruder(1)
        case['objects'].append(case['objects'][-1] | {'objectId': 102})
        self.assertEqual(self.play('deployed', [case])[0]['memory']['defActive'], 0)
        row = self.play('both_coverage', [case])[0]
        self.assertEqual(row['memory']['defActive'], 1)
        self.assertIn(row['memory']['bestId'], (101, 102))
        for obj in case['objects'][-2:]: obj['objectTarget'] = 0
        self.assertEqual(self.play('both_coverage', [case])[0]['memory']['defActive'], 0)

    def test_components_compose_exactly_and_fit_budget(self):
        rows = []
        for team in (0, 1):
            for size in (40, 160, 240):
                case = final_approach(team, 4, 100)
                case['objects'] += [f.obj(3000+i, team=i%2, x=i%116, y=i*7%116) for i in range(size-len(case['objects']))]
                cases = [case | {'self': case['self'] | {'selfClass': c}} for c in range(team*5, team*5+5)]
                results = {n: self.play(n, cases) for n in VARIANTS}
                rows += [r for rs in results.values() for r in rs]
                unchanged = 'blue_coverage' if team == 0 else 'red_coverage'
                component = 'red_coverage' if team == 0 else 'blue_coverage'
                actions = lambda n: [r['actions'] for r in results[n]]
                self.assertEqual(actions('deployed'), actions(unchanged))
                self.assertEqual(actions('both_coverage'), actions(component))
        self.assertLessEqual(max(r['instructions'] for r in rows), 20000)
        self.assertLessEqual(max(r['work'] for r in rows), 50000)
        print('Coverage dense decisions', len(rows), 'max instructions/work', max(r['instructions'] for r in rows), max(r['work'] for r in rows))


if __name__ == '__main__': unittest.main()
