import unittest
import test_policy_ir as f
import test_rush_unblock as unblock
from test_rush_defense import scene
from test_jordan_root import final_approach
from red_pressure import make, VARIANTS


def survivor_case(tick, hero_class=1):
    case = scene(0, count=5 if tick in (100, 800) else 1, worldTick=tick)
    case['self'].update(selfClass=hero_class, selfX=50, selfY=40)
    case['objects'][2].update(objectX=96, objectY=25)
    for obj in case['objects'][4:]: obj.update(objectX=90, objectY=25)
    return case


class PressureTests(unittest.TestCase):
    factory = staticmethod(make)
    run_vm = f.RealVmTests.run_vm
    play = unblock.UnblockTests.play

    @classmethod
    def setUpClass(cls): f.RealVmTests.setUpClass.__func__(cls)

    def test_survivor_does_not_permanently_recall_attackers(self):
        cases = [survivor_case(t) for t in range(100, 801)]
        old = self.play('deployed', cases)
        new = self.play('pressure20', cases)
        self.assertEqual(old[600-100]['memory']['defActive'], 1)
        self.assertEqual([new[t-100]['memory']['defActive'] for t in (100, 579, 580, 799, 800)], [1, 1, 0, 0, 1])
        sentries = self.play('pressure20', [survivor_case(t, 0) for t in range(100, 801)])
        self.assertTrue(all(x['memory']['defActive'] == 1 for x in sentries))

    def test_blue_commands_and_dense_budget(self):
        rows = []
        for name in VARIANTS:
            for team in (0, 1):
                for size in (40, 160, 240):
                    case = final_approach(team, 4, 100)
                    case['objects'] += [f.obj(3000+i, team=i%2, x=i%116, y=i*7%116) for i in range(size-len(case['objects']))]
                    cases = [case | {'self': case['self'] | {'selfClass': c}} for c in range(team*5, team*5+5)]
                    rr = self.play(name, cases); rows += rr
                    if team == 1:
                        self.assertEqual([r['actions'] for r in rr], [r['actions'] for r in self.play('deployed', cases)])
        self.assertLessEqual(max(r['instructions'] for r in rows), 20000)
        self.assertLessEqual(max(r['work'] for r in rows), 50000)
        print('Pressure dense decisions', len(rows), 'max instructions/work', max(r['instructions'] for r in rows), max(r['work'] for r in rows))


if __name__ == '__main__': unittest.main()
