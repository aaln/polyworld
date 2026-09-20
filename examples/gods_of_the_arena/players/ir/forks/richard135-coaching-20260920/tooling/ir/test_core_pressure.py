import unittest
import test_policy_ir as f
import test_rush_unblock as unblock
from test_jordan_root import final_approach
from core_pressure import make,VARIANTS
from policy_ir import compile_policy,extract


class CorePressureTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=unblock.UnblockTests.play

    @classmethod
    def setUpClass(cls): f.RealVmTests.setUpClass.__func__(cls)

    def test_god_attacker_overrides_cheaper_combat_target(self):
        first=final_approach(0,4,100)
        first['self'].update(selfClass=0,selfX=105,selfY=14)
        second=final_approach(0,0,101)
        second['self'].update(selfClass=0,selfX=105,selfY=14)
        ranger=f.obj(106,kind=2,team=1,x=102,y=14,hp=561)
        ranger['objectTarget']=1
        druid=f.obj(108,kind=2,team=1,x=103,y=17,hp=346)
        druid['objectTarget']=100
        second['objects'] += [ranger,druid]
        self.assertEqual(self.play('pressure_parent',[first,second])[-1]['memory']['bestId'],108)
        for name in VARIANTS[2:]:
            row=self.play(name,[first,second])[-1]
            self.assertEqual(row['memory']['bestId'],106,name)
            self.assertTrue(any(a['command']=='attackTarget' and a['arguments']==[106] for a in row['actions']),name)

    def test_blue_parity_dense_runtime_and_ir_roundtrip(self):
        rows=[]
        for name in VARIANTS[2:]:
            p=make(name); self.assertEqual(extract(compile_policy(p),p),p)
            for team in (0,1):
                for n in (40,160,240):
                    case=final_approach(team,4,100)
                    case['objects'] += [f.obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(n-len(case['objects']))]
                    cases=[case|{'self':case['self']|{'selfClass':c}} for c in range(team*5,team*5+5)]
                    rr=self.play(name,cases); rows+=rr
                    if team==1:self.assertEqual([r['actions'] for r in rr],[r['actions'] for r in self.play('pressure_parent',cases)])
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        print('Core dense decisions',len(rows),'max instructions/work',max(r['instructions'] for r in rows),max(r['work'] for r in rows))


if __name__=='__main__': unittest.main()
