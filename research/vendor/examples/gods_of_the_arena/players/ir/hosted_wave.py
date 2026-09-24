"""Historical40-pair XP study. New studies use hosted_batch.py with N episodes.

Use Metta's virtualenv. Commands are resumable; creation uses stable idempotency
keys. This runner uploads no policy and never changes a league champion.
"""
import argparse
from collections import Counter
import gzip
import importlib.util
import json
import os
from pathlib import Path
import time

import httpx

from policy_ir import digest, read, write

API = "https://softmax.com/api/observatory"
TERMINAL = {"completed", "failed", "cancelled", "error"}
HELPER = Path.home() / ".codex/skills/run-eval/scripts/eval_request.py"


class ResilientClient(httpx.Client):
    """Retry transient reads and explicitly idempotent XP creation only."""
    def request(self, method, url, **kwargs):
        if method.upper() == 'POST' and str(url) in (
                '/v2/experience-requests', '/v2/counterfactual-evals'):
            body = kwargs.get('json') or {}
            # Counterfactual defaults can exceed the user's per-request limit;
            # require an explicit paired-comparison count for that endpoint.
            count = (body.get('num_episodes', 1) if str(url) == '/v2/experience-requests'
                     else body.get('n'))
            if type(count) is not int or not 1 <= count <= 100:
                raise ValueError('XP and counterfactual requests require 1–100 games/comparisons')
        safe = method.upper() == 'GET' or (
            method.upper() == 'POST' and str(url) == '/v2/experience-requests'
            and bool((kwargs.get('json') or {}).get('idempotency_key')))
        for attempt in range(6 if safe else 1):
            try:
                response = super().request(method, url, **kwargs)
            except httpx.TransportError:
                if not safe or attempt == 5:
                    raise
            else:
                pending_artifact = (method.upper() == 'GET' and
                                    str(url).startswith('/v2/episode-requests/') and
                                    '/artifacts/' in str(url) and response.status_code == 404)
                # Completed episode status can precede publication of its logs
                # or replay. Retry that read, retaining a final404 as an error;
                # never substitute artifacts, drop a game or resubmit a seed.
                if not pending_artifact and response.status_code != 429 and response.status_code < 500:
                    return response
                if not safe or attempt == 5:
                    return response
                response.close()
            time.sleep(min(30, 2 ** (attempt + 1)))
        raise RuntimeError('Unreachable retry state')


