"""Verify and add retrospective Glory diagnostics to the frozen hosted A/B.

No new games or policy actions. Never changes the original win gate. It waits
for the primary hosted comparison before updating IR, avoiding concurrent writes.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
import json
from pathlib import Path
import random
import statistics
import subprocess
import time

from glory_metrics import json_values, seat_values
from policy_ir import HERE, bundle, compile_policy, digest, extract, read, write


def audit_one(folder, binary, sha):
    result = read(folder / "results.json")
    tape = folder / "replay.bin"
    tape_sha = digest(tape.read_bytes())
    output = folder / "glory-audit.json"
    if not output.exists():
        proc = subprocess.run([str(binary), "--replay", str(tape)],
                              capture_output=True, text=True, timeout=600)
        if proc.returncode:
            (folder / "glory-audit.stderr.log").write_text(proc.stderr)
            raise ValueError(f"XP audit failed: {folder.name}")
        audit = json.loads(proc.stdout.splitlines()[-1])
        audit.update(binary_sha256=sha, replay_sha256=tape_sha)
        write(output, audit)
    audit = read(output)
    if (audit["binary_sha256"] != sha or audit["replay_sha256"] != tape_sha
            or audit["hash_mismatches"] or audit["ticks"] != audit["recorded_ticks"]
            or audit["actions_consumed"] != audit["recorded_actions"]):
        raise ValueError("Incomplete XP replay audit")
    for key in ["ticks", "seed", "scores", "total_xp"]:
        if audit[key] != result[key]:
            raise ValueError(f"Published result disagrees with replay {key}")
    seat_values(result)
    return folder


def bootstrap_interval(deltas):
    rng = random.Random(9152026)
    means = sorted(statistics.fmean(rng.choices(deltas, k=len(deltas))) for _ in range(10000))
    return [means[249], means[9749]]


def summarize(rows):
    return {"games": len(rows), "wins": sum(row["win"] for row in rows),
            **{"mean_" + key: statistics.fmean(row[key] for row in rows)
               for key in ["xp", "minutes", "score", "glory", "hero_kills", "tower_last_hits", "footman_last_hits"]}}


def write_feedback(study, directory):
    primary = read(study / "result.json")
    if primary["audited_games"] != 80 or primary["independent_pairs"] != 40:
        raise ValueError("A complete verified primary comparison is required")
    by_id = {path.parent.name: path.parent for path in (study / "artifacts").glob("*/*/.done")}
    pairs = []
    for pair in primary["pairs"]:
        row = {}
        for arm in ["control", "candidate"]:
            source = pair[arm]
            folder = by_id[source["episode"]]
            result, audit = read(folder / "results.json"), read(folder / "glory-audit.json")
            hero = audit["heroes"][source["slot"]]
            xp = hero["total_xp"] - 150 * hero["kills"]
            gold = hero["earned_gold"] - 100 * hero["kills"]
            towers = (5 * gold - 3 * xp) // 75
            footmen = (xp - 100 * towers) // 25
            if min(towers, footmen) < 0 or (xp, gold) != (100 * towers + 25 * footmen, 75 * towers + 15 * footmen):
                raise ValueError("Current reward accounting did not reconstruct last hits")
            values = json_values(seat_values(result)[source["slot"]])
            row[arm] = {**values, "episode": source["episode"], "seed": source["seed"],
                        "slot": source["slot"], "class": source["class"],
                        "minutes": result["ticks"] / 1440, "hero_kills": hero["kills"],
                        "tower_last_hits": towers, "footman_last_hits": footmen,
                        "audit_sha256": digest((folder / "glory-audit.json").read_bytes())}
        row["glory_delta"] = row["candidate"]["glory"] - row["control"]["glory"]
        pairs.append(row)
    delta = statistics.fmean(pair["glory_delta"] for pair in pairs)
    report = {"analysis": "retrospective_secondary_metric", "promotion_eligible": False,
              "formula": "win * (total_xp - 100 * ticks / 1440)",
              "primary_win_gate": "unchanged", "game_version": primary["game_version"],
              "verified_games": 80, "independent_pairs": 40,
              "control": summarize([p["control"] for p in pairs]),
              "candidate": summarize([p["candidate"] for p in pairs]),
              "paired_mean_glory_delta": delta,
              "paired_glory_bootstrap_95_percent_interval": bootstrap_interval([p["glory_delta"] for p in pairs]),
              "class_splits": {name: {arm: summarize([p[arm] for p in pairs if p[arm]["class"] == name])
                                      for arm in ["control", "candidate"]}
                               for name in sorted({p["control"]["class"] for p in pairs})},
              "limitations": ["Glory was requested after these games completed; this is exploratory, not a new passing gate.",
                              "Small sample and fixed roster; class splits have four cases each.",
                              "The live league ranks binary wins with Elo, not Glory.",
                              "Glory may be negative on wins; losses and draws are zero. Win-rate qualification remains mandatory."],
              "pairs": pairs}
    path = HERE / "glory-hosted-20260915.json"
    write(path, report)
    write(directory / "result.json", report)
    policy_path = HERE / "hypotheses/wave_local_balance.evaluated.ir.json"
    policy = read(policy_path)
    basic = compile_policy(policy)
    if digest(basic.encode()) != primary["candidate_source_sha256"]:
        raise ValueError("Glory report refers to a different policy")
    updated = deepcopy(policy)
    ref = {"artifact": str(path), "sha256": digest(path.read_bytes())}
    updated["belief"]["claims"]["B_glory_measured"] = {
        "claim": f"Exploratory Glory on forty verified hosted pairs: candidate mean{report['candidate']['mean_glory']:.2f}, v2 mean{report['control']['mean_glory']:.2f}, paired delta{delta:+.2f}. All lifetime XP values matched full replays. This secondary analysis does not change the original fort-win gate or establish superiority.",
        "status": "requires_review", "evidence": [ref]}
    updated["update"]["revision"] += 1
    updated["update"]["parent"] = digest(policy)
    updated["update"]["change"] = {"origin": "glory_feedback", "primary_win_gate_changed": False}
    updated["update"]["evidence"].append(ref)
    if compile_policy(updated) != basic or extract(basic, updated) != updated:
        raise ValueError("Glory feedback changed policy actions")
    bundle(updated, directory / "evaluated")
    write(policy_path, updated)
    (HERE / "hypotheses/wave_local_balance.evaluated.bas").write_text(basic)
    print(json.dumps({k: v for k, v in report.items() if k not in {"pairs", "class_splits"}}, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("study", type=Path)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    study, directory = args.study.resolve(), args.directory.resolve()
    folders = sorted(path.parent for path in (study / "artifacts").glob("*/*/.done"))
    if len(folders) != 80:
        raise ValueError("Exactly80 completed hosted artifacts are required")
    binary = directory / "audit"
    sha = digest(binary.read_bytes())
    write(directory / "audit-provenance.json", {"binary_sha256": sha,
          "source_sha256": digest((HERE / "audit_glory.nim").read_bytes()),
          "game_source": read(study / "plan.json")["game_source"],
          "purpose": "Verify lifetime XP and final reward counters from complete existing tapes; no new games."})
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        jobs = [pool.submit(audit_one, folder, binary, sha) for folder in folders]
        for count, future in enumerate(as_completed(jobs), 1):
            future.result()
            if count % 5 == 0:
                print(f"Glory XP audits: {count}/80 verified", flush=True)
    print("XP verified; waiting for the original full comparison before secondary feedback.", flush=True)
    while not (study / "result.json").exists():
        time.sleep(10)
    write_feedback(study, directory)


if __name__ == "__main__":
    main()
