"""Real VM checks for conditional rear coverage and full-team counterpressure."""
from copy import deepcopy
import unittest
import test_policy_ir as f
import test_rush_unblock as u
import test_coach_assembled as assembly
from test_rush_defense import scene
from hero_binding import class_id
from binding import CONTRACTS
from coach_mobile import make,STUDY,VARIANTS
from policy_ir import write,compile_policy,extract

MEMORY=assembly.MEMORY+('cpRearNeeded','cpWaveUntil','cpNearbyEnemies')


class MobileTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=u.UnblockTests.play
    sequence=assembly.AssembledTests.sequence
    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_initial_combat_unchanged(self):
        for n in VARIANTS[1:]:
            for slot in range(5):
                cases=self.sequence(slot)[:2]
                self.assertEqual([r['actions'] for r in self.play('deployed',cases)],
                                 [r['actions'] for r in self.play(n,cases)])

    def test_all_five_attack_when_rear_is_quiet(self):
        for n in VARIANTS[1:]:
            for slot in range(5):
                r=self.play(n,self.sequence(slot)[:3],MEMORY)[-1]['memory']
                self.assertEqual(r['cpMode'],1);self.assertEqual(r['cpAdvance'],1)
                self.assertEqual(r['defActive'],0)

    def test_only_two_supports_guard_observed_single_raider(self):
        for n in VARIANTS[1:]:
            guards=[]
            for slot in range(5):
                cases=self.sequence(slot)[:3]
                for c in cases[1:]:c['objects'].append(f.obj(888,kind=2,team=1,x=83,y=22))
                r=self.play(n,cases,MEMORY)[-1]['memory']
                self.assertEqual(r['cpMode'],1)
                if r['defActive']:guards.append(slot)
                else:self.assertEqual(r['cpAdvance'],1)
            self.assertEqual(guards,[2,3])

    def test_spread_three_hero_rush_recalls_all(self):
        for n in VARIANTS[1:]:
            for slot in range(5):
                cases=self.sequence(slot)[:3]
                fresh=deepcopy(cases[-1]);fresh['self']['worldTick']=461
                fresh['objects'] += [f.obj(105+i,kind=2,team=1,x=70+i*7,y=50-i*4) for i in range(3)]
                cases.append(fresh);r=self.play(n,cases,MEMORY)[-1]['memory']
                self.assertEqual(r['cpMode'],0);self.assertEqual(r['defActive'],1)

    def test_creep_only_intrusion_reassigns_support_without_full_recall(self):
        for n in VARIANTS[1:]:
            for slot in (1,2,3):
                cases=self.sequence(slot)[:3]
                for tick in range(461,470):
                    c=deepcopy(cases[2]);c['self']['worldTick']=tick
                    c['objects'].append(f.obj(888,kind=3,team=1,x=104,y=12));cases.append(c)
                r=self.play(n,cases,MEMORY)[-1]['memory']
                self.assertGreater(r['cpWaveUntil'],469)
                self.assertEqual(r['defActive'],int(slot in (2,3)))

    def test_blue_parity_roundtrip_and_runtime(self):
        old=make('deployed');rows=[]
        for n in VARIANTS[1:]:
            p=make(n);self.assertEqual(extract(compile_policy(p),p),p)
            for key,s in p['skill'].items():
                prior=old['skill'][key]
                if s!=prior:self.assertEqual(CONTRACTS[s['operator']].source(s['parameters']).split('\nelse\n',1)[1],CONTRACTS[prior['operator']].source(prior['parameters']).split('\nelse\n',1)[1])
            for team in (0,1):
                for slot in range(5):
                    c=scene(team,count=5,worldTick=100,selfGold=150);c['self']['selfClass']=class_id(team,slot)
                    c['objects'] += [f.obj(1000+i,kind=3,team=i%2,x=i%116,y=i*7%116) for i in range(180)]
                    rows+=self.play(n,[c],('bestId','defActive'))
            c=self.sequence(2)[:3]
            for x in c:x['objects'] += [f.obj(1000+i,kind=3,team=i%2,x=i%116,y=i*7%116) for i in range(180)]
            rows+=self.play(n,c,MEMORY)
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(STUDY/'vm-budget.json',{'decisions':len(rows),'instructions':max(r['instructions'] for r in rows),'work':max(r['work'] for r in rows)})


if __name__=='__main__':unittest.main()
