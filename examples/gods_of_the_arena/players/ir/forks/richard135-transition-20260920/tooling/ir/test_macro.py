from pathlib import Path
import tempfile
import unittest
import test_policy_ir as f
from macro_candidates import make, VARIANTS
from policy_ir import compile_policy, extract

class MacroTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): f.RealVmTests.setUpClass.__func__(cls)
    run_vm=f.RealVmTests.run_vm

    def run_policy(self,name,cases,memory=('bestId',)):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'policy.bas';p.write_text(compile_policy(make(name)))
            return self.run_vm(p,cases,memory)

    def test_visible_fort_wins_but_protected_fort_does_not(self):
        enemies=[f.obj(101,kind=2,team=1,x=21),f.obj(2,kind=1,team=1,x=44)]
        rows=self.run_policy('objectives',[f.fixture(enemies),f.fixture([enemies[0],enemies[1]|{'objectAlive':0}],worldTick=2)])
        self.assertEqual([r['memory']['bestId'] for r in rows],[2,101])

    def test_mobile_pursuit_is_bounded_in_both_targeting_operators(self):
        for n in ['bounded','objectives']:
            row=self.run_policy(n,[f.fixture([f.obj(101,kind=2,team=1,x=60)])])[0]
            self.assertEqual(row['memory']['bestId'],0)
            self.assertFalse(any(a['command']=='attackTarget' for a in row['actions']))

    def test_lane_assignment_mirrors_and_resets_after_respawn(self):
        for team in [0,1]:
            moves=[]
            for slot in range(5):
                x,y=(105,11) if team==0 else (11,105)
                row=self.run_policy('lanes',[f.fixture(selfId=100+5*team+slot,selfTeam=team,selfX=x,selfY=y)])[0]
                move=next(a['arguments'] for a in row['actions'] if a['command']=='walkTo')
                moves.append(move if team==0 else [116-move[0],116-move[1]])
            self.assertEqual(moves,[[76,12],[76,12],[81,30],[108,44],[108,44]])
        cases=[f.fixture(selfId=100,selfX=76,selfY=12),f.fixture(selfId=100,selfX=105,selfY=11,worldTick=500)]
        rows=self.run_policy('lanes',cases,('laneStage',))
        self.assertEqual([r['memory']['laneStage'] for r in rows],[1,0])

    def test_vm_limits_all_classes_and_ir_symbolic_parity(self):
        objects=[f.obj(1000+i,team=i%2,x=2+i%105,y=4+i%90) for i in range(160)]
        cases=[f.fixture(objects,selfClass=c,selfId=100+c,selfGold=150) for c in range(10)]
        for n in VARIANTS:
            p=make(n);self.assertEqual(extract(compile_policy(p),p),p)
            for r in self.run_policy(n,cases):
                self.assertLessEqual(r['instructions'],20000)
                self.assertLessEqual(r['work'],50000)

if __name__=='__main__':unittest.main()
