"""Adversarial public-observation tests executed by the real BASIC VM."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import ir
import study

VM = Path(os.environ.get("GOTA_MICROPLAY_VM", ir.ROOT / "tmp/gota-ir/microplay-20260920/scenario-vm"))


def obj(id, x, y, hp=200, team=1, kind=2, target=0, alive=1):
    return {"objectId": id, "objectX": x, "objectY": y, "objectHp": hp,
            "objectTeam": team, "objectKind": kind, "objectTarget": target, "objectAlive": alive}


class MicroplayTests(unittest.TestCase):
    def run_skill(self, objects, *, selected=200, own_id=101, parameters=None,
                  operator="microplay_local_target_v1"):
        parameters = parameters or {"finish": 1, "assist": 1, "ally_tiles": 8}
        contract = ir.binding.CONTRACTS[operator]
        source = f"bestId = {selected}\nbestDistance = 1\n" + contract.source(parameters)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "skill.bas"
            path.write_text(source)
            fixture = {"self": {"selfId": own_id, "selfTeam": 0, "selfX": 50, "selfY": 50,
                                   "selfAttackRange": 600000, "selfAttackDamage": 30,
                                   "selfHp": 250, "selfMaxHp": 250},
                       "inventory": [], "objects": objects}
            reply = subprocess.run([str(VM), str(path)], input=json.dumps({"decisions": [fixture],
                    "memory": ["bestId", "mpAssist", "mpPick"]}), text=True, capture_output=True, check=True)
        return json.loads(reply.stdout)[0]

    def test_finish_before_assistance(self):
        row = self.run_skill([obj(200, 51, 50), obj(201, 53, 50, hp=25),
                              obj(100, 49, 50, team=0, target=200)])
        self.assertEqual(row["memory"]["bestId"], 201)
        self.assertEqual(row["actions"], [])  # selection only; action arbitration remains parent

    def test_no_chase_of_far_wounded_target(self):
        row = self.run_skill([obj(200, 51, 50), obj(201, 55, 50, hp=1)])
        self.assertEqual(row["memory"]["bestId"], 200)

    def test_integer_diagonal_uncertainty(self):
        row = self.run_skill([obj(200, 51, 50), obj(201, 54, 51, hp=1)])
        self.assertEqual(row["memory"]["bestId"], 200)

    def test_join_lower_id_ally(self):
        row = self.run_skill([obj(200, 51, 50), obj(201, 53, 50),
                              obj(100, 49, 50, team=0, target=201)])
        self.assertEqual(row["memory"]["bestId"], 201)

    def test_never_follow_higher_id_back(self):
        row = self.run_skill([obj(200, 51, 50), obj(201, 53, 50),
                              obj(102, 49, 50, team=0, target=201)])
        self.assertEqual(row["memory"]["bestId"], 200)

    def test_missing_dead_and_friendly_targets(self):
        for target in [[], [obj(201, 53, 50, hp=0)], [obj(201, 53, 50, alive=0)],
                       [obj(201, 53, 50, team=0)]]:
            with self.subTest(target=target):
                row = self.run_skill([obj(200, 51, 50), obj(100, 49, 50, team=0, target=201)] + target)
                self.assertEqual(row["memory"]["bestId"], 200)

    def test_dead_or_distant_ally_does_not_count(self):
        for ally in [obj(100, 49, 50, team=0, target=201, hp=0),
                     obj(100, 40, 50, team=0, target=201)]:
            row = self.run_skill([obj(200, 51, 50), obj(201, 53, 50), ally])
            self.assertEqual(row["memory"]["bestId"], 200)

    def test_preserve_structure_and_no_target(self):
        for selected in (200, 0):
            row = self.run_skill([obj(200, 51, 50, kind=4), obj(201, 52, 50, hp=1)], selected=selected)
            self.assertEqual(row["memory"]["bestId"], selected)

    def test_bounded_scan_and_deterministic_tie(self):
        row = self.run_skill([obj(200, 51, 50), obj(202, 53, 50, hp=25), obj(201, 53, 50, hp=25)] +
                             [obj(1000 + i, 55, 55, kind=3) for i in range(500)])
        self.assertEqual(row["memory"]["bestId"], 201)
        self.assertLess(row["instructions"], 5000)

    def test_fixture_partitions_and_symmetry(self):
        discovery, holdout = study.fixtures("discovery"), study.fixtures("holdout")
        self.assertEqual(len(discovery), 64)
        self.assertEqual(len(holdout), 160)
        self.assertFalse({f["id"] for f in discovery} & {f["id"] for f in holdout})
        for fixture in discovery + holdout:
            self.assertEqual(len({a["slot"] for a in fixture["actors"]}), len(fixture["actors"]))
            self.assertEqual({a["slot"] // 5 for a in fixture["actors"] if a["controller"] == "subject"}, {fixture["side"]})

    def test_v2_integer_cell_bound(self):
        import ir_v2
        for dx, dy, expected in [(1, 1, 201), (3, 0, 201), (4, 3, 200)]:
            row = self.run_skill([obj(200, 51, 50), obj(201, 50 + dx, 50 + dy, hp=1)],
                                 operator="microplay_local_target_v2")
            self.assertEqual(row["memory"]["bestId"], expected)

    def test_v2_reach_bound_against_subtile_positions(self):
        # Independent geometric oracle for every admitted cell offset, including
        # negative coordinates and adversarial opposite cell corners.
        for range_hundredths in (90, 120, 250, 300, 330, 400, 600):
            for dx in range(-7, 8):
                for dy in range(-7, 8):
                    bound = ((abs(dx) + 1) * 100) ** 2 + ((abs(dy) + 1) * 100) ** 2
                    if bound <= range_hundredths ** 2:
                        for sx, sy, tx, ty in [(0, 0, 99, 99), (99, 99, 0, 0),
                                              (0, 99, 99, 0), (99, 0, 0, 99)]:
                            actual = (dx * 100 + tx - sx) ** 2 + (dy * 100 + ty - sy) ** 2
                            self.assertLessEqual(actual, range_hundredths ** 2)

    def test_v3_preserves_self_defense_unless_ally_more_vulnerable(self):
        import ir_v3
        for hp, target, expected in [(200, 101, 200), (80, 101, 201), (200, 0, 201)]:
            row = self.run_skill([obj(200, 51, 50, target=target), obj(201, 53, 50),
                                  obj(100, 49, 50, hp=hp, team=0, target=201)],
                                 operator="microplay_local_target_v3")
            self.assertEqual(row["memory"]["bestId"], expected)

    def test_v4_units_and_budget_gate(self):
        import ir_v4
        params = {"finish": 1, "assist": 1, "ally_tiles": 8,
                  "range_percent": 60, "object_limit": 48}
        objects = [obj(200, 51, 50), obj(201, 51, 51, hp=1)]
        row = self.run_skill(objects, operator="microplay_local_target_v4", parameters=params)
        self.assertEqual(row["memory"]["bestId"], 201)
        objects += [obj(1000 + i, 55, 55, kind=3) for i in range(47)]
        row = self.run_skill(objects, operator="microplay_local_target_v4", parameters=params)
        self.assertEqual(row["memory"]["bestId"], 200)
        self.assertEqual(row["memory"]["mpPick"], 0)
        self.assertLess(row["instructions"], 50)

    def test_v4_range_preserves_measured_inner_sixty_percent(self):
        for world_range in [70000, 330000, 300000, 240000, 75000,
                            76000, 390000, 330000, 270000, 80000]:
            self.assertEqual(world_range * 60 // 60000, world_range // 1000)


if __name__ == "__main__":
    unittest.main()
