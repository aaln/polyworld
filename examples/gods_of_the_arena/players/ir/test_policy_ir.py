"""Structural and real-VM coaching fidelity tests; run unittest discovery here."""

from copy import deepcopy
import json
import os
from pathlib import Path
import random
import subprocess
import unittest

import basic_syntax
from policy_ir import (HERE, ROOT, bundle, compile_policy, executable, extract,
                       read, validate)


BASE = read(HERE / "base.ir.json")
WAVE = read(HERE / "waveguard_r4.ir.json")
LAYERED = read(HERE / "layered.ir.json")


class StructuralTests(unittest.TestCase):
    def test_original_baseline_and_both_round_trips(self):
        source = (HERE.parent / "base.bas").read_text()
        self.assertEqual(basic_syntax.parse(source), basic_syntax.parse(compile_policy(BASE)))
        self.assertEqual(extract(source, BASE), BASE)
        for policy in (BASE, WAVE, LAYERED):
            self.assertEqual(extract(compile_policy(policy), policy), policy)

    def test_symbolic_parameter_edit_updates_behavior_and_reviews(self):
        source = compile_policy(WAVE).replace("dx * 2 / scale", "dx * 3 / scale")
        # Every occurrence is part of the same declared parameter.
        with self.assertRaises(ValueError):
            extract(source, WAVE)
        source = source.replace("dy * 2 / scale", "dy * 3 / scale").replace("scale > 2 then", "scale > 3 then")
        recovered = extract(source, WAVE)
        self.assertEqual(recovered["skill"]["fallback"]["parameters"]["offset_tiles"], 3)
        self.assertIn("goal/G_wave", recovered["update"]["needs_review"])
        self.assertEqual(recovered["belief"]["claims"]["B_wave"]["status"], "requires_review")
        self.assertEqual(recovered["goal"], WAVE["goal"])
        self.assertEqual(basic_syntax.parse(source), basic_syntax.parse(compile_policy(recovered)))

    def test_ir_parameter_edit_changes_symbolic_behavior(self):
        changed = deepcopy(BASE)
        changed["skill"]["consume"]["parameters"]["heal_numerator"] = 4
        self.assertIn("selfMaxHp * 4", compile_policy(changed))
        self.assertEqual(extract(compile_policy(changed), BASE)["skill"], changed["skill"])

    def test_sustain_skill_round_trip_and_reverse_edit(self):
        changed = deepcopy(WAVE)
        changed["skill"]["sustain"]["operator"] = "buy_sustain_only"
        source = compile_policy(changed)
        self.assertNotIn("buyItem(4)", source)
        self.assertEqual(extract(source, changed), changed)
        recovered = extract(source, WAVE)
        self.assertEqual(recovered["skill"], changed["skill"])
        self.assertIn("goal/G_capacity", recovered["update"]["needs_review"])

    def test_weighted_targeting_round_trip_and_parameter_bounds(self):
        changed = deepcopy(BASE)
        changed["skill"]["observe"] = {"operator": "weighted_enemy", "parameters": {
            "hero_weight": 1, "footman_weight": 4, "structure_weight": 4}}
        source = compile_policy(changed)
        self.assertEqual(extract(source, changed), changed)
        self.assertEqual(extract(source, BASE)["skill"], changed["skill"])
        changed["skill"]["observe"]["parameters"]["hero_weight"] = 0
        with self.assertRaises(ValueError):
            compile_policy(changed)

    def test_unknown_or_unaccounted_code_is_rejected(self):
        source = compile_policy(BASE)
        for bad in ["buyItem(20)\n" + source, source + "buyItem(20)\n",
                    source.replace("distance < bestDistance", "distance <= bestDistance"),
                    source.replace("' @rule R2", "' @rule R1"),
                    source.replace("walkTo(64, 64)", "walkTo(128, 64)"),
                    source + "\nprint 1\n"]:
            with self.subTest(source=bad[-60:]), self.assertRaises(ValueError):
                extract(bad, BASE)

    def test_real_control_flow_and_order_are_extracted(self):
        source = compile_policy(BASE).replace("if bestId = 0 then\n  walkTo", "if bestId <> 0 then\n  walkTo")
        result = extract(source, BASE)
        self.assertEqual(result["strategy"][-1]["when"], "candidate_exists")
        self.assertNotEqual(executable(result), executable(BASE))
        start = compile_policy(BASE)
        prefix, rest = start.split("' @rule E1")
        sustain, rest = rest.split("' @rule E2")
        equipment, tail = rest.split("' @rule R4")
        reordered = prefix + "' @rule E2" + equipment + "' @rule E1" + sustain + "' @rule R4" + tail
        self.assertEqual(extract(reordered, BASE)["strategy"][4]["id"], "E2")

    def test_binding_guard_and_memory_drift_rejected(self):
        changed = deepcopy(WAVE)
        changed["belief"]["grounded"]["memory"].append("imaginary_enemy_intent")
        with self.assertRaises(ValueError):
            validate(changed)
        changed = deepcopy(BASE)
        changed["strategy"][1], changed["strategy"][2] = changed["strategy"][2], changed["strategy"][1]
        with self.assertRaises(ValueError):
            compile_policy(changed)

    def test_formatting_changes_do_not_claim_behavior_change(self):
        source = compile_policy(BASE).upper().replace("' @RULE", "' @rule")
        source = source.replace("WALKTO(64, 64)", "WALKTO((64), (64)) ' formatting")
        self.assertEqual(extract(source, BASE), BASE)

    def test_immutable_bundle(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "revision"
            manifest = bundle(BASE, path)
            self.assertTrue(manifest["structural_parity"])
            self.assertEqual(read(path / "extracted.ir.json"), BASE)
            with self.assertRaises(FileExistsError):
                bundle(BASE, path)


def obj(id, kind=3, team=0, x=30, y=20, hp=100, alive=1):
    return dict(objectId=id, objectKind=kind, objectTeam=team, objectClass=-1,
                objectX=x, objectY=y, objectHp=hp, objectAlive=alive)


def fixture(objects=(), **changes):
    self_data = dict(selfId=1, selfTeam=0, selfClass=0, selfX=20, selfY=20,
                     selfHp=100, selfMaxHp=100, selfMana=100, selfMaxMana=100,
                     selfGold=0, selfLevel=1, worldTick=1)
    self_data.update(changes)
    return {"self": self_data, "objects": list(objects), "inventory": [0] * 6}


class RealVmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vm = ROOT / "tmp/gota-ir/scenario-vm"
        cls.vm.parent.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ, POLYWORLD_DEPS=str(ROOT))
        subprocess.run(["nim", "c", "-d:headless", "--hints:off", f"-o:{cls.vm}",
                        str(HERE / "scenario_vm.nim")], cwd=ROOT, env=env, check=True,
                       capture_output=True, text=True)
        for policy, filename in [(BASE, "base.generated.bas"), (WAVE, "waveguard_r4.generated.bas"),
                                 (LAYERED, "layered.generated.bas")]:
            if (HERE / filename).read_text() != compile_policy(policy):
                raise AssertionError(f"stale checked-in generated policy: {filename}")

    def run_vm(self, source, decisions, memory=()):
        result = subprocess.run([str(self.vm), str(source)], input=json.dumps(
            {"decisions": decisions, "memory": list(memory)}), text=True, capture_output=True, check=True)
        return json.loads(result.stdout)

    def test_baseline_command_trace_parity_all_classes(self):
        rng = random.Random(1729)
        decisions = []
        for index in range(200):
            objects = [obj(100+j, kind=rng.randrange(1,5), team=rng.randrange(2),
                           x=rng.randrange(128), y=rng.randrange(128), alive=rng.randrange(2)) for j in range(20)]
            case = fixture(objects, selfClass=index % 10, selfHp=rng.randrange(101),
                           selfMana=rng.randrange(101), selfGold=rng.randrange(501), worldTick=index+1)
            case["inventory"] = [rng.randrange(21) for _ in range(6)]
            case["returns"] = {name: rng.randrange(2) for name in ["walkTo", "attackTarget", "buyItem", "useItem"]}
            decisions.append(case)
        original = self.run_vm(HERE.parent / "base.bas", decisions, ["bestId", "decisions"])
        regenerated = self.run_vm(HERE / "base.generated.bas", decisions, ["bestId", "decisions"])
        self.assertEqual(original, regenerated)

    def test_wave_waypoint_retention_and_lost_escort(self):
        fort = obj(5, kind=1, x=0, y=20)
        first = fixture([fort, obj(11), obj(10)])  # stable ID breaks distance tie
        second = fixture([fort, obj(11, x=21), obj(10, x=35)], worldTick=2)
        third = fixture([fort, obj(11, x=21), obj(10, hp=0, alive=0)], worldTick=3)
        fourth = fixture([fort], worldTick=4)
        result = self.run_vm(HERE / "waveguard_r4.generated.bas", [first, second, third, fourth], ["escortId"])
        self.assertEqual([r["memory"]["escortId"] for r in result], [10, 10, 11, 0])
        self.assertEqual([r["actions"][-1]["arguments"] for r in result], [[28,20], [33,20], [19,20], [64,64]])

    def test_combat_and_economy_stay_baseline(self):
        case = fixture([obj(9, team=1, kind=2, x=21)], selfHp=20, selfMana=20, selfGold=200)
        case["inventory"] = [1, 2, 3, 4, 0, 0]
        before = self.run_vm(HERE / "base.generated.bas", [case])[0]["actions"]
        after = self.run_vm(HERE / "waveguard_r4.generated.bas", [case])[0]["actions"]
        self.assertEqual(before, after)
        self.assertEqual(before[0]["command"], "attackTarget")
        self.assertNotIn("walkTo", [a["command"] for a in after])

    def test_protected_structure_is_not_selected_and_fog_is_not_death(self):
        result = self.run_vm(HERE / "waveguard_r4.generated.bas", [
            fixture([obj(7, kind=4, team=1, x=20, hp=100, alive=0)]),
            fixture([obj(8, kind=2, team=1, x=20)], worldTick=2),
            fixture([], worldTick=3)], ["bestId"])
        self.assertEqual([r["memory"]["bestId"] for r in result], [0, 8, 0])
        self.assertEqual(WAVE["belief"]["grounded"]["memory"],
                         ['decisions', 'escortId', 'lastJoinTick', 'lastJoinX', 'lastJoinY', 'stalled'])

    def test_stall_and_rejection_have_bounded_fallbacks(self):
        cases = [fixture([obj(5, kind=1, x=0, y=20), obj(10)], worldTick=t) for t in range(1,50)]
        result = self.run_vm(HERE / "waveguard_r4.generated.bas", cases, ["escortId"])
        self.assertEqual(result[47]["actions"][-1]["arguments"], [64,64])
        self.assertEqual(result[47]["memory"]["escortId"], 0)
        case = fixture([obj(10)])
        case["returns"] = {"walkTo": 0}
        result = self.run_vm(HERE / "waveguard_r4.generated.bas", [case], ["escortId", "moveAccepted"])[0]
        self.assertEqual(len([a for a in result["actions"] if a["command"] == "walkTo"]), 2)
        self.assertEqual(result["actions"][-1]["arguments"], [64,64])
        self.assertEqual(result["memory"], {"escortId":0, "moveAccepted":0})

    def test_offset_domain_and_negative_integer_rounding(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "offset.bas"
            for offset in range(9):
                policy = deepcopy(WAVE)
                policy["skill"]["fallback"]["parameters"]["offset_tiles"] = offset
                source.write_text(compile_policy(policy))
                recovered = extract(source.read_text(), WAVE)
                self.assertEqual(recovered["skill"], policy["skill"])
                result = self.run_vm(source, [fixture([obj(5, kind=1, x=0, y=20), obj(10)])])
                self.assertEqual(result[0]["actions"][-1]["arguments"], [30-offset, 20])
            policy["skill"]["fallback"]["parameters"]["offset_tiles"] = 2
            source.write_text(compile_policy(policy))
            result = self.run_vm(source, [fixture([obj(5, kind=1, x=0, y=0), obj(10, x=30, y=20)])])
            # -40/30 truncates toward zero in BASIC: -1, not Python's -2.
            self.assertEqual(result[0]["actions"][-1]["arguments"], [28, 19])

    def test_sustain_preserves_emergency_purchases_and_spares_low_gold(self):
        import tempfile
        policy = deepcopy(WAVE)
        policy["skill"]["sustain"]["operator"] = "buy_sustain_only"
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "sustain.bas"
            source.write_text(compile_policy(policy))
            cases = [fixture([obj(9, team=1, x=21)], selfHp=20, selfMana=20, selfGold=150),
                     fixture([obj(9, team=1, x=21)], selfHp=100, selfMana=100, selfGold=40)]
            results = self.run_vm(source, cases)
            purchases = [[a["arguments"][0] for a in r["actions"] if a["command"] == "buyItem"]
                         for r in results]
            self.assertEqual(purchases[0][:3], [2, 1, 3])
            self.assertIn(7, purchases[0])
            self.assertNotIn(4, purchases[0])
            self.assertEqual(purchases[1], [])
            self.assertEqual(results[1]["actions"][0], {"command": "attackTarget", "arguments": [9], "accepted": 1})

    def test_weighted_targeting_trades_distance_without_ignoring_exposure(self):
        import tempfile
        policy = deepcopy(BASE)
        policy["skill"]["observe"] = {"operator": "weighted_enemy", "parameters": {
            "hero_weight": 1, "footman_weight": 4, "structure_weight": 4}}
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "weighted.bas"
            source.write_text(compile_policy(policy))
            cases = [fixture([obj(11, team=1, x=22), obj(12, kind=2, team=1, x=23)]),
                     fixture([obj(11, team=1, x=22), obj(12, kind=2, team=1, x=29)]),
                     fixture([obj(13, kind=4, team=1, x=20, alive=0), obj(11, team=1, x=22)]),
                     fixture([obj(11, team=1, x=22), obj(12, kind=2, team=1, x=24)])]
            results = self.run_vm(source, cases, ["bestId"])
            self.assertEqual([r["memory"]["bestId"] for r in results], [12, 11, 11, 11])

    def test_wave_local_ignores_distant_heroes_and_prefers_local_footmen(self):
        escort = obj(10, kind=3, team=0, x=20, y=20)
        local_foot = obj(21, kind=3, team=1, x=22, y=20)
        local_hero = obj(22, kind=2, team=1, x=21, y=20)
        far_hero = obj(23, kind=2, team=1, x=50, y=50)
        protected = obj(24, kind=4, team=1, x=20, y=20, hp=100, alive=0)
        results = self.run_vm(HERE / "layered.generated.bas", [
            fixture([escort, far_hero]),
            fixture([escort, local_hero, far_hero], worldTick=2),
            fixture([escort, local_foot, local_hero], worldTick=3),
            fixture([escort, protected, far_hero], worldTick=4),
            fixture([far_hero], worldTick=5),
        ], ["bestId", "escortId"])
        self.assertEqual([r["memory"]["bestId"] for r in results], [0, 22, 21, 0, 0])
        self.assertEqual([r["memory"]["escortId"] for r in results], [10, 10, 10, 10, 0])
        self.assertEqual(results[0]["actions"][-1]["command"], "walkTo")
        self.assertEqual(results[1]["actions"][0], {"command": "attackTarget", "arguments": [22], "accepted": 1})
        self.assertNotIn("walkTo", [a["command"] for a in results[1]["actions"]])
        self.assertEqual(results[4]["actions"][-1]["arguments"], [64, 64])


if __name__ == "__main__":
    unittest.main()
