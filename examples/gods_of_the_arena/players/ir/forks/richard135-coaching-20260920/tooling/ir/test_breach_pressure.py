import unittest
import test_policy_ir as f
import test_rush_unblock as unblock
from test_rush_defense import scene
from test_red_pressure import survivor_case
from test_jordan_root import final_approach
from breach_pressure import make,VARIANTS
from policy_ir import compile_policy,extract


class BreachTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=unblock.UnblockTests.play

    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_near_three_hero_breach_without_distant_recall(self):
        far=scene(0,count=3,worldTick=100);far['self']['selfClass']=1
        near=survivor_case(100);near['objects']=near['objects'][:7]
        for name in VARIANTS[2:]:
            self.assertEqual(self.play(name,[far])[0]['memory']['defActive'],0)
            self.assertEqual(self.play(name,[near])[0]['memory']['defActive'],1)
        self.assertEqual(self.play('pressure_parent',[near])[0]['memory']['defActive'],0)

    def test_blue_parity_and_dense_runtime(self):
        rows=[]
        for name in VARIANTS[2:]:
            p=make(name);self.assertEqual(extract(compile_policy(p),p),p)
            for team in (0,1):
                for n in (40,160,240):
                    case=final_approach(team,4,100)
                    case['objects'] += [f.obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(n-len(case['objects']))]
                    cases=[case|{'self':case['self']|{'selfClass':c}} for c in range(team*5,team*5+5)]
                    rr=self.play(name,cases);rows+=rr
                    if team==1:self.assertEqual([r['actions'] for r in rr],[r['actions'] for r in self.play('pressure_parent',cases)])
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        print('Breach dense decisions',len(rows),'max instructions/work',max(r['instructions'] for r in rows),max(r['work'] for r in rows))


if __name__=='__main__':unittest.main()
