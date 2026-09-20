"""Native tests: restore middle quiet release, retain side-siege alarm and red."""
from copy import deepcopy
import unittest
from binding import CONTRACTS
from hero_binding import class_id
from policy_ir import compile_policy,extract,write
from relh154_scoped import make,STUDY,VARIANTS
from test_relh154 import side_scene
from test_rush_defense import scene
import test_rush_unblock as u
import test_policy_ir as f

class ScopedTests(unittest.TestCase):
    factory=staticmethod(make)
    play=u.UnblockTests.play
    run_vm=f.RealVmTests.run_vm
    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_middle_alarm_actions_and_release_match_deployed(self):
        for slot in (1,4):
            cases=[]
            for tick in range(100,801):
                c=scene(1,count=3 if tick==100 else 0,worldTick=tick)
                c['self'].update(selfId=105+slot,selfClass=class_id(1,slot),selfX=90,selfY=10)
                cases.append(c)
            old=self.play('deployed',cases,('defActive','defUntil','perimeterLastCombat'))
            for n in ('legacy','scoped'):
                new=self.play(n,cases,('defActive','defUntil','perimeterLastCombat'))
                self.assertEqual([r['actions'] for r in new],[r['actions'] for r in old])
                self.assertEqual([r['memory'] for r in new],[r['memory'] for r in old])
                self.assertEqual(new[-1]['memory']['defActive'],0)

    def test_side_alarm_and_scoped_travel(self):
        for n in ('legacy','scoped'):
            for slot in range(5):
                self.assertEqual(self.play(n,[side_scene(slot,150)],('defActive',))[0]['memory']['defActive'],1)
                self.assertEqual(self.play(n,[side_scene(slot,149)],('defActive',))[0]['memory']['defActive'],0)
                cases=[side_scene(slot,150,tick=100)]+[side_scene(slot,150,count=0,tick=t) for t in range(101,701)]
                r=self.play(n,cases,('defActive',))[-1]
                self.assertEqual(r['memory']['defActive'],int(n=='scoped' or slot in (0,2,3)))

    def test_roundtrip_red_and_budget(self):
        b=make('deployed')['skill']['observe'];red=CONTRACTS[b['operator']].source(b['parameters']).split('\nelse\n',1)[0];rows=[]
        for n in VARIANTS:
            p=make(n);self.assertEqual(extract(compile_policy(p),p),p)
            o=p['skill']['observe'];self.assertEqual(CONTRACTS[o['operator']].source(o['parameters']).split('\nelse\n',1)[0],red)
            for team in (0,1):
                for slot in range(5):
                    c=side_scene(slot,150) if team else scene(0,count=4,worldTick=1080)
                    c['self'].update(selfClass=class_id(team,slot),selfId=100+team*5+slot,selfGold=150)
                    c['objects'] += [f.obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(240-len(c['objects']))]
                    rows+=self.play(n,[c])
        self.assertLessEqual(max(r['instructions'] for r in rows),20000);self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(STUDY/'vm-budget.json',{'passed':True,'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),'max_work':max(r['work'] for r in rows)})

if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ScopedTests))
    write(STUDY/'vm-proof.json',{'passed':r.wasSuccessful(),'tests':r.testsRun,'errors':len(r.errors),'failures':len(r.failures)})
    raise SystemExit(0 if r.wasSuccessful() else 1)
