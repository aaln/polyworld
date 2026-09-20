"""Native boundary tests for small-raid distance gates without changing escalation."""
from copy import deepcopy
import unittest
import test_policy_ir as f
import test_rush_unblock as u
from test_rush_defense import scene
from hero_binding import class_id
from policy_ir import write
from autoresearch_nearraids import make,STUDY,VARIANTS

MEMORY=('defActive','defUntil','pairedRush','raidSelfD','raidNearer')


def bounded_case(slot,distance,count=2,tick=100):
    c=scene(count=count,worldTick=tick,selfGold=150)
    c['objects'][2]['objectHp']=800
    c['self'].update(selfId=100+slot,selfClass=class_id(0,slot),selfX=67,selfY=43+distance)
    for i in range(5):
        x,y=(67,43+distance) if i==slot else ((67,43) if i==(slot+1)%5 else (116,115))
        c['objects'].append(f.obj(100+i,kind=2,team=0,x=x,y=y,hp=400))
    return c


class NearbyTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=u.UnblockTests.play

    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_distance_bound_is_inclusive_for_every_red_class(self):
        for name in VARIANTS[1:]:
            radius=int(name[4:])
            for slot in range(5):
                for d in (radius-1,radius,radius+1):
                    r=self.play(name,[bounded_case(slot,d)],MEMORY)[0]
                    self.assertEqual(r['memory']['defActive'],int(d<=radius))
                    self.assertEqual(r['memory']['raidSelfD'],d*d)

    def test_large_group_and_existing_commitment_bypass_distance_rejection(self):
        for name in VARIANTS[1:]:
            for slot in range(5):
                far=bounded_case(slot,70,count=4)
                self.assertEqual(self.play(name,[far],MEMORY)[0]['memory']['defActive'],1)
                first=bounded_case(slot,20);away=bounded_case(slot,70,tick=101)
                r=self.play(name,[first,away],MEMORY)
                self.assertEqual(r[0]['memory']['defUntil'],820)
                self.assertEqual(r[-1]['memory']['pairedRush'],0)
                self.assertEqual(r[-1]['memory']['defActive'],1)

    def test_blue_parity_equipment_and_dense_limits(self):
        rows=[]
        for name in VARIANTS[1:]:
            for team in (0,1):
                for slot in range(5):
                    c=bounded_case(slot,20) if team==0 else scene(1,count=5,worldTick=100,selfGold=150)
                    if team==1:
                        c['self']['selfClass']=class_id(1,slot)
                        self.assertEqual(self.play(name,[c])[0]['actions'],self.play('parent',[c])[0]['actions'])
                    c['objects'] += [f.obj(1000+i,kind=3,team=i%2,x=i%116,y=i*7%116) for i in range(220)]
                    r=self.play(name,[c],MEMORY)[0];rows.append(r)
                    self.assertTrue(any(a['command']=='buyItem' and a['accepted'] for a in r['actions']))
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(STUDY/'vm-budget.json',{'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),'max_work':max(r['work'] for r in rows)})


if __name__=='__main__':unittest.main()
