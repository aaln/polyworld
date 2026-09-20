"""Exercise terminal priority in the real VM, including the runtime budget."""
import tempfile
import unittest
from pathlib import Path

import test_policy_ir as fixtures
from coached_finish import make, VARIANTS
from policy_ir import compile_policy, extract


class FinishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.RealVmTests.setUpClass.__func__(cls)

    run_vm = fixtures.RealVmTests.run_vm

    def decisions(self, name, cases):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'policy.bas'
            source.write_text(compile_policy(make(name)))
            return self.run_vm(source, cases, ['bestId'])

    def test_guard_and_exposed_god_priority(self):
        guard = fixtures.obj(30, kind=4, team=1, x=28, y=20)
        barracks = fixtures.obj(44, kind=5, team=1, x=22, y=20)
        god = fixtures.obj(2, kind=1, team=1, x=32, y=20, alive=0)
        cases = [fixtures.fixture([guard, barracks, god], selfClass=7),
                 fixtures.fixture([guard, barracks, god | {'objectAlive': 1}], selfClass=7)]
        self.assertEqual([r['memory']['bestId'] for r in self.decisions('all', cases)], [30, 2])

    def test_nearby_mobile_threat_preserves_defense(self):
        guard = fixtures.obj(30, kind=4, team=1, x=28, y=20)
        enemy = fixtures.obj(107, kind=2, team=1, x=22, y=20)
        row = self.decisions('all', [fixtures.fixture([guard, enemy], selfClass=7)])[0]
        self.assertEqual(row['memory']['bestId'], 107)

    def test_roundtrip_and_dense_runtime_budget(self):
        objects = [fixtures.obj(1000+i, team=i%2, x=i%116, y=(i*7)%116) for i in range(160)]
        for name in VARIANTS:
            ir = make(name)
            self.assertEqual(extract(compile_policy(ir), ir), ir)
            rows = self.decisions(name, [fixtures.fixture(objects, selfClass=c, selfGold=150)
                                         for c in range(10)])
            for row in rows:
                self.assertLessEqual(row['work'], 50000)
                self.assertLessEqual(row['instructions'], 20000)


if __name__ == '__main__':
    unittest.main()
