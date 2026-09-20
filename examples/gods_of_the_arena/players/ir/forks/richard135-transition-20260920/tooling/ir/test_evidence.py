"""Evidence gates must reject mismatched games and correlated pseudo-samples."""

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from local_feedback import feedback
from local_gate import significance
from hypothesis_study import confirmatory_gate, regression_sweep
from policy_ir import HERE, compile_policy, digest, executable, read, write
from xp_feedback import compare


class EvidenceTests(unittest.TestCase):
    def test_balanced_independent_validation_and_regression_screen(self):
        pairs = [{"seed": seed, "class": seed % 10, "delta": int(seed < 15)} for seed in range(120)]
        self.assertTrue(confirmatory_gate({"pairs": pairs, "gain": 15/120}, .1)["passed"])
        duplicate = deepcopy(pairs)
        duplicate[-1]["seed"] = 0
        with self.assertRaises(ValueError):
            confirmatory_gate({"pairs": duplicate, "gain": 15/120}, .1)
        unbalanced = deepcopy(pairs)
        unbalanced[-1]["class"] = 0
        self.assertFalse(confirmatory_gate({"pairs": unbalanced, "gain": 15/120}, .1)["passed"])
        for row in pairs:
            hero = {"score":1,"timeout":False,"deaths":2,"decisions":100,"equipment_count":3,"level":4}
            row.update(control=hero, candidate={**hero,"score":0})
        sweep = regression_sweep({"pairs":pairs})
        self.assertEqual(len(sweep["comparisons"]),55)
        self.assertEqual(len(sweep["flagged"]),11)
        self.assertTrue(all(row["metric"] == "win" for row in sweep["flagged"]))

    def test_local_feedback_preserves_behavior_and_rejects_wrong_evidence(self):
        policy = read(HERE / "base.ir.json")
        source = compile_policy(policy)
        pairs = [{"seed": seed, "slot": slot, "score": int(slot < 6),
                  "control_score": int(slot < 5), "delta": int(slot == 5)}
                 for seed in range(20) for slot in range(10)]
        summary = {"episodes": 200, "seat_comparisons": 200,
                   "wins": 120, "control_wins": 100, "pairs": pairs}
        report = {"source_sha256": digest(source.encode()), "held_out": summary,
                  "gate": significance(summary, alpha=0.025), "hosted_evaluation_eligible": True}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            write(path, report)
            updated = feedback(policy, path)
            self.assertEqual(compile_policy(updated), source)
            self.assertEqual(executable(updated), executable(policy))
            self.assertEqual(updated["update"]["parent"], digest(policy))
            self.assertEqual(updated["belief"]["claims"]["B_local_gate"]["status"], "supported")
            for field, value in [("source_sha256", "wrong"), ("hosted_evaluation_eligible", False),
                                 ("gate", {**report["gate"], "one_sided_sign_test_p": 0.9}),
                                 ("held_out", {**summary, "wins": 121})]:
                changed = {**report, field: value}
                write(path, changed)
                with self.subTest(field=field), self.assertRaises(ValueError):
                    feedback(policy, path)

    def test_seed_gate_uses_independent_clusters(self):
        pairs = [{"seed": seed, "slot": slot, "delta": int(slot < 5)}
                 for seed in range(20) for slot in range(10)]
        result = significance({"pairs": pairs})
        self.assertTrue(result["passed"])
        self.assertEqual(result["one_sided_sign_test_p"], 2**-20)
        self.assertFalse(significance({"pairs": pairs[:10]})["passed"])
        with self.assertRaises(ValueError):
            significance({"pairs": pairs + pairs[:10]})

    def test_statistical_and_practical_thresholds_both_apply(self):
        pairs = [{"seed": seed, "slot": slot, "delta": int(slot == 0 and seed < 19)}
                 for seed in range(20) for slot in range(10)]
        result = significance({"pairs": pairs})
        self.assertLess(result["one_sided_sign_test_p"], 0.05)
        self.assertFalse(result["passed"])  # 9.5 percentage points, below the 10-point gate.

    def test_hosted_comparison_rejects_roster_config_and_version_drift(self):
        control = [{"episode_request_id": f"before-{s}", "slot": s, "seed": 42,
                    "coworld_id": "cow-fixed", "game_version": "fixed", "game_config": {"seed": 42},
                    "roster": ["base"] * s + ["<candidate>"] + ["base"] * (9-s),
                    "score": 0, "equipment_count": 1, "deaths": 2, "timeout": False}
                   for s in range(10)]
        candidate = deepcopy(control)
        for row in candidate:
            row["episode_request_id"] = "after-" + str(row["slot"])
            row["score"] = 1
        self.assertEqual(compare(control, candidate)["paired_win_delta"], 1)
        for key, value in [("roster", ["different"] * 10), ("game_config", {"seed": 43}),
                           ("game_version", "different"), ("episode_request_id", "before-0")]:
            changed = deepcopy(candidate)
            changed[0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                compare(control, changed)
        with self.assertRaises(ValueError):
            compare(control, candidate[:-1])


if __name__ == "__main__":
    unittest.main()
