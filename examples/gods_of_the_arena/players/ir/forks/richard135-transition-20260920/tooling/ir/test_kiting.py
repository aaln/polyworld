"""Actual BASIC VM timing, fallback, survival and reverse extraction checks."""
from pathlib import Path
import tempfile
import unittest
import test_policy_ir as f
from policy_ir import HERE,read,compile_policy,extract

class KitingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): f.RealVmTests.setUpClass.__func__(cls)
    run_vm=f.RealVmTests.run_vm
    def play(self,cases,policy=None):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'policy.bas';p.write_text(compile_policy(policy or read(HERE/'hypotheses/burst_kite.ir.json')))
            return self.run_vm(p,cases,['kiteBursts','kiteEscapes','kiteStillTicks','kiteUntil'])
    def cases(self,n=32,**kw):
        return [f.fixture([f.obj(100,team=1,x=22)],selfClass=1,worldTick=t,**kw) for t in range(1,n+1)]
    def motion(self,r): return [a['command'] for a in r['actions'] if a['command'] in ('walkTo','attackTarget')]
    def test_fire_before_retreat_and_resume(self):
        rs=self.play(self.cases())
        self.assertTrue(all(self.motion(r)==['attackTarget'] for r in rs[:18]))
        self.assertTrue(all(self.motion(r)==['walkTo'] for r in rs[18:28]))
        self.assertEqual(rs[18]['actions'][0]['arguments'],[17,20])
        self.assertTrue(all(self.motion(r)==['attackTarget'] for r in rs[28:]))
    def test_critical_escape_melee_and_failed_walk_restores_attack(self):
        a=f.fixture([f.obj(100,team=1,x=22)],worldTick=1,selfHp=40)
        b=f.fixture([f.obj(100,team=1,x=22)],worldTick=2,selfHp=34)
        rs=self.play([a,b]);self.assertEqual(self.motion(rs[1]),['walkTo'])
        b['returns']={'walkTo':0};rs=self.play([a,b])
        self.assertEqual(self.motion(rs[1]),['walkTo','attackTarget'])
        self.assertEqual(rs[1]['memory']['kiteUntil'],0)
    def test_target_change_movement_gap_and_melee_never_normal_kite(self):
        cases=self.cases()
        for i,c in enumerate(cases):c['objects'][0]['objectId']=100+i%2
        self.assertTrue(all(self.motion(r)==['attackTarget'] for r in self.play(cases)))
        cases=self.cases()
        for i,c in enumerate(cases):c['self']['selfX']=20+i%2
        self.assertTrue(all(self.motion(r)==['attackTarget'] for r in self.play(cases)))
        cases=self.cases()
        for c in cases:c['self']['selfClass']=0
        self.assertTrue(all(self.motion(r)==['attackTarget'] for r in self.play(cases)))
        cases=self.cases(18)+[f.fixture([f.obj(100,team=1,x=22)],worldTick=300,selfClass=1)]
        self.assertEqual(self.motion(self.play(cases)[-1]),['attackTarget'])
    def test_no_target_and_blocked_route(self):
        c=self.cases()
        for x in c:x['blocked']=[[17,20]]
        self.assertTrue(all(self.motion(r)==['attackTarget'] for r in self.play(c)))
        c=self.cases(19)+[f.fixture([],worldTick=20,selfClass=1)]
        r=self.play(c)[-1];self.assertEqual(r['memory']['kiteUntil'],0)
        self.assertEqual(self.motion(r),['walkTo']) # unchanged R4 fallback
    def test_reverse_parameter_and_belief_review(self):
        p=read(HERE/'hypotheses/burst_kite.ir.json');s=compile_policy(p)
        self.assertEqual(extract(s,p),p)
        q=extract(s.replace('selfMaxHp * 35','selfMaxHp * 40'),p)
        self.assertEqual(q['skill']['attack']['parameters']['critical_percent'],40)
        self.assertIn('goal/G_kite',q['update']['needs_review'])
        self.assertEqual(q['belief']['claims']['B_kite']['status'],'requires_review')

if __name__=='__main__':unittest.main()
