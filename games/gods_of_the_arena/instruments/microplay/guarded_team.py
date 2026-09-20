"""Prospective refinement and untouched confirmation for threat-aware teamwork."""
import argparse
import json
from pathlib import Path

import ir_v3
import study
import study_v2
import team_confirmation

base_fixtures = study_v2.fixtures


def fixtures(partition):
    cases = base_fixtures("discovery" if partition == "discovery" else "holdout")
    for case in cases:
        case["id"] = case["id"].replace("/tight/", "/guarded/", 1)
        case["seed"] += 6000
        for actor in case["actors"]:
            actor["x"] += 1 if partition == "discovery" else -3
            actor["y"] += 3
            if "hp" in actor:
                actor["hp"] += 5 if partition == "discovery" else 10
    return cases


study.ir = ir_v3
study.fixtures = fixtures


def evaluate(directory, partition):
    result = study.evaluate(directory, partition)
    rows = json.loads((directory / (partition + "-summary.json")).read_text())
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
    study.write(directory / (partition + "-result.json"), result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=lambda p: Path(p).resolve())
    parser.add_argument("command", choices=("prepare", "discovery", "holdout", "audit"))
    parser.add_argument("--partition", choices=("discovery", "holdout"), default="discovery")
    args = parser.parse_args()
    if args.command == "prepare":
        study.prepare(args.directory)
        path = args.directory / "plan.json"
        plan = json.loads(path.read_text())
        plan["instrument_sha256"].update({name: ir_v3.sha(study.HERE / name) for name in
             ("ir_v2.py", "ir_v3.py", "study_v2.py", "team_confirmation.py", "guarded_team.py")})
        plan["selection"] = {
            "candidate": "combined", "control": "finish", "reference": "parent",
            "requirements": ["strictly fewer allied deaths than finish and parent",
                "no fewer enemy deaths than either control", "no additional allied deaths in either spell mode",
                "identical duel-control state hashes"],
            "holdout": "Run only if discovery passes; same gates, no parameter changes.",
            "scope": "Local cooperative skill; no league promotion."}
        plan["predecessor"] = "Combined v2 failed cooperation confirmation: automatic-spell deaths36 vs finish34."
        study.write(path, plan)
    elif args.command in ("discovery", "holdout"):
        if args.command == "holdout":
            assert json.loads((args.directory / "discovery-result.json").read_text())["selected"] == "combined"
        study.run(args.directory, args.command, arms=("parent", "finish", "combined"))
        evaluate(args.directory, args.command)
    else:
        study.run(args.directory, args.partition, arms=("parent", "finish", "combined"), audit=True)
