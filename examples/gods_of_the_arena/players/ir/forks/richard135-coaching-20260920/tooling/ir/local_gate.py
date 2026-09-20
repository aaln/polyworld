"""Screen IR candidates against baseline; freeze one before a held-out gate.

All ten seats are tested separately on every seed, with nine baseline players.
Significance uses independent seed clusters, not correlated individual seats.
No hosted request is launched by this program.
"""

import argparse
from math import comb
from pathlib import Path

from policy_ir import bundle, digest, read, write
from research import batch, numbers, run_episode, score_batch


def significance(summary, minimum_gain=0.10, alpha=0.05):
    seeds = sorted({p["seed"] for p in summary["pairs"]})
    if not seeds:
        raise ValueError("no completed seed evidence")
    deltas = []
    for seed in seeds:
        rows = [p for p in summary["pairs"] if p["seed"] == seed]
        if len(rows) != 10 or {p["slot"] for p in rows} != set(range(10)):
            raise ValueError("each independent seed must cover all ten seats exactly once")
        deltas.append(sum(p["delta"] for p in rows) / 10)
    positive, negative = sum(d > 0 for d in deltas), sum(d < 0 for d in deltas)
    nonzero = positive + negative
    p_value = sum(comb(nonzero, k) for k in range(positive, nonzero + 1)) / 2**nonzero
    gain = sum(p["delta"] for p in summary["pairs"]) / len(summary["pairs"])
    return {"seed_clusters": len(seeds), "seed_deltas": dict(zip(seeds, deltas)),
            "positive_seeds": positive, "negative_seeds": negative,
            "tied_seeds": len(seeds) - nonzero, "one_sided_sign_test_p": p_value,
            "mean_paired_gain": gain, "minimum_gain": minimum_gain, "alpha": alpha,
            "passed": len(seeds) >= 20 and gain >= minimum_gain and p_value < alpha,
            "interpretation": "Sign test of positive versus negative independent seed deltas; ties excluded. "
                              f"The practical gate additionally requires at least {minimum_gain * 100:g} percentage points mean gain. "
                              "This establishes baseline-roster evidence, not wider-field superiority."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, action="append", required=True)
    parser.add_argument("--selection-seeds", type=numbers, required=True)
    parser.add_argument("--held-out-seeds", type=numbers, required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--minimum-gain", type=float, default=0.10)
    args = parser.parse_args()
    if set(args.selection_seeds) & set(args.held_out_seeds):
        parser.error("selection and held-out seeds must be disjoint")
    if (len(set(args.selection_seeds)) != len(args.selection_seeds)
            or len(set(args.held_out_seeds)) != len(args.held_out_seeds)
            or not args.selection_seeds or len(args.held_out_seeds) < 20):
        parser.error("unique seeds required, including at least 20 held-out seeds")
    if not 1 <= args.workers <= 4:
        parser.error("workers must be in 1..4")
    if not 0 < args.alpha < 1 or not 0 < args.minimum_gain <= 1:
        parser.error("alpha must be in (0,1) and minimum gain in (0,1]")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    baseline, binary = args.baseline.resolve(), args.binary.resolve()
    plan = {"selection_seeds": args.selection_seeds, "held_out_seeds": args.held_out_seeds,
            "candidates": [str(p) for p in args.candidate],
            "baseline_sha256": digest(baseline.read_bytes()), "binary_sha256": digest(binary.read_bytes()),
            "gate": {"minimum_gain": args.minimum_gain, "alpha": args.alpha, "minimum_seed_clusters": 20},
            "selection": "highest paired win gain; tie-break candidate input order",
            "roster": "one changed seat and nine baseline, all ten seats per seed",
            "stop_rule": "one frozen winner and one held-out gate; do not tune or retest on these held-out seeds"}
    write(output / "plan.json", plan)
    controls = {}
    for seed in args.selection_seeds:
        controls[seed] = run_episode(binary, baseline, baseline, seed, set(), output / f"control-{seed}")
    summaries, directories = [], []
    for index, path in enumerate(args.candidate):
        policy = read(path)
        directory = output / f"candidate-{index}"
        bundle(policy, directory)
        directories.append(directory)
        results = batch(binary, baseline, directory / "policy.bas", args.selection_seeds,
                        output / f"selection-{index}", args.workers)
        summary = score_batch(results, controls)
        summaries.append(summary)
        write(output / f"selection-{index}.json", summary)
        print(f"SCREEN {policy['id']}: {summary['wins']}/{summary['seat_comparisons']} "
              f"vs {summary['control_wins']} baseline", flush=True)
    winner = max(range(len(summaries)), key=lambda i: (summaries[i]["paired_delta"], -i))
    selected = directories[winner]
    write(output / "selected.json", {"candidate_index": winner, "bundle": str(selected),
                                    "source_sha256": digest((selected / "policy.bas").read_bytes()),
                                    "frozen_before_held_out": True})
    for seed in args.held_out_seeds:
        controls[seed] = run_episode(binary, baseline, baseline, seed, set(), output / f"control-{seed}")
    held_out = score_batch(batch(binary, baseline, selected / "policy.bas", args.held_out_seeds,
                                 output / "held-out", args.workers), controls)
    gate = significance(held_out, minimum_gain=args.minimum_gain, alpha=args.alpha)
    result = {"selected_candidate": winner, "source_sha256": digest((selected / "policy.bas").read_bytes()),
              "selection": summaries[winner], "held_out": held_out, "gate": gate,
              "hosted_evaluation_eligible": gate["passed"]}
    write(output / "result.json", result)
    print({"held_out_wins": held_out["wins"], "baseline_wins": held_out["control_wins"], "gate": gate}, flush=True)


if __name__ == "__main__":
    main()
