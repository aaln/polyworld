from pathlib import Path
import tempfile
import unittest

import test_policy_ir as f
from class_release_candidates import make
from policy_ir import HERE,compile_policy,read,extract
from release_workspace import RUN

class ClassReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        f.RealVmTests.setUpClass.__func__(cls)
    run_vm=f.RealVmTests.run_vm

    def trace(self, source, cases):
        rows = self.run_vm(source, cases)
        for row in rows:
            self.assertLessEqual(row["instructions"], 20000)
            self.assertLessEqual(row["work"], 50000)
        return [row["actions"] for row in rows]

    def test_other_nine_classes_keep_parent_action_trace(self):
        parent=RUN/'local/candidates/footprint/policy.bas'
        with tempfile.TemporaryDirectory() as temp:
            for name in ['berserker_plain','berserker_base']:
                source=Path(temp)/'p.bas';source.write_text(compile_policy(make(name)))
                for cls in range(9):
                    cases=[f.fixture([f.obj(100,kind=2,team=1,x=23),f.obj(44,kind=5,team=1,x=24)],
                           selfClass=cls,worldTick=t,selfAttacksLanded=t//3,selfAttackCooldown=12,
                           selfAttackRange=330000,selfGold=150,selfHp=40 if t%2 else 90) for t in range(1,12)]
                    self.assertEqual(self.trace(parent,cases),self.trace(source,cases))

    def test_reverse_extraction_recovers_class_routing_and_requests_goal_review(self):
        parent=read(RUN/'hosted-discovery/footprint/feedback/policy.ir.json')
        candidate=make('berserker_base')
        recovered=extract(compile_policy(candidate),parent)
        self.assertEqual(recovered['skill'],candidate['skill'])
        self.assertIn('goal/G_base',recovered['update']['needs_review'])
        self.assertIn('goal/G_cadence',recovered['update']['needs_review'])

    def test_berserker_base_matches_waveguard_actions(self):
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)/'p.bas';source.write_text(compile_policy(make('berserker_base')))
            cases=[f.fixture([f.obj(100,kind=2,team=1,x=23),f.obj(44,kind=5,team=1,x=24)],
                   selfClass=9,worldTick=t,selfAttacksLanded=t//3,selfAttackCooldown=12,
                   selfAttackRange=80000,selfGold=150,selfHp=40 if t%2 else 90) for t in range(1,20)]
            self.assertEqual(self.trace(HERE/'waveguard_xp.evaluated.bas',cases),self.trace(source,cases))

if __name__=='__main__': unittest.main()
