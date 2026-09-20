import unittest
from copy import deepcopy
from fractions import Fraction

from glory_metrics import policy_values, seat_values


class GloryTest(unittest.TestCase):
    def result(self, outcome="RedTeam", ticks=1440):
        return {"ticks": ticks, "outcome": outcome, "total_xp": [125] * 10,
                "scores": [int((outcome == "RedTeam" and i < 5) or
                               (outcome == "BlueTeam" and i >= 5)) for i in range(10)]}

    def test_win_loss_and_negative_winner(self):
        result = self.result()
        values = seat_values(result)
        self.assertEqual(values[0]["glory"], 25)
        self.assertEqual(values[5]["score"], 25)
        self.assertEqual(values[5]["glory"], 0)
        result["total_xp"][0] = 0
        self.assertEqual(seat_values(result)[0]["glory"], -100)

    def test_fractional_minutes_are_not_rounded(self):
        values = seat_values(self.result(ticks=721))
        self.assertEqual(values[0]["time_penalty"], Fraction(3605, 72))

    def test_draws_keep_score_but_zero_glory(self):
        result = self.result("time_limit", 28800)
        result["total_xp"] = [0] * 10
        for row in seat_values(result):
            self.assertEqual((row["win"], row["score"], row["glory"]), (0, -2000, 0))

    def test_mono_averages_heroes_before_policy_comparison(self):
        result = self.result()
        result["total_xp"] = [100, 200, 300, 400, 500] + [100] * 5
        values = policy_values(result, ["a"] * 5 + ["b"] * 5)
        self.assertEqual(values["a"]["glory"], 200)
        self.assertEqual(values["a"]["win"], 1)
        self.assertEqual(values["b"]["glory"], 0)

    def test_missing_xp_and_contradictory_outcomes_fail(self):
        result = self.result()
        for field in ["total_xp", "scores"]:
            broken = deepcopy(result)
            del broken[field]
            with self.assertRaises(ValueError):
                seat_values(broken)
        result["scores"][9] = 1
        with self.assertRaises(ValueError):
            seat_values(result)


if __name__ == "__main__":
    unittest.main()
