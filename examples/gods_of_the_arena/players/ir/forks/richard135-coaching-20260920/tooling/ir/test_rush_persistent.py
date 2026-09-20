import tempfile
import unittest
from pathlib import Path

import test_policy_ir as f
import test_rush_defense as previous
from policy_ir import compile_policy, extract
from rush_persistent import make, VARIANTS


class PersistentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        f.RealVmTests.setUpClass.__func__(cls)

    run_vm = f.RealVmTests.run_vm

    def play(self, name, cases):
        ir = make(name)
        with tempfile.TemporaryDirectory() as directory:
            src = Path(directory)/'policy.bas'
            src.write_text(compile_policy(ir))
            return self.run_vm(src, cases, ['defActive', 'defUntil', 'defMates', 'bestId'])

    def test_one_surviving_invader_refreshes_an_existing_commitment(self):
        start = previous.scene(worldTick=100)
        survivor = previous.scene(count=1, worldTick=101)
        survivor['objects'][-1].update(objectX=95, objectY=18, objectTarget=1)
        rows = self.play('sticky', [start, survivor])
        self.assertEqual([r['memory']['defActive'] for r in rows], [1, 1])
        self.assertEqual(rows[1]['memory']['defUntil'], 101+1440)
        self.assertEqual(self.play('sticky', [survivor])[0]['memory']['defActive'], 0)

    def test_gather_before_attacking_not_before_travel(self):
        case = previous.scene(); case['self'].update(selfX=67, selfY=46)
        alone = self.play('together', [case])[0]
        self.assertEqual(alone['memory']['bestId'], 0)
        self.assertTrue(any(a['command'] == 'walkTo' for a in alone['actions']))
        case['objects'] += [f.obj(100+i, kind=2, team=0, x=67+i, y=46) for i in range(3)]
        group = self.play('together', [case])[0]
        self.assertEqual(group['memory']['defMates'], 3)
        self.assertIn(group['memory']['bestId'], range(105, 110))

    def test_parity_and_crowd_boundaries(self):
        rows = []
        for name in VARIANTS:
            ir = make(name)
            self.assertEqual(extract(compile_policy(ir), ir), ir)
            for active in (False, True):
                for count in (39, 40, 41, 79, 80, 81, 160):
                    case = previous.scene(count=5 if active else 0, selfGold=150)
                    case['objects'] += [f.obj(2000+i, team=i%2, x=i%116, y=i*7%116) for i in range(count-len(case['objects']))]
                    rows += self.play(name, [case | {'self': case['self'] | {'selfClass': c}} for c in range(10)])
        self.assertLess(max(r['instructions'] for r in rows), 20000)
        self.assertLess(max(r['work'] for r in rows), 50000)


if __name__ == '__main__':
    unittest.main()
