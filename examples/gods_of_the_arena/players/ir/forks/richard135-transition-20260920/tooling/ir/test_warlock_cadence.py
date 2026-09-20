import unittest
import test_policy_ir as f
import test_rush_unblock as unblock
from test_jordan_root import final_approach
from warlock_cadence import make,STUDY
from policy_ir import compile_policy,extract,write


class WarlockTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=unblock.UnblockTests.play

    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def cases(self,cls):
        team=cls//5
        result=[]
        for tick,hits in [(1,0),(2,1)]:
            enemy=f.obj(200,kind=2,team=1-team,x=22);enemy['objectTarget']=1
            case=f.fixture([enemy],selfClass=cls,selfTeam=team,worldTick=tick,selfAttacksLanded=hits,
                selfAttackCooldown=12,selfAttackRange=330000)
            case['abilities']=[{'abilityCharges':1,'abilityCooldown':0} for _ in range(4)]
            case['abilities'][3]['abilityCooldown']=1
            result.append(case)
        return result

    def test_red_warlock_can_cast_both_regular_spells_during_retreat(self):
        cases=self.cases(3)
        before=self.play('pressure_parent',cases)[-1]
        self.assertFalse(any(a['command']=='castTarget' for a in before['actions']))
        row=self.play('warlock',cases)[-1]
        self.assertEqual([a['arguments'] for a in row['actions'] if a['command']=='castTarget'],[[2,200]])
        cases[-1]['abilities'][2]['abilityCooldown']=1
        row=self.play('warlock',cases)[-1]
        self.assertEqual([a['arguments'] for a in row['actions'] if a['command']=='castTarget'],[[1,200]])
        cases[-1]['returns']={'walkTo':0}
        self.assertFalse(any(a['command']=='castTarget' for a in self.play('warlock',cases)[-1]['actions']))

    def test_other_classes_blue_parity_and_dense_runtime(self):
        p=make('warlock');self.assertEqual(extract(compile_policy(p),p),p)
        for cls in range(10):
            if cls==3:continue
            cases=self.cases(cls)
            self.assertEqual([r['actions'] for r in self.play('warlock',cases)],
                [r['actions'] for r in self.play('pressure_parent',cases)])
        rows=[]
        for cls in range(5):
            a=final_approach(0,4,100);b=final_approach(0,0,101)
            b['objects'] += [f.obj(3000+i,team=1,x=102+i%3,y=11) for i in range(238)]
            cases=[c|{'self':c['self']|{'selfClass':cls,'selfX':105,'selfY':11}} for c in (a,b)]
            rows+=self.play('warlock',cases)
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(STUDY/'vm-stress.json',{'passed':True,'dense_decisions':len(rows),
            'max_instructions':max(r['instructions'] for r in rows),'max_fixture_work':max(r['work'] for r in rows)})


if __name__=='__main__':unittest.main()
