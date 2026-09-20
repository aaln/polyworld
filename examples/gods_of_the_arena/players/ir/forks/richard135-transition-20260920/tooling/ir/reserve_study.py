"""Predeclared equipment-cap experiment; local discovery gates fresh confirmation."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import random
import subprocess

from hypothesis_study import confirmatory_gate, paired, regression_sweep, run_arms
from policy_ir import HERE, ROOT, bundle, compile_policy, digest, read, refresh_grounding, write
from study_report import class_summary, load_cases


def candidate():
    parent = read(HERE / "duelist.ir.json")
    policy = deepcopy(parent)
    policy["id"] = "gota_duelist_reserve_consumables"
    policy["skill"]["equipment"] = {"operator": "buy_equipment_reserved", "parameters": {"equipment_cap": 4}}
    for claim in policy["belief"]["claims"].values():
        claim["claim"] = "Ancestor Duelist evidence, not candidate evidence. " + claim["claim"]
        claim["status"] = "requires_review"
    policy["belief"]["claims"]["B_reserve"] = {
        "claim": "Six permanent items can prevent emergency healing purchases. Capping gear at four may preserve consumable access and improve wins, at the cost of equipment stats. Other consumables can still compete for space.",
        "status": "untested", "evidence": []}
    policy["goal"]["G_reserve"] = {"preference": "Keep at least two of six slots free of permanent equipment for healing and mana.", "provenance": "authored"}
    next(r for r in policy["strategy"] if r["id"] == "E2")["for"].append("G_reserve")
    policy["update"] = {"revision": parent["update"]["revision"]+1, "parent": digest(parent),
                        "change": {"origin": "preregistered_hypothesis", "hypothesis": "reserve_consumables", "equipment_cap": 4},
                        "needs_review": ["belief/"+key for key in policy["belief"]["claims"]],
                        "evidence": parent["update"]["evidence"]}
    refresh_grounding(policy)
    return policy


def purchase_audit(binary, replay, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    replay_hash = digest(replay.read_bytes())
    binary_hash = digest(binary.read_bytes())
    if destination.exists():
        result = read(destination)
        if result["replay_sha256"] != replay_hash or result["binary_sha256"] != binary_hash:
            raise ValueError("purchase audit inputs changed")
        return result
    proc = subprocess.run([str(binary), "--replay", str(replay)], cwd=ROOT,
                          capture_output=True, text=True, timeout=180, check=True)
    result = json.loads(proc.stdout.splitlines()[-1])
    if result["hash_mismatches"] != 0:
        raise ValueError("purchase audit state mismatch")
    result.update(replay_sha256=replay_hash, binary_sha256=binary_hash)
    write(destination, result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--auditor", type=Path, required=True)
    args = parser.parse_args()
    directory, binary, auditor = args.output.resolve(), args.binary.resolve(), args.auditor.resolve()
    baseline = HERE.parent / "base.bas"
    directory.mkdir(parents=True, exist_ok=True)
    if not (directory / "plan.json").exists():
        bundle(read(HERE / "duelist.ir.json"), directory / "parent")
        bundle(candidate(), directory / "candidate")
        slots = list(range(10))*12
        random.Random(91063000).shuffle(slots)
        plan = {"created_at": datetime.now(timezone.utc).isoformat(),
                "published_commit": "27a8fd51eadf48d2f69591cca4287074e9058e8f", "game_version": "2026.9.10.3",
                "binary_sha256": digest(binary.read_bytes()), "auditor_sha256": digest(auditor.read_bytes()),
                "baseline_sha256": digest(baseline.read_bytes()),
                "sources": {arm: digest((directory / arm / "policy.bas").read_bytes()) for arm in ["parent", "candidate"]},
                "selection_cases": [{"seed": seed, "slot": slot} for seed in range(63000,63006) for slot in range(10)],
                "validation_cases": [{"seed": 64000+i, "slot": slot} for i,slot in enumerate(slots)],
                "discovery_rule": "At least four added wins/60, with parent exceeding four gear in at least three classes and candidate never exceeding four. Audit every discovery replay for accepted purchases and every state hash.",
                "validation_rule": "120 independent seeds, 12/class. Gain>=.05 over Duelist and >=.10 over default, paired exact p<.025 each. No adverse Bonferroni flag for win, timeout, death rate or level overall/by class; equipment reduction is the intended tradeoff and reported separately.",
                "stop_rule": "No validation unless discovery qualifies; freeze one cap=4 candidate. No early stopping, additional candidates, reused seeds or changed thresholds. Hosted field comparison required before league promotion.",
                "authorization": "User 2026-09-10: update the policy on softmax league when ready; local-first preference persists."}
        write(directory / "plan.json", plan)
    plan = read(directory / "plan.json")
    for path,key in [(binary,"binary_sha256"),(auditor,"auditor_sha256"),(baseline,"baseline_sha256")]:
        if digest(path.read_bytes()) != plan[key]:
            raise ValueError("pinned runtime or baseline changed")
    sources = {arm: directory / arm / "policy.bas" for arm in plan["sources"]}
    for arm,path in sources.items():
        if digest(path.read_bytes()) != plan["sources"][arm]:
            raise ValueError("frozen source changed")
    run_arms(binary, baseline, sources, plan["selection_cases"], directory / "discovery", 8)
    # Reload and hash-check the whole completed batch before looking at means.
    rows = {arm: load_cases(directory,"discovery",arm,plan["selection_cases"],sha,plan["baseline_sha256"])
            for arm,sha in plan["sources"].items()}
    jobs = [(arm, case) for arm in sources for case in plan["selection_cases"]]
    def audit_job(job):
        arm,case = job
        name = f"seed-{case['seed']}-slot-{case['slot']}"
        return purchase_audit(auditor, directory / "discovery" / arm / name / "episode.replay",
                              directory / "purchase-audits" / arm / (name+".json"))
    with ThreadPoolExecutor(max_workers=8) as pool:
        audits = list(pool.map(audit_job,jobs))
    purchases = {arm: {"healing_rejected_no_space":0,"healing_purchases":0,"healing_gold":0,"equipment_purchases":0} for arm in sources}
    for (arm,case),audit in zip(jobs,audits):
        h = audit["heroes"][case["slot"]]
        purchases[arm]["healing_rejected_no_space"] += h["healing_rejected_no_space"]
        purchases[arm]["healing_purchases"] += sum(h["successful_purchases"][1:3])
        purchases[arm]["healing_gold"] += sum(h["gold_spent"][1:3])
        purchases[arm]["equipment_purchases"] += sum(h["successful_purchases"][5:])
        if arm == "candidate" and sum(h["successful_purchases"][5:]) > 4:
            raise ValueError("equipment cap violated")
    screen = paired(rows["parent"],rows["candidate"])
    activated = sorted({p["class"] for p in screen["pairs"] if p["control"]["equipment_count"] > 4})
    qualifies = screen["wins"]-screen["control_wins"] >= 4 and len(activated) >= 3
    report = {"plan":plan,"discovery":screen,"by_class":class_summary(screen),"purchases":purchases,
              "activated_classes":activated,"qualifies":qualifies,"validation":None,
              "hosted_evaluation_eligible":False,"completed_games":120,"invalid_games_scored":0,
              "state_hash_audited_games":120,"verdict":"discovery_inconclusive"}
    write(directory / "discovery.json",report)
    print(json.dumps({"candidate_wins":screen["wins"],"parent_wins":screen["control_wins"],"activated_classes":activated,"qualifies":qualifies}),flush=True)
    if qualifies:
        write(directory / "selected.json", {"source_sha256":plan["sources"]["candidate"],"frozen_before_validation":True})
        run_arms(binary,baseline,{**sources,"baseline":baseline},plan["validation_cases"],directory / "validation",8)
        held = {arm:load_cases(directory,"validation",arm,plan["validation_cases"],sha,plan["baseline_sha256"])
                for arm,sha in {**plan["sources"],"baseline":plan["baseline_sha256"]}.items()}
        comparisons = {arm:paired(held[arm],held["candidate"]) for arm in ["parent","baseline"]}
        gates = {arm:confirmatory_gate(s,.05 if arm=="parent" else .10) for arm,s in comparisons.items()}
        sweeps = {arm:regression_sweep(s) for arm,s in comparisons.items()}
        flags = {arm:[r for r in sweep["comparisons"] if r["metric"] != "final_equipment" and r["adverse_sign_p"] < .05/44]
                 for arm,sweep in sweeps.items()}
        passed = all(g["passed"] for g in gates.values()) and not any(flags.values())
        report.update(validation=comparisons,gates=gates,regressions=sweeps,blocking_regressions=flags,
                      regression_alpha=.05/44,hosted_evaluation_eligible=passed,completed_games=480,
                      verdict="passed_local_confirmation" if passed else "local_confirmation_inconclusive")
    write(directory / "result.json",report)
    destination = HERE / "reserve-20260910-result.json"
    write(destination,report)
    reference = {"artifact":str(destination.relative_to(ROOT)),"sha256":digest(destination.read_bytes())}
    original = read(directory / "candidate" / "policy.ir.json")
    updated = deepcopy(original)
    updated["belief"]["claims"]["B_reserve"].update(status="requires_review",evidence=[reference])
    updated["belief"]["claims"]["B_reserve_result"] = {
        "claim": f"Cap four: discovery {screen['wins']}/60 wins versus Duelist {screen['control_wins']}/60; six independent seed clusters. Equipment pressure activated in classes {activated}. Verdict {report['verdict']}. Accepted-purchase counts and per-class results are recorded. Local evidence does not establish hosted field superiority.",
        "status":"supported","evidence":[reference]}
    updated["belief"]["claims"]["B_reserve_capacity"] = {
        "claim": "All 120 discovery replays matched every state hash. Accepted-purchase audits: "
                 + json.dumps(purchases, sort_keys=True)
                 + ". The candidate never acquired more than four equipment items. This supports the capacity mechanism; consumables can still block each other and better win performance is unconfirmed.",
        "status":"supported","evidence":[reference]}
    updated["update"].update(parent=digest(original),revision=original["update"]["revision"]+1,
                             change={"origin":"experiment_feedback","verdict":report["verdict"]},
                             evidence=[*original["update"]["evidence"],reference])
    refresh_grounding(updated)
    if compile_policy(updated) != compile_policy(original):
        raise ValueError("evidence update changed the tested BASIC")
    if not (directory / "evaluated").exists():
        bundle(updated,directory / "evaluated")
    write(HERE / "hypotheses" / "reserve.ir.json",updated)
    (HERE / "hypotheses" / "reserve.bas").write_text(compile_policy(updated))
    print(json.dumps({"verdict":report["verdict"],"hosted_evaluation_eligible":report["hosted_evaluation_eligible"]}),flush=True)


if __name__ == "__main__":
    main()
