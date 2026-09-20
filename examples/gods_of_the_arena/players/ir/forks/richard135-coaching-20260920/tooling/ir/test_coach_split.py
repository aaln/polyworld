"""Execute the coached allocation and recall in the real BASIC VM."""
from copy import deepcopy
import unittest
import test_policy_ir as f
import test_rush_unblock as u
from test_g002_quiet_watch import gate_case
from test_rush_defense import scene
from hero_binding import class_id
from binding import CONTRACTS
from coach_split import make, STUDY, VARIANTS
from policy_ir import write, compile_policy, extract

MEMORY = ('bestId','defActive','defUntil','defPointX','defPointY','cpMode','cpBack',
          'cpAdvance','cpAssigned','cpContact','cpAnchor','cpQuiet','rushStage')


class SplitTests(unittest.TestCase):
    factory = staticmethod(make)
    run_vm = f.RealVmTests.run_vm
    play = u.UnblockTests.play

    @classmethod
    def setUpClass(cls): f.RealVmTests.setUpClass.__func__(cls)

    def sequence(self, slot):
        cases = [gate_case(100), gate_case(101,0), gate_case(220,0), gate_case(221)]
        for c in cases: c['self']['selfClass'] = class_id(0,slot)
        return cases

    def test_initial_defense_is_unchanged(self):
        for name in VARIANTS[1:]:
            for slot in range(5):
                cases=self.sequence(slot)[:2]
                a=self.play('deployed',cases)
                b=self.play(name,cases)
                self.assertEqual([r['actions'] for r in a],[r['actions'] for r in b])

    def test_two_rearguards_three_center_attackers_and_group_recall(self):
        for name in VARIANTS[1:]:
            guards=[]; attackers=[]
            for slot in range(5):
                r=self.play(name,self.sequence(slot),MEMORY)
                m=r[2]['memory']
                self.assertEqual(m['cpMode'],1)
                if m['cpBack']:
                    guards.append(slot);self.assertEqual(m['defActive'],1)
                else:
                    attackers.append(slot);self.assertEqual(m['defActive'],0)
                    self.assertEqual(m['cpAdvance'],1)
                    self.assertEqual(m['bestId'],19)
                    self.assertTrue(any(a['command']=='attackTarget' and a['arguments']==[19] for a in r[2]['actions']))
                self.assertEqual(r[3]['memory']['defActive'],1)
                self.assertEqual(r[3]['memory']['cpMode'],0)
            self.assertEqual(len(guards),2);self.assertEqual(len(attackers),3)

    def test_center_waypoint_replaces_distant_side_structure_chase(self):
        for name in VARIANTS[1:]:
            cases=self.sequence(1)[:3]
            for c in cases:c['objects'][3]['objectId']=25
            r=self.play(name,cases,MEMORY)[-1]
            self.assertEqual(r['memory']['bestId'],0)
            self.assertTrue(any(a['command']=='walkTo' and a['arguments']==[81,30] for a in r['actions']))

    def test_live_contact_delays_release_dead_enemy_does_not(self):
        for name in VARIANTS[1:]:
            for living in (True,False):
                cases=self.sequence(1)[:3]
                for case in cases[1:]:
                    e=f.obj(555,kind=2,team=1,x=95,y=22,hp=100 if living else 0)
                    e['objectAlive']=int(living);case['objects'].append(e)
                r=self.play(name,cases,MEMORY)
                self.assertEqual(r[-1]['memory']['cpMode'],int(not living))

    def test_missing_friendly_anchor_transfers_without_erasing_assignment(self):
        for name in VARIANTS[1:]:
            cases=self.sequence(3)[:3]
            for case in cases[1:]:case['objects']=[o for o in case['objects'] if o['objectId']!=18]
            r=self.play(name,cases,MEMORY)
            self.assertEqual(r[-1]['memory']['cpAssigned'],1)
            self.assertEqual(r[-1]['memory']['defActive'],1)
            self.assertEqual([r[-1]['memory'][k] for k in ('defPointX','defPointY')],[105,11])

    def test_core_damage_recalls_attackers(self):
        for name in VARIANTS[1:]:
            cases=self.sequence(1)[:3]
            hit=deepcopy(cases[-1]);hit['self']['worldTick']=221
            hit['objects'][0]['objectHp']-=12;cases.append(hit)
            r=self.play(name,cases,MEMORY)
            self.assertEqual(r[-2]['memory']['cpAdvance'],1)
            self.assertEqual(r[-1]['memory']['cpMode'],0)
            self.assertEqual(r[-1]['memory']['defActive'],1)

    def test_blue_source_parity_roundtrip_and_dense_runtime(self):
        parent=make('deployed');rows=[]
        for name in VARIANTS[1:]:
            p=make(name);self.assertEqual(extract(compile_policy(p),p),p)
            for k,s in p['skill'].items():
                old=parent['skill'][k]
                if s!=old:
                    self.assertEqual(CONTRACTS[s['operator']].source(s['parameters']).split('\nelse\n',1)[1],
                                     CONTRACTS[old['operator']].source(old['parameters']).split('\nelse\n',1)[1])
            for team in (0,1):
                for active in (False,True):
                    c=scene(team,count=5 if active else 0,worldTick=100,selfGold=150)
                    c['objects'] += [f.obj(1000+i,kind=3,team=i%2,x=i%116,y=i*7%116) for i in range(180)]
                    for slot in range(5):
                        rows+=self.play(name,[c|{'self':c['self']|{'selfClass':class_id(team,slot)}}],('bestId','defActive'))
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(STUDY/'vm-budget.json',{'decisions':len(rows),'instructions':max(r['instructions'] for r in rows),'work':max(r['work'] for r in rows)})


if __name__=='__main__':unittest.main()
