"""Supported siege prerequisites in the real BASIC VM and reverse IR edits."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

import test_policy_ir as f
from policy_ir import HERE, compile_policy, extract, read


class SiegeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        f.RealVmTests.setUpClass.__func__(cls)

    run_vm = f.RealVmTests.run_vm

    def play(self, cases, policy=None):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "policy.bas"
            path.write_text(compile_policy(policy or read(HERE / "hypotheses/supported_siege.ir.json")))
            return self.run_vm(path, cases, ["bestId", "siegeOverrides"])

    def test_only_exposed_near_supported_structures_override_nearest(self):
        enemy = f.obj(100, team=1, x=21)
        tower = f.obj(101, kind=4, team=1, x=28)
        support = f.obj(200, x=27)
        cases = [f.fixture([enemy, tower, support]),
                 f.fixture([enemy, tower]),
                 f.fixture([enemy, tower, dict(support, objectHp=0)]),
                 f.fixture([enemy, dict(tower, objectAlive=0), support]),
                 f.fixture([enemy, dict(tower, objectX=29), support]),
                 f.fixture([enemy, tower, dict(support, objectX=22)]),
                 f.fixture([enemy, tower, support], selfHp=59),
                 f.fixture([enemy, tower, support], selfHp=60)]
        results = self.play(cases)
        self.assertEqual([r["memory"]["bestId"] for r in results],
                         [101, 100, 100, 100, 100, 100, 100, 101])
        self.assertEqual(results[-1]["memory"]["siegeOverrides"], 2)

    def test_fort_priority_ties_and_no_enemy(self):
        support = f.obj(200, x=25)
        tower = f.obj(101, kind=4, team=1, x=24)
        fort = f.obj(102, kind=1, team=1, x=28)
        cases = [f.fixture([support, tower, fort]),
                 f.fixture([support, tower, dict(tower, objectId=99)]),
                 f.fixture([support])]
        self.assertEqual([r["memory"]["bestId"] for r in self.play(cases)], [102, 99, 0])

    def test_reverse_edit_changes_behavior_and_invalidates_beliefs(self):
        policy = read(HERE / "hypotheses/supported_siege.ir.json")
        source = compile_policy(policy)
        self.assertEqual(extract(source, policy), policy)
        edited = source.replace("selfMaxHp * 60", "selfMaxHp * 70")
        recovered = extract(edited, policy)
        self.assertEqual(recovered["skill"]["observe"]["parameters"]["health_percent"], 70)
        self.assertIn("goal/G_siege", recovered["update"]["needs_review"])
        self.assertEqual(recovered["belief"]["claims"]["B_supported_siege"]["status"], "requires_review")
        case = f.fixture([f.obj(100, team=1, x=21), f.obj(101, kind=4, team=1, x=28),
                          f.obj(200, x=27)], selfHp=65)
        self.assertEqual(self.play([case], policy)[0]["memory"]["bestId"], 101)
        self.assertEqual(self.play([case], recovered)[0]["memory"]["bestId"], 100)
        with self.assertRaises(ValueError):
            extract(source + "\ncastTarget(0, selfId)\n", policy)


if __name__ == "__main__":
    unittest.main()
