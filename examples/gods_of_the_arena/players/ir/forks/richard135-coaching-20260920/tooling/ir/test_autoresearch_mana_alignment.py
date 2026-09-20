"""Native VM threshold boundaries and invariant combat/healing on both lineups."""
import unittest
import test_policy_ir as f
import test_rush_unblock as u
from test_rush_defense import scene
from hero_binding import class_id
from policy_ir import write
from autoresearch_mana_alignment import make, STUDY


class ManaAlignmentTests(unittest.TestCase):
    factory = staticmethod(make)
    run_vm = f.RealVmTests.run_vm
    play = u.UnblockTests.play

    @classmethod
    def setUpClass(cls):
        f.RealVmTests.setUpClass.__func__(cls)

    def test_consumption_strict_boundaries_all_classes(self):
        for team in (0,1):
            for slot in range(5):
                for mana in (39,40,49,50,100):
                    case=f.fixture(selfTeam=team,selfClass=class_id(team,slot),selfMana=mana)
                    case['inventory']=[7,5,6,11,9,3]
                    for name in ('parent','mana50','buy40'):
                        row=self.play(name,[case],())[0]
                        used=any(a['command']=='useItem' and a['arguments']==[5] for a in row['actions'])
                        self.assertEqual(used,mana<(50 if name=='mana50' else 40))

    def test_buy40_keeps_healing_and_funds_checks(self):
        for mana in (39,40,49,50):
            for gold in (44,45,150):
                case=f.fixture(selfMana=mana,selfGold=gold,selfHp=20)
                for name in ('parent','mana50','buy40'):
                    row=self.play(name,[case],())[0]
                    actions=row['actions']
                    bought=any(a['command']=='buyItem' and a['arguments']==[3] for a in actions)
                    self.assertEqual(bought,mana<(40 if name=='buy40' else 50) and gold>=45)
                    heal=[a for a in actions if a['command']=='buyItem' and a['arguments'][0] in (1,2)]
                    parent=self.play('parent',[case],())[0]
                    self.assertEqual(heal,[a for a in parent['actions'] if a['command']=='buyItem' and a['arguments'][0] in (1,2)])

    def test_no_mana_no_potion_and_full_mana_do_not_change_commands(self):
        for team in (0,1):
            for slot in range(5):
                case=scene(team,count=5,worldTick=100,selfGold=150)
                case['self'].update(selfClass=class_id(team,slot),selfMana=100,selfMaxMana=100)
                for name in ('mana50','buy40'):
                    self.assertEqual(self.play(name,[case])[0]['actions'],self.play('parent',[case])[0]['actions'])
                case['self'].update(selfMana=0,selfMaxMana=0)
                for name in ('mana50','buy40'):
                    self.assertEqual(self.play(name,[case])[0]['actions'],self.play('parent',[case])[0]['actions'])

    def test_equipment_and_dense_budget_both_colors(self):
        rows=[]
        for name in ('mana50','buy40'):
            for team in (0,1):
                for slot in range(5):
                    case=scene(team,count=5,worldTick=100,selfGold=150)
                    case['self'].update(selfClass=class_id(team,slot),selfMana=45,selfMaxMana=100)
                    case['objects'] += [f.obj(1000+i,kind=3,team=i%2,x=i%116,y=i*7%116) for i in range(220)]
                    row=self.play(name,[case])[0];rows.append(row)
                    self.assertTrue(any(a['command']=='buyItem' and a['arguments'][0]>4 for a in row['actions']))
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(STUDY/'vm-budget.json',{'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),'max_work':max(r['work'] for r in rows),'scope':'Native BASIC VM with scripted command acceptance. Full game verifies live inventory and gameplay.'})


if __name__=='__main__':unittest.main()
