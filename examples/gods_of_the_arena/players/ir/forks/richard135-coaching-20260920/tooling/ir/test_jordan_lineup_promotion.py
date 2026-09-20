"""A large Jordan gain must not hide a regression in another deployment mode."""
import copy
import unittest

from jordan_lineup_promote import validate_result
from jordan_lineup_wide import ROOT, metric_checks
from coached_league_live import arm_plan
from policy_ir import read, digest


class PromotionGuards(unittest.TestCase):
    def setUp(self):
        self.plan = read(ROOT / 'plan.json')
        mixed = {'games': 200, 'allied_wins': 128, 'both_gear': 200, 'opposed_draws': 0,
                 'rosters': {'0': 64, '1': 64}, 'classes': {str(i): {'games': 16, 'wins': 12} for i in range(10)}}
        self.arms = {a: copy.deepcopy(mixed) for a in ('control', 'candidate')}
        self.heads = {r['id']: {a: {'games': 80, 'wins': 60 if a == 'control' else 64,
                      'colors': {'red': {'win': 30}, 'blue': {'win': 30 if a == 'control' else 34}}}
                      for a in ('control', 'candidate')} for r in self.plan['rivals']}

    def result(self):
        checks = metric_checks(self.plan, self.arms, self.heads, True, True)
        return {'passed': all(checks.values()), 'checks': checks, 'heads': self.heads, 'arms': self.arms,
                'plan_sha256': digest(self.plan), 'games_per_head_arm': 1040, 'games_per_mixed_arm': 200}

    def test_complete_nonregressing_evidence_can_pass(self):
        validate_result(self.plan, self.result())

    def test_prepared_mixed_requests_match_complete_frozen_design(self):
        for arm in ('control', 'candidate'):
            for i in range(2):
                self.assertEqual(read(ROOT / 'mixed' / arm / f'part-{i}/plan.json'), arm_plan(self.plan, arm, i))

    def test_side_regression_is_not_hidden_by_overall_gain(self):
        h = next(iter(self.heads.values()))['candidate']
        h.update(wins=65, colors={'red': {'win': 25}, 'blue': {'win': 40}})
        with self.assertRaises(ValueError): validate_result(self.plan, self.result())

    def test_mixed_regression_blocks_even_large_direct_gain(self):
        self.arms['candidate']['allied_wins'] = 119
        with self.assertRaises(ValueError): validate_result(self.plan, self.result())

    def test_stale_success_flag_cannot_bypass_metric_recomputation(self):
        r = self.result()
        r['arms']['candidate']['both_gear'] = 199
        with self.assertRaises(ValueError): validate_result(self.plan, r)

    def test_missing_rival_or_changed_plan_blocks(self):
        r = copy.deepcopy(self.result()); r['heads'].pop(next(iter(r['heads'])))
        with self.assertRaises(ValueError): validate_result(self.plan, r)
        r = self.result(); r['plan_sha256'] = 'changed'
        with self.assertRaises(ValueError): validate_result(self.plan, r)


if __name__ == '__main__': unittest.main()
