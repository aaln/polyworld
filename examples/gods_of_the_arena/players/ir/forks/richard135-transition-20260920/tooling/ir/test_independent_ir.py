"""Independent reconstruction, parent-free lifting and actual-VM parity."""

from copy import deepcopy
from pathlib import Path
import random
import tempfile
import unittest

import basic_syntax
import independent_ir as fresh
import test_policy_ir as fixtures
from policy_ir import HERE, compile_policy, extract, read


class IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.RealVmTests.setUpClass.__func__(cls)

    run_vm = fixtures.RealVmTests.run_vm

    def test_independent_ast_and_parent_free_lifting(self):
        source = (HERE.parent / "base.bas").read_text()
        policy = fresh.derive()
        self.assertEqual(basic_syntax.parse(fresh.compile_policy(policy)), basic_syntax.parse(source))
        self.assertEqual(fresh.extract(source)["skill"], policy["skill"])
        edited = source.replace("selfMaxHp * 3", "selfMaxHp * 4").replace("walkTo(64, 64)", "walkTo(65, 63)")
        lifted = fresh.extract(edited)
        self.assertEqual(lifted["skill"]["inventory"]["heal_ratio"], [4,5])
        self.assertEqual(lifted["skill"]["fallback"]["point"], [65,63])
        self.assertEqual(basic_syntax.parse(fresh.compile_policy(lifted)),basic_syntax.parse(edited))
        self.assertTrue(lifted["update"]["needs_review"])

    def test_independent_reader_rejects_unmodeled_behavior(self):
        source = (HERE.parent / "base.bas").read_text()
        for edit in [source+"\nbuyItem(20)\n",source.replace("distance < bestDistance","distance <= bestDistance"),
                     source.replace("hasHeal = 0 then","hasHeal = 1 then")]:
            with self.assertRaises(ValueError):
                fresh.extract(edit)
        policy = fresh.derive()
        policy["strategy"]["phases"].reverse()
        with self.assertRaises(ValueError):
            fresh.compile_policy(policy)
        policy = fresh.derive()
        policy["skill"]["inventory"]["presence"] = "after_use"
        with self.assertRaises(ValueError):
            fresh.compile_policy(policy)

    def test_independent_lowering_matches_real_vm_for_all_classes(self):
        rng = random.Random(91165000)
        cases = []
        for i in range(500):
            objects = [fixtures.obj(j+100,kind=rng.randrange(1,5),team=rng.randrange(2),
                                    x=rng.randrange(128),y=rng.randrange(128),alive=rng.randrange(2)) for j in range(16)]
            case = fixtures.fixture(objects,selfClass=i%10,selfHp=rng.randrange(101),selfGold=rng.randrange(1001),
                                    selfMana=rng.randrange(101),worldTick=i+1)
            case["inventory"] = [rng.randrange(21) for _ in range(6)]
            case["returns"] = {name:rng.randrange(2) for name in ["walkTo","attackTarget","buyItem","useItem"]}
            cases.append(case)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)/"fresh.bas"
            source.write_text(fresh.compile_policy(fresh.derive()))
            original = self.run_vm(HERE.parent/"base.bas",cases,["bestId","hasHeal","emptySlot","decisions"])
            reconstructed = self.run_vm(source,cases,["bestId","hasHeal","emptySlot","decisions"])
            self.assertEqual(original,reconstructed)

    def test_current_ir_can_incorporate_unmarked_symbolic_edits(self):
        parent = read(HERE / "base.ir.json")
        source = (HERE.parent / "base.bas").read_text().replace("selfMaxHp * 3","selfMaxHp * 4")
        result = extract(source,parent)
        self.assertEqual(result["skill"]["consume"]["parameters"]["heal_numerator"],4)
        self.assertEqual(basic_syntax.parse(compile_policy(result)),basic_syntax.parse(source))
        self.assertIn("goal/G_capacity",result["update"]["needs_review"])


if __name__ == "__main__":
    unittest.main()
