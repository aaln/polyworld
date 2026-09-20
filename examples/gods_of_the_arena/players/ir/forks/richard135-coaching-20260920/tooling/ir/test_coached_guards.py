import tempfile
from pathlib import Path
import unittest
import test_policy_ir as f
from coached_guards import make,VARIANTS
from policy_ir import compile_policy,extract


class GuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)
    run_vm=f.RealVmTests.run_vm

    def decisions(self,name,cases):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'policy.bas';p.write_text(compile_policy(make(name)))
            return self.run_vm(p,cases,['bestId','pushHold','pushLane'])

    def test_guard_progression_and_god_exposure(self):
        guard=f.obj(30,kind=4,team=1,x=20,y=20)
        other=f.obj(31,kind=4,team=1,x=25,y=20)
        god=f.obj(2,kind=1,team=1,x=28,y=20,alive=0)
        cases=[f.fixture([god,other,guard],selfAttackRange=390000),
               f.fixture([god,other,guard|{'objectHp':0}],selfAttackRange=390000),
               f.fixture([god|{'objectAlive':1}],selfAttackRange=390000)]
        self.assertEqual([r['memory']['bestId'] for r in self.decisions('team',cases)],[30,31,2])

    def test_melee_waits_and_ranged_withdraws_under_aggro(self):
        guard=f.obj(30,kind=4,team=1,x=20,y=20)
        creep=f.obj(900,kind=3,team=0,x=23,y=20)
        cases=[f.fixture([guard],selfAttackRange=70000),
               f.fixture([guard,creep],selfAttackRange=70000),
               f.fixture([guard|{'objectTarget':1}],selfAttackRange=390000)]
        self.assertEqual([r['memory']['bestId'] for r in self.decisions('team',cases)],[0,30,0])

    def test_team_lane_and_siege_focus(self):
        self.assertEqual(self.decisions('team',[f.fixture(selfTeam=1)])[0]['memory']['pushLane'],0)
        tower=f.obj(25,kind=4,team=1,x=28,y=20)
        enemy=f.obj(107,kind=2,team=1,x=20,y=28)
        c=f.fixture([tower,enemy],selfAttackRange=390000)
        self.assertEqual(self.decisions('focus',[c])[0]['memory']['bestId'],25)
        self.assertEqual(self.decisions('team',[c])[0]['memory']['bestId'],107)

    def test_roundtrips_and_dense_budget(self):
        objs=[f.obj(1000+i,team=i%2,x=i%116,y=(i*7)%116) for i in range(160)]
        for n in VARIANTS:
            p=make(n);self.assertEqual(extract(compile_policy(p),p),p)
            for row in self.decisions(n,[f.fixture(objs,selfClass=c,selfGold=150) for c in range(10)]):
                self.assertLessEqual(row['work'],50000)
                self.assertLessEqual(row['instructions'],20000)


if __name__=='__main__':unittest.main()
