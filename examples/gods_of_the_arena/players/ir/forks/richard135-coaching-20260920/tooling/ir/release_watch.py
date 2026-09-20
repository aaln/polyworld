"""Read-only watcher for a change to the league's exact published executable.

Run with ../metta/.venv/bin/python. A changed manifest is a notification, not
permission to combine outcomes from different game builds.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time

from coworld.api_client import CoworldApiClient
from softmax.auth import get_api_server


def identity(coworld):
    game = coworld["manifest"]["game"]
    return {"coworld_id": coworld["id"], "game_version": coworld["version"],
            "image": game["runnable"]["image"], "source_url": game["runnable"]["source_url"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--minutes", type=int, default=30)
    args = parser.parse_args()
    args.directory.mkdir(parents=True, exist_ok=False)
    reference = identity(json.loads(args.reference.read_text()))
    deadline = time.monotonic() + args.minutes * 60
    league_id = "league_3c60897b-25cf-4b37-9d1a-8554c1198f28"
    with CoworldApiClient.from_login(server_url=get_api_server()) as client:
        while True:
            now = datetime.now(timezone.utc)
            league = json.loads(client.get_text(f"/v2/leagues/{league_id}"))
            coworld = json.loads(client.get_text(f"/v2/coworlds/{league['game']['coworld_id']}"))
            current = identity(coworld)
            status = {"read_at": now.isoformat(), "reference": reference, "current": current,
                      "changed": current != reference}
            (args.directory / "status.json").write_text(json.dumps(status, indent=2) + "\n")
            if status["changed"]:
                (args.directory / "league.json").write_text(json.dumps(league, indent=2) + "\n")
                (args.directory / "coworld.json").write_text(json.dumps(coworld, indent=2) + "\n")
                print(json.dumps(status, indent=2), flush=True)
                return
            if time.monotonic() >= deadline:
                print("No published league build change during this observation window.", flush=True)
                return
            time.sleep(min(60, max(0, deadline - time.monotonic())))


if __name__ == "__main__":
    main()
