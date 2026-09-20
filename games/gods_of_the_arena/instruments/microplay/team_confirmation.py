"""Fresh prospective test of cooperation beyond the selected finishing skill."""
import argparse
import json
from pathlib import Path
import shutil
import time

import study
import study_v2


def prepare(directory, prior):
    if (directory / "plan.json").exists():
        raise ValueError("Plan already frozen")
    result = json.loads((prior / "discovery-result.json").read_text())
    assert result["selected"] == "finish"
    directory.mkdir(parents=True, exist_ok=True)
    shutil.copytree(prior / "policies", directory / "policies", dirs_exist_ok=True)
    shutil.copy2(prior / "encounter", directory / "encounter")
    plan = json.loads((prior / "plan.json").read_text())
    cases = []
    for case in study_v2.fixtures("holdout"):
        if case["family"] not in ("ally_rescue", "crossfire", "duel_control"):
            continue
        case["id"] = case["id"].replace("holdout/tight", "cooperation/fresh")
        case["partition"] = "cooperation"
        case["seed"] += 3000
        for actor in case["actors"]:
            actor["x"] += 4
            actor["y"] += 2
            if "hp" in actor:
                actor["hp"] += 15
        cases.append(case)
    plan["created_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    plan["objective"] = "Test whether assistance reduces allied deaths beyond finishing alone."
    plan["discovery"] = cases
    plan["holdout"] = []
    plan["prior_discovery_sha256"] = study.ir.sha(prior / "discovery-result.json")
    plan["instrument_sha256"]["team_confirmation.py"] = study.ir.sha(Path(__file__))
    plan["selection"] = {
        "candidate": "combined", "control": "finish", "reference": "parent",
        "requirements": ["strictly fewer allied deaths than finish and parent",
                         "no fewer enemy deaths than finish or parent",
                         "no additional allied deaths per spell mode relative to finish or parent",
                         "identical duel-control state hashes versus parent"],
        "scope": "Local cooperative skill only; no league promotion."}
    study.write(directory / "plan.json", plan)
    print(json.dumps({"frozen": str(directory / "plan.json"), "cases": len(cases)}))


def evaluate(directory):
    result = study.evaluate(directory, "discovery")
    rows = json.loads((directory / "discovery-summary.json").read_text())
    total = result["totals"]
    checks = {}
    for control in ("parent", "finish"):
        checks[control] = {
            "fewer_ally_deaths": total["combined"]["ally_deaths"] < total[control]["ally_deaths"],
            "no_fewer_enemy_deaths": total["combined"]["enemy_deaths"] >= total[control]["enemy_deaths"],
            "spell_strata_survival": all(
                sum(r["ally_deaths"] for r in rows if r["arm"] == "combined" and r["automatic_spells"] == s) <=
                sum(r["ally_deaths"] for r in rows if r["arm"] == control and r["automatic_spells"] == s)
                for s in (False, True))}
    checks["duel_control_parity"] = result["gates"]["combined"]["duel_control_parity"]
    passed = checks["duel_control_parity"] and all(all(checks[c].values()) for c in ("parent", "finish"))
    result["gates"] = checks
    result["selected"] = "combined" if passed else None
    result["partition"] = "cooperation_confirmation"
    study.write(directory / "cooperation-result.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=lambda p: Path(p).resolve())
    parser.add_argument("command", choices=("prepare", "run", "audit"))
    parser.add_argument("--prior", type=lambda p: Path(p).resolve(),
                        default=study.ir.ROOT / "tmp/gota-ir/microplay-v2-20260920")
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.directory, args.prior)
    else:
        study.run(args.directory, "discovery", arms=("parent", "finish", "combined"), audit=args.command == "audit")
        if args.command == "run":
            evaluate(args.directory)
