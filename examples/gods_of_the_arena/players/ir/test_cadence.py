"""Actual BASIC VM checks: post-hit recovery, emergency retreat, and parity."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

import test_policy_ir as f
from binding import CONTRACTS
from policy_ir import HERE, compile_policy, extract, read, refresh_grounding, validate


def policy(all_classes=0, recovery_ticks=1):
    p = deepcopy(read(HERE / 'optimizer_motion_weapon.evaluated.ir.json'))
    p['skill']['attack'] = {'operator': 'cadence_motion', 'parameters':
        CONTRACTS['cadence_motion'].defaults() | {'targeted': 0, 'threat_tiles': 7,
            'risk_hp': 55, 'all_classes': all_classes, 'recovery_ticks': recovery_ticks}}
    refresh_grounding(p)
    return p


class CadenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        f.RealVmTests.setUpClass.__func__(cls)

    run_vm = f.RealVmTests.run_vm

    def play(self, cases, **parameters):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'policy.bas'
            source.write_text(compile_policy(policy(**parameters)))
            return self.run_vm(source, cases, ['motionActive', 'kiteTrigger', 'recoverySteps', 'kiteEscapes'])

    def case(self, tick, hits=0, hero_class=1, hp=100):
        enemy = f.obj(100, team=1, x=23)
        enemy['objectTarget'] = 1
        return f.fixture([enemy], selfClass=hero_class, worldTick=tick, selfAttacksLanded=hits,
                         selfAttackCooldown=12, selfAttackRange=330000, selfHp=hp)

    def test_recovery_waits_for_hit_then_resumes_next_tick(self):
        r = self.play([self.case(1), self.case(2, 1), self.case(3, 1)])
        self.assertEqual([x['memory']['motionActive'] for x in r], [0, 1, 0])
        self.assertEqual(r[1]['memory']['recoverySteps'], 1)

    def test_low_hp_escape_retains_long_movement(self):
        r = self.play([self.case(1, hp=80), self.case(2, hp=35), self.case(3, hp=35)])
        self.assertEqual([x['memory']['motionActive'] for x in r], [0, 1, 1])
        self.assertEqual(r[1]['memory']['kiteTrigger'], 2)
        self.assertEqual(r[1]['memory']['recoverySteps'], 0)

    def test_melee_is_explicit_and_respawn_does_not_reuse_hit(self):
        cases = [self.case(1, hero_class=0), self.case(2, 1, hero_class=0), self.case(300, 1, hero_class=0)]
        self.assertEqual(self.play(cases)[1]['memory']['motionActive'], 0)
        r = self.play(cases, all_classes=1)
        self.assertEqual([x['memory']['motionActive'] for x in r], [0, 1, 0])

    def test_round_trip_parameter_edit_and_version_guard(self):
        p = policy()
        source = compile_policy(p)
        self.assertEqual(extract(source, p), p)
        p = policy(all_classes=1, recovery_ticks=4)
        self.assertEqual(extract(compile_policy(p), p), p)
        p['execution']['game_version'] = '2026.9.15.2'
        with self.assertRaises(ValueError):
            validate(p)


if __name__ == '__main__':
    unittest.main()
