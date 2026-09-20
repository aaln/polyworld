"""Behavioral tests for the separately attributable research hypotheses."""

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

import test_policy_ir as fixtures
from binding import CONTRACTS
from policy_ir import HERE, compile_policy, executable, extract, read, refresh_grounding


def variant(operator):
    policy = deepcopy(read(HERE / "duelist.ir.json"))
    skill = ("observe" if operator == "weighted_enemy_recovery" else
             "equipment" if operator == "buy_equipment_reserved" else "sustain")
    policy["skill"][skill] = {"operator": operator, "parameters": CONTRACTS[operator].defaults()}
    refresh_grounding(policy)
    return policy


class HypothesisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.RealVmTests.setUpClass.__func__(cls)

    run_vm = fixtures.RealVmTests.run_vm

    def run_policy(self, policy, cases, memory=()):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "candidate.bas"
            source.write_text(compile_policy(policy))
            return self.run_vm(source, cases, memory)

    def test_new_contracts_round_trip_and_symbolic_recovery_edit(self):
        for operator in ["weighted_enemy_recovery", "buy_single_heal"]:
            policy = variant(operator)
            recovered = extract(compile_policy(policy), policy)
            self.assertEqual(executable(recovered), executable(policy))
        policy = variant("weighted_enemy_recovery")
        edited = compile_policy(policy).replace("pursuitStalled >= 72", "pursuitStalled >= 96")
        recovered = extract(edited, policy)
        self.assertEqual(recovered["skill"]["observe"]["parameters"]["stall_ticks"], 96)
        self.assertTrue(recovered["update"]["needs_review"])

    def test_stalled_target_is_excluded_then_becomes_eligible(self):
        policy = variant("weighted_enemy_recovery")
        objects = [fixtures.obj(10, kind=2, team=1, x=24), fixtures.obj(20, team=1, x=25)]
        cases = [fixtures.fixture(objects, worldTick=tick) for tick in range(1, 75)]
        cases.append(fixtures.fixture(objects, worldTick=313))
        results = self.run_policy(policy, cases, ["bestId", "blockedId", "blockedUntil", "recoveryActivations"])
        self.assertEqual(results[71]["memory"]["bestId"], 10)
        self.assertEqual(results[72]["memory"], {"bestId":20, "blockedId":10,
                                                "blockedUntil":313, "recoveryActivations":1})
        self.assertEqual(results[73]["memory"]["bestId"], 20)
        self.assertEqual(results[-1]["memory"]["bestId"], 10)

    def test_damage_movement_fog_and_respawn_gap_reset_progress(self):
        policy = variant("weighted_enemy_recovery")
        cases = [fixtures.fixture([fixtures.obj(10, kind=2, team=1, x=24, hp=1000-t)], worldTick=t)
                 for t in range(1, 100)]
        results = self.run_policy(policy, cases, ["recoveryActivations"])
        self.assertEqual(results[-1]["memory"]["recoveryActivations"], 0)
        policy["skill"]["observe"]["parameters"]["stall_ticks"] = 3
        objects = [fixtures.obj(10, kind=2, team=1, x=24)]
        cases = [fixtures.fixture(objects, worldTick=1), fixtures.fixture(objects, worldTick=2),
                 fixtures.fixture(objects, worldTick=3, selfX=21), fixtures.fixture([], worldTick=4),
                 fixtures.fixture(objects, worldTick=5), fixtures.fixture(objects, worldTick=50),
                 fixtures.fixture(objects, worldTick=51)]
        results = self.run_policy(policy, cases, ["pursuitStalled", "recoveryActivations"])
        self.assertEqual([r["memory"]["pursuitStalled"] for r in results], [0,1,0,0,0,0,1])
        self.assertEqual(results[-1]["memory"]["recoveryActivations"], 0)

    def test_single_heal_retains_emergencies_and_rejection_fallback(self):
        policy = variant("buy_single_heal")
        healthy = fixtures.fixture(selfGold=150)
        poor = fixtures.fixture(selfHp=20, selfGold=40)
        injured = fixtures.fixture(selfHp=20, selfMana=20, selfGold=150)
        rejected = deepcopy(injured)
        rejected["returns"] = {"buyItem":0}
        results = self.run_policy(policy, [healthy, poor, injured, rejected])
        purchases = [[a for a in r["actions"] if a["command"] == "buyItem"] for r in results]
        heals = [[a["arguments"][0] for a in row if a["arguments"][0] in [1,2]] for row in purchases]
        self.assertEqual(heals, [[], [1], [2], [2,1]])
        self.assertIn(3, [a["arguments"][0] for a in purchases[2]])
        for row in purchases:
            self.assertLessEqual(sum(a["accepted"] for a in row if a["arguments"][0] in [1,2]),1)

    def test_structure_priority_never_attacks_a_protected_structure(self):
        policy = read(HERE / "duelist.ir.json")
        policy["skill"]["observe"]["parameters"]["structure_weight"] = 1
        objects = [fixtures.obj(10, kind=2, team=1, x=24), fixtures.obj(20, kind=4, team=1, x=23)]
        protected = deepcopy(objects)
        protected[1]["objectAlive"] = 0
        results = self.run_policy(policy, [fixtures.fixture(objects), fixtures.fixture(protected)], ["bestId"])
        self.assertEqual([r["memory"]["bestId"] for r in results], [20,10])

    def test_equipment_reservation_caps_accepted_purchases_within_decision(self):
        policy = variant("buy_equipment_reserved")
        cases = []
        for equipment in [[], [7,5,6], [7,5,6,9], [7,5,6,9,11]]:
            case = fixtures.fixture(selfGold=10000)
            case["inventory"] = equipment + [0] * (6-len(equipment))
            cases.append(case)
        results = self.run_policy(policy, cases, ["gearCount"])
        gear = [[a for a in r["actions"] if a["command"] == "buyItem" and a["arguments"][0] > 4]
                for r in results]
        self.assertEqual([len(row) for row in gear], [4,1,0,0])
        self.assertEqual([r["memory"]["gearCount"] for r in results], [4,4,4,5])
        rejected = deepcopy(cases[1])
        rejected["returns"] = {"buyItem":0}
        result = self.run_policy(policy, [rejected], ["gearCount"])[0]
        self.assertEqual(result["memory"]["gearCount"], 3)
        self.assertGreater(len(result["actions"]), 1)

    def test_equipment_reservation_parity_reverse_edit_and_sustain(self):
        policy = variant("buy_equipment_reserved")
        source = compile_policy(policy)
        self.assertEqual(extract(source, policy), policy)
        edited = source.replace("gearCount < 4", "gearCount < 5")
        recovered = extract(edited, policy)
        self.assertEqual(recovered["skill"]["equipment"]["parameters"]["equipment_cap"], 5)
        self.assertTrue(recovered["update"]["needs_review"])
        injured = fixtures.fixture(selfHp=20, selfMana=20, selfGold=10000)
        injured["inventory"] = [7,5,6,9,0,0]
        result = self.run_policy(policy, [injured])[0]
        self.assertEqual([a["arguments"][0] for a in result["actions"] if a["command"] == "buyItem"], [2,1,3])

    def test_hp_investment_uses_missing_gear_and_stops_after_acceptance(self):
        policy = variant("buy_hp_investment")
        cases = []
        for owned in [[],[5],[5,6],[5,6,9]]:
            case = fixtures.fixture(selfHp=10,selfGold=150)
            case["inventory"] = owned + [0]*(6-len(owned))
            cases.append(case)
        # Use separate VMs so counters are per case; production counters persist.
        for case,expected,bonus in zip(cases,[5,6,9,None],[50,60,70,0]):
            result = self.run_policy(policy,[case],["hpGearInvestments","hpGearGrantedHp"])[0]
            buys = [a["arguments"][0] for a in result["actions"] if a["command"]=="buyItem"]
            self.assertEqual(buys[:3], [expected,2,1] if expected else [2,1,5])
            self.assertEqual(result["memory"],{"hpGearInvestments":int(expected is not None),"hpGearGrantedHp":bonus})

    def test_hp_investment_preserves_fallbacks_and_round_trips(self):
        policy = variant("buy_hp_investment")
        source = compile_policy(policy)
        self.assertEqual(extract(source,policy),policy)
        edited = source.replace("selfHp * 2 < selfMaxHp * 1", "selfHp * 3 < selfMaxHp * 1")
        self.assertEqual(extract(edited,policy)["skill"]["sustain"]["parameters"]["hp_denominator"],3)
        cases = [fixtures.fixture(selfHp=10,selfGold=40),fixtures.fixture(selfGold=150),
                 fixtures.fixture(selfHp=10,selfGold=150),fixtures.fixture(selfHp=10,selfGold=150)]
        cases[2]["inventory"]=[1,0,0,0,0,0] # Earlier healing stock blocks the new phase.
        cases[3]["inventory"]=[7,8,10,11,12,13] # No space blocks it.
        for case in cases:
            result = self.run_policy(policy,[case],["hpGearInvestments"])[0]
            self.assertEqual(result["memory"]["hpGearInvestments"],0)
        rejected = fixtures.fixture(selfHp=10,selfGold=150)
        rejected["returns"]={"buyItem":0}
        result=self.run_policy(policy,[rejected],["hpGearInvestments"])[0]
        buys=[a["arguments"][0] for a in result["actions"] if a["command"]=="buyItem"]
        self.assertEqual(buys[:5],[5,6,9,2,1])
        self.assertEqual(result["memory"]["hpGearInvestments"],0)


if __name__ == "__main__":
    unittest.main()
