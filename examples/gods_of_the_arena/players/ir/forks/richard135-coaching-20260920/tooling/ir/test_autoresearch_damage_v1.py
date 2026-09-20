"""Native damage alarm boundaries, all-class purchases, and runtime budgets."""
from copy import deepcopy
import unittest
import test_policy_ir as f
import test_rush_unblock as u
from test_rush_defense import scene
from hero_binding import class_id
from policy_ir import write
from autoresearch_damage_study import make, STUDY, VARIANTS

MEMORY=('defActive','defUntil','defCount','pairedRush','pairAnchorHp','bestId')


class DamageTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=u.UnblockTests.play

    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_damage_threshold_for_each_red_lane(self):
        for name in VARIANTS[1:]:
            for tower in (10,16,22):
                for missing in (int(name[6:])-1,int(name[6:])):
                    c=scene(count=2,worldTick=1000)
                    c['objects'][2].update(objectId=tower,objectHp=950-missing)
                    for o in c['objects'][4:]:o['objectTarget']=tower
                    r=self.play(name,[c],MEMORY)[0]
                    self.assertEqual(r['memory']['defActive'],int(missing>=int(name[6:])))
                    self.assertEqual(self.play('parent',[c],MEMORY)[0]['memory']['defActive'],0)

    def test_rejects_absent_dead_single_or_expired_evidence(self):
        for name in VARIANTS[1:]:
            base=scene(count=2,worldTick=1000);base['objects'][2]['objectHp']=500
            for kind in ('single','dead_enemy','dead_tower','foreign_tower','late'):
                c=deepcopy(base)
                if kind=='single':c['objects'].pop()
                if kind=='dead_enemy':c['objects'][-1].update(objectHp=0,objectAlive=0)
                if kind=='dead_tower':c['objects'][2]['objectHp']=0
                if kind=='foreign_tower':c['objects'][2]['objectTeam']=1
                if kind=='late':c['self']['worldTick']=7201
                self.assertEqual(self.play(name,[c],MEMORY)[0]['memory']['defActive'],0,kind)
            protected=deepcopy(base);protected['objects'][2]['objectAlive']=0
            self.assertEqual(self.play(name,[protected],MEMORY)[0]['memory']['defActive'],1)

    def test_blue_and_untriggered_red_commands_match_parent(self):
        for name in VARIANTS[1:]:
            for team in (0,1):
                for slot in range(5):
                    for count in (0,2,5):
                        c=scene(team,count=count,worldTick=100,selfGold=150)
                        c['self']['selfClass']=class_id(team,slot)
                        if team==1:c['objects'][3]['objectHp']=500
                        self.assertEqual(self.play(name,[c])[0]['actions'],self.play('parent',[c])[0]['actions'])

    def test_dense_runtime_and_equipment_all_classes(self):
        rows=[]
        for name in VARIANTS[1:]:
            for team in (0,1):
                for slot in range(5):
                    c=scene(team,count=2,worldTick=100,selfGold=150)
                    c['self']['selfClass']=class_id(team,slot)
                    c['objects'][2 if team==0 else 3]['objectHp']=500
                    c['objects'] += [f.obj(1000+i,kind=3,team=i%2,x=i%116,y=i*7%116) for i in range(220)]
                    r=self.play(name,[c],MEMORY)[0];rows.append(r)
                    self.assertTrue(any(a['command']=='buyItem' and a['accepted'] for a in r['actions']))
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(STUDY/'vm-budget.json',{'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),'max_work':max(r['work'] for r in rows)})


if __name__=='__main__':unittest.main()
