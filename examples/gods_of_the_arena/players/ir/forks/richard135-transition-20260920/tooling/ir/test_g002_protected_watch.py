"""Replay-derived real-VM regressions for quiet release with retained recall."""
from copy import deepcopy
import unittest
import test_policy_ir as f
import test_rush_unblock as u
from test_rush_defense import scene
from hero_binding import class_id
from g002_protected_watch import make, STUDY, VARIANTS
from policy_ir import compile_policy, extract, write
from binding import CONTRACTS

MEMORY=('bestId','defActive','defUntil','defPointX','defPointY','watchAdvance','watchQuiet','watchAnchor')

def gate_case(tick=100,count=5):
    s=scene(0,count=count,worldTick=tick)
    s['self'].update(selfX=100,selfY=15,selfClass=5)
    s['objects'][2].update(objectId=18,objectX=96,objectY=19,objectHp=1950)
    for e in s['objects'][4:]:e.update(objectX=84,objectY=26,objectTarget=18)
    s['objects'][4:4]=[f.obj(28,kind=4,team=0,x=106,y=16,hp=1950,alive=0),f.obj(29,kind=4,team=0,x=99,y=9,hp=1950,alive=0)]
    return s


class WatchTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=u.UnblockTests.play
    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_original_engagement_and_rally_before_quiet(self):
        for name in VARIANTS[1:]:
            cases=[gate_case(),gate_case(101)]
            old=self.play('deployed',cases)
            new=self.play(name,cases)
            self.assertEqual([r['actions'] for r in old],[r['actions'] for r in new])
            self.assertEqual([r['memory'] for r in old],[r['memory'] for r in new])

    def test_quiet_advance_keeps_single_survivor_recall(self):
        for name,wait in [('guard20',480),('guard30',720)]:
            cases=[gate_case(),gate_case(101,0),gate_case(101+wait,0)]
            single=gate_case(102+wait,1);cases.append(single)
            r=self.play(name,cases,MEMORY)
            self.assertEqual(r[2]['memory']['defActive'],0)
            self.assertEqual(r[2]['memory']['watchAdvance'],1)
            self.assertGreater(r[2]['memory']['defUntil'],cases[2]['self']['worldTick'])
            self.assertEqual(r[3]['memory']['defActive'],1)
            self.assertEqual(r[3]['memory']['watchAdvance'],0)
            self.assertEqual(r[3]['memory']['bestId'],0)
            # With the lease gone, one survivor cannot initiate the group alarm.
            fresh=self.play(name,[single],MEMORY)[0]
            self.assertEqual(fresh['memory']['defActive'],0)

    def test_travel_and_fresh_group_do_not_count_as_quiet(self):
        for name in VARIANTS[1:]:
            first=gate_case(); far=gate_case(2000,0);far['self'].update(selfX=55,selfY=55)
            r=self.play(name,[first,far,gate_case(2001)],MEMORY)
            self.assertTrue(all(v['memory']['defActive'] for v in r))
            self.assertEqual(r[1]['memory']['watchQuiet'],2000)

    def test_dead_anchor_transfers_without_clearing_pressure_memory(self):
        for name in VARIANTS[1:]:
            gone=gate_case(101,0);gone['objects'][2]['objectHp']=0
            r=self.play(name,[gate_case(),gone],MEMORY)
            self.assertEqual(r[-1]['memory']['defUntil'],r[0]['memory']['defUntil'])
            self.assertEqual(r[-1]['memory']['defActive'],1)
            self.assertEqual([r[-1]['memory'][k] for k in ('defPointX','defPointY')],[105,11])

    def test_core_guard_loss_interrupts_advance_and_targets_creeps(self):
        for name in VARIANTS[1:]:
            first=gate_case(); quiet=gate_case(901,0)
            unsafe=gate_case(902,0);unsafe['objects'][4]['objectHp']=974
            unsafe['objects'].append(f.obj(2000,kind=3,team=1,x=104,y=12,hp=60))
            rows=self.play(name,[first,quiet,unsafe],MEMORY)
            self.assertEqual(rows[1]['memory']['watchAdvance'],1)
            self.assertEqual(rows[2]['memory']['watchAdvance'],0)
            self.assertEqual(rows[2]['memory']['bestId'],2000)
            self.assertEqual([rows[2]['memory'][k] for k in ('defPointX','defPointY')],[105,11])

    def test_blue_source_parity_rally_spacing_and_runtime(self):
        parent=make('deployed');rows=[]
        for name in VARIANTS[1:]:
            p=make(name);self.assertEqual(extract(compile_policy(p),p),p)
            for k,s in p['skill'].items():
                old=parent['skill'][k]
                if s!=old:
                    self.assertEqual(CONTRACTS[s['operator']].source(s['parameters']).split('\nelse\n',1)[1],CONTRACTS[old['operator']].source(old['parameters']).split('\nelse\n',1)[1])
            moves=[]
            for slot in range(5):
                c=gate_case();c['self'].update(selfClass=class_id(0,slot),selfId=100+slot,selfX=103,selfY=8)
                # A distant selected objective initiates recall; no local target yet.
                c['self'].update(selfX=100,selfY=60)
                r=self.play(name,[c],MEMORY)[0]
                moves.append(tuple([a['arguments'] for a in r['actions'] if a['command']=='walkTo'][-1]))
            self.assertEqual(len(set(moves)),1)
            for team in (0,1):
                c=scene(team,worldTick=100,selfGold=150)
                c['objects'] += [f.obj(1000+i,kind=3,team=i%2,x=i%116,y=i*7%116) for i in range(150)]
                rows += self.play(name,[c|{'self':c['self']|{'selfClass':class_id(team,slot)}} for slot in range(5)],('bestId','defActive'))
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(STUDY/'vm-budget.json',{'decisions':len(rows),'max_instructions':max(r['instructions'] for r in rows),'max_work':max(r['work'] for r in rows)})

if __name__=='__main__':unittest.main()
