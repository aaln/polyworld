import tempfile
from pathlib import Path
import unittest
import test_policy_ir as f
from coached_candidates import make,VARIANTS
from policy_ir import compile_policy,extract


class CoachedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)
    run_vm=f.RealVmTests.run_vm

    def policy(self,name,cases):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'policy.bas';p.write_text(compile_policy(make(name)))
            return self.run_vm(p,cases,['bestId','pushHold','pushCreeps','pushLane','pushRotations'])

    def test_no_tower_attack_without_creeps_and_no_chasing_under_it(self):
        tower=f.obj(25,kind=4,team=1,x=95,y=104)
        enemy=f.obj(107,kind=2,team=1,x=90,y=104)
        row=self.policy('outer',[f.fixture([tower,enemy],selfX=88,selfY=104)])[0]
        self.assertEqual(row['memory']['bestId'],0)
        self.assertEqual(row['memory']['pushHold'],1)
        self.assertFalse(any(a['command']=='attackTarget' for a in row['actions']))
        move=next(a['arguments'] for a in row['actions'] if a['command']=='walkTo')
        self.assertGreaterEqual((move[0]-95)**2+(move[1]-104)**2,81)

    def test_creep_support_and_sticky_hero_aggro(self):
        tower=f.obj(25,kind=4,team=1,x=95,y=104)
        creep=f.obj(1001,kind=3,team=0,x=93,y=104)
        cases=[f.fixture([tower,creep]),f.fixture([tower|{'objectTarget':100},creep],worldTick=2),
               f.fixture([tower|{'objectTarget':1001},creep],worldTick=3)]
        rows=self.policy('outer',cases)
        self.assertEqual([r['memory']['bestId'] for r in rows],[25,0,25])

    def test_supported_rotation_requires_progress_and_wait(self):
        tower=f.obj(26,kind=4,team=1,x=47,y=104)
        alt=f.obj(19,kind=4,team=1,x=51,y=73)
        creep=f.obj(1001,kind=3,team=0,x=51,y=75)
        rows=self.policy('rotate',[f.fixture([tower,alt,creep],worldTick=t) for t in [1,200,242]])
        self.assertEqual([r['memory']['pushLane'] for r in rows],[2,2,1])
        self.assertEqual(rows[-1]['memory']['pushRotations'],1)

    def test_exposed_fort_overrides_hold_and_barracks(self):
        objs=[f.obj(2,kind=1,team=1),f.obj(25,kind=4,team=1),f.obj(44,kind=5,team=1)]
        row=self.policy('outer',[f.fixture(objs)])[0]
        self.assertEqual(row['memory']['bestId'],2)
        self.assertEqual(row['memory']['pushHold'],0)

    def test_vm_budget_and_semantic_roundtrip(self):
        objects=[f.obj(1000+i,team=i%2,x=i%116,y=(i*7)%116) for i in range(160)]
        for n in VARIANTS:
            p=make(n);self.assertEqual(extract(compile_policy(p),p),p)
            for row in self.policy(n,[f.fixture(objects,selfClass=c,selfGold=150) for c in range(10)]):
                self.assertLessEqual(row['work'],50000)
                self.assertLessEqual(row['instructions'],20000)


if __name__=='__main__':unittest.main()
