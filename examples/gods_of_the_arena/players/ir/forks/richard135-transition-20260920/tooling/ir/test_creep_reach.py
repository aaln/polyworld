import unittest
import test_policy_ir as f
import test_rush_unblock as u
from test_jordan_root import final_approach
from creep_reach import make,STUDY
from policy_ir import compile_policy,extract,write


class CreepReachTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=u.UnblockTests.play

    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_actual_rally_boundary_and_runtime(self):
        first=final_approach(0,4,100);case=u.core_scene(0);case['self'].update(worldTick=101,selfX=108,selfY=34,selfClass=2)
        for c in (first,case):c['objects'][0]['objectY']=10
        old=self.play('pressure_parent',[first,case])[-1]
        self.assertEqual(old['memory']['bestId'],0)
        rows=[]
        for name in ('reach28','reach32'):
            p=make(name);self.assertEqual(extract(compile_policy(p),p),p)
            row=self.play(name,[first,case])[-1];self.assertIn(row['memory']['bestId'],range(2149,2155))
            for cls in range(5):
                a=final_approach(0,4,100);b=final_approach(0,0,101)
                b['objects'] += [f.obj(3000+i,team=1,x=84+i%5,y=11) for i in range(238)]
                rows+=self.play(name,[x|{'self':x['self']|{'selfClass':cls,'selfX':105,'selfY':11}} for x in (a,b)])
        write(STUDY/'vm-stress.json',{'passed':True,'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),
             'max_fixture_work':max(r['work'] for r in rows),'scope':'Hosted rounded boundary fixture plus same dense active red runtime screen; fullgames separatelyrequired'})


if __name__=='__main__':unittest.main()
