"""Native tests for rank allocation, continued commitments and escalation."""
from copy import deepcopy
import unittest
import test_policy_ir as f
import test_rush_unblock as u
from test_rush_defense import scene
from hero_binding import class_id
from policy_ir import write
from autoresearch_rankraid import make,STUDY,VARIANTS

MEMORY=('defActive','defUntil','defHoldTicks','pairedRush','raidNearer','raidScoped')


def ranked_case(slot,count=2,tick=100,tie=False,dead_first=False):
    c=scene(count=count,worldTick=tick,selfGold=150)
    c['objects'][2]['objectHp']=800
    positions=[(67+(0 if tie else i*3),43) for i in range(5)]
    for i,(x,y) in enumerate(positions):
        c['objects'].append(f.obj(100+i,kind=2,team=0,x=x,y=y,hp=0 if dead_first and i==0 else 400))
    c['self'].update(selfId=100+slot,selfClass=class_id(0,slot),selfX=positions[slot][0],selfY=positions[slot][1])
    return c


class RankedTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=u.UnblockTests.play

    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_rank_ties_and_dead_allies(self):
        for name in VARIANTS[1:]:
            for tie in (False,True):
                for dead in (False,True):
                    for slot in range(int(dead),5):
                        r=self.play(name,[ranked_case(slot,tie=tie,dead_first=dead)],MEMORY)[0]
                        self.assertEqual(r['memory']['pairedRush'],int(slot<int(dead)+2))
                        self.assertEqual(r['memory']['defActive'],int(slot<int(dead)+2))

    def test_large_group_still_recalls_everyone(self):
        for name in VARIANTS[1:]:
            for slot in range(5):
                r=self.play(name,[ranked_case(slot,count=4)],MEMORY)[0]
                self.assertEqual(r['memory']['defActive'],1)
                self.assertEqual(r['memory']['raidScoped'],0)
                self.assertEqual(r['memory']['defHoldTicks'],7200 if slot in (0,2,3) else 1440)

    def test_short_hold_survivor_refresh_expiry_and_escalation(self):
        first=ranked_case(0)
        quiet=scene(count=0,worldTick=101)
        end=scene(count=0,worldTick=820)
        r=self.play('rank2short',[first,quiet,end],MEMORY)
        self.assertEqual(r[0]['memory']['defUntil'],820)
        self.assertEqual(r[1]['memory']['defActive'],1)
        self.assertEqual(r[2]['memory']['defActive'],0)
        r=self.play('rank2short',[first,ranked_case(0,count=1,tick=101)],MEMORY)
        self.assertEqual(r[-1]['memory']['defUntil'],820)
        continuing=ranked_case(0,count=1,tick=101)
        continuing['objects'][4].update(objectX=70,objectY=43)
        r=self.play('rank2short',[first,continuing],MEMORY)
        self.assertEqual(r[-1]['memory']['defUntil'],821)
        r=self.play('rank2short',[first,ranked_case(0,count=4,tick=101)],MEMORY)
        self.assertEqual(r[-1]['memory']['defUntil'],7301)
        self.assertEqual(r[-1]['memory']['raidScoped'],0)
        self.assertEqual(self.play('rank2',[first],MEMORY)[0]['memory']['defUntil'],7300)

    def test_blue_parity_equipment_and_dense_limits(self):
        rows=[]
        for name in VARIANTS[1:]:
            for team in (0,1):
                for slot in range(5):
                    c=ranked_case(slot) if team==0 else scene(1,count=5,worldTick=100,selfGold=150)
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
