"""Default XP runner: one request with N episodes, never a per-game POST loop.

Use Metta's virtualenv. Each policy arm gets one frozen request. The API derives
seeds from the request ID; different arm requests are independent seed cohorts.
"""
import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import time

from policy_ir import read, write

DEFAULT_EPISODES = 40
MAX_EPISODES = 100


def batch_body(plan, count=DEFAULT_EPISODES):
    if type(count) is not int or not 2 <= count <= MAX_EPISODES:
        raise ValueError("A batch requires2–100 episodes; default40")
    refs = [plan["policy_version"]] + [v["id"] for v in plan["opponents"]]
    if len(refs) != 10 or len(set(refs)) != 10:
        raise ValueError("Pin one subject and nine distinct incumbent versions")
    config = deepcopy(plan["config"])
    if "seed" in config:
        raise ValueError("A fixed seed would repeat boards; omit it for an independent batch")
    return {"idempotency_key": f"gota-batch-{plan['run_id']}-{plan['policy_version'][:8]}-{count}",
            "target": deepcopy(plan["target"]), "game_config_overrides": config,
            "roster": [{"slot": -1, "player": {"policy_ref": ref}} for ref in refs],
            "num_episodes": count,
            "notes": plan.get("notes", f"{count}-episode field evaluation in one XP request. Fixed incumbent versions, rotated hero seats and independent platform-generated seeds. Report wins and Glory descriptively; not a seed-matched A/B or promotion gate.")}


def harvest(c, directory, watch):
    from hosted_wave import TERMINAL, episodes, fetch

    plan = read(directory / "plan.json")
    body = read(directory / "batch/request.json")
    xreq = read(directory / "batch/created.json")["id"]
    count = body["num_episodes"]
    while True:
        rows = episodes(c, xreq)
        write(directory / "batch/episodes.json", rows)
        complete = 0
        for ep in rows:
            if ep["status"] in TERMINAL:
                fetch(c, ep, directory / "artifacts", plan["policy_version"])
                complete += 1
        write(directory / "progress.json", {"request": xreq, "requested": count,
              "episodes_created": len(rows), "complete_and_fetched": complete})
        print(f"One batch: {complete}/{count} complete and fetched", flush=True)
        if complete == count:
            seeds, seats = [], []
            expected_roster = Counter(r["player"]["policy_ref"] for r in body["roster"])
            for ep in rows:
                result = read(directory / "artifacts" / ep["id"] / "results.json")
                if Counter(ep["policy_version_ids"]) != expected_roster:
                    raise ValueError("Frozen roster changed")
                if ep["coworld_id"] != plan["target"]["coworld_id"]:
                    raise ValueError("Game build changed")
                config = {k: v for k, v in ep["game_config"].items() if k not in {"seed", "players", "tokens"}}
                if config != plan["config"]:
                    raise ValueError("Engine configuration changed")
                seeds.append(result["seed"])
                seats.append(ep["policy_version_ids"].index(plan["policy_version"]))
            if len(set(seeds)) != count:
                raise ValueError("Repeated effective seeds in batch")
            expected_seats = Counter({slot: count // 10 + int(slot < count % 10)
                                      for slot in range(10)})
            if Counter(seats) != +expected_seats:
                raise ValueError("Unexpected subject-seat rotation")
            write(directory / "collection.json", {"request_count": 1, "episodes": count,
                  "unique_effective_seeds": count, "seats": dict(Counter(seats)),
                  "comparison_design": "independent_seed_cohort", "all_artifacts_fetched": True,
                  "replay_audit_status": "pending; collection alone is not validated performance"})
            return
        if not watch:
            return
        time.sleep(15)


def main():
    from hosted_wave import client, create

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("command", choices=["launch", "harvest"])
    parser.add_argument("--episodes", type=int, default=DEFAULT_EPISODES)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--watch", action="store_true")
    args = parser.parse_args()
    with client() as c:
        if args.command == "launch":
            body = batch_body(read(args.directory / "plan.json"), args.episodes)
            xreq = create(c, body, args.directory / "batch", args.dry_run)
            print(json.dumps({"request": xreq, "num_episodes": args.episodes,
                              "requests_created": 0 if args.dry_run else 1}), flush=True)
        else:
            harvest(c, args.directory, args.watch)


if __name__ == "__main__":
    main()
