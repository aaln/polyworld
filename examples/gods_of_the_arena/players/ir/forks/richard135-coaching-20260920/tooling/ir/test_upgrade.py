"""Current-game ordered equipment behavior, including symbolic reverse edits."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

import test_policy_ir as fixtures
from binding import CONTRACTS
from policy_ir import HERE, compile_policy, extract, grounded, read, refresh_grounding


def candidate():
    policy = deepcopy(read(HERE / "waveguard_xp.evaluated.ir.json"))
    policy["execution"]["game_version"] = "2026.9.15.1"
    policy["skill"]["equipment"] = {"operator":"buy_ordered_loadout",
                                     "parameters":CONTRACTS["buy_ordered_loadout"].defaults()}
    refresh_grounding(policy)
    return policy


class UpgradeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.RealVmTests.setUpClass.__func__(cls)

    run_vm = fixtures.RealVmTests.run_vm

    def play(self, cases, policy=None):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"policy.bas";p.write_text(compile_policy(policy or candidate()))
            return self.run_vm(p,cases,["loadoutPurchases"])

    def test_ordered_equipment_is_class_independent_and_stops_after_plan(self):
        plan=[11,13,16,18,20];cases=[]
        for c in range(10):
            for n in range(6):
                f=fixtures.fixture(selfClass=c,selfGold=1000)
                f["inventory"]=plan[:n]+[0]*(6-n)
                cases.append(f)
        result=self.play(cases)
        buys=[[a["arguments"][0] for a in r["actions"] if a["command"]=="buyItem"] for r in result]
        self.assertEqual(buys,([[item] for item in plan]+[[]])*10)
        self.assertEqual(result[-1]["memory"]["loadoutPurchases"],50)

    def test_saves_for_next_item_and_respects_full_inventory_and_rejection(self):
        poor=fixtures.fixture(selfGold=100)
        waiting=fixtures.fixture(selfGold=140);waiting["inventory"][0]=11
        full=fixtures.fixture(selfGold=1000);full["inventory"]=[1,2,3,4,5,6]
        rejected=fixtures.fixture(selfGold=150);rejected["returns"]={"buyItem":0}
        results=self.play([poor,waiting,full,rejected])
        buys=[[a for a in r["actions"] if a["command"]=="buyItem"] for r in results]
        self.assertEqual([len(x) for x in buys],[0,0,0,1])
        self.assertEqual(results[-1]["memory"]["loadoutPurchases"],0)

    def test_symbolic_edit_lifts_and_changes_next_item(self):
        p=candidate();s=compile_policy(p)
        self.assertEqual(extract(s,p),p)
        # Both occurrences of the parameter must agree in the complete AST.
        edited=s.replace("loadoutItem = 11 then","loadoutItem = 12 then").replace("loadoutNext = 11\n","loadoutNext = 12\n")
        recovered=extract(edited,p)
        self.assertEqual(recovered["skill"]["equipment"]["parameters"]["first_item"],12)
        self.assertTrue(recovered["update"]["needs_review"])
        actions=self.play([fixtures.fixture(selfGold=150)],recovered)[0]["actions"]
        self.assertEqual([a["arguments"] for a in actions if a["command"]=="buyItem"],[[12]])
        bad=deepcopy(p);bad["skill"]["equipment"]["parameters"]["second_item"]=11
        with self.assertRaises(ValueError):compile_policy(bad)

    def test_current_grounding_does_not_reuse_old_poison_contract(self):
        facts=grounded(candidate())["temporal_execution"]["facts"]
        self.assertIn("normal attack range",facts["poison"])
        self.assertIn("explicit",facts["spells"].lower())


if __name__=="__main__":unittest.main()
