from pathlib import Path
import tempfile
import unittest

import test_policy_ir as f
from lich_release import make, PARENT
from policy_ir import HERE, compile_policy, extract, read


class LichRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        f.RealVmTests.setUpClass.__func__(cls)

    run_vm = f.RealVmTests.run_vm

    def test_all_classes_match_the_intended_controller(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'candidate.bas'
            source.write_text(compile_policy(make()))
            for cls in range(10):
                parent = (HERE / 'cadence_all.evaluated.bas' if cls == 7 else
                          PARENT / 'local/candidates/berserker_base/policy.bas')
                cases = [f.fixture([f.obj(100, kind=2, team=1, x=23), f.obj(44, kind=5, team=1, x=24)],
                    selfClass=cls, worldTick=t, selfAttacksLanded=t//3, selfAttackCooldown=12,
                    selfAttackRange=330000, selfGold=150, selfHp=40 if t%2 else 90) for t in range(1,20)]
                actual, expected = self.run_vm(source, cases), self.run_vm(parent, cases)
                self.assertEqual([r['actions'] for r in actual], [r['actions'] for r in expected], cls)
                for row in actual:
                    self.assertLessEqual(row['instructions'], 20000)
                    self.assertLessEqual(row['work'], 50000)

    def test_symbolic_edit_recovers_routing_and_flags_intent(self):
        old = read(PARENT / 'hosted-confirmation/berserker_base/feedback/policy.ir.json')
        candidate = make()
        recovered = extract(compile_policy(candidate), old)
        self.assertEqual(recovered['skill'], candidate['skill'])
        self.assertIn('goal/G_base', recovered['update']['needs_review'])
        self.assertEqual(extract(compile_policy(candidate), candidate), candidate)


if __name__ == '__main__':
    unittest.main()
