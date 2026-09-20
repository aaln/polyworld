"""Freeze, execute, and evaluate paired native microplay experiments."""
import argparse
from collections import defaultdict
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import ir

HERE = Path(__file__).resolve().parent
PINNED = ir.ROOT.parent / "polyworld-gota-clean-20260916-r5"
DEPS = ir.ROOT.parent / "gota-research-20260916/deps"
RELEASE = "f2ab9598d8f8001b6beae3e66404e341770c803f"
ARMS = ("parent", "finish", "assist", "combined")


def write(path, data):
    Path(path).write_text(json.dumps(data, indent=2) + "\n")


def actor(slot, cls, x, y, controller="fixed", **kwargs):
    return dict(slot=slot, **{"class": cls}, x=x, y=y,
                controller=controller, **kwargs)


def fixtures(partition):
    """Prospective layout variation, not a claim of independent match seeds."""
    classes = (1, 2, 6, 8) if partition == "discovery" else tuple(range(10))
    result = []
    for cls in classes:
        for side in (0, 1):
            for spells in (False, True):
                for family in ("finish_window", "ally_rescue", "duel_control", "crossfire"):
                    subject = side * 5 + 1
                    ally = side * 5
                    enemy = (1 - side) * 5
                    direction = 1 if side == 0 else -1
                    x, y = (56, 18) if partition == "discovery" else (62, 19)
                    # Holdout changes class coverage, geometry, HP, and initiative.
                    dy = 1 if partition == "discovery" else -1
                    weak = 14 if partition == "discovery" else 19
                    actors = [actor(subject, cls, x, y, "subject")]
                    if family == "finish_window":
                        actors += [actor(enemy, 0, x + direction * 2, y, target=subject),
                                   actor(enemy + 1, 1, x + direction * 3, y + dy,
                                         "fixed", target=subject, hp=weak)]
                    elif family == "ally_rescue":
                        actors += [actor(ally, 0, x + direction * 2, y + 2 * dy,
                                         target=enemy + 1, hp=90 if partition == "discovery" else 110),
                                   actor(enemy, 0, x + direction * 2, y, target=subject),
                                   actor(enemy + 1, 4, x + direction * 3, y + 2 * dy,
                                         target=ally, hp=100 if partition == "discovery" else 125)]
                    elif family == "duel_control":
                        actors += [actor(enemy, 0, x + direction * 2, y + dy, target=subject)]
                    else:
                        actors += [actor(ally, 1, x, y + 2 * dy, "subject"),
                                   actor(enemy, 4, x + direction * 2, y, target=subject),
                                   actor(enemy + 1, 6, x + direction * 3, y + 2 * dy,
                                         target=ally)]
                    key = f"{partition}/{family}/class{cls}/side{side}/spells{int(spells)}"
                    result.append({"id": key, "family": family, "partition": partition,
                                   "class": cls, "side": side, "automatic_spells": spells,
                                   "seed": 910000 + len(result) + (1000 if partition == "holdout" else 0),
                                   "ticks": 144, "actors": actors})
    return result


