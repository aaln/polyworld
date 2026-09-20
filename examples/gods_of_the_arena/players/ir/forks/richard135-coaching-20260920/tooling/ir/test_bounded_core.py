import unittest
import test_policy_ir as f
import test_rush_unblock as unblock
from test_jordan_root import final_approach
from bounded_core import make,VARIANTS,STUDY,CANDIDATES
from policy_ir import compile_policy,extract,write


class BoundedCoreTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=unblock.UnblockTests.play

    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_dense_red_budget_and_normal_blue_parity(self):
        rows=[]
        for name in CANDIDATES:
            p=make(name);self.assertEqual(extract(compile_policy(p),p),p)
            for cls in range(5):
                for near in (False,True):
                    a=final_approach(0,4,100);b=final_approach(0,0,101)
                    b['objects'] += [f.obj(3000+i,team=1,x=102+i%3 if near else 84+i%5,y=11) for i in range(238)]
                    cases=[c|{'self':c['self']|{'selfClass':cls,'selfX':105,'selfY':11}} for c in (a,b)]
                    rows+=self.play(name,cases)
            for cls in range(5,10):
                case=final_approach(1,4,100)
                case['objects'] += [f.obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(240-len(case['objects']))]
                case['self']['selfClass']=cls
                rr=self.play(name,[case]);rows+=rr
                self.assertEqual(rr[0]['actions'],self.play('deployed',[case])[0]['actions'])
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(STUDY/'vm-stress.json',{'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),
            'max_fixture_work':max(r['work'] for r in rows),'passed':True,'scope':'240hostilecreeps near/far redallclasses,240mixedblueparity; fullgameworkverifiedseparately'})
        print('Bounded core stress',len(rows),max(r['instructions'] for r in rows),max(r['work'] for r in rows))

    def test_core_priority_and_safe_farm(self):
        first=final_approach(0,4,100);first['self'].update(selfClass=0,selfX=105,selfY=14)
        threat=final_approach(0,0,101);threat['self'].update(selfClass=0,selfX=105,selfY=14)
        ranger=f.obj(106,kind=2,team=1,x=102,y=14,hp=561);ranger['objectTarget']=1
        druid=f.obj(108,kind=2,team=1,x=103,y=17,hp=346);druid['objectTarget']=100
        threat['objects'] += [ranger,druid]
        quiet=final_approach(0,0,101);quiet['self'].update(selfClass=0,selfX=105,selfY=14)
        quiet['objects'].append(f.obj(1000,kind=3,team=1,x=84,y=11,hp=60))
        unsafe=quiet|{'objects':quiet['objects'][:2]+[f.obj(106,kind=2,team=1,x=95,y=35,hp=500)]+quiet['objects'][2:]}
        for name in CANDIDATES:
            self.assertEqual(self.play(name,[first,threat])[-1]['memory']['bestId'],106)
            self.assertEqual(self.play(name,[first,quiet])[-1]['memory']['bestId'],1000 if name.startswith('farm') else 0)
            self.assertEqual(self.play(name,[first,unsafe])[-1]['memory']['bestId'],0)


if __name__=='__main__':unittest.main()
