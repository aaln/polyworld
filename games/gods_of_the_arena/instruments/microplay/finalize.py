"""Qualify final explicit-unit/budget binding against frozen v3 encounters."""
import argparse
import json
from pathlib import Path
import shutil

import ir_v4
import study


def prepare(directory, previous):
    directory.mkdir(parents=True, exist_ok=True)
    if (directory / "plan.json").exists():
        raise ValueError("Already frozen")
    plan = json.loads((previous / "plan.json").read_text())
    plan["policies"] = ir_v4.build(directory / "policies")
    shutil.copy2(previous / "encounter", directory / "encounter")
    plan["instrument_sha256"].update({name: ir_v4.sha(study.HERE / name) for name in ("ir_v4.py", "finalize.py")})
    plan["objective"] = "Implementation qualification against already observed v3 holdout; not new held-out discovery."
    plan["implementation_parent"] = str(previous)
    plan["selection"] = {"requirement": "Every encounter has identical per-tick world hashes and outcome metrics to v3.",
                         "additional": "Normal full-game VM/replay qualification for the48object budget gate."}
    study.write(directory / "plan.json", plan)


def run(directory):
    study.run(directory, "holdout", arms=("parent", "finish", "combined"))
    plan = json.loads((directory / "plan.json").read_text())
    prior = Path(plan["implementation_parent"])
    rows = json.loads((directory / "holdout-summary.json").read_text())
    old = json.loads((prior / "holdout-summary.json").read_text())
    ignore = {"trace_sha256", "max_instructions", "max_work"}
    assert [{k: v for k, v in r.items() if k not in ignore} for r in rows] == [
        {k: v for k, v in r.items() if k not in ignore} for r in old]
    study.write(directory / "equivalence.json", {"exact_state_and_outcomes": True, "encounters": len(rows),
        "ticks": len(rows) * 144, "source": str(prior), "scope": "Reused v3 cases, not independent confirmation."})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=lambda p: Path(p).resolve())
    parser.add_argument("command", choices=("prepare", "run"))
    parser.add_argument("--previous", type=lambda p: Path(p).resolve(),
                        default=ir_v4.ROOT / "tmp/gota-ir/microplay-v3-20260920")
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.directory, args.previous)
    else:
        run(args.directory)
