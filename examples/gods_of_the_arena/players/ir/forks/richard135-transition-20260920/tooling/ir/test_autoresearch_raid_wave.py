"""Native interaction tests for the preregistered raid-wave combination."""
from copy import deepcopy
import unittest
import test_policy_ir as f
import test_rush_unblock as u
import test_coach_assembled as a
from test_rush_defense import scene
from hero_binding import class_id
from autoresearch_raid_wave import make, STUDY
from policy_ir import write


class RaidWaveTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=u.UnblockTests.play
    sequence=a.AssembledTests.sequence

    @classmethod
    def setUpClass(cls): f.RealVmTests.setUpClass.__func__(cls)

    def test_pair_damage_threshold_and_quiet_release(self):
        for slot in range(5):
            cases=self.sequence(slot)[:3]
            for c in cases:
                c['objects'][2].update(objectId=16, objectHp=800)
                enemies=[o for o in c['objects'] if o['objectKind']==2 and o['objectTeam']==1]
                for o in enemies[2:]:c['objects'].remove(o)
            rows=self.play('raid_wave',cases,('defActive','cpAdvance','pairedRush'))
            self.assertEqual(rows[0]['memory']['pairedRush'],1)
            self.assertEqual(rows[0]['memory']['defActive'],1)
            self.assertEqual(rows[-1]['memory']['cpAdvance'],1)
            self.assertEqual(rows[-1]['memory']['defActive'],0)
            cases[0]['objects'][2]['objectHp']=801
            self.assertEqual(self.play('raid_wave',cases[:1],('defActive',))[0]['memory']['defActive'],0)

    def test_rear_pressure_and_fort_damage_recall(self):
        for slot in range(5):
            cases=self.sequence(slot)[:3]
            for c in cases[1:]:c['objects'].append(f.obj(888,kind=2,team=1,x=83,y=22))
            self.assertEqual(self.play('raid_wave',cases,('defActive',))[-1]['memory']['defActive'],int(slot in (2,3)))
            cases=self.sequence(slot)[:3]
            hit=deepcopy(cases[-1]);hit['self']['worldTick']=461;hit['objects'][0]['objectHp']-=12
            self.assertEqual(self.play('raid_wave',cases+[hit],('defActive',))[-1]['memory']['defActive'],1)

    def test_blue_parity_and_all_class_equipment_budgets(self):
        rows=[]
        for team in (0,1):
            for slot in range(5):
                for count in (0,2,5):
                    c=scene(team,count=count,worldTick=100,selfGold=150)
                    c['self']['selfClass']=class_id(team,slot)
                    if team==1:
                        self.assertEqual(self.play('raid_wave',[c])[0]['actions'],self.play('parent',[c])[0]['actions'])
                    c['objects'][2 if team==0 else 3]['objectHp']=500
                    c['objects'] += [f.obj(1000+i,kind=3,team=i%2,x=i%116,y=i*7%116) for i in range(220)]
                    row=self.play('raid_wave',[c])[0];rows.append(row)
                    self.assertTrue(any(x['command']=='buyItem' and x['accepted'] for x in row['actions']))
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(STUDY/'vm-budget.json',{'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),'max_work':max(r['work'] for r in rows)})


if __name__=='__main__':unittest.main()
