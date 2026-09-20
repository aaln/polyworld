"""Read the target league through Metta's official authenticated API client.

Use ../metta/.venv/bin/python; credentials stay in the existing Softmax login.
This script performs GET requests only and requires a new output directory.
"""

import argparse
from datetime import datetime, timezone
import json

from coworld.api_client import CoworldApiClient
from softmax.auth import get_api_server

from binding import GAME_VERSIONS
from policy_ir import digest, write


def main():
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--league", default="league_3c60897b-25cf-4b37-9d1a-8554c1198f28")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    client = CoworldApiClient.from_login(server_url=get_api_server())

    def get(name, path):
        data = json.loads(client.get_text(path))
        write(args.output / f"{name}.json", data)
        return data

    league = get("league", f"/v2/leagues/{args.league}")
    coworld = get("coworld", f"/v2/coworlds/{league['game']['coworld_id']}")
    divisions = get("divisions", f"/v2/divisions?league_id={args.league}")
    for division in divisions:
        get(f"leaderboard-{division['id']}", f"/v2/divisions/{division['id']}/leaderboard")
    # Live rounds use cursor pagination; the checked-out typed list_rounds
    # expects offset fields, so use its public get_text method for raw JSON.
    get("rounds", f"/v2/rounds?league_id={args.league}&limit=2")
    write(args.output / "snapshot.json", {
        "read_at": datetime.now(timezone.utc).isoformat(), "league_id": args.league,
        "game_version": coworld["version"], "matches_binding_version": coworld["version"] in GAME_VERSIONS,
        "files": {p.name: digest(p.read_bytes()) for p in sorted(args.output.iterdir())},
    })
    print(json.dumps({"game_version": coworld["version"], "matches_binding_version": coworld["version"] in GAME_VERSIONS,
                      "division_count": len(divisions), "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
