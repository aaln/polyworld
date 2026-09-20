import unittest
from copy import deepcopy

from hosted_batch import batch_body


class BatchTest(unittest.TestCase):
    def setUp(self):
        self.plan = {"run_id": "test", "policy_version": "subject-uuid",
                     "opponents": [{"id": f"rival-{i}"} for i in range(9)],
                     "config": {"max_ticks": 28800},
                     "target": {"coworld_id": "cow-test", "variant_id": "competition"}}

    def test_one_body_holds_all_episodes_and_rotates_frozen_versions(self):
        body = batch_body(self.plan, 40)
        self.assertEqual(body["num_episodes"], 40)
        self.assertEqual(len(body["roster"]), 10)
        self.assertTrue(all(row["slot"] == -1 for row in body["roster"]))
        self.assertNotIn("seed", body["game_config_overrides"])
        self.assertEqual(body, batch_body(self.plan, 40))

    def test_default_maximum_and_rejected_singletons(self):
        self.assertEqual(batch_body(self.plan)["num_episodes"], 40)
        self.assertEqual(batch_body(self.plan, 100)["num_episodes"], 100)
        for count in [0, 1, 101, True]:
            with self.assertRaises(ValueError):
                batch_body(self.plan, count)

    def test_pinned_seed_cannot_masquerade_as_independent_games(self):
        self.plan["config"]["seed"] = 2026
        with self.assertRaises(ValueError):
            batch_body(self.plan)

    def test_changing_arm_preserves_roster_except_subject(self):
        candidate = deepcopy(self.plan)
        candidate["policy_version"] = "candidate-uuid"
        control_body, candidate_body = batch_body(self.plan), batch_body(candidate)
        self.assertEqual(control_body["roster"][1:], candidate_body["roster"][1:])
        self.assertNotEqual(control_body["idempotency_key"], candidate_body["idempotency_key"])


if __name__ == "__main__":
    unittest.main()
