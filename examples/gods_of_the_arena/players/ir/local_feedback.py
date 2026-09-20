"""Feed a completed local gate into beliefs without changing tested BASIC.

The report describes the whole frozen policy. It cannot establish which of its
individual hypotheses caused the result, even when the policy passes the gate.
"""

import argparse
from copy import deepcopy
from pathlib import Path

from local_gate import significance
from policy_ir import bundle, compile_policy, digest, executable, read


def feedback(policy, report_path, beliefs=()):
    report = read(report_path)
    source = compile_policy(policy)
    if digest(source.encode()) != report["source_sha256"]:
        raise ValueError("local evidence refers to different generated BASIC")
    summary = report["held_out"]
    for row in summary["pairs"]:
        if (row["score"] not in (0, 1) or row["control_score"] not in (0, 1)
                or row["delta"] != row["score"] - row["control_score"]):
            raise ValueError("invalid paired scores")
    if (summary["wins"] != sum(p["score"] for p in summary["pairs"])
            or summary["control_wins"] != sum(p["control_score"] for p in summary["pairs"])
            or summary["seat_comparisons"] != len(summary["pairs"])
            or summary["episodes"] != len(summary["pairs"])):
        raise ValueError("local totals disagree with completed pairs")
    gate = significance(summary, report["gate"]["minimum_gain"], report["gate"]["alpha"])
    # Normalize integer seed keys to their JSON representation before comparing.
    gate["seed_deltas"] = {str(seed): delta for seed, delta in gate["seed_deltas"].items()}
    if gate != report["gate"] or report["hosted_evaluation_eligible"] != gate["passed"]:
        raise ValueError("reported gate disagrees with independent recomputation")
    result = deepcopy(policy)
    reference = {"artifact": str(report_path), "sha256": digest(Path(report_path).read_bytes())}
    for name in beliefs:
        claim = result["belief"]["claims"][name]
        claim["status"] = "requires_review"
        claim["evidence"].append(reference)
    verdict = "passed_local_gate" if gate["passed"] else "failed_local_gate"
    result["belief"]["claims"]["B_local_gate"] = {
        "claim": (
            f"Frozen BASIC {report['source_sha256']} {verdict}: "
            f"{summary['wins']}/{summary['seat_comparisons']} candidate wins versus "
            f"{summary['control_wins']}/{summary['seat_comparisons']} matched baseline wins, "
            f"across {gate['seed_clusters']} independent seeds with all ten seats tested separately. "
            f"Paired gain {gate['mean_paired_gain']:+.4f}; seed sign-test p={gate['one_sided_sign_test_p']:.6g}, "
            f"alpha={gate['alpha']}, required gain={gate['minimum_gain']}. "
            "This measures the complete configuration among nine default policies. "
            "It does not isolate individual changes or establish wider-field strength."
        ),
        "status": "supported" if gate["passed"] else "requires_review",
        "evidence": [reference],
    }
    reviews = set(policy["update"]["needs_review"]) | {f"belief/{name}" for name in beliefs}
    if not gate["passed"]:
        reviews.add("belief/B_local_gate")
    result["update"] = {
        "revision": policy["update"]["revision"] + 1, "parent": digest(policy),
        "change": {"origin": "local_episode_feedback", "verdict": verdict},
        "needs_review": sorted(reviews), "evidence": policy["update"]["evidence"] + [reference],
    }
    if executable(result) != executable(policy) or compile_policy(result) != source:
        raise ValueError("belief feedback changed tested behavior")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--belief", action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    updated = feedback(read(args.ir), args.report, args.belief)
    manifest = bundle(updated, args.output)
    print({"verdict": updated["update"]["change"]["verdict"],
           "parity": manifest["structural_parity"], "output": str(args.output)})


if __name__ == "__main__":
    main()
