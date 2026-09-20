import unittest
import test_policy_ir as f
from test_rush_unblock import UnblockTests
from test_mixed_backdoor import intruder
from policy_ir import compile_policy,extract
from mixed_backdoor_protected import make,VARIANTS


class ProtectedTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=UnblockTests.play

    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_full_group_then_one_survivor_keeps_group_commitment(self):
        first=intruder(remote=True);first['objects'][-1]['objectId']=100
        for i in range(1,5):first['objects'].append(first['objects'][-1]|{'objectId':100+i})
        single=intruder(tick=101,remote=True)
        gone=intruder(tick=1000,remote=True);gone['objects']=gone['objects'][:-1]
        expired=intruder(tick=7500,remote=True);expired['objects']=expired['objects'][:-1]
        for name in VARIANTS[2:]:
            rows=self.play(name,[first,single,gone,expired])
            self.assertEqual([r['memory']['defActive'] for r in rows],[1,1,1,0],name)

    def test_unpreceded_solo_duty_remains_short(self):
        first=intruder();first['self']['selfClass']=7
        gone=intruder(tick=600);gone['self']['selfClass']=7;gone['objects']=gone['objects'][:-1]
        for name in VARIANTS[2:]:
            self.assertEqual([r['memory']['defActive'] for r in self.play(name,[first,gone])],[1,0])
        self.assertEqual(self.play('protected_near',[intruder(remote=True)])[0]['memory']['defActive'],0)

    def test_dense_budget_and_parity(self):
        rows=[]
        for name in VARIANTS[2:]:
            p=make(name);self.assertEqual(extract(compile_policy(p),p),p)
            for team in (0,1):
                for n in (40,80,160,240):
                    case=intruder(team,remote=True)
                    case['objects'] += [f.obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(n-len(case['objects']))]
                    rows+=self.play(name,[case|{'self':case['self']|{'selfClass':c}} for c in range(10)])
        print('Protected-defense decisions',len(rows),'max instructions/work',max(r['instructions'] for r in rows),max(r['work'] for r in rows))


if __name__=='__main__':unittest.main()
