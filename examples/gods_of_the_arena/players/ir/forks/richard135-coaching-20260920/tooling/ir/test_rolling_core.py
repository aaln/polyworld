import unittest
import test_policy_ir as f
import test_rush_unblock as u
from test_jordan_root import final_approach
from rolling_core import make,STUDY
from policy_ir import write


class RollingCoreTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=u.UnblockTests.play

    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_late_creep_discovery_and_persistence_without_hero_trigger(self):
        for name in ('scan8',):
            initial=u.core_scene(0)
            initial_row=self.play(name,[initial],('bestId','defActive','creepCoreId'))[0]
            self.assertIn(initial_row['memory']['creepCoreId'],range(2149,2155))
            self.assertEqual(initial_row['memory']['defActive'],1)
            case=u.core_scene(0);case['objects']=case['objects'][:4]
            case['objects'] += [f.obj(3000+i,team=1,x=70,y=50) for i in range(220)]
            enemy=f.obj(4000,team=1,x=104,y=14,hp=60);enemy['objectTarget']=1
            case['objects'].append(enemy)
            first=final_approach(0,4,100);first['self'].update(selfX=90,selfY=5,selfClass=2)
            cases=[first]+[case|{'self':case['self']|{'worldTick':t}} for t in range(101,140)]
            rows=self.play(name,cases,('bestId','defActive','creepCoreId'))
            found=[i for i,r in enumerate(rows) if r['memory']['creepCoreId']==4000]
            self.assertTrue(found)
            self.assertLessEqual(found[0],len(case['objects'])//int(name[4:])+2)
            self.assertTrue(all(r['memory']['bestId']==4000 and r['memory']['defActive']==1 for r in rows[found[0]:]))
            gone=case|{'objects':case['objects'][:-1],'self':case['self']|{'worldTick':140}}
            self.assertNotEqual(self.play(name,cases+[gone])[-1]['memory']['bestId'],4000)

    def test_scope_and_dense_runtime(self):
        rows=[]
        for name in ('scan8',):
            for cls in range(5):
                for near in (False,True):
                    a=final_approach(0,4,100);b=final_approach(0,0,101)
                    b['objects'] += [f.obj(3000+i,team=1,x=102+i%3 if near else 84+i%5,y=11) for i in range(238)]
                    cases=[c|{'self':c['self']|{'selfClass':cls,'selfX':105,'selfY':11}} for c in (a,b)]
                    rows+=self.play(name,cases)
            for cls in range(5,10):
                c=u.core_scene(1);c['self']['selfClass']=cls
                self.assertEqual(self.play(name,[c])[0]['actions'],self.play('deployed',[c])[0]['actions'])
        result={'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),
                'max_fixture_work':max(r['work'] for r in rows),'passed':True}
        write(STUDY/'vm-stress.json',result);print(result)


if __name__=='__main__':unittest.main()
