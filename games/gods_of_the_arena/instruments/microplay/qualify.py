"""Complete normal games and exact action replay checks for microplay integration."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys

import ir_v3 as ir
from study import write


def last_json(output):
    return json.loads(next(line for line in reversed(output.splitlines()) if line.startswith("{")))


def run_game(job, directory, binary, config):
    path = directory / job["id"]
    path.mkdir()
    command = [str(binary), "--config", str(config), "--seed", str(job["seed"]),
               "--ticks", "28800", "--record", str(path / "replay.bin")]
    for policy in job["roster"]:
        command.extend(["--bot", policy + ":5"])
    process = subprocess.run(command, text=True, capture_output=True)
    (path / "run.log").write_text(process.stdout + process.stderr)
    assert process.returncode == 0, (path, process.stdout, process.stderr)
    result = last_json(process.stdout)
    assert result["complete"]
    assert all(h["max_instructions"] <= 20000 and h["max_work"] <= 50000 for h in result["heroes"])
    write(path / "result.json", result)
    replay = subprocess.run([str(binary), "--replay", str(path / "replay.bin")], text=True, capture_output=True)
    (path / "replay.log").write_text(replay.stdout + replay.stderr)
    assert replay.returncode == 0, (path, replay.stdout, replay.stderr)
    audit = last_json(replay.stdout)
    assert audit["ticks"] == result["ticks"] and audit["state_hash"] == result["state_hash"]
    assert audit["hash_mismatches"] == 0
    write(path / "audit.json", audit)
    print(job["id"], "complete", result["ticks"], "ticks; exact replay", flush=True)
    return job | {"result": result, "replay_exact": True, "replay_sha256": ir.sha(path / "replay.bin")}


def main(study):
    directory = study / "integration"
    directory.mkdir()
    binary = ir.ROOT / "tmp/gota-ir/microplay-v2-20260920/integration"
    config = json.loads((ir.ROOT / "tmp/gota-ir/jordan268-counter-20260920/local-config.json").read_text())
    write(directory / "config.json", config)
    policies = {name: str(study / "policies" / (name + ".bas")) for name in ("parent", "finish", "combined")}
    jobs = []
    for seed in (920101, 920102):
        jobs.append({"id": f"{seed}-parent", "arm": "parent", "side": None, "seed": seed,
                     "roster": [policies["parent"], policies["parent"]]})
        for arm in ("finish", "combined"):
            for side in (0, 1):
                roster = [policies["parent"], policies["parent"]]
                roster[side] = policies[arm]
                jobs.append({"id": f"{seed}-{arm}-{side}", "arm": arm, "side": side, "seed": seed, "roster": roster})
    plan = {"schema": "gota-microplay-integration/1", "purpose": "Full-game activation, VM limits, and exact replay; no win gate.",
            "binary_sha256": ir.sha(binary), "instrument_sha256": ir.sha(Path(__file__)),
            "nim_sha256": ir.sha(Path(__file__).with_name("integration.nim")),
            "policies": {k: ir.sha(v) for k, v in policies.items()}, "jobs": jobs}
    write(directory / "plan.json", plan)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(run_game, job, directory, binary, directory / "config.json") for job in jobs]
        results = [future.result() for future in futures]
    write(directory / "result.json", {"complete_games": len(results), "all_replays_exact": True, "games": results,
          "max_instructions": max(h["max_instructions"] for r in results for h in r["result"]["heroes"]),
          "refinements": sum(h["refinements"] for r in results for h in r["result"]["heroes"])})


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
