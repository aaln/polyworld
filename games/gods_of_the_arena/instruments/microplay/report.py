"""Export reusable semantic research, action records, and evaluated policy IR."""
from collections import defaultdict
from copy import deepcopy
import gzip
import json
from pathlib import Path
import shutil

import ir_v4 as ir
from study import write

DOC = ir.ROOT / "docs/microplay/2026-09-20"
BUNDLE = ir.ROOT / "examples/gods_of_the_arena/players/ir/forks/microplay"
LAYERS = ("situation", "belief", "goal", "skill", "strategy", "execution", "update")
STUDIES = {"v1": "microplay-20260920", "v2": "microplay-v2-20260920",
           "team": "microplay-team-20260920", "v3": "microplay-v3-20260920",
           "v4": "microplay-v4-20260920"}


def ref(path):
    return {"artifact": str(path.relative_to(ir.ROOT)), "sha256": ir.sha(path)}


def export():
    DOC.mkdir(parents=True, exist_ok=True)
    BUNDLE.mkdir(parents=True, exist_ok=True)
    evidence = DOC / "evidence"
    evidence.mkdir(exist_ok=True)
    studies = {}
    for key, name in STUDIES.items():
        source = ir.ROOT / "tmp/gota-ir" / name
        dest = evidence / key
        dest.mkdir(exist_ok=True)
        for pattern in ("plan.json", "*-result.json", "*-summary.json", "*-audit.json",
                        "equivalence.json", "budget-stress.json", "*.jsonl.gz"):
            for path in source.glob(pattern):
                if "-audit.jsonl.gz" not in path.name:
                    shutil.copy2(path, dest / path.name)
        if (source / "integration/result.json").exists():
            shutil.copy2(source / "integration/result.json", dest / "integration-result.json")
            shutil.copy2(source / "integration/plan.json", dest / "integration-plan.json")
        plan = json.loads((dest / "plan.json").read_text())
        outcomes = {p.name: json.loads(p.read_text()) for p in dest.glob("*-result.json")}
        studies[key] = {"schema": "gota-experiment-ir/1", "id": name,
            "situation": {"encounters": plan["unit"], "scope": plan["limits"]},
            "belief": {"hypotheses": plan["objective"], "measured_results": outcomes},
            "goal": {"primary": plan["objective"], "metrics": plan["metrics"]},
            "skill": {"arms": plan["policies"]}, "strategy": {"prospective_gates": plan["selection"]},
            "execution": {"plan": ref(dest / "plan.json"), "runtime": plan["source"],
                          "artifacts": [ref(p) for p in sorted(dest.iterdir())]},
            "update": {"parent": plan.get("predecessor", plan.get("implementation_parent")),
                       "evidence_status": "retained_including_failures"}}
        write(evidence / (key + ".ir.json"), studies[key])

    v3 = evidence / "v3"
    v4 = evidence / "v4"
    result = json.loads((v3 / "holdout-result.json").read_text())
    assert result["selected"] == "combined"
    assert json.loads((v3 / "holdout-audit.json").read_text())["exact"]
    assert json.loads((v4 / "equivalence.json").read_text())["exact_state_and_outcomes"]
    integration = json.loads((v4 / "integration-result.json").read_text())
    assert integration["all_replays_exact"]

    decision_count = 0
    decision_path = DOC / "decisions.ir.jsonl.gz"
    with gzip.open(v4 / "holdout.jsonl.gz", "rt") as raw, gzip.open(decision_path, "wt") as output:
        for line in raw:
            encounter = json.loads(line)
            if not encounter["id"].endswith("/combined"):
                continue
            for event in encounter["decisions"]:
                decision = event["decision"]
                if decision["refinement"] <= 0 or decision["selected"] == decision["original"]:
                    continue
                obs = event["observation"]
                target = next(o for o in obs["objects"] if o["id"] == decision["selected"])
                finishing = target["hp"] <= obs["selfAttackDamage"]
                node = {"schema": "gota-action-ir/1", "id": f"{encounter['id']}/{event['tick']}/{event['slot']}",
                    "situation": {"public_observation": obs, "visibility": "host-filtered; no hidden state"},
                    "belief": {"target_alive_observed": target["alive"], "hp_at_most_one_basic_hit": finishing,
                               "ally_intent_is_not_execution": True},
                    "goal": ["secure_reachable_finish" if finishing else "help_vulnerable_ally"],
                    "skill": {"operator": "microplay_local_target_v4", "branch": "finish" if finishing else "assist"},
                    "strategy": {"selected_target": decision["selected"], "parent_target": decision["original"],
                                 "observed_ally_target": decision["ally_intent"], "priority": 2 if finishing else 1},
                    "execution": event["execution"] | {"instructions": event["instructions"], "work": event["work"]},
                    "update": {"outcome_scope": "Outcome is measured for the entire encounter, not attributed to this single decision.",
                               "encounter_metrics": encounter["metrics"], "causal_claim": None}}
                assert set(LAYERS) <= node.keys()
                output.write(json.dumps(node, separators=(",", ":")) + "\n")
                decision_count += 1

    rows = json.loads((v3 / "holdout-summary.json").read_text())
    strata = {}
    for dimension in ("automatic_spells", "family", "class", "side"):
        strata[dimension] = {}
        for value in sorted({r[dimension] for r in rows}):
            strata[dimension][str(value)] = {
                arm: {metric: sum(r[metric] for r in rows if r["arm"] == arm and r[dimension] == value)
                      for metric in ("enemy_deaths", "ally_deaths", "basic_hits", "refined_decisions")}
                for arm in ("parent", "finish", "combined")}

    semantics = {"schema": "gota-microplay-research-ir/1", "id": "gota_microplay_20260920",
        "situation": {
            "game_version": "2026.9.16.5", "source": "f2ab9598d8f8001b6beae3e66404e341770c803f",
            "units": {"tick_hz": 24, "world_units_per_tile": 60000,
                      "object_positions": "integer tiles", "selfAttackRange": "world units"},
            "observability": ["Self data at decision start; visible object queries through real host.",
                "Unseen enemies are unknown. Zero objectTarget can hide an unobserved target.",
                "No private target HP maxima, enemy cooldowns, future HP or intention inference."],
            "mechanics": ["walkTo clears attack intent even before pathfinding acceptance.",
                "Attack windup reaches damage at45percent of class attack duration.",
                "selfAttacksLanded is a hit event; target selection or an accepted command is not a hit.",
                "Target selection also affects automatic offensive spells; spell modes must be stratified.",
                "automatic_spells=false disables automatic casts only. Explicit casts from the unchanged parent remain possible; this is not a pure basic-attack experiment.",
                "HP loss per tick is a net damage proxy and can mask simultaneous healing."],
            "erratum": "Earlier prototypes treated100000worldunits as a tile. ActualWorldScale=60000. V2/v3 thus used60percent of true reach. V4 makes this tested conservative setting explicit; it does not expand range."},
        "belief": {
            "finishing": {"status": "supported_locally", "claim": "Reach-bounded finishing improved the prospectively selected160case v2holdout.",
                          "evidence": ref(evidence / "v2/holdout-result.json")},
            "unguarded_assistance": {"status": "rejected", "claim": "Overall survival improvement masked two additional automatic-spell deaths versus finishing in the cooperative confirmation.",
                          "evidence": ref(evidence / "team/cooperation-result.json")},
            "guarded_assistance": {"status": "supported_locally", "claim": "Guarded assistance reduced deaths beyond finishing on160fresh v3cases; additional survival gain occurred in the manual-spell stratum. Automatic-spell survival matched finishing.",
                          "evidence": ref(v3 / "holdout-result.json")},
            "field_strength": {"status": "untested", "claim": "No live or general full-game improvement established. Ten final normal integration games activated zero refinements."}},
        "goal": {"primary": "Better individual and cooperative local combat; not fort-win optimization.",
                 "order": ["ally survival with spell-mode guard", "enemy elimination without sacrificing allies", "execution validity"]},
        "skill": {"binding": "microplay_local_target_v4", "parameters": {"finish": 1, "assist": 1,
                  "ally_tiles": 8, "range_percent": 60, "object_limit": 48},
                  "contract": ir.binding.CONTRACTS["microplay_local_target_v4"].meaning,
                  "extension_point": "After observe and before attack; reads/writes candidate; issues no commands."},
        "strategy": {"priority": ["observable reachable one-hit finisher", "lower-ID ally assistance with self-threat guard", "parent target"],
                     "fallback": "Original selection when crowded, unavailable, hidden, dead, friendly, distant, or structure-targeted.",
                     "decision_records": ref(decision_path), "refined_decisions": decision_count},
        "execution": {"experiments": [ref(evidence / (key + ".ir.json")) for key in STUDIES],
                      "heldout": result, "strata": strata, "final_integration": integration,
                      "equivalence": ref(v4 / "equivalence.json")},
        "update": {"status": "qualified_local_skill_library", "live_champions_changed": False,
                   "lineage": ["v1inactive", "v2finishing_passed_assistance_rejected", "v3guarded_teamwork_passed",
                               "v4explicit_units_and_bounded_cost_equivalent"],
                   "next_hypotheses": ["Measure naturally occurring close-combat opportunity coverage before deployment.",
                       "Test class-specific spell/target interactions and larger team fights prospectively.",
                       "Develop melee-specific spacing and peel skills; do not infer improvement for every class.",
                       "Test broader reach percentages as new hypotheses, preserving60percent control."]}}
    assert set(LAYERS) <= semantics.keys()
    write(DOC / "research.ir.json", semantics)

    manifests = {}
    for arm, name in (("combined", "policy"), ("finish", "finish")):
        source_dir = ir.ROOT / "tmp/gota-ir/microplay-v4-20260920/policies"
        policy = json.loads((source_dir / (arm + ".ir.json")).read_text())
        policy["belief"]["claims"]["B_microplay"] = {
            "claim": "Qualified in constructed six-second encounters only. Final v4 reproduces v3 state/outcome sequences. Full-game benefit unproven; integration activated zero refinements.",
            "status": "supported", "evidence": [ref(DOC / "research.ir.json"), ref(v4 / "equivalence.json")]}
        policy["update"]["needs_review"] = ["Live generalization and natural opportunity coverage remain untested."]
        policy["update"]["evidence"].append(ref(DOC / "research.ir.json"))
        ir.compiler.refresh_grounding(policy)
        basic = ir.compiler.compile_policy(policy)
        assert basic == (source_dir / (arm + ".bas")).read_text()
        assert ir.compiler.extract(basic, policy) == policy
        write(BUNDLE / (name + ".ir.json"), policy)
        (BUNDLE / (name + ".bas")).write_text(basic)
        manifests[name] = {"ir_sha256": ir.compiler.digest(policy), "basic_sha256": ir.sha(BUNDLE / (name + ".bas")),
                           "roundtrip": True, "tested_basic_unchanged": True}
    write(BUNDLE / "manifest.json", {"schema": "gota-microplay-bundle/1", "policies": manifests,
          "research": ref(DOC / "research.ir.json"), "compiler_parent": ref(ir.PARENT / "compiler.zip"),
          "contracts": [ref(Path(__file__).with_name(name)) for name in ("ir.py", "ir_v2.py", "ir_v3.py", "ir_v4.py")]})

    totals = result["totals"]
    table = "\n".join(f"| {label} | {totals[arm]['enemy_deaths']} | {totals[arm]['ally_deaths']} |" for arm, label in
                       (("parent", "Original"), ("finish", "Finishing only"), ("combined", "Finishing + guarded assistance")))
    text = f"""# Gota microplay: individual finishing and cooperative target choice

The new local combat skill reduced allied deaths **60→50** and increased enemy eliminations **239→243** across 160 matched held-out six-second scenarios. Assistance reduced deaths beyond finishing alone, **56→50**. These are constructed encounter results on pinned release 2026.9.16.5, not a live-field or fort-win claim.

| Policy | Enemy eliminations | Allied deaths |
| --- | ---: | ---: |
{table}

![Held-out combat outcomes, with allied deaths split by automatic casting mode](heldout.png)

The skill finishes a wounded visible enemy already inside its conservative reach bound, then considers the target of a nearby lower-ID ally. It keeps self-defense when the current enemy targets self, unless that ally has less than half self's HP. Lower-ID leadership prevents reciprocal target-following loops. Structures and macro choices keep their existing behavior. Crowded observations fall back to the parent to bound VM cost.

Automatic spells matter: unguarded assistance reduced total deaths but caused two extra Crossbowman deaths versus finishing. That variant was rejected. The guard eliminated that regression in fresh scenarios. In the final holdout, the **additional assistance benefit occurred with manual spells** (12→6 allied deaths); with automatic spells, assistance matched finishing (44 deaths each, versus 48 for the original). Do not claim an additional teamwork survival gain in the automatic-spell stratum.

The study covered all ten class assignments on both colors, four encounter families, automatic/manual spells, fixed opponents, and two-subject crossfire. “Manual spells” means automatic casting is disabled; explicit casts from the unchanged parent remain possible. The original plan's suggestion that this isolates basic attacks was too strong. Mirrored colors and repeated trajectories are correlated; no independent-sample significance claim is made. Per-class, family, side and spell-mode counts are in the [research IR](research.ir.json). Raw public observations, per-tick world hashes, VM decisions, outcomes, frozen plans and failed experiments are retained under [evidence](evidence/).

An explicit units correction is retained: the engine uses 60,000 world units per tile. The earlier range expression accidentally used 60% of true reach. The final binding names this measured 60% setting and preserves its behavior, verified against **480 encounters / 69,120 tick hashes**. Wider reach is untested. The first inactive experiment and this explanation error remain in the lineage.

All original 1,864 experimental rollouts were repeated with exact observation/decision/state output. The final binding additionally matched 480 of those encounters after the units/budget refinement. Fifteen focused tests pass. **{integration['complete_games']} final normal games** completed with exact action replays and no VM errors; peak instructions were **{integration['max_instructions']}/20000**. Those games activated **{integration['refinements']} refinements**, so they establish runtime compatibility and baseline behavior only. Their repeated trajectories provide limited coverage.

Use the [evaluated executable policy IR](../../../examples/gods_of_the_arena/players/ir/forks/microplay/policy.ir.json), [generated BASIC](../../../examples/gods_of_the_arena/players/ir/forks/microplay/policy.bas), [action-level semantic records](decisions.ir.jsonl.gz), and [reproduction tools](../../../games/gods_of_the_arena/instruments/microplay/README.md). The policy and research each use situation, belief, goal, skill, strategy, execution and update layers. Live champions and the existing research daemon were not changed.
"""
    (DOC / "README.md").write_text(text)
    print(json.dumps({"report": str(DOC / "README.md"), "policy": str(BUNDLE / "policy.ir.json"),
                      "semantic_decisions": decision_count, "policies": manifests}, indent=2))


if __name__ == "__main__":
    export()
