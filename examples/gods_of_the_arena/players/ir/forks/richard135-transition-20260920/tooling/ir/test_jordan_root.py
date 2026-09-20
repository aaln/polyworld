import unittest
import test_policy_ir as f
from policy_ir import compile_policy,extract
from test_rush_unblock import UnblockTests
from test_rush_defense import scene
from jordan_root import make,VARIANTS


def final_approach(team=1,count=1,tick=101):
    case=scene(team,count=0,worldTick=tick)
    case['objects']=case['objects'][:2]
    for i in range(count):
        case['objects'].append(f.obj(103+i,kind=2,team=1-team,x=15+i if team else 101-i,y=95 if team else 21,hp=682))
    case['self'].update(selfClass=7 if team else 2,selfX=6 if team else 110,selfY=101 if team else 15,selfHp=520,selfMaxHp=520)
    return case


class RootTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=UnblockTests.play
    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_visible_approach_outside_self_circle_engages_on_both_colors(self):
        for team in (0,1):
            cases=[final_approach(team,4,100),final_approach(team)]
            old=self.play('deployed_parent',cases)[-1]
            self.assertEqual(old['memory']['bestId'],0)
            for n in VARIANTS[2:]:
                if team==0 and n=='blue_front20':continue
                new=self.play(n,cases)[-1]
                self.assertEqual(new['memory']['bestId'],103,n)
                self.assertTrue(any(a['command']=='attackTarget' and a['arguments']==[103] for a in new['actions']),n)

    def test_quiet_release_reacquires_observed_rush(self):
        cases=[final_approach(1,4,100),final_approach(1,0,101),final_approach(1,0,581),final_approach(1,4,582)]
        rows=self.play('release_all20',cases)
        self.assertEqual([r['memory']['defActive'] for r in rows],[1,1,0,1])
        self.assertEqual(self.play('perimeter24',cases)[2]['memory']['defActive'],1)
        self.assertEqual(self.play('release20',cases)[2]['memory']['defActive'],1) # mage stays sentry

    def test_no_global_recall_without_trigger_and_red_scope_parity(self):
        for team in (0,1):
            cases=[scene(team,count=0,worldTick=1,selfGold=150)]
            old=self.play('blue_assigned',cases)[0]['actions']
            for n in VARIANTS[2:]:self.assertEqual(self.play(n,cases)[0]['actions'],old,n)
        cases=[final_approach(0,4,100),final_approach(0)]
        self.assertEqual([r['actions'] for r in self.play('blue_front20',cases)], [r['actions'] for r in self.play('blue_assigned',cases)])

    def test_destroyed_anchor_redirects_coverage_to_own_god(self):
        first=scene(1,count=5,worldTick=100)
        first['self'].update(selfClass=7)
        last=scene(1,count=0,worldTick=101)
        last['self'].update(selfClass=7,selfX=6,selfY=101)
        last['objects'][3]['objectHp']=0
        last['objects'].append(f.obj(2000,kind=3,team=0,x=23,y=95,hp=60))
        result=self.play('perimeter18',[first,last],('bestId','perimeterAnchor','perimeterX','perimeterY'))[-1]
        self.assertEqual(result['memory']['perimeterAnchor'],2)
        self.assertEqual(result['memory']['bestId'],2000)

    def test_ongoing_perimeter_target_prevents_quiet_release(self):
        cases=[final_approach(1,4,100)]+[final_approach(1,1,tick) for tick in (101,580,600)]
        rows=self.play('release_all20',cases)
        self.assertTrue(all(r['memory']['defActive']==1 and r['memory']['bestId']!=0 for r in rows))

    def test_roundtrip_and_dense_vm_budget(self):
        rows=[]
        for n in VARIANTS[2:]:
            p=make(n);self.assertEqual(extract(compile_policy(p),p),p)
            for team in (0,1):
                for size in (40,80,160,240):
                    a=final_approach(team,4,100)
                    a['objects'] += [f.obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(size-len(a['objects']))]
                    rows+=self.play(n,[a|{'self':a['self']|{'selfClass':c}} for c in range(team*5,team*5+5)])
        print('Root decisions',len(rows),'max instructions/work',max(r['instructions'] for r in rows),max(r['work'] for r in rows))

if __name__=='__main__':unittest.main()
