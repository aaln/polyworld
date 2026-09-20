import unittest
from copy import deepcopy
import test_policy_ir as f
import test_rush_unblock as u
from test_red_pressure import survivor_case
from test_jordan_root import final_approach
from test_rush_defense import scene
from counterpush import make, STUDY, VARIANTS
from policy_ir import compile_policy, extract, write


class CounterpushTests(unittest.TestCase):
    factory = staticmethod(make)
    run_vm = f.RealVmTests.run_vm
    play = u.UnblockTests.play

    @classmethod
    def setUpClass(cls): f.RealVmTests.setUpClass.__func__(cls)

    def test_quiet_release_and_fresh_rush_recall(self):
        for name, quiet in [('release20',480), ('release40',960), ('tank60',480)]:
            for hero in (0,1,2,3,4):
                wait = 1440 if hero == 0 and name == 'tank60' else quiet
                cases = [survivor_case(t, hero) for t in range(100, 102+wait)]
                # An isolated nearby survivor is NOT targeting the anchor.
                for case in cases[1:]:
                    case['objects'] = case['objects'][:5]
                    case['objects'][-1]['objectTarget'] = 0
                cases[-1] = survivor_case(101+wait, hero)
                cases[-1]['objects'] = deepcopy(cases[0]['objects'])
                rows = self.play(name,cases)
                self.assertEqual(rows[0]['memory']['defActive'],1)
                self.assertEqual(rows[wait-1]['memory']['defActive'],1)
                self.assertEqual(rows[wait]['memory']['defActive'],0)
                self.assertEqual(rows[-1]['memory']['defActive'],1)

    def test_disappearing_owned_anchor_releases_before_quiet_timeout(self):
        for hero in range(5):
            first = survivor_case(100,hero)
            gone = survivor_case(101,hero)
            gone['objects'] = [o for o in gone['objects'][:4] if o['objectId'] != 16]
            rows = self.play('tank60',[first,gone])
            self.assertEqual([r['memory']['defActive'] for r in rows],[1,0])

    def test_standing_structure_attack_and_local_combat_retain_defense(self):
        cases = [survivor_case(t,2) for t in range(100,701)]
        for case in cases[1:]: case['objects'][-1]['objectTarget'] = 16
        self.assertTrue(all(r['memory']['defActive'] for r in self.play('release20',cases)))
        cases = [scene(worldTick=t,count=4 if t==100 else 1) for t in range(100,701)]
        for c in cases:
            c['self'].update(selfClass=2,selfX=64,selfY=46)
            if c['self']['worldTick']>100:c['objects'][-1]['objectTarget']=0
        self.assertTrue(all(r['memory']['defActive'] for r in self.play('release20',cases)))

    def test_spacing_blue_parity_and_runtime(self):
        rows=[]
        for name in VARIANTS[2:]:
            policy=make(name);self.assertEqual(extract(compile_policy(policy),policy),policy)
            moves=[]
            for hero in range(5):
                c=survivor_case(100,hero)
                r=self.play(name,[c])[0]
                moves.append(tuple([a['arguments'] for a in r['actions'] if a['command']=='walkTo'][-1]))
            self.assertEqual(len(set(moves)),5)
            for team in (0,1):
                for size in (40,80,160,240):
                    c=final_approach(team,4,100)
                    c['objects'] += [f.obj(3000+i,team=i%2,x=i%116,y=i*7%116) for i in range(size-len(c['objects']))]
                    cases=[c|{'self':c['self']|{'selfClass':k}} for k in range(team*5,team*5+5)]
                    rr=self.play(name,cases);rows+=rr
                    if team==1:self.assertEqual([r['actions'] for r in rr],[r['actions'] for r in self.play('deployed',cases)])
        write(STUDY/'vm-stress.json',{'passed':True,'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),'max_fixture_work':max(r['work'] for r in rows),'scope':'Fixtures test transitions, spacing, blue parity and bounded active mixed density; complete games still required.'})


if __name__=='__main__':unittest.main()