def helper():
    path = Path(os.environ.get('GOTA_EVAL_HELPER', str(HELPER)))
    spec = importlib.util.spec_from_file_location("eval_request", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def client():
    token = os.environ.get('SOFTMAX_TOKEN')
    if not token:
        try:
            from softmax.auth import get_api_server, load_current_token
        except ImportError as error:
            raise RuntimeError('Set SOFTMAX_TOKEN through the remote secret store, or install the local softmax CLI.') from error
        token = load_current_token(server=get_api_server())
    return ResilientClient(base_url=API, headers={
        "Authorization": f"Bearer {token}"},
        timeout=120, follow_redirects=True)


def get(c, path):
    response = c.get(path)
    response.raise_for_status()
    return response.json()


def create(c, body, folder, dry_run=False):
    folder.mkdir(parents=True, exist_ok=True)
    request = folder / "request.json"
    if request.exists() and read(request) != body:
        raise ValueError("Refusing to change a frozen request")
    write(request, body)
    issues = helper().validate_body(c, body)
    if issues:
        raise ValueError(issues)
    write(folder / "dry-run.json", {"valid_live_schema": True, "body_sha256": digest(body)})
    if dry_run:
        return None
    receipt = folder / "created.json"
    if not receipt.exists():
        response = c.post("/v2/experience-requests", json=body)
        response.raise_for_status()
        write(receipt, response.json())
    return read(receipt)["id"]


def control_body(plan):
    refs = [plan["control_version"]] + [v["id"] for v in plan["opponents"]]
    return {"idempotency_key": "gota-wave-local-20260915-control40",
            "target": plan["target"], "game_config_overrides": plan["config"],
            "roster": [{"slot": -1, "player": {"policy_ref": v}} for v in refs],
            "num_episodes": plan["episodes_per_arm"],
            "notes": "Directional matched wave-local control. Forty independent generated seeds, pinned incumbent versions. Candidate reuses each effective seed and actual roster. No promotion from this batch."}


def receipts(directory, arm):
    folder = "control" if arm == "control" else "candidate-requests"
    return sorted((directory / folder).glob("*/created.json"))


def episodes(c, xreq):
    data = get(c, f"/v2/experience-requests/{xreq}/episodes")
    return data if isinstance(data, list) else data["episodes"]


def fetch(c, episode, directory, own_version):
    folder = directory / episode["id"]
    if (folder / ".done").exists():
        return
    folder.mkdir(parents=True, exist_ok=True)
    write(folder / "episode.json", episode)
    if episode["status"] != "completed":
        raise ValueError(f"Failed episode requires explicit recovery: {episode['id']}")
    base = f"/v2/episode-requests/{episode['id']}"
    for kind, name in [("results", "results.json"), ("replay", "replay.bin"), ("logs", "game.log")]:
        response = c.get(f"{base}/artifacts/{kind}")
        response.raise_for_status()
        data = response.content
        if kind == "replay" and data.startswith(b"\x1f\x8b"):
            data = gzip.decompress(data)
        temporary = folder / (name + ".tmp")
        temporary.write_bytes(data)
        temporary.replace(folder / name)
    if (folder / 'game.log').read_text().startswith('Pod logs were not captured:'):
        # Preserve the platform's capture-failure marker and retrieve the
        # game's structured per-VM status; never synthesize a successful log.
        write(folder / 'player-status.json', get(c, f'{base}/artifacts/player-status'))
    roster = episode["policy_version_ids"]
    if roster.count(own_version) != 1:
        raise ValueError("Subject must occupy exactly one seat")
    slot = roster.index(own_version)
    response = c.get(f"{base}/{own_version}/policy-logs/{slot}")
    if response.status_code == 200:
        (folder / "own-policy.log").write_bytes(response.content)
    elif response.status_code != 404:
        response.raise_for_status()
    (folder / ".done").write_text("core artifacts complete\n")


def harvest(c, directory, arm, watch):
    plan = read(directory / "plan.json")
    version = plan["control_version"] if arm == "control" else read(directory / "uploaded-version.json")["id"]
    while True:
        requests = receipts(directory, arm)
        if not requests:
            raise ValueError("No request receipts")
        total = done = fetched = 0
        for receipt in requests:
            xreq = read(receipt)["id"]
            rows = episodes(c, xreq)
            write(receipt.parent / "episodes.json", rows)
            total += len(rows)
            for ep in rows:
                if ep["status"] not in TERMINAL:
                    continue
                done += 1
                fetch(c, ep, directory / "artifacts" / xreq, version)
                fetched += 1
        write(directory / (arm + "-progress.json"), {
            "total": total, "terminal": done, "fetched": fetched, "requests": len(requests)})
        print(f"{arm}: {done}/{total} terminal; {fetched} fetched", flush=True)
        if not watch or (total == plan["episodes_per_arm"] and done == total):
            return
        time.sleep(15)


def candidate_bodies(directory):
    plan = read(directory / "plan.json")
    candidate = read(directory / "uploaded-version.json")["id"]
    xreq = read(directory / "control/batch/created.json")["id"]
    folders = sorted((directory / "artifacts" / xreq).glob("*/.done"))
    if len(folders) != plan["episodes_per_arm"]:
        raise ValueError("Control must drain and all artifacts arrive first")
    cases = []
    expected = Counter([plan["control_version"]] + [v["id"] for v in plan["opponents"]])
    for marker in folders:
        folder = marker.parent
        ep, result = read(folder / "episode.json"), read(folder / "results.json")
        if ep["status"] != "completed" or ep["coworld_id"] != plan["target"]["coworld_id"]:
            raise ValueError("Control failed or ran another build")
        roster = ep["policy_version_ids"]
        if Counter(roster) != expected:
            raise ValueError("Control roster changed")
        if "scripts: 10/10 active" not in (folder / "game.log").read_text():
            raise ValueError("Control VM validity is not established")
        slot = roster.index(plan["control_version"])
        cfg = {k: v for k, v in ep["game_config"].items() if k not in {"seed", "players", "tokens"}}
        if cfg != plan["config"]:
            raise ValueError("Effective control configuration differs from frozen plan")
        cfg["seed"] = result["seed"]
        roster = [candidate if v == plan["control_version"] else v for v in roster]
        body = {"idempotency_key": "gota-wave-local-20260915-" + ep["id"],
                "target": plan["target"], "game_config_overrides": cfg,
                "num_episodes": 1,
                "roster": [{"slot": i, "player": {"policy_ref": v}} for i, v in enumerate(roster)],
                "notes": f"Directional wave-local candidate matched to {ep['id']}; exact effective seed and seat roster; only Aaron's policy changes."}
        cases.append({"control_episode": ep["id"], "seed": result["seed"], "slot": slot, "body": body})
    if len({case["seed"] for case in cases}) != len(cases):
        raise ValueError("Control seeds are not independent")
    if Counter(case["slot"] for case in cases) != Counter({slot: 4 for slot in range(10)}):
        raise ValueError("Unexpected seat coverage")
    return sorted(cases, key=lambda case: (case["slot"], case["seed"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("command", choices=["control", "candidate", "harvest"])
    parser.add_argument("--arm", choices=["control", "candidate"], default="control")
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    with client() as c:
        if args.command == "control":
            xreq = create(c, control_body(read(args.directory / "plan.json")),
                          args.directory / "control/batch", args.dry_run)
            print(json.dumps({"arm": "control", "xreq": xreq, "dry_run": args.dry_run}), flush=True)
        elif args.command == "harvest":
            harvest(c, args.directory, args.arm, args.watch)
        else:
            cases = candidate_bodies(args.directory)
            if any(not (args.directory / "candidate-requests" / case["control_episode"] / "created.json").exists()
                   for case in cases):
                raise ValueError("New one-episode XP requests are disabled by user preference. Use hosted_batch.py with --episodes N.")
            write(args.directory / "matched-cases.json", cases)
            for case in cases:
                xreq = create(c, case["body"], args.directory / "candidate-requests" / case["control_episode"], args.dry_run)
                print(json.dumps({"arm": "candidate", "control": case["control_episode"], "xreq": xreq}), flush=True)
                if not args.dry_run:
                    time.sleep(1)


if __name__ == "__main__":
    main()
