#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx", "pyyaml"]
# ///
"""
eval_request.py — create and monitor hosted eval batches (experience requests).

The platform contract this script encodes (verified live 2026-07-15):
  * POST /v2/experience-requests takes a roster-shaped body; `roster` is the
    only required field and additionalProperties is false — a stray key 4xxs.
  * The authoritative schema is the LIVE OpenAPI at
    <server>/api/observatory/openapi.json. When a call starts 4xxing,
    re-derive the body from there; don't retry blind.

Subcommands:
  resolve  --policy NAME[:vN]            -> policy_version id (latest if no :vN)
  create   BODY.json [--dry-run]         -> validate against live schema; POST unless --dry-run
  get      XREQ_ID                       -> request status summary
  episodes XREQ_ID [--json]              -> per-episode status/scores table
  monitor  XREQ_ID [--interval N]        -> poll until all episodes terminal

Auth: reads the softmax CLI's stored token (run `softmax login` first).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import httpx

# The Observatory v2 API base (verified live 2026-07-15: /v2/* routes 404 on
# the bare /api base; they live under /api/observatory).
DEFAULT_SERVER = "https://softmax.com/api/observatory"
OPENAPI_PATH = "/openapi.json"

TERMINAL = {"completed", "failed", "cancelled", "error"}


# ---------- auth ----------

def load_token() -> str:
    """Read the current softmax auth token.

    The auth library has renamed over time; try the import paths in order,
    then fall back to the credentials file directly.
    """
    try:
        from softmax.auth import load_current_token  # type: ignore
        return load_current_token(server="https://softmax.com")
    except Exception:
        pass
    try:
        from softmax.auth import load_current_cogames_token  # type: ignore
        return load_current_cogames_token()
    except Exception:
        pass
    creds = Path.home() / ".softmax" / "credentials.yaml"
    if creds.exists():
        import yaml
        data = yaml.safe_load(creds.read_text()) or {}
        tokens = data.get("tokens") or {}
        # keyed by API server URL; prefer the softmax.com entry, else any
        for server, tok in tokens.items():
            if "softmax.com" in server and tok:
                return tok
        for tok in tokens.values():
            if tok:
                return tok
    sys.exit("No softmax credentials found — run `softmax login` first.")


def client(server: str) -> httpx.Client:
    return httpx.Client(
        base_url=server,
        headers={"Authorization": f"Bearer {load_token()}"},
        timeout=60.0,
    )


# ---------- schema validation (the dry-run) ----------

def validate_body(c: httpx.Client, body: dict) -> list[str]:
    """Check a request body against the LIVE OpenAPI schema.

    Shallow but catches the failure modes that actually happen: unknown keys
    (additionalProperties: false), missing required fields, and wrong
    top-level types. Deep per-field validation is the server's job.
    """
    spec = c.get(OPENAPI_PATH).json()
    post = spec["paths"]["/v2/experience-requests"]["post"]
    ref = post["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    schema = spec["components"]["schemas"][ref.split("/")[-1]]

    problems: list[str] = []
    allowed = set(schema.get("properties", {}))
    for key in body:
        if key not in allowed:
            problems.append(f"unknown key {key!r} (allowed: {sorted(allowed)})")
    for req in schema.get("required", []):
        if req not in body:
            problems.append(f"missing required key {req!r}")
    if "roster" in body and not isinstance(body["roster"], list):
        problems.append("`roster` must be a list of seat entries")
    return problems


# ---------- subcommands ----------

def cmd_resolve(c: httpx.Client, args: argparse.Namespace) -> None:
    name, _, ver = args.policy.partition(":")
    r = c.get("/v2/policy-versions", params={"q": name, "mine": True, "limit": 200})
    r.raise_for_status()
    data = r.json()
    rows = data if isinstance(data, list) else data.get("policy_versions", data.get("items", []))
    matches = [v for v in rows if (v.get("policy_name") or v.get("name")) == name]
    if not matches:
        seen = sorted({v.get("policy_name") or v.get("name", "?") for v in rows})
        sys.exit(f"No policy named {name!r} among yours. Nearby: {seen[:10]}")

    def vnum(v: dict) -> int:
        raw = v.get("version") or v.get("version_number") or 0
        return int(str(raw).lstrip("v") or 0)

    if ver:
        want = int(ver.lstrip("v"))
        hits = [v for v in matches if vnum(v) == want]
        if not hits:
            sys.exit(f"{name} has no version {ver} (latest: v{max(map(vnum, matches))})")
        chosen = hits[0]
    else:
        chosen = max(matches, key=vnum)
    print(json.dumps({
        "policy": name,
        "version": f"v{vnum(chosen)}",
        "policy_version_id": chosen.get("id") or chosen.get("policy_version_id"),
    }, indent=2))


def cmd_create(c: httpx.Client, args: argparse.Namespace) -> None:
    body = json.loads(Path(args.body).read_text())
    problems = validate_body(c, body)
    if problems:
        print("Body fails the live schema:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        sys.exit(1)
    if args.dry_run:
        print("Dry run OK — body validates against the live schema. Not POSTed.")
        return
    r = c.post("/v2/experience-requests", json=body, timeout=120.0)
    if r.status_code >= 400:
        sys.exit(f"POST failed {r.status_code}: {r.text[:500]}\n"
                 f"Re-derive the body from {OPENAPI_PATH}; don't retry blind.")
    data = r.json()
    xreq = data.get("id") or data.get("experience_request_id")
    print(json.dumps({"created": xreq, "response": data}, indent=2, default=str))


def fetch_request(c: httpx.Client, xreq: str) -> dict:
    r = c.get(f"/v2/experience-requests/{xreq}")
    r.raise_for_status()
    return r.json()


def fetch_episodes(c: httpx.Client, xreq: str) -> list[dict]:
    r = c.get(f"/v2/experience-requests/{xreq}/episodes")
    if r.status_code == 404:  # some deployments expose episodes only via query
        r = c.get("/v2/episodes", params={"episode_request_id": xreq})
    r.raise_for_status()
    data = r.json()
    return data if isinstance(data, list) else data.get("episodes", [])


def cmd_get(c: httpx.Client, args: argparse.Namespace) -> None:
    print(json.dumps(fetch_request(c, args.xreq), indent=2, default=str))


def episode_rows(eps: list[dict]) -> tuple[int, int, list[str]]:
    lines, done = [], 0
    for e in eps:
        status = e.get("status", "?")
        if status in TERMINAL:
            done += 1
        scores = e.get("scores") or e.get("results", {}).get("scores") or ""
        lines.append(f"  {e.get('id', '?'):<40} {status:<12} {scores}")
    return done, len(eps), lines


def cmd_episodes(c: httpx.Client, args: argparse.Namespace) -> None:
    eps = fetch_episodes(c, args.xreq)
    if args.json:
        print(json.dumps(eps, indent=2, default=str))
        return
    done, total, lines = episode_rows(eps)
    print(f"{args.xreq}: {done}/{total} terminal")
    print("\n".join(lines))


def cmd_monitor(c: httpx.Client, args: argparse.Namespace) -> None:
    while True:
        eps = fetch_episodes(c, args.xreq)
        done, total, _ = episode_rows(eps)
        print(f"{time.strftime('%H:%M:%S')} {args.xreq}: {done}/{total} terminal", flush=True)
        if total and done == total:
            print("All episodes terminal.")
            return
        time.sleep(args.interval)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--server", default=DEFAULT_SERVER)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("resolve"); p.add_argument("--policy", required=True); p.set_defaults(fn=cmd_resolve)
    p = sub.add_parser("create"); p.add_argument("body"); p.add_argument("--dry-run", action="store_true"); p.set_defaults(fn=cmd_create)
    p = sub.add_parser("get"); p.add_argument("xreq"); p.set_defaults(fn=cmd_get)
    p = sub.add_parser("episodes"); p.add_argument("xreq"); p.add_argument("--json", action="store_true"); p.set_defaults(fn=cmd_episodes)
    p = sub.add_parser("monitor"); p.add_argument("xreq"); p.add_argument("--interval", type=int, default=30); p.set_defaults(fn=cmd_monitor)

    args = ap.parse_args()
    with client(args.server) as c:
        args.fn(c, args)


if __name__ == "__main__":
    main()
