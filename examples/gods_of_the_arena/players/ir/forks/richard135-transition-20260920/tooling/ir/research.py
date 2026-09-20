"""Bounded local IR research: fidelity -> parity -> selection -> held-out games.

Every candidate changes only the declared R4 offset. The winner is frozen before
held-out games. Results update the evidence layer, then compile/extract again.
This measures baseline-filled local seats, not live league strength or the
broader hypothesis that semantic IR beats direct code optimization.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess

from policy_ir import (HERE, ROOT, bundle, digest, executable, extract, read,
                       refresh_grounding, write)


def run_episode(binary, baseline, candidate, seed, slots, directory):
    directory.mkdir(parents=True, exist_ok=False)
    replay = directory / "episode.replay"
    command = [str(binary), "--seed", str(seed), "--ticks", "28800", "--record", str(replay)]
    command.extend(f"--bot:{candidate if slot in slots else baseline}" for slot in range(10))
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=180, check=True)
    (directory / "stdout.log").write_text(result.stdout)
    (directory / "stderr.log").write_text(result.stderr)
    summary = json.loads(result.stdout.splitlines()[-1])
    if summary["ticks"] > 28800 or len(summary["heroes"]) != 10:
        raise ValueError("invalid episode result")
    trace = Path(str(replay) + ".trace.jsonl")
    with trace.open() as stream:
        for line in stream:
            event = json.loads(line)
            expected = "R2" if event["candidate_id"] != 0 else "R4"
            if event["tactical_rule"] != expected:
                raise ValueError("trace contradicts the actual target predicate")
    summary.update({"candidate_slots": sorted(slots), "command": command,
                    "replay_sha256": digest(replay.read_bytes()), "trace_sha256": digest(trace.read_bytes()),
                    "baseline_sha256": digest(Path(baseline).read_bytes()),
                    "candidate_sha256": digest(Path(candidate).read_bytes())})
    write(directory / "result.json", summary)
    return summary


def score_batch(results, controls):
    pairs = []
    for result in results:
        for slot in result["candidate_slots"]:
            hero = result["heroes"][slot]
            control = controls[result["seed"]]["heroes"][slot]
            pairs.append({"seed": result["seed"], "slot": slot, "team": hero["team"], "class": hero["class"],
                          "score": hero["score"], "control_score": control["score"],
                          "delta": hero["score"] - control["score"], "timeout": result["timeout"],
                          "deaths": hero["deaths"], "control_deaths": control["deaths"],
                          "fallback_decisions": hero["fallback_decisions"]})
    return {"episodes": len(results), "seat_comparisons": len(pairs),
            "wins": sum(p["score"] for p in pairs), "control_wins": sum(p["control_score"] for p in pairs),
            "paired_delta": sum(p["delta"] for p in pairs) / len(pairs),
            "timeouts": sum(r["timeout"] for r in results), "pairs": pairs}


def batch(binary, baseline, candidate, seeds, directory, workers, teams=False):
    jobs = {}
    results = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for seed in seeds:
            rosters = [set(range(5)), set(range(5, 10))] if teams else [{s} for s in range(10)]
            for slots in rosters:
                label = "_".join(str(s) for s in sorted(slots))
                future = pool.submit(run_episode, binary, baseline, candidate, seed, slots,
                                     directory / f"seed-{seed}-slots-{label}")
                jobs[future] = (seed, label)
        for future in as_completed(jobs):
            result = future.result()
            results.append(result)
            seed, label = jobs[future]
            print(f"{directory.name}: seed={seed} seats={label} winner={result['winner']} ticks={result['ticks']}", flush=True)
    return sorted(results, key=lambda r: (r["seed"], r["candidate_slots"]))


def numbers(text):
    return [int(value) for value in text.split(",")]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--offsets", type=numbers, default=[0, 2])
    parser.add_argument("--selection-seeds", type=numbers, default=[2026, 2027])
    parser.add_argument("--held-out-seeds", type=numbers, default=[3026, 3027])
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    if (not args.offsets or len(set(args.offsets)) != len(args.offsets)
            or any(offset < 0 or offset > 8 for offset in args.offsets)):
        parser.error("offsets must be distinct integers in 0..8")
    if not 1 <= args.workers <= 4:
        parser.error("workers must be in 1..4")
    if (not args.selection_seeds or not args.held_out_seeds
            or len(set(args.selection_seeds)) != len(args.selection_seeds)
            or len(set(args.held_out_seeds)) != len(args.held_out_seeds)
            or set(args.selection_seeds) & set(args.held_out_seeds)):
        parser.error("selection and held-out seeds must be nonempty, unique and disjoint")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    plan = {"offsets": args.offsets, "selection_seeds": args.selection_seeds,
            "held_out_seeds": args.held_out_seeds, "maximum_ticks": 28800,
            "candidate_seats": list(range(10)), "workers": args.workers,
            "started_at": datetime.now(timezone.utc).isoformat()}
    write(output / "plan.json", plan)
    env = dict(os.environ, POLYWORLD_DEPS=str(ROOT))
    proof = subprocess.run(["python3", "-m", "unittest", "discover", "-s", str(HERE), "-p", "test_*.py", "-v"],
                           cwd=ROOT, env=env, text=True, capture_output=True)
    (output / "fidelity.log").write_text(proof.stdout + proof.stderr)
    proof.check_returncode()
    binary = output / "episode"
    build = subprocess.run(["nim", "c", "-d:headless", "--hints:off", f"-o:{binary}", str(HERE / "episode.nim")],
                           cwd=ROOT, env=env, text=True, capture_output=True)
    (output / "build.log").write_text(build.stdout + build.stderr)
    build.check_returncode()
    write(output / "harness.json", {
        "sources": {p.name: digest(p.read_bytes()) for p in
                    [HERE / "research.py", HERE / "episode.nim", HERE / "scenario_vm.nim", HERE / "test_policy_ir.py"]},
        "episode_binary_sha256": digest(binary.read_bytes()),
        "nim_version": subprocess.check_output(["nim", "--version"], text=True),
        "dependency_lock": digest((ROOT / "coworld/dependencies.lock").read_bytes()),
    })
    base = read(HERE / "base.ir.json")
    bundle(base, output / "base")
    baseline = output / "base/policy.bas"
    controls = {}
    for seed in args.selection_seeds:
        controls[seed] = run_episode(binary, baseline, baseline, seed, set(), output / f"control-{seed}")
    # The harness normalizes only the replay creation timestamp. Full action
    # tapes include setup and per-tick state hashes as well as every command.
    seed = args.selection_seeds[0]
    original = HERE.parent / "base.bas"
    run_episode(binary, original, original, seed, set(), output / "original-baseline")
    left = (output / "original-baseline/episode.replay").read_bytes()
    right = (output / f"control-{seed}/episode.replay").read_bytes()
    if left != right:
        raise ValueError("original and generated baseline full-game replays differ")
    write(output / "baseline-parity.json", {"seed": seed, "identical_action_and_state_tape": True,
                                          "creation_timestamp_normalized": True,
                                          "replay_sha256": digest(left), "actions": controls[seed]["actions"]})
    print("Full-game baseline replay parity passed", flush=True)
    selection = {}
    for offset in args.offsets:
        candidate = deepcopy(read(HERE / "waveguard_r4.ir.json"))
        parent_hash = digest(candidate)
        candidate["id"] = f"gota_waveguard_r4_offset_{offset}"
        candidate["skill"]["fallback"]["parameters"]["offset_tiles"] = offset
        candidate["update"].update({"parent": parent_hash, "revision": candidate["update"]["revision"] + 1,
                                   "change": {"origin": "declared_parameter_sweep", "rule": "R4", "offset_tiles": offset}})
        refresh_grounding(candidate)
        directory = output / f"offset-{offset}"
        bundle(candidate, directory)
        results = batch(binary, baseline, directory / "policy.bas", args.selection_seeds,
                        output / f"selection-{offset}", args.workers)
        selection[offset] = score_batch(results, controls)
        write(output / f"selection-{offset}.json", selection[offset])
    # Predeclared tie-break: prefer the smaller offset. Held-out outcomes never
    # choose a different candidate or a new threshold in this run.
    winner = max(args.offsets, key=lambda offset: (selection[offset]["paired_delta"], -offset))
    write(output / "selected.json", {"offset_tiles": winner, "selection": selection[winner],
                                    "tie_break": "smaller offset", "frozen_before_held_out": True})
    for seed in args.held_out_seeds:
        controls[seed] = run_episode(binary, baseline, baseline, seed, set(), output / f"control-{seed}")
    selected = output / f"offset-{winner}/policy.bas"
    held_out = score_batch(batch(binary, baseline, selected, args.held_out_seeds,
                                 output / "held-out", args.workers), controls)
    teams = score_batch(batch(binary, baseline, selected, args.held_out_seeds,
                              output / "teams", args.workers, teams=True), controls)
    promising = selection[winner]["paired_delta"] > 0 and held_out["paired_delta"] > 0
    result = {"selected_offset": winner, "selection": selection[winner], "held_out": held_out,
              "five_vs_five": teams, "fidelity_passed": True, "baseline_replay_parity": True,
              "verdict": "promising_local_candidate" if promising else "no_demonstrated_improvement",
              "limitations": ["Few seed clusters; ten seats per seed are correlated.",
                              "Teammates and opponents use the bundled baseline; no live league evaluation.",
                              "No direct-code optimization control: this does not test the general IR research hypothesis."]}
    write(output / "result.json", result)
    # Feed observations back into the semantic artifact, preserve authored goals,
    # then prove the evidence update did not silently mutate executable behavior.
    evaluated = extract(selected.read_text(), read(output / f"offset-{winner}/policy.ir.json"))
    before = executable(evaluated)
    evaluated["update"] = {
        "revision": evaluated["update"]["revision"] + 1, "parent": digest(evaluated),
        "change": {"origin": "episode_feedback", "verdict": result["verdict"]},
        "needs_review": [],
        "evidence": [{"artifact": str(output / "result.json"), "sha256": digest((output / "result.json").read_bytes())}],
    }
    claim = evaluated["belief"]["claims"]["B_wave"]
    # A small correlated sample can inform the belief without turning it into a
    # proved fact. Leave it untested at the generalization level, with evidence.
    claim["status"] = "requires_review"
    claim["evidence"] = evaluated["update"]["evidence"]
    evaluated["update"]["needs_review"] = ["belief/B_wave"]
    bundle(evaluated, output / "evaluated")
    if executable(evaluated) != before:
        raise ValueError("episode feedback silently changed executable behavior")
    print(json.dumps({"verdict": result["verdict"], "selected_offset": winner,
                      "selection_delta": selection[winner]["paired_delta"],
                      "held_out_delta": held_out["paired_delta"], "output": str(output)}, indent=2), flush=True)


if __name__ == "__main__":
    main()
