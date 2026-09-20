"""Audit every hosted tape and feed the completed paired evidence into the IR."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
import math
from pathlib import Path
import re
import subprocess
import time

from policy_ir import HERE, bundle, compile_policy, digest, extract, read, write


def verify_vm_validity(folder):
    """Require all ten VMs, using the game's equivalent structured status if logs were lost.

    Published .3 sets each status exit_code from the same sticky BASIC failure
    flag reported by the headless VM summary. A completed API episode alone is
    insufficient: the game can continue after disabling an individual VM.
    """
    log = (folder / 'game.log').read_text()
    active = re.findall(r'scripts: (\d+)/10 active', log)
    proof = {'log_sha256': digest((folder / 'game.log').read_bytes())}
    if active:
        if active[-1] != '10':
            raise ValueError('A BASIC VM was disabled')
        proof['method'] = 'headless_summary'
    elif log.startswith('Pod logs were not captured:') and (folder / 'player-status.json').exists():
        status = read(folder / 'player-status.json')
        players = status.get('players', [])
        if (status.get('schema_version') != '1' or len(players) != 10 or
                sorted(p.get('slot', -1) for p in players) != list(range(10)) or
                any(p.get('state') != 'exited' or p.get('exit_code') != 0 or
                    p.get('reason') != 'Completed' for p in players)):
            raise ValueError('Structured status does not prove ten successful BASIC VMs')
        proof.update(method='structured_player_status_after_log_capture_failure',
                     status_sha256=digest((folder / 'player-status.json').read_bytes()))
    else:
        raise ValueError('Final VM validity missing')
    write(folder / 'vm-validity.json', proof)


def verify(folder, binary, binary_hash):
    ep, result = read(folder / "episode.json"), read(folder / "results.json")
    tape = folder / "replay.bin"
    sha = digest(tape.read_bytes())
    dest = folder / "audit.json"
    if not dest.exists():
        proc = subprocess.run([str(binary), "--replay", str(tape.resolve())],
                              capture_output=True, text=True, timeout=600)
        (folder / "audit.stderr.log").write_text(proc.stderr)
        if proc.returncode:
            raise ValueError(f"Replay audit failed: {ep['id']}")
        audit = json.loads(proc.stdout.splitlines()[-1])
        audit.update(binary_sha256=binary_hash, replay_sha256=sha)
        write(dest.with_suffix(".tmp"), audit)
        dest.with_suffix(".tmp").replace(dest)
    audit = read(dest)
    if (audit["binary_sha256"] != binary_hash or audit["replay_sha256"] != sha
            or audit["hash_mismatches"] or audit["ticks"] != result["ticks"]
            or audit["recorded_ticks"] != result["ticks"]
            or audit["actions_consumed"] != audit["recorded_actions"]
            or audit["seed"] != result["seed"]):
        raise ValueError("Incomplete or mismatched replay")
    if ep["status"] != "completed":
        raise ValueError("Incomplete episode")
    verify_vm_validity(folder)
    if [h["score"] for h in audit["heroes"]] != result["scores"]:
        raise ValueError("Replay and result scores disagree")
    if {p["position"]: p["score"] for p in ep["participant_scores"]} != dict(enumerate(result["scores"])):
        raise ValueError("API and result scores disagree")
    return ep["id"]


def compare(directory):
    plan = read(directory / "plan.json")
    cases = read(directory / "matched-cases.json")
    candidate = read(directory / "uploaded-version.json")["id"]
    control_xreq = read(directory / "control/batch/created.json")["id"]
    pairs = []
    for case in cases:
        control_folder = directory / "artifacts" / control_xreq / case["control_episode"]
        candidate_xreq = read(directory / "candidate-requests" / case["control_episode"] / "created.json")["id"]
        folders = list((directory / "artifacts" / candidate_xreq).glob("*/.done"))
        if len(folders) != 1:
            raise ValueError("Each pair needs exactly one complete candidate episode")
        candidate_folder = folders[0].parent
        rows = []
        for folder, own in [(control_folder, plan["control_version"]), (candidate_folder, candidate)]:
            ep, result, audit = [read(folder / name) for name in ["episode.json", "results.json", "audit.json"]]
            roster = ep["policy_version_ids"]
            if roster.count(own) != 1 or roster.index(own) != case["slot"]:
                raise ValueError("Subject seat changed")
            cfg = {k: v for k, v in ep["game_config"].items() if k not in {"seed", "players", "tokens"}}
            if (ep["coworld_id"] != plan["target"]["coworld_id"] or ep["coworld_version"] != plan["game_version"]
                    or result["seed"] != case["seed"] or cfg != plan["config"]):
                raise ValueError("Game build, effective seed or engine config changed")
            hero = audit["heroes"][case["slot"]]
            rows.append({"episode": ep["id"], "seed": result["seed"], "slot": case["slot"],
                         "class": hero["class"], "score": result["scores"][case["slot"]],
                         "ticks": result["ticks"], "timeout": result["outcome"] == "time_limit",
                         "deaths": hero["deaths"], "first_gear_tick": hero["first_gear_tick"],
                         "commands": hero["command_attempts_by_kind"],
                         "roster": ["<subject>" if v == own else v for v in roster],
                         "artifacts": {name: digest((folder / name).read_bytes()) for name in
                                       ["episode.json", "results.json", "audit.json", "replay.bin", "game.log"]}})
        if rows[0]["roster"] != rows[1]["roster"]:
            raise ValueError("Opponents or teammates differ between arms")
        pairs.append({"control": rows[0], "candidate": rows[1], "delta": rows[1]["score"] - rows[0]["score"]})
    if len(pairs) != 40 or len({p["control"]["seed"] for p in pairs}) != 40:
        raise ValueError("Incomplete or repeated independent cases")
    if Counter(p["control"]["slot"] for p in pairs) != Counter({slot: 4 for slot in range(10)}):
        raise ValueError("Incomplete class coverage")
    wins = {arm: sum(p[arm]["score"] for p in pairs) for arm in ["control", "candidate"]}
    positive, negative = (sum(p["delta"] == value for p in pairs) for value in [1, -1])
    discordant = positive + negative
    p_value = sum(math.comb(discordant, k) for k in range(positive, discordant + 1)) / 2 ** discordant
    report = {"rung": "directional", "promotion_eligible": False, "game_version": plan["game_version"],
              "episodes_per_arm": 40, "independent_pairs": 40, "audited_games": 80,
              "candidate_source_sha256": plan["candidate_source_sha256"], "wins": wins,
              "paired_win_delta": (wins["candidate"] - wins["control"]) / 40,
              "positive_pairs": positive, "negative_pairs": negative, "paired_exact_one_sided_p": p_value,
              "verdict": "directionally_promising" if positive > negative else "no_demonstrated_improvement",
              "timeouts": {arm: sum(p[arm]["timeout"] for p in pairs) for arm in wins},
              "bought_equipment_cases": {arm: sum(p[arm]["first_gear_tick"] >= 0 for p in pairs) for arm in wins},
              "class_wins": {name: {arm: sum(p[arm]["score"] for p in pairs if p[arm]["class"] == name) for arm in wins}
                             for name in sorted({p["control"]["class"] for p in pairs})},
              "limitations": plan["limitations"], "pairs": pairs}
    path = HERE / "wave-local-hosted-20260915.json"
    write(path, report)
    policy_path = HERE / "hypotheses/wave_local_balance.evaluated.ir.json"
    policy = read(policy_path)
    original_basic = compile_policy(policy)
    if digest(original_basic.encode()) != plan["candidate_source_sha256"]:
        raise ValueError("Current IR no longer produces the tested candidate")
    updated = deepcopy(policy)
    ref = {"artifact": str(path), "sha256": digest(path.read_bytes())}
    updated["belief"]["claims"]["B_wave_hosted"] = {
        "claim": f"On published {plan['game_version']}, forty matched independent incumbent games yielded {wins['candidate']} candidate fort wins versus {wins['control']} unchanged v2 wins. All80 replay state sequences matched. This is directional evidence on one frozen roster; superiority is unconfirmed.",
        "status": "requires_review", "evidence": [ref]}
    updated["update"]["revision"] += 1
    updated["update"]["parent"] = digest(policy)
    updated["update"]["change"] = {"origin": "hosted_xp_feedback", "verdict": report["verdict"]}
    updated["update"]["evidence"].append(ref)
    if compile_policy(updated) != original_basic or extract(original_basic, updated) != updated:
        raise ValueError("Hosted feedback broke IR/BASIC parity")
    bundle(updated, directory / "evaluated")
    write(policy_path, updated)
    (HERE / "hypotheses/wave_local_balance.evaluated.bas").write_text(original_basic)
    write(directory / "result.json", report)
    print(json.dumps({k: v for k, v in report.items() if k != "pairs"}, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    d = args.directory.resolve()
    binary = d / "audit"
    sha = digest(binary.read_bytes())
    write(d / "audit-provenance.json", {"binary_sha256": sha,
          "source_sha256": digest((d / "audit_hosted_wave.nim").read_bytes()),
          "game_source": read(d / "plan.json")["game_source"]})
    attempted, verified, pending = set(), set(), {}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        while len(verified) < 80:
            for future, folder in list(pending.items()):
                if future.done():
                    verified.add(future.result())
                    del pending[future]
                    print(f"Hosted replay audits: {len(verified)}/80 verified", flush=True)
            for marker in sorted((d / "artifacts").glob("*/*/.done")):
                folder = marker.parent
                if folder in attempted or len(pending) >= args.workers:
                    continue
                attempted.add(folder)
                pending[pool.submit(verify, folder, binary, sha)] = folder
            time.sleep(1)
    compare(d)


if __name__ == "__main__":
    main()
