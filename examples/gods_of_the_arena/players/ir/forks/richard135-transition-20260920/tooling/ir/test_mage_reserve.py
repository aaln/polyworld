import unittest
import test_policy_ir as f
import test_rush_unblock as unblock
from test_jordan_root import final_approach
from mage_reserve import make,VARIANTS,STUDY
from policy_ir import compile_policy,extract,write


class MageReserveTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=unblock.UnblockTests.play

    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_reserves_space_and_other_classes_unchanged(self):
        for name in VARIANTS[2:]:
            p=make(name);self.assertEqual(extract(compile_policy(p),p),p)
            for cls in range(10):
                case=f.fixture([],worldTick=1,selfClass=cls,selfTeam=cls//5,selfHp=1000,selfMaxHp=1000,selfMana=1000,selfMaxMana=1000,selfGold=1000)
                case['inventory']=[12,6,10,9,0,0]
                row=self.play(name,[case])[0]
                if cls in (2,3):
                    purchases=[a for a in row['actions'] if a['command']=='buyItem' and a['arguments'][0]>4 and a['accepted']]
                    self.assertEqual(len(purchases),int(name[3:])-4)
                else:self.assertEqual(row['actions'],self.play('pressure_parent',[case])[0]['actions'])

    def test_dense_red_budget(self):
        rows=[]
        for name in VARIANTS[2:]:
            for cls in range(5):
                a=final_approach(0,4,100);b=final_approach(0,0,101)
                b['objects'] += [f.obj(3000+i,team=1,x=102+i%3,y=11) for i in range(238)]
                cases=[c|{'self':c['self']|{'selfClass':cls,'selfX':105,'selfY':11}} for c in (a,b)]
                rows+=self.play(name,cases)
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(STUDY/'vm-stress.json',{'passed':True,'dense_decisions':len(rows),
            'max_instructions':max(r['instructions'] for r in rows),'max_fixture_work':max(r['work'] for r in rows)})


if __name__=='__main__':unittest.main()
