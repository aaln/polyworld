"""Confirmed hit events must precede normal retreat, including across respawns."""
from pathlib import Path
import tempfile
import unittest
import test_policy_ir as f
from policy_ir import HERE,read,compile_policy,extract,validate

class HitKitingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)
    run_vm=f.RealVmTests.run_vm
    def play(self,cases,p=None):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'policy.bas';path.write_text(compile_policy(p or read(HERE/'hypotheses/confirmed_hit_kite.ir.json')))
            return self.run_vm(path,cases,['kiteBursts','kiteEscapes','kiteUntil','kiteLastHits'])
    def case(self,t,hits=0,**kw):
        return f.fixture([f.obj(100,team=1,x=22)],selfClass=1,worldTick=t,selfAttacksLanded=hits,selfAttackCooldown=12,**kw)
    def motion(self,r):return [a['command'] for a in r['actions'] if a['command'] in ('attackTarget','walkTo')]
    def test_never_cancel_windup_without_hit(self):
        rs=self.play([self.case(t) for t in range(1,61)])
        self.assertTrue(all(self.motion(r)==['attackTarget'] for r in rs))
        self.assertEqual(rs[-1]['memory']['kiteBursts'],0)
    def test_hit_then_bounded_retreat_then_resume(self):
        cases=[self.case(1)]+[self.case(t,1) for t in range(2,15)]
        rs=self.play(cases)
        self.assertEqual(self.motion(rs[0]),['attackTarget'])
        self.assertTrue(all(self.motion(r)==['walkTo'] for r in rs[1:11]))
        self.assertTrue(all(self.motion(r)==['attackTarget'] for r in rs[11:]))
        self.assertEqual(rs[-1]['memory']['kiteBursts'],1)
    def test_counter_not_reused_after_respawn_or_missing_target(self):
        cases=[self.case(1,9),self.case(2,10),self.case(300,10),self.case(301,10)]
        rs=self.play(cases);self.assertEqual([self.motion(r) for r in rs],[['attackTarget'],['walkTo'],['attackTarget'],['attackTarget']])
        c=self.case(3,11);c['objects']=[]
        rs=self.play([self.case(1,9),self.case(2,10),c,self.case(4,11)])
        self.assertEqual(self.motion(rs[-1]),['attackTarget'])
    def test_emergency_can_interrupt_windup_and_failed_walk_restores_attack(self):
        a=self.case(1,selfHp=40);b=self.case(2,selfHp=34)
        for c in [a,b]:c['self']['selfClass']=0
        self.assertEqual(self.play([a,b])[-1]['memory']['kiteEscapes'],1)
        b['returns']={'walkTo':0}
        self.assertEqual(self.motion(self.play([a,b])[-1]),['walkTo','attackTarget'])
    def test_disabled_emergency_does_not_interrupt_attack(self):
        p=read(HERE/'hypotheses/hit_no_escape.ir.json')
        rs=self.play([self.case(1,selfHp=40),self.case(2,selfHp=20)],p)
        self.assertEqual(self.motion(rs[-1]),['attackTarget'])
        self.assertEqual(rs[-1]['memory']['kiteEscapes'],0)
    def test_targeted_requires_current_aggro_and_a_new_hit(self):
        p=read(HERE/'hypotheses/hit_targeted.ir.json')
        cases=[self.case(1),self.case(2,1),self.case(3,1),self.case(4,2)]
        for c in cases[2:]:c['objects'][0]['objectTarget']=1
        rs=self.play(cases,p)
        self.assertEqual([self.motion(r) for r in rs],[['attackTarget'],['attackTarget'],['attackTarget'],['walkTo']])
        a=self.case(1,selfHp=40);b=self.case(2,selfHp=20)
        self.assertEqual(self.motion(self.play([a,b],p)[-1]),['attackTarget'])
        b['objects'][0]['objectTarget']=1
        self.assertEqual(self.motion(self.play([a,b],p)[-1]),['walkTo'])
    def test_spell_kiting_casts_after_successful_move_in_priority_order(self):
        p=read(HERE/'hypotheses/spell_short.ir.json')
        a=self.case(1);b=self.case(2,1)
        for c in [a,b]:c['abilities']=[{'abilityCharges':1,'abilityCooldown':0} for _ in range(4)]
        r=self.play([a,b],p)[-1]
        commands=[a for a in r['actions'] if a['command'] in ('walkTo','castTarget')]
        self.assertEqual([a['command'] for a in commands],['walkTo','castTarget'])
        self.assertEqual(commands[-1]['arguments'],[3,100])
        b['abilities'][3]['abilityCooldown']=1
        r=self.play([a,b],p)[-1]
        self.assertEqual([a['arguments'] for a in r['actions'] if a['command']=='castTarget'],[[2,100]])
        b['returns']={'walkTo':0}
        self.assertNotIn('castTarget',[a['command'] for a in self.play([a,b],p)[-1]['actions']])
    def test_druid_does_not_cast_friendly_heals_at_enemy(self):
        p=read(HERE/'hypotheses/spell_short.ir.json');a=self.case(1);b=self.case(2,1)
        for c in [a,b]:
            c['self']['selfClass']=3;c['abilities']=[{'abilityCharges':1,'abilityCooldown':0} for _ in range(4)]
            c['abilities'][3]['abilityCharges']=0
        r=self.play([a,b],p)[-1]
        self.assertEqual(self.motion(r),['walkTo'])
        self.assertNotIn('castTarget',[a['command'] for a in r['actions']])
    def test_reverse_edit_and_version_guard(self):
        p=read(HERE/'hypotheses/confirmed_hit_kite.ir.json');source=compile_policy(p)
        self.assertEqual(extract(source,p),p)
        q=extract(source.replace('worldTick + 10','worldTick + 8'),p)
        self.assertEqual(q['skill']['attack']['parameters']['retreat_ticks'],8)
        self.assertEqual(q['belief']['claims']['B_kite']['status'],'requires_review')
        p['execution']['game_version']='2026.9.15.2'
        with self.assertRaises(ValueError):validate(p)
if __name__=='__main__':unittest.main()
