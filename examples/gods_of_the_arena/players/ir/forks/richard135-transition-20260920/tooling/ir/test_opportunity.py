"""Real VM checks for target opportunities and IR/BASIC parity."""
from pathlib import Path
import tempfile
import unittest

import test_policy_ir as f
from economy_candidates import VARIANTS, make_policy
from policy_ir import compile_policy, extract


class OpportunityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): f.RealVmTests.setUpClass.__func__(cls)
    run_vm = f.RealVmTests.run_vm

    def choose(self, objects, name='last_hit_motion', **values):
        fixture = f.fixture(objects, selfClass=1, selfLevel=1, selfAttackRange=330000,
                            selfAttackDamage=30, **values)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'policy.bas'; path.write_text(compile_policy(make_policy(name)))
            return self.run_vm(path, [fixture], ['bestId', 'bestDistance'])[0]['memory']

    def test_killable_hero_then_creep_over_nearest_full_hp_enemy(self):
        enemies = [f.obj(100, team=1, kind=2, x=21, hp=500),
                   f.obj(101, team=1, kind=3, x=23, hp=20),
                   f.obj(102, team=1, kind=2, x=24, hp=25)]
        self.assertEqual(self.choose(enemies)['bestId'], 102)
        self.assertEqual(self.choose(enemies[:-1]), {'bestId': 101, 'bestDistance': 9})

    def test_distant_low_hp_does_not_gain_last_hit_bonus(self):
        enemies = [f.obj(100, team=1, x=21, hp=500), f.obj(101, team=1, x=40, hp=1)]
        self.assertEqual(self.choose(enemies)['bestId'], 100)

    def test_protected_structure_and_friendly_unit_remain_ineligible(self):
        enemies = [f.obj(100, team=1, x=22), f.obj(101, team=1, kind=4, x=21, alive=0),
                   f.obj(102, team=0, x=20, hp=1)]
        self.assertEqual(self.choose(enemies, 'finish_motion')['bestId'], 100)

    def test_objective_bonus_applies_only_in_range(self):
        enemies = [f.obj(100, team=1, x=21), f.obj(101, team=1, kind=4, x=23, hp=900)]
        self.assertEqual(self.choose(enemies, 'finish_motion')['bestId'], 101)
        enemies[1]['objectX'] = 30
        self.assertEqual(self.choose(enemies, 'finish_motion')['bestId'], 100)

    def test_all_successor_irs_round_trip_and_default_center_is_explicit(self):
        for name in VARIANTS:
            p = make_policy(name)
            self.assertEqual(extract(compile_policy(p), p), p)
        self.assertEqual(make_policy('center_motion')['skill']['fallback']['operator'], 'walk_point')


if __name__ == '__main__': unittest.main()
