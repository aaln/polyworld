"""Real-VM evidence for earlier blue side-siege recall and preserved red behavior."""
from copy import deepcopy
import unittest
from binding import CONTRACTS
from hero_binding import class_id
from policy_ir import compile_policy,extract,write
from relh154_research import make,STUDY,VARIANTS
from test_rush_defense import scene
import test_rush_unblock as unblock
import test_policy_ir as f


def side_scene(slot=0,damage=50,count=2,tick=1080,anchor=25):
    c=scene(1,count=count,worldTick=tick)
    c['self'].update(selfId=105+slot,selfClass=class_id(1,slot),selfX=20,selfY=15)
    maxhp={13:950,14:1300,15:1950,25:950,26:1300,27:1950}[anchor]
    c['objects'][3].update(objectId=anchor,objectX=95,objectY=104,objectHp=maxhp-damage)
    for i,e in enumerate(c['objects'][4:]):
        e.update(objectId=100+i,objectClass=class_id(0,i),objectX=99+i,objectY=102,objectTarget=anchor)
    return c

class RelhWarningTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=unblock.UnblockTests.play
    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_actual_classes_and_damage_thresholds(self):
        for slot in range(5):
            for name in VARIANTS:
                for damage in (0,49,50,149,150):
                    r=self.play(name,[side_scene(slot,damage)],('defActive',))[0]
                    self.assertEqual(bool(r['memory']['defActive']),name.startswith('pair') and damage>=int(name[4:]),(slot,name,damage,r))

    def test_damage_must_be_near_visible_enemy_pair_in_early_window(self):
        for name in ('pair50','pair150'):
            for anchor in (13,14,15,25,26,27):
                c=side_scene(damage=150,anchor=anchor)
                self.assertEqual(self.play(name,[c],('defActive',))[0]['memory']['defActive'],1)
            for kind in ('single','late','dead','far'):
                c=side_scene(damage=150)
                if kind=='single':c['objects'].pop()
                if kind=='late':c['self']['worldTick']=3601
                if kind=='dead':c['objects'][3]['objectHp']=0
                if kind=='far':
                    for e in c['objects'][4:]:e.update(objectX=50,objectY=50)
                self.assertEqual(self.play(name,[c],('defActive',))[0]['memory']['defActive'],0,(name,kind))

    def test_travel_is_not_quiet_arrival(self):
        for name in ('pair50','pair150'):
            cases=[side_scene(slot=2,damage=150,tick=100)]
            cases += [side_scene(slot=2,damage=150,count=0,tick=t) for t in range(101,821)]
            rows=self.play(name,cases,('defActive','perimeterLastCombat'))
            self.assertEqual(rows[-1]['memory']['defActive'],1)
            self.assertEqual(rows[-1]['memory']['perimeterLastCombat'],820)

    def test_roundtrip_red_branch_and_dense_actual_classes(self):
        baseline=make('deployed')['skill']['observe'];rows=[]
        red=CONTRACTS[baseline['operator']].source(baseline['parameters']).split('\nelse\n',1)[0]
        for name in VARIANTS:
            p=make(name);self.assertEqual(extract(compile_policy(p),p),p)
            o=p['skill']['observe'];self.assertEqual(CONTRACTS[o['operator']].source(o['parameters']).split('\nelse\n',1)[0],red)
            for team in (0,1):
                for slot in range(5):
                    for active in (False,True):
                        c=side_scene(slot,damage=150,count=4 if active else 0) if team else scene(0,count=4 if active else 0,worldTick=1080)
                        c['self'].update(selfId=100+team*5+slot,selfClass=class_id(team,slot),selfGold=150)
                        c['objects'] += [f.obj(3000+i,kind=3,team=i%2,x=i%116,y=i*7%116) for i in range(240-len(c['objects']))]
                        rows+=self.play(name,[c])
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(STUDY/'vm-budget.json',{'passed':True,'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),'max_work':max(r['work'] for r in rows)})

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(RelhWarningTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    write(STUDY/'vm-proof.json',{'passed':result.wasSuccessful(),'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors)})
    raise SystemExit(0 if result.wasSuccessful() else 1)