def prepare(directory):
    directory.mkdir(parents=True, exist_ok=True)
    if (directory / "plan.json").exists():
        raise ValueError("Plan already frozen; use a new directory for a new experiment")
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PINNED, text=True).strip() == RELEASE
    # All tracked changes in the engine/runtime would invalidate this release pin.
    tracked = subprocess.check_output(["git", "diff", "HEAD", "--", "src", "examples/gods_of_the_arena",
                                       "coworld/dependencies.lock", "config.nims"], cwd=PINNED, text=True)
    assert not tracked, "Pinned runtime contains tracked edits"
    policies = ir.build(directory / "policies")
    staging = PINNED / "tmp/microplay"
    staging.mkdir(parents=True, exist_ok=True)
    shutil.copy2(HERE / "encounter.nim", staging / "encounter.nim")
    env = os.environ | {"POLYWORLD_DEPS": str(DEPS)}
    with (directory / "build.log").open("w") as log:
        subprocess.run(["nim", "c", "-d:headless", "-d:release", "--hints:off",
                        "-o:" + str(directory / "encounter"), str(staging / "encounter.nim")],
                       cwd=PINNED, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    plan = {
        "schema": "gota-microplay-study/1", "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "objective": "Improve local individual play and allied combat; no fort-win selection gate.",
        "game_version": "2026.9.16.5", "source": RELEASE, "runtime_root": str(PINNED),
        "parent_basic_sha256": ir.sha(ir.PARENT / "policy.bas"),
        "policies": policies,
        "instrument_sha256": {p.name: ir.sha(p) for p in (HERE / "ir.py", HERE / "study.py", HERE / "encounter.nim")},
        "binary_sha256": ir.sha(directory / "encounter"),
        "unit": "matched six-second encounter, same layout/classes/resources/seed/opponent controller",
        "discovery": fixtures("discovery"), "holdout": fixtures("holdout"),
        "selection": {
            "priority": ["no additional allied deaths overall or in either spell-mode stratum",
                         "strictly more enemy deaths", "higher enemy net HP loss as tie break"],
            "control": "duel_control must have identical complete state-hash sequences",
            "holdout": "Freeze at most one discovery winner; require same gates on untouched holdout.",
            "no_promotion": "This evaluates a local skill module, not full-game or league superiority."},
        "metrics": {
            "enemy_deaths": "All active enemy first deaths during the encounter; no respawn within 144ticks.",
            "ally_deaths": "Deaths of every active allied participant, including fixed-controller helpers.",
            "enemy_hp_loss": "Sum max(previous_HP-current_HP,0) per tick. A net damage proxy; simultaneous healing can mask damage.",
            "ally_hp_loss": "Same net HP loss proxy for all allied participants.",
            "basic_hits": "Actual subject selfAttacksLanded increments; engine counter, not command count.",
            "target_switches": "Changes between nonzero engine target intents, not cancelled swings.",
            "instruction_budget": "Real host maxInstructions=20000; work<=50000; failures invalidate experiment."},
        "limits": ["Constructed encounters, not randomly sampled competitive games.",
                   "Hero classes may be placed on either color to separate class from side.",
                   "Non-subject fixed controllers expose a known attack intent; they are not learned opponent replicas.",
                   "Automatic and manual spells are separate strata; manual spells isolate basic mechanics.",
                   "Pinned historical release; no claim that this is the current hosted release.",
                   "Initial state is constructed; audit is deterministic fixture replay, not a normal hosted replay."]}
    write(directory / "plan.json", plan)
    print(json.dumps({"frozen": str(directory / "plan.json"), "discovery_cases": len(plan["discovery"]),
                      "holdout_cases": len(plan["holdout"])}))


def metric(row, fixture):
    ours = [m for m in row["metrics"] if m["team"] == fixture["side"]]
    theirs = [m for m in row["metrics"] if m["team"] != fixture["side"]]
    return {"enemy_deaths": sum(m["deaths"] for m in theirs),
            "ally_deaths": sum(m["deaths"] for m in ours),
            "enemy_hp_loss": sum(m["damage_taken"] for m in theirs),
            "ally_hp_loss": sum(m["damage_taken"] for m in ours),
            "basic_hits": sum(m["basic_hits"] for m in ours if m["subject"]),
            "target_switches": sum(m["target_switches"] for m in ours if m["subject"]),
            "max_instructions": max(m["max_instructions"] for m in ours),
            "max_work": max(m["max_work"] for m in ours),
            "refined_decisions": sum(d["decision"]["refinement"] > 0 and
                                     d["decision"]["selected"] != d["decision"]["original"]
                                     for d in row["decisions"])}


def check_frozen(directory, plan):
    assert ir.sha(directory / "encounter") == plan["binary_sha256"]
    for name, expected in plan["instrument_sha256"].items():
        assert ir.sha(HERE / name) == expected, f"Frozen instrument changed: {name}"
    for name, hashes in plan["policies"].items():
        assert ir.sha(directory / "policies" / (name + ".bas")) == hashes["basic_sha256"]


def run(directory, partition, arms=None, audit=False):
    plan = json.loads((directory / "plan.json").read_text())
    check_frozen(directory, plan)
    if arms is None:
        if partition == "discovery":
            arms = ARMS
        else:
            selected = json.loads((directory / "discovery-result.json").read_text())["selected"]
            if selected is None:
                raise ValueError("No discovery qualifier; do not consume holdout")
            arms = ("parent", selected)
    cases = []
    for fixture in plan[partition]:
        for arm in arms:
            cases.append(fixture | {"id": fixture["id"] + "/" + arm,
                                    "policy": str(directory / "policies" / (arm + ".bas"))})
    suffix = "-audit" if audit else ""
    raw = directory / (partition + suffix + ".jsonl.gz")
    summary = directory / (partition + suffix + "-summary.json")
    if raw.exists() or summary.exists():
        raise ValueError("Evidence exists; refusing overwrite")
    request_path = directory / (partition + suffix + "-request.json")
    write(request_path, {"cases": cases})
    results = []
    with request_path.open() as request, gzip.open(raw, "wt") as output, (directory / (partition + suffix + ".stderr")).open("w") as errors:
        process = subprocess.Popen([str(directory / "encounter")], stdin=request,
                                   stdout=subprocess.PIPE, stderr=errors, text=True)
        for line in process.stdout:
            output.write(line)
            row = json.loads(line)
            case = cases[len(results)]
            assert row["id"] == case["id"] and row["ticks"] == case["ticks"] and row["vm_valid"]
            stats = metric(row, case)
            assert stats["max_instructions"] <= 20000 and stats["max_work"] <= 50000
            results.append({"id": row["id"], "arm": row["id"].split("/")[-1],
                            "family": case["family"], "side": case["side"], "class": case["class"],
                            "automatic_spells": case["automatic_spells"], **stats,
                            "state_sequence_sha256": hashlib.sha256(json.dumps(row["state_hashes"]).encode()).hexdigest(),
                            "trace_sha256": hashlib.sha256(line.encode()).hexdigest()})
            if len(results) % 16 == 0:
                print(f"{partition}{suffix}: {len(results)}/{len(cases)} encounters", flush=True)
        assert process.wait() == 0, (directory / (partition + suffix + ".stderr")).read_text()
    assert len(results) == len(cases), "Incomplete native run"
    write(summary, results)
    if audit:
        previous = json.loads((directory / (partition + "-summary.json")).read_text())
        assert results == previous, "Deterministic replay mismatch"
        write(directory / (partition + "-audit.json"), {"exact": True, "encounters": len(results),
              "ticks_compared": len(results) * 144, "full_observation_decision_and_state_sequences": True,
              "raw_sha256": ir.sha(raw), "plan_sha256": ir.sha(directory / "plan.json")})
    return results


def evaluate(directory, partition):
    rows = json.loads((directory / (partition + "-summary.json")).read_text())
    by_arm = defaultdict(list)
    for row in rows:
        by_arm[row["arm"]].append(row)
    sums = {}
    for arm, values in by_arm.items():
        sums[arm] = {key: sum(row[key] for row in values) for key in
                     ("enemy_deaths", "ally_deaths", "enemy_hp_loss", "ally_hp_loss", "basic_hits", "refined_decisions")}
        sums[arm]["encounters"] = len(values)
        sums[arm]["max_instructions"] = max(row["max_instructions"] for row in values)
    baseline = {r["id"].rsplit("/", 1)[0]: r for r in by_arm["parent"]}
    gates = {}
    for arm, values in by_arm.items():
        if arm == "parent":
            continue
        gates[arm] = {
            "more_enemy_deaths": sums[arm]["enemy_deaths"] > sums["parent"]["enemy_deaths"],
            "no_added_ally_deaths": sums[arm]["ally_deaths"] <= sums["parent"]["ally_deaths"],
            "spell_strata_survival": all(sum(r["ally_deaths"] for r in values if r["automatic_spells"] == spells) <=
                sum(r["ally_deaths"] for r in by_arm["parent"] if r["automatic_spells"] == spells) for spells in (False, True)),
            "duel_control_parity": all(r["state_sequence_sha256"] == baseline[r["id"].rsplit("/", 1)[0]]["state_sequence_sha256"]
                                       for r in values if r["family"] == "duel_control")}
    qualified = [arm for arm, checks in gates.items() if all(checks.values())]
    selected = max(qualified, key=lambda arm: (sums[arm]["enemy_deaths"], sums[arm]["enemy_hp_loss"])) if qualified else None
    result = {"schema": "gota-microplay-result/1", "partition": partition, "totals": sums,
              "gates": gates, "selected": selected, "plan_sha256": ir.sha(directory / "plan.json"),
              "scope": "Constructed short encounters on pinned release; no full-game/league inference."}
    write(directory / (partition + "-result.json"), result)
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=lambda p: Path(p).resolve())
    parser.add_argument("command", choices=("prepare", "discovery", "holdout", "evaluate", "audit"))
    parser.add_argument("--partition", choices=("discovery", "holdout"), default="discovery")
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.directory)
    elif args.command in ("discovery", "holdout"):
        run(args.directory, args.command)
        evaluate(args.directory, args.command)
    elif args.command == "evaluate":
        evaluate(args.directory, args.partition)
    else:
        run(args.directory, args.partition, audit=True)
