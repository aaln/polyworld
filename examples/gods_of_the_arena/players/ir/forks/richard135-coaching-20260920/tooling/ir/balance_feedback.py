"""Turn a completed balance study into evidence-linked IR and a readable report.

This never promotes a policy. Even a passing simulated balance study must be
validated against the actual published release and hosted incumbents.
"""
import argparse
from copy import deepcopy
from html import escape
from pathlib import Path

from hypothesis_study import sign_p
from policy_ir import HERE, compile_policy, digest, extract, read, write


def finish(directory, stage):
    plan = read(directory / "plan.json")
    wave_local = plan.get("hypothesis") == "wave_local_balance"
    name = "wave-local" if wave_local else "supported-siege"
    title = "Wave-local combat" if wave_local else "Supported siege"
    belief = "B_wave_local" if wave_local else "B_supported_siege"
    rule = ("Only R1 changes: fight enemies within six tiles of a retained living allied footman, "
            "preferring footmen, heroes, then structures; otherwise rejoin the wave."
            if wave_local else
            "Only R1 changes: prioritize an exposed fort, then tower, within eight tiles, with a living "
            "allied creep within five tiles and at least 60% HP. Otherwise choose the nearest enemy.")
    result = read(directory / (stage + "-result.json"))
    if result["games"] != len(plan[stage]) * 3 or result["audited_games"] != result["games"]:
        raise ValueError("Incomplete stage")
    if result["invalid_games_scored"] != 0:
        raise ValueError("Invalid games cannot enter feedback")
    rows = {}
    for arm in ["parent", "candidate", "baseline"]:
        rows[arm] = []
        for case in plan[stage]:
            folder = directory / stage / arm / f"seed-{case['seed']}-slot-{case['slot']}"
            game = read(folder / "result.json")
            audit = read(folder / "audit.json")
            if (game["candidate_sha256"] != plan["sources"][arm]
                    or game["binary_sha256"] != plan["binary_sha256"]
                    or audit["binary_sha256"] != plan["auditor_sha256"]
                    or audit["hash_mismatches"] != 0
                    or audit["actions_consumed"] != game["actions"]
                    or audit["ticks"] != game["ticks"]
                    or audit["replay_sha256"] != game["replay_sha256"]
                    or digest((folder / "episode.replay").read_bytes()) != game["replay_sha256"]):
                raise ValueError(f"Invalid evidence: {folder}")
            hero = game["heroes"][case["slot"]]
            rows[arm].append({**hero, "timeout": game["timeout"], "ticks": game["ticks"]})

    def summarize(items):
        decisions = sum(x["decisions"] for x in items)
        return {"n": len(items), "wins": sum(x["score"] for x in items),
                "timeouts": sum(x["timeout"] for x in items),
                "deaths": sum(x["deaths"] for x in items),
                "mean_level": sum(x["level"] for x in items) / len(items),
                "structure_intent_share": sum(x["target_kinds_after_tick"][1]
                                             + x["target_kinds_after_tick"][4] for x in items) / max(1, decisions),
                "deaths_per_1000_decisions": 1000 * sum(x["deaths"] for x in items) / max(1, decisions)}

    descriptive = {arm: {"all": summarize(items),
                         "Red": summarize([x for x in items if x["team"] == 0]),
                         "Blue": summarize([x for x in items if x["team"] == 1])}
                   for arm, items in rows.items()}
    paired = {}
    for arm, comparison in result["comparisons"].items():
        positive = sum(x["delta"] > 0 for x in comparison["pairs"])
        negative = sum(x["delta"] < 0 for x in comparison["pairs"])
        paired[arm] = {"positive_pairs": positive, "negative_pairs": negative,
                       "one_sided_exact_p": sign_p(positive, negative)}
    report = {"plan": plan, "result": result, "descriptive": descriptive,
              "paired": paired, "simulation_only": plan["runtime"]["simulation_only"],
              "promotion_allowed": False}
    prefix = HERE / (name + "-20260915-" + stage)
    evidence_path = prefix.with_suffix(".json")
    write(evidence_path, report)

    policy_name = "wave_local_balance" if wave_local else "supported_siege"
    evaluated_path = HERE / "hypotheses" / (policy_name + ".evaluated.ir.json")
    parent = read(evaluated_path if evaluated_path.exists() else directory / "candidate/policy.ir.json")
    if compile_policy(parent).encode() != (directory / "candidate/policy.bas").read_bytes():
        raise ValueError("Existing IR evidence belongs to a different executable")
    policy = deepcopy(parent)
    counts = {k: descriptive[k]["all"]["wins"] for k in rows}
    verdict = "passed the fixed local gate" if result["passed"] else "failed the fixed local gate"
    claim = (f"On {plan['runtime']['runtime_identity']}, {stage} {verdict}: "
             f"candidate {counts['candidate']}/{len(plan[stage])}, unchanged v2 {counts['parent']}, "
             f"default {counts['baseline']}. The mechanism diagnostic changed in "
             f"{result['activation']['games']} cases. All {result['games']} full replays matched. "
             "This is an announcement-based simulation; published-release and hosted incumbent "
             "superiority remain unconfirmed. These results alone do not qualify the policy for promotion.")
    evidence = {"artifact": str(evidence_path.relative_to(HERE.parents[3])),
                "sha256": digest(evidence_path.read_bytes())}
    policy["belief"]["claims"][belief] = {
        "claim": claim, "status": "requires_review", "evidence": [evidence]}
    policy["update"]["revision"] += 1
    policy["update"]["parent"] = digest(parent)
    policy["update"]["change"] = {"origin": "evaluation_feedback", "stage": stage,
                                    "gate_passed": result["passed"], "promotion_allowed": False}
    policy["update"]["evidence"].append(evidence)
    source = compile_policy(policy)
    if source.encode() != (directory / "candidate/policy.bas").read_bytes():
        raise ValueError("Evidence feedback changed evaluated BASIC")
    if extract(source, policy) != policy:
        raise ValueError("Feedback broke the IR round trip")
    write(evaluated_path, policy)
    (HERE / "hypotheses" / (policy_name + ".evaluated.bas")).write_text(source)

    table = []
    for team in ["all", "Red", "Blue"]:
        for arm in ["parent", "candidate", "baseline"]:
            x = descriptive[arm][team]
            table.append(f"<tr><td>{team}</td><td>{arm}</td><td>{x['wins']}/{x['n']}</td>"
                         f"<td>{x['timeouts']}</td><td>{x['mean_level']:.2f}</td>"
                         f"<td>{x['structure_intent_share']:.1%}</td>"
                         f"<td>{x['deaths_per_1000_decisions']:.2f}</td></tr>")
    html = ("<!doctype html><meta charset='utf-8'><title>GOTA " + title + "</title>"
            "<style>body{font:16px system-ui;max-width:1000px;margin:40px auto;padding:0 24px;line-height:1.5}"
            "table{border-collapse:collapse;width:100%}td,th{padding:8px;text-align:left;border-bottom:1px solid #ccc}"
            "code{overflow-wrap:anywhere}</style><h1>" + title + ": " + escape(stage) + "</h1>"
            "<p>" + escape(claim) + "</p><table><tr><th>Side</th><th>Policy</th><th>Wins</th>"
            "<th>Draws</th><th>Mean final level</th><th>Structure target share</th><th>Deaths / 1000 decisions</th>"
            "</tr>" + "".join(table) + "</table><p>Structure target share measures attack intent, "
            "not damage dealt. Side samples are small. Win changes compare the same independent seed and seat.</p>"
            "<p>" + escape(rule) + "</p>"
            "<p>IR evidence feedback preserved the exact tested BASIC: <code>" + plan["sources"]["candidate"]
            + "</code>.</p><p><a href='" + evidence_path.name + "'>Full evidence and preregistered gates</a></p>")
    prefix.with_suffix(".html").write_text(html)
    return {"claim": claim, "report": str(prefix.with_suffix('.html')), "descriptive": descriptive,
            "paired": paired, "activation": result["activation"], "passed": result["passed"]}


if __name__ == "__main__":
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--stage", choices=["screen", "validation"], default="screen")
    args = parser.parse_args()
    print(json.dumps(finish(args.directory, args.stage), indent=2))
