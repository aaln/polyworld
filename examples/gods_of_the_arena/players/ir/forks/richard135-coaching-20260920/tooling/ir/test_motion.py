"""Real-VM contracts for turn-aware retreats and action arbitration."""
from pathlib import Path
import tempfile
import unittest
import test_policy_ir as f
from motion_candidates import make_policy
from policy_ir import compile_policy, extract, validate


class MotionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): f.RealVmTests.setUpClass.__func__(cls)
    run_vm = f.RealVmTests.run_vm

    def case(self, tick, hits=0, **values):
        enemy = f.obj(100, team=1, x=22)
        enemy['objectTarget'] = 1
        return f.fixture([enemy], selfClass=1,worldTick=tick,selfAttacksLanded=hits,
                         selfAttackCooldown=12,selfAttackRange=330000,**values)

    def play(self, cases, name='motion_targeted'):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'p.bas';p.write_text(compile_policy(make_policy(name)))
            return self.run_vm(p,cases,['kiteBursts','motionActive','motionX','motionY','motionCompletions','kiteEscapes'])

    def motion(self, row):
        return [a for a in row['actions'] if a['command'] in ('walkTo','attackTarget')]

    def test_hit_required_and_destination_stays_fixed_until_separation(self):
        cases=[self.case(t) for t in range(1,10)] + [self.case(t,1) for t in range(10,30)]
        rows=self.play(cases)
        self.assertTrue(all(self.motion(r)[-1]['command']=='attackTarget' for r in rows[:9]))
        self.assertTrue(all(self.motion(r)[-1]['command']=='walkTo' for r in rows[9:]))
        self.assertEqual(len({tuple(self.motion(r)[-1]['arguments']) for r in rows[9:]}),1)
        self.assertEqual(rows[-1]['memory']['kiteBursts'],1)
        cases[-1]['self']['selfX']=17
        rows=self.play(cases)
        self.assertEqual(self.motion(rows[-1])[-1]['command'],'attackTarget')
        self.assertEqual(rows[-1]['memory']['motionCompletions'],1)

    def test_retreat_is_bounded_and_respawn_does_not_reuse_old_hit(self):
        rows=self.play([self.case(1)]+[self.case(t,1) for t in range(2,70)])
        self.assertEqual(self.motion(rows[-1])[-1]['command'],'attackTarget')
        rows=self.play([self.case(1,10),self.case(2,11),self.case(300,11)])
        self.assertEqual(self.motion(rows[-1])[-1]['command'],'attackTarget')

    def test_early_escape_survives_no_candidate_fallback(self):
        a=self.case(1,selfHp=70);b=self.case(2,selfHp=40)
        for c in (a,b):
            c['objects'][0].update(objectKind=4,objectAlive=0,objectHp=900)
        row=self.play([a,b],'early_pressure')[-1]
        self.assertEqual(row['memory']['kiteEscapes'],1)
        self.assertEqual(len(self.motion(row)),1)
        self.assertEqual(self.motion(row)[0]['command'],'walkTo')

    def test_failed_walk_restores_attack_and_does_not_cast(self):
        a=self.case(1);b=self.case(2,1);b['returns']={'walkTo':0}
        b['abilities']=[{'abilityCharges':1,'abilityCooldown':0} for _ in range(4)]
        row=self.play([a,b])[-1]
        self.assertEqual(self.motion(row)[-1]['command'],'attackTarget')
        self.assertNotIn('castTarget',[a['command'] for a in row['actions']])

    def test_tower_detour_preserves_near_attack_and_diverts_remote_pursuit(self):
        a=self.case(1);a['objects'].append(f.obj(14,kind=4,team=0,x=23,hp=1200,alive=0))
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'p.bas';p.write_text(compile_policy(make_policy('tower_route')))
            near=self.run_vm(p,[a],['towerDetours'])[0]
            self.assertEqual(self.motion(near)[-1]['command'],'attackTarget')
            a['objects'][0]['objectX']=40
            far=self.run_vm(p,[a],['towerDetours'])[0]
            self.assertEqual(self.motion(far)[-1]['command'],'walkTo')
            self.assertEqual(far['memory']['towerDetours'],1)

    def test_reverse_extraction_and_version_guard(self):
        p=make_policy('combined');source=compile_policy(p)
        self.assertEqual(extract(source,p),p)
        q=extract(source.replace('motionStart + 12','motionStart + 16'),p)
        self.assertEqual(q['skill']['attack']['parameters']['min_ticks'],16)
        p['execution']['game_version']='2026.9.15.2'
        with self.assertRaises(ValueError):validate(p)


if __name__=='__main__':unittest.main()
