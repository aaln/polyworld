"""Validate matched hosted evidence, update beliefs, and regenerate an IR bundle.

Download each arm's artifacts and run audit_replay against the published runtime
first. Failed, incomplete, or mismatched episodes cannot update the policy.
"""

import argparse
from copy import deepcopy
from pathlib import Path

from policy_ir import bundle, compile_policy, digest, executable, read, write


def load_arm(directory, policy_version):
    rows = []
    for path in sorted(Path(directory).glob("*/episode.json")):
        episode = read(path)
        if episode["status"] != "completed" or not (path.parent / ".done").exists():
            raise ValueError(f"incomplete episode: {episode['id']}")
        roster = episode["policy_version_ids"]
        if len(roster) != 10 or roster.count(policy_version) != 1:
            raise ValueError("each episode must contain exactly one candidate seat")
        slot = roster.index(policy_version)
        result = read(path.parent / "results.json")
        audit = read(path.parent / "audit.json")
        if audit["hash_mismatches"] != 0 or result["ticks"] != audit["ticks"]:
            raise ValueError("replay verification failed")
        if "scripts: 10/10 active" not in (path.parent / "game.log").read_text():
            raise ValueError("all ten VMs must remain active for behavioral comparison")
        hero = audit["heroes"][slot]
        score = result["scores"][slot]
        participant = next(p for p in episode["participant_scores"] if p["position"] == slot)
        if score not in (0, 1) or score != hero["score"] or score != participant["score"]:
            raise ValueError("artifact, replay and API scores disagree")
        roster = ["<candidate>" if v == policy_version else v for v in roster]
        rows.append({
            "episode_request_id": episode["id"], "slot": slot,
            "seed": result["seed"], "coworld_id": episode["coworld_id"],
            "game_version": episode["coworld_version"], "game_config": episode["game_config"],
            "roster": roster, "score": score, "ticks": result["ticks"],
            "timeout": result["outcome"] == "time_limit", "deaths": hero["deaths"],
            "equipment_count": sum(item not in {"NoItem", "IronrootRation", "VitalityElixir",
                                                 "ManaPotion", "PoisonPotion"} for item in hero["inventory"]),
            "poison_purchase_attempts": hero["buy_attempts_by_item"][4],
            "artifact_hashes": {p.name: digest(p.read_bytes()) for p in
                                [path, path.parent / "results.json", path.parent / "audit.json",
                                 path.parent / "replay.bin", path.parent / "game.log"]},
        })
    return rows


def compare(control, candidate):
    def indexed(rows):
        entries = {(r["seed"], r["slot"]): r for r in rows}
        if not rows or len(entries) != len(rows):
            raise ValueError("empty arm or duplicate seed/seat")
        for seed in {r["seed"] for r in rows}:
            if {r["slot"] for r in rows if r["seed"] == seed} != set(range(10)):
                raise ValueError("each seed must cover all ten candidate seats")
        return entries

    before, after = indexed(control), indexed(candidate)
    if before.keys() != after.keys():
        raise ValueError("arms have different seed/seat coverage")
    pairs = []
    for key in sorted(before):
        left, right = before[key], after[key]
        for field in ["coworld_id", "game_version", "game_config", "roster"]:
            if left[field] != right[field]:
                raise ValueError(f"unmatched {field} at seed/seat {key}")
        if left["episode_request_id"] == right["episode_request_id"]:
            raise ValueError("a control episode cannot also be its candidate")
        pairs.append({"seed": key[0], "slot": key[1], "control": left, "candidate": right,
                      "score_delta": right["score"] - left["score"]})
    control_wins, candidate_wins = sum(r["score"] for r in control), sum(r["score"] for r in candidate)
    return {
        "episodes_per_arm": len(pairs), "seed_clusters": len({p["seed"] for p in pairs}),
        "control_wins": control_wins, "candidate_wins": candidate_wins,
        "paired_win_delta": (candidate_wins - control_wins) / len(pairs),
        "control_equipment_items": sum(r["equipment_count"] for r in control),
        "candidate_equipment_items": sum(r["equipment_count"] for r in candidate),
        "control_deaths": sum(r["deaths"] for r in control),
        "candidate_deaths": sum(r["deaths"] for r in candidate),
        "control_timeouts": sum(r["timeout"] for r in control),
        "candidate_timeouts": sum(r["timeout"] for r in candidate),
        "verdict": "directionally_promising" if candidate_wins > control_wins else "no_demonstrated_improvement",
        "limitations": ["Rotated seats sharing a seed are correlated.",
                        "No established verdict sample floor for GOTA; results are directional.",
                        "Final equipment and death totals also depend on episode length.",
                        "This experiment does not isolate wave following or compare IR research with direct-code research."],
        "pairs": pairs,
    }


def feedback(policy, report_path):
    report = read(report_path)
    if digest(compile_policy(policy).encode()) != report["candidate_source_sha256"]:
        raise ValueError("report refers to different generated BASIC")
    result = deepcopy(policy)
    reference = {"artifact": str(report_path), "sha256": digest(Path(report_path).read_bytes())}
    result["update"] = {
        "revision": policy["update"]["revision"] + 1, "parent": digest(policy),
        "change": {"origin": "hosted_xp_feedback", "verdict": report["verdict"]},
        "needs_review": ["belief/B_wave", "belief/B_equipment"],
        "evidence": policy["update"]["evidence"] + [reference],
    }
    claim = result["belief"]["claims"]["B_equipment"]
    claim["claim"] = (
        f"Matched hosted games: sustain-only won {report['candidate_wins']}/{report['episodes_per_arm']} "
        f"versus v1 {report['control_wins']}/{report['episodes_per_arm']}. "
        f"Final equipment totaled {report['candidate_equipment_items']} versus {report['control_equipment_items']}. "
        "These observations inform the equipment-saving hypothesis; broader strength remains unresolved."
    )
    claim["status"] = "requires_review"
    claim["evidence"].append(reference)
    if executable(result) != executable(policy):
        raise ValueError("evidence feedback changed executable behavior")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--control-version", required=True)
    parser.add_argument("--candidate-version", required=True)
    parser.add_argument("--ir", type=Path, required=True)
    parser.add_argument("--upload-request", type=Path, required=True)
    parser.add_argument("--uploaded-version", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = compare(load_arm(args.control, args.control_version), load_arm(args.candidate, args.candidate_version))
    policy = read(args.ir)
    upload = read(args.upload_request)
    version = read(args.uploaded_version)
    if (version["id"] != args.candidate_version
            or digest(compile_policy(policy).encode()) != upload["content_hash"]):
        raise ValueError("IR/generated source does not match the uploaded version receipt")
    report.update({"control_policy_version_id": args.control_version,
                   "candidate_policy_version_id": args.candidate_version,
                   "candidate_source_sha256": upload["content_hash"]})
    write(args.report, report)
    updated = feedback(policy, args.report)
    manifest = bundle(updated, args.output)
    if (args.output / "policy.bas").read_text() != compile_policy(policy):
        raise ValueError("belief feedback changed BASIC bytes")
    print({"verdict": report["verdict"], "control_wins": report["control_wins"],
           "candidate_wins": report["candidate_wins"], "parity": manifest["structural_parity"],
           "output": str(args.output)})


if __name__ == "__main__":
    main()
