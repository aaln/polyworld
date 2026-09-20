"""Native watched-anchor priority, scope, inherited behavior and resource checks."""
from copy import deepcopy
import unittest
import test_policy_ir as f
import test_rush_unblock as u
import test_autoresearch_role_raid as role_tests
from test_rush_defense import scene
from hero_binding import class_id
from policy_ir import write
from autoresearch_core_focus import make,STUDY

def focus_case(radius=10,slot=0,**changes):
    x=105-radius
    objects=[f.obj(1,kind=1,team=0,x=105,y=11,hp=400,alive=0),
             f.obj(2,kind=1,team=1,x=11,y=105,hp=400,alive=0),
             f.obj(28,kind=4,team=0,x=x,y=11,hp=975)]
    for i in range(4):
        enemy=f.obj(105+i,kind=2,team=1,x=x+4+i%2,y=12+i%2)
        enemy['objectTarget']=28;objects.append(enemy)
    creep=f.obj(1000,kind=3,team=1,x=x+1,y=11,hp=60);creep['objectTarget']=28;objects.append(creep)
    return f.fixture(objects,selfTeam=0,selfId=100,selfClass=class_id(0,slot),selfX=x+1,selfY=12,worldTick=100,selfGold=150,**changes)

class CoreFocusTests(unittest.TestCase):
    factory=staticmethod(lambda name:make('rolecore20' if name=='role64' else name))
    run_vm=f.RealVmTests.run_vm
    play=u.UnblockTests.play
    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)
    test_role_arbitration=role_tests.RoleRaidTests.test_small_alarm_keeps_attack_roles_on_parent_commands
    test_ally_rank=role_tests.RoleRaidTests.test_all_ally_rank_and_dead_allies_are_respected
    test_commitments=role_tests.RoleRaidTests.test_group_defense_and_remembered_scoped_hold_survive

    def test_observed_core_creep_priority_all_red_classes(self):
        for name in ('core20','rolecore20'):
            control='parent' if name=='core20' else 'role64_reference'
            for slot in range(5):
                case=focus_case(slot=slot)
                old=self.play(control,[case])[0]
                new=self.play(name,[case],('bestId','defActive','coreFocusAnchor'))[0]
                self.assertIn(old['memory']['bestId'],range(105,109))
                self.assertEqual(new['memory']['coreFocusAnchor'],28)
                self.assertEqual(new['memory']['bestId'],1000)
                self.assertTrue(any(a['command']=='attackTarget' and a['arguments']==[1000] for a in new['actions']))

    def test_radius_target_liveness_and_geometry_boundaries(self):
        for name in ('core20','rolecore20'):
            control='parent' if name=='core20' else 'role64_reference'
            for radius in (20,21):
                case=focus_case(radius=radius)
                row=self.play(name,[case])[0]
                self.assertEqual(row['memory']['bestId']==1000,radius==20)
            for change in ('no_target','dead_creep','friendly_creep','dead_anchor','far_creep'):
                case=focus_case();creep=case['objects'][-1]
                if change=='no_target':creep['objectTarget']=0
                if change=='dead_creep':creep.update(objectHp=0,objectAlive=0)
                if change=='friendly_creep':creep['objectTeam']=0
                if change=='dead_anchor':case['objects'][2].update(objectHp=0,objectAlive=0)
                if change=='far_creep':creep.update(objectX=60,objectY=90)
                self.assertEqual(self.play(name,[case])[0]['actions'],self.play(control,[case])[0]['actions'],change)

    def test_visibility_gap_clears_priority_without_canceling_hold(self):
        for name in ('core20','rolecore20'):
            first=focus_case();gap=deepcopy(first);gap['self']['worldTick']=101;gap['objects']=gap['objects'][:3]+gap['objects'][-1:]
            rows=self.play(name,[first,gap],('defActive','coreFocusAnchor'))
            self.assertEqual([r['memory']['coreFocusAnchor'] for r in rows],[28,0])
            self.assertEqual(rows[-1]['memory']['defActive'],1)

    def test_blue_parity_healing_and_dense_equipment_budget(self):
        rows=[]
        for name in ('core20','rolecore20'):
            control='parent' if name=='core20' else 'role64_reference'
            for team in (0,1):
                for slot in range(5):
                    case=focus_case(slot=slot) if team==0 else scene(1,count=5,worldTick=100,selfGold=150)
                    case['self']['selfClass']=class_id(team,slot)
                    case['objects'] += [f.obj(1200+i,kind=3,team=i%2,x=i%116,y=i*7%116) for i in range(220)]
                    row=self.play(name,[case])[0];rows.append(row)
                    if team==1:self.assertEqual(row['actions'],self.play(control,[case])[0]['actions'])
                    self.assertTrue(any(a['command']=='buyItem' and a['arguments'][0]>4 for a in row['actions']))
            case=focus_case();case['self']['selfHp']=20
            healing=lambda r:[a for a in r['actions'] if a['command']=='buyItem' and a['arguments'][0] in (1,2)]
            self.assertEqual(healing(self.play(name,[case])[0]),healing(self.play(control,[case])[0]))
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(STUDY/'vm-budget.json',{'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),'max_work':max(r['work'] for r in rows),'scope':'Native BASIC VM with scripted command acceptance. Complete games separately verify actual equipment and survival.'})

if __name__=='__main__':unittest.main()
