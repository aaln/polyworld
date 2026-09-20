"""Prospective followup after the v1 non-activation result; no old data pooled."""
import argparse
import json
from pathlib import Path

import ir_v2
import study

original_fixtures = study.fixtures


def fixtures(partition):
    cases = original_fixtures(partition)
    for case in cases:
        subject = next(a for a in case["actors"] if a["controller"] == "subject")
        x, y = subject["x"], subject["y"]
        direction = 1 if case["side"] == 0 else -1
        dy = 1 if partition == "discovery" else -1
        for actor in case["actors"]:
            if actor["slot"] // 5 != case["side"]:
                actor["x"] = x + direction
                actor["y"] = y if actor["slot"] % 5 == 0 else y + dy
            elif actor is not subject:
                actor["x"] = x
                actor["y"] = y + dy
        case["id"] = case["id"].replace(partition + "/", partition + "/tight/", 1)
    return cases


study.ir = ir_v2
study.fixtures = fixtures

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=lambda p: Path(p).resolve())
    parser.add_argument("command", choices=("prepare", "discovery", "holdout", "evaluate", "audit"))
    parser.add_argument("--partition", choices=("discovery", "holdout"), default="discovery")
    args = parser.parse_args()
    if args.command == "prepare":
        study.prepare(args.directory)
        path = args.directory / "plan.json"
        plan = json.loads(path.read_text())
        plan["instrument_sha256"].update({name: ir_v2.sha(study.HERE / name)
                                           for name in ("ir_v2.py", "study_v2.py")})
        plan["predecessor"] = {"study": "microplay-20260920", "outcome": "No target refinements in256encounters; no qualifier."}
        study.write(path, plan)
    elif args.command in ("discovery", "holdout"):
        study.run(args.directory, args.command)
        study.evaluate(args.directory, args.command)
    elif args.command == "evaluate":
        study.evaluate(args.directory, args.partition)
    else:
        study.run(args.directory, args.partition, audit=True)
