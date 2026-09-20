"""Resume a preregistered, one-change-at-a-time local hypothesis study.

Discovery covers every seat on six seeds. A qualifying winner is frozen before
120 independent validation seeds, with balanced classes. Candidate, Duelist,
and default-baseline arms use identical seed/seat assignments and nine default
policies. Only complete games are compared. No hosted requests are launched.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from datetime import datetime, timezone
from math import comb
from pathlib import Path
import random

from binding import CONTRACTS
from policy_ir import HERE, ROOT, bundle, compile_policy, digest, read, refresh_grounding, write
from research import run_episode


HYPOTHESES = {
    "recovery": {
        "belief": "B_recovery", "goal": "G_recovery", "rule": "R1", "skill": "observe",
        "description": "Temporarily exclude a target after 72 stationary, unchanged-target-HP ticks; retry after 240 ticks.",
        "claim": "Unproductive pursuits persist because weighted_enemy has no progress memory. Bounded exclusion may restore useful movement and fort pressure; stationary combat or allied damage can confuse the progress proxy.",
    },
    "structures": {
        "belief": "B_structure", "goal": "G_structure", "rule": "R1", "skill": "observe",
        "description": "Set exposed-structure distance weight to 1, equal to heroes, while footmen retain weight 4.",
        "claim": "Hero preference can divert attention from nearby exposed objectives. Equal structure priority may convert pressure into fort wins, but can increase tower exposure.",
    },
    "single_heal": {
        "belief": "B_single_heal", "goal": "G_single_heal", "rule": "E1", "skill": "sustain",
        "description": "Attempt a ration only if the elixir purchase did not succeed; preserve all other sustain rules.",
        "claim": "The independent elixir and ration attempts can buy both in one decision, spending 80 gold and occupying two slots. Buying one may preserve equipment capacity, but can reduce immediate survival.",
    },
}


def make_variant(parent, name):
    hypothesis = HYPOTHESES[name]
    policy = deepcopy(parent)
    policy["id"] = "gota_duelist_" + name
    if name == "structures":
        policy["skill"]["observe"]["parameters"]["structure_weight"] = 1
    else:
        operator = "weighted_enemy_recovery" if name == "recovery" else "buy_single_heal"
        policy["skill"][hypothesis["skill"]] = {"operator": operator, "parameters": CONTRACTS[operator].defaults()}
    for claim in policy["belief"]["claims"].values():
        claim["claim"] = "Ancestor Duelist evidence; not evidence for this new candidate. " + claim["claim"]
        claim["status"] = "requires_review"
    policy["belief"]["claims"][hypothesis["belief"]] = {
        "claim": hypothesis["claim"], "status": "untested", "evidence": []}
    policy["goal"][hypothesis["goal"]] = {"preference": hypothesis["description"], "provenance": "authored"}
    for rule in policy["strategy"]:
        if rule["id"] == hypothesis["rule"]:
            rule["for"].append(hypothesis["goal"])
    policy["update"] = {
        "revision": parent["update"]["revision"] + 1, "parent": digest(parent),
        "change": {"origin": "preregistered_hypothesis", "hypothesis": name,
                   "description": hypothesis["description"]},
        "needs_review": ["belief/" + key for key in policy["belief"]["claims"]],
        "evidence": parent["update"]["evidence"],
    }
    refresh_grounding(policy)
    return policy


def completed_case(binary, baseline, source, seed, slot, directory):
    result_path = directory / "result.json"
    if result_path.exists():
        result = read(result_path)
        if (result["seed"] != seed or result["candidate_slots"] != [slot]
                or result["candidate_sha256"] != digest(source.read_bytes())
                or result["baseline_sha256"] != digest(baseline.read_bytes())
                or result["command"][0] != str(binary)
                or result["replay_sha256"] != digest((directory / "episode.replay").read_bytes())
                or result["trace_sha256"] != digest((directory / "episode.replay.trace.jsonl").read_bytes())):
            raise ValueError(f"cached case does not match frozen inputs: {directory}")
        return result
    if directory.exists():
        # Preserve interrupted artifacts; never silently treat them as evidence.
        directory.rename(directory.with_name(directory.name + ".incomplete-" + datetime.now().strftime("%H%M%S%f")))
    return run_episode(binary, baseline, source, seed, {slot}, directory)


def run_arms(binary, baseline, sources, cases, directory, workers):
    results = {name: [] for name in sources}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        jobs = {pool.submit(completed_case, binary, baseline, source, case["seed"], case["slot"],
                            directory / name / f"seed-{case['seed']}-slot-{case['slot']}"): name
                for name, source in sources.items() for case in cases}
        for index, future in enumerate(as_completed(jobs), 1):
            results[jobs[future]].append(future.result())
            print(f"{directory.name}: {index}/{len(jobs)} complete", flush=True)
    return {name: sorted(rows, key=lambda r: (r["seed"], r["candidate_slots"])) for name, rows in results.items()}


def sign_p(positive, negative):
    total = positive + negative
    return sum(comb(total, k) for k in range(positive, total + 1)) / 2**total


def paired(control, candidate):
    def index(rows):
        result = {(row["seed"], row["candidate_slots"][0]): row for row in rows}
        if not rows or len(result) != len(rows) or any(len(r["candidate_slots"]) != 1 for r in rows):
            raise ValueError("empty, duplicated, or multi-seat case")
        return result
    before, after = index(control), index(candidate)
    if before.keys() != after.keys():
        raise ValueError("unmatched seed/seat assignments")
    pairs = []
    for seed, slot in sorted(before):
        left, right = before[seed, slot], after[seed, slot]
        a, b = left["heroes"][slot], right["heroes"][slot]
        if a["class"] != b["class"] or a["team"] != b["team"] or left["baseline_sha256"] != right["baseline_sha256"]:
            raise ValueError("unmatched class, team, or surrounding policies")
        pairs.append({"seed": seed, "slot": slot, "class": a["class"], "team": a["team"],
                      "control": {**a, "timeout": left["timeout"]},
                      "candidate": {**b, "timeout": right["timeout"]},
                      "delta": b["score"] - a["score"]})
    return {"cases": len(pairs), "wins": sum(p["candidate"]["score"] for p in pairs),
            "control_wins": sum(p["control"]["score"] for p in pairs),
            "gain": sum(p["delta"] for p in pairs) / len(pairs), "pairs": pairs}


def confirmatory_gate(summary, minimum_gain):
    rows = summary["pairs"]
    if len({p["seed"] for p in rows}) != len(rows):
        raise ValueError("validation requires one candidate seat per independent seed")
    positive = sum(p["delta"] > 0 for p in rows)
    negative = sum(p["delta"] < 0 for p in rows)
    counts = [sum(p["class"] == c for p in rows) for c in range(10)]
    p_value = sign_p(positive, negative)
    return {"independent_seeds": len(rows), "class_counts": counts,
            "positive_pairs": positive, "negative_pairs": negative,
            "gain": summary["gain"], "one_sided_exact_p": p_value,
            "alpha": 0.025, "minimum_gain": minimum_gain,
            "passed": len(rows) == 120 and counts == [12] * 10
                      and summary["gain"] >= minimum_gain and p_value < 0.025}


def activation(summary, name):
    rows = summary["pairs"]
    def rate(arm, metric):
        return sum(metric(p[arm]) for p in rows) / sum(p[arm]["decisions"] for p in rows)
    if name == "recovery":
        counts = [p["candidate"]["recovery_activations"] or 0 for p in rows]
        classes = sorted({p["class"] for p, count in zip(rows, counts) if count > 0})
        return {"activations": sum(counts), "classes_activated": classes, "observed": len(classes) >= 3}
    if name == "structures":
        metric = lambda h: h["target_kinds_after_tick"][1] + h["target_kinds_after_tick"][4]
        before, after = rate("control", metric), rate("candidate", metric)
    else:
        metric = lambda h: h["double_heal_attempt_ticks"]
        before, after = rate("control", metric), rate("candidate", metric)
    return {"control_rate": before, "candidate_rate": after,
            "observed": after > before if name == "structures" else after < before}


def regression_sweep(summary):
    metrics = {
        "win": (lambda h: h["score"], 1),
        "timeout": (lambda h: int(h["timeout"]), -1),
        "deaths_per_1000_decisions": (lambda h: 1000 * h["deaths"] / max(1, h["decisions"]), -1),
        "final_equipment": (lambda h: h["equipment_count"], 1),
        "final_level": (lambda h: h["level"], 1),
    }
    comparisons = []
    for group in ["all", *range(10)]:
        rows = [p for p in summary["pairs"] if group == "all" or p["class"] == group]
        for metric, (value, direction) in metrics.items():
            deltas = [value(p["candidate"]) - value(p["control"]) for p in rows]
            worse, better = sum(d * direction < 0 for d in deltas), sum(d * direction > 0 for d in deltas)
            p_value = sign_p(worse, better)
            comparisons.append({"class": group, "metric": metric, "n": len(rows),
                                "mean_delta": sum(deltas) / len(deltas), "adverse_sign_p": p_value,
                                "flagged": p_value < 0.05 / 55})
    return {"threshold": 0.05 / 55, "flagged": [r for r in comparisons if r["flagged"]],
            "comparisons": comparisons,
            "limitations": "Per-class n=12 has low power; end-of-game equipment/levels and death rates depend on game length."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    if not 1 <= args.workers <= 8:
        parser.error("workers must be in 1..8")
    output, binary = args.output.resolve(), args.binary.resolve()
    baseline = HERE.parent / "base.bas"
    output.mkdir(parents=True, exist_ok=True)
    if not (output / "plan.json").exists():
        parent = read(HERE / "duelist.ir.json")
        bundle(parent, output / "parent")
        for name in HYPOTHESES:
            bundle(make_variant(parent, name), output / name)
        slots = list(range(10)) * 12
        random.Random(9102026).shuffle(slots)
        plan = {"created_at": datetime.now(timezone.utc).isoformat(), "game_version": "2026.9.10.3",
                "published_commit": "27a8fd51eadf48d2f69591cca4287074e9058e8f",
                "binary_sha256": digest(binary.read_bytes()), "baseline_sha256": digest(baseline.read_bytes()),
                "sources": {name: digest((output / name / "policy.bas").read_bytes()) for name in ["parent", *HYPOTHESES]},
                "selection_cases": [{"seed": s, "slot": slot} for s in range(61000,61006) for slot in range(10)],
                "validation_cases": [{"seed": 62000+i, "slot": slot} for i, slot in enumerate(slots)],
                "selection_rule": "At least four added wins over parent plus observed mechanism; choose most wins, tie order recovery/structures/single_heal.",
                "validation_rule": "One frozen winner; 120 independent seeds, 12/class. Versus parent: gain>=0.05 and exact paired p<0.025. Versus baseline: gain>=0.10 and p<0.025. No flagged regression in either 55-test sweep. Both wins gates must pass.",
                "stop_rule": "Do not inspect validation aggregates early, change N, tune on validation cases, or validate another winner in this study.",
                "scope": "Local baseline-filled rosters only. No live-field superiority claim. All three suggestions receive full discovery experiments; only a qualifying winner gets confirmation."}
        write(output / "plan.json", plan)
    plan = read(output / "plan.json")
    if digest(binary.read_bytes()) != plan["binary_sha256"] or digest(baseline.read_bytes()) != plan["baseline_sha256"]:
        raise ValueError("runtime or baseline changed since preregistration")
    sources = {name: output / name / "policy.bas" for name in plan["sources"]}
    for name, source in sources.items():
        if digest(source.read_bytes()) != plan["sources"][name]:
            raise ValueError("frozen candidate bytes changed")
    discovery = run_arms(binary, baseline, sources, plan["selection_cases"], output / "discovery", args.workers)
    screens = {}
    for name in HYPOTHESES:
        summary = paired(discovery["parent"], discovery[name])
        summary["activation"] = activation(summary, name)
        summary["qualifies"] = summary["wins"] - summary["control_wins"] >= 4 and summary["activation"]["observed"]
        screens[name] = summary
    write(output / "discovery.json", screens)
    eligible = [name for name in HYPOTHESES if screens[name]["qualifies"]]
    if not eligible:
        write(output / "result.json", {"verdict": "no_qualifying_discovery_candidate", "discovery": screens,
                                      "hosted_evaluation_eligible": False, "validation": None})
        print("No discovery candidate qualified for validation", flush=True)
        return
    winner = max(eligible, key=lambda name: screens[name]["wins"])
    selected = {"name": winner, "source_sha256": plan["sources"][winner], "frozen_before_validation": True}
    if (output / "selected.json").exists() and read(output / "selected.json") != selected:
        raise ValueError("frozen selection changed")
    write(output / "selected.json", selected)
    print(f"Frozen validation candidate: {winner}", flush=True)
    arms = run_arms(binary, baseline, {"parent": sources["parent"], "candidate": sources[winner], "baseline": baseline},
                    plan["validation_cases"], output / "validation", args.workers)
    comparisons = {name: paired(arms[name], arms["candidate"]) for name in ["parent", "baseline"]}
    gates = {name: confirmatory_gate(summary, .05 if name == "parent" else .10) for name, summary in comparisons.items()}
    sweeps = {name: regression_sweep(summary) for name, summary in comparisons.items()}
    passed = all(g["passed"] for g in gates.values()) and not any(s["flagged"] for s in sweeps.values())
    write(output / "result.json", {"verdict": "passed_local_confirmation" if passed else "local_confirmation_inconclusive",
                                  "winner": winner, "source_sha256": selected["source_sha256"], "discovery": screens,
                                  "validation": comparisons, "gates": gates, "regressions": sweeps,
                                  "hosted_evaluation_eligible": passed})
    print({"winner": winner, "gates": gates, "hosted_evaluation_eligible": passed}, flush=True)


if __name__ == "__main__":
    main()
