"""Compile semantic policies, extract supported BASIC edits, and check parity.

Run with Python 3.10+; no third-party packages are required.
"""

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import sys

import basic_syntax
from independent_ir import temporal_facts
from binding import CONTRACTS, GAME_VERSIONS, PREDICATES, VERSION, guarded


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SCHEMA = "gota-semantic-policy/1"
LAYERS = ("situation", "belief", "goal", "skill", "strategy", "execution", "update")
IDENTIFIER = re.compile(r"[A-Za-z][A-Za-z0-9_]*\Z")


def digest(value):
    if not isinstance(value, bytes):
        value = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(value).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + "\n")


def fields(value, expected, context):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError(f"{context}: expected exactly {', '.join(expected)}")


def grounded(policy):
    """Derived facts never masquerade as recovered author intention."""
    operators = {s["operator"] for s in policy["skill"].values()}
    return {
        "situation": {
            "observation": "Bassy Q16.16 decimals for fractional action coordinates, integer snapshot tiles and IDs; six inventory slots; shared public hero draft.",
            "structure_alive": "For structures objectAlive means exposed; positive HP means standing.",
            "predicates": {r["when"]: PREDICATES[r["when"]][2] for r in policy["strategy"]},
        },
        "belief": {
            "memory": sorted({m for op in operators for m in CONTRACTS[op].memory}),
            "lifetime": "BASIC globals start at zero per episode and persist across decisions and respawns. "
                        "join_wave revalidates an escort by observed living ID whenever selected.",
            "uncertainty": ("Unseen enemies are unobserved. Visible object target IDs are exposed; zero can mean no target or a target outside visibility. Future enemy intentions remain unknown." if policy["execution"]["game_version"] == "2026.9.15.3" else "Unseen enemies are unknown. Visible targets may be masked. Only the draft roster, allied positions and visible opponents inform live choices."),
        },
        "skills": {name: {"meaning": CONTRACTS[s["operator"]].meaning,
                           "parameters": s["parameters"],
                           "actions": list(CONTRACTS[s["operator"]].actions)}
                   for name, s in policy["skill"].items()},
        "temporal_execution": {"facts": temporal_facts(policy["execution"]["game_version"]),
                               "rule_order": [r["id"] for r in policy["strategy"]],
                               "action_arbitration": "Rules execute in order; multiple commands can affect shared engine state during one decision."},
    }


def refresh_grounding(policy):
    facts = grounded(policy)
    policy["situation"]["grounded"] = facts["situation"]
    policy["belief"]["grounded"] = facts["belief"]


def validate(policy):
    fields(policy, ("schema", "id", *LAYERS), "policy")
    if policy["schema"] != SCHEMA or not IDENTIFIER.fullmatch(policy["id"]):
        raise ValueError("unsupported policy schema or invalid ID")
    fields(policy["execution"], ("binding", "game_version", "language"), "execution")
    if (policy["execution"]["binding"] != VERSION or policy["execution"]["language"] != "BASIC"
            or policy["execution"]["game_version"] not in GAME_VERSIONS):
        raise ValueError("execution binding/version mismatch")
    fields(policy["situation"], ("grounded", "notes"), "situation")
    fields(policy["belief"], ("grounded", "claims"), "belief")
    fields(policy["update"], ("revision", "parent", "change", "needs_review", "evidence"), "update")
    if type(policy["update"]["revision"]) is not int or policy["update"]["revision"] < 0:
        raise ValueError("revision must be a nonnegative integer")
    if not isinstance(policy["update"]["needs_review"], list) or not isinstance(policy["update"]["evidence"], list):
        raise ValueError("update reviews and evidence must be lists")
    for name, goal in policy["goal"].items():
        fields(goal, ("preference", "provenance"), f"goal {name}")
        if goal["provenance"] not in ("authored", "interpretation", "unknown"):
            raise ValueError("goal provenance must identify authorship/interpretation/unknown")
    for name, belief in policy["belief"]["claims"].items():
        fields(belief, ("claim", "status", "evidence"), f"belief {name}")
        if belief["status"] not in ("untested", "supported", "contradicted", "requires_review"):
            raise ValueError("invalid belief status")
    for name, skill in policy["skill"].items():
        fields(skill, ("operator", "parameters"), f"skill {name}")
        if skill["operator"] not in CONTRACTS:
            raise ValueError(f"unsupported operator: {skill['operator']}")
        if skill["operator"] in ("confirmed_hit_kite", "targeted_hit_kite", "spell_hit_kite", "motion_feedback", "cadence_motion", "tower_detour", "opportunity_enemy") and policy["execution"]["game_version"] != "2026.9.15.3":
            raise ValueError("confirmed_hit_kite requires the published 2026.9.15.3 combat observations")
        CONTRACTS[skill["operator"]].source(skill["parameters"])
        if skill['operator'] in ('motion_feedback', 'cadence_motion') and skill['parameters']['min_ticks'] > skill['parameters']['max_ticks']:
            raise ValueError('minimum retreat duration exceeds its maximum')
        if skill["operator"] == "buy_ordered_loadout" and len(set(skill["parameters"].values())) != 5:
            raise ValueError("ordered loadout requires five distinct equipment items")
    if not policy["strategy"]:
        raise ValueError("strategy must contain rules")
    seen, used, available = set(), set(), set()
    for rule in policy["strategy"]:
        fields(rule, ("id", "when", "skill", "for"), "strategy rule")
        if not IDENTIFIER.fullmatch(rule["id"]) or rule["id"] in seen:
            raise ValueError("rule IDs must be unique identifiers")
        seen.add(rule["id"])
        if rule["when"] not in PREDICATES or rule["skill"] not in policy["skill"]:
            raise ValueError(f"unbound rule: {rule['id']}")
        if not rule["for"] or any(g not in policy["goal"] for g in rule["for"]):
            raise ValueError(f"rule {rule['id']} needs explicit goal references")
        used.add(rule["skill"])
        op = CONTRACTS[policy["skill"][rule["skill"]]["operator"]]
        required = set(op.reads) | set(PREDICATES[rule["when"]][1])
        if not required <= available:
            raise ValueError(f"{rule['id']} reads facts before unconditional observation: {required - available}")
        if rule["when"] == "always":
            available.update(op.writes)
    if used != set(policy["skill"]):
        raise ValueError("unused skills would have no executable counterpart")
    facts = grounded(policy)
    for layer in ("situation", "belief"):
        if policy[layer]["grounded"] != facts[layer]:
            raise ValueError(f"{layer} grounding drift: run refresh after a deliberate IR edit")
    return policy


def compile_policy(policy):
    validate(policy)
    lines = [f"' Generated from {policy['id']}; {SCHEMA}; {VERSION}",
             "' @rule comments identify regions only; the extractor reads all executable statements."]
    for rule in policy["strategy"]:
        skill = policy["skill"][rule["skill"]]
        body = CONTRACTS[skill["operator"]].source(skill["parameters"])
        condition = PREDICATES[rule["when"]][0]
        if condition is not None:
            body = guarded(condition, body)
        lines.extend(["", f"' @rule {rule['id']}", body])
    source = "\n".join(lines) + "\n"
    if len(source.encode()) > 65536:
        raise ValueError("generated BASIC exceeds the host's 64 KiB limit")
    return source


def executable(policy):
    return {"execution": policy["execution"], "skill": policy["skill"],
            "strategy": [{k: r[k] for k in ("id", "when", "skill")} for r in policy["strategy"]]}


def differences(before, after, path=""):
    if isinstance(before, dict) and isinstance(after, dict):
        result = []
        for key in sorted(before.keys() | after.keys()):
            result.extend(differences(before.get(key), after.get(key), f"{path}/{key}"))
        return result
    if before != after:
        return [{"path": path, "before": before, "after": after}]
    return []


def extract(source, parent):
    """Recover supported behavior; parent supplies identity and attributed rationale.

    Region labels are not semantic evidence. Each region must completely match
    exactly one skill/guard contract. No command or statement may be ignored.
    Unmarked baseline-family BASIC can also be lifted by the independent
    source-derived reader. Unknown statements still fail closed.
    """
    validate(parent)
    regions = []
    current = []
    for line in source.splitlines():
        marker = re.fullmatch(r"\s*'\s*@rule\s+([A-Za-z][A-Za-z0-9_]*)\s*", line)
        if marker:
            if not regions and basic_syntax.parse("\n".join(current)):
                raise ValueError("unaccounted-for code before the first rule")
            if regions:
                regions[-1][1].extend(current)
            regions.append((marker[1], []))
            current = []
        else:
            current.append(line)
    if not regions:
        if basic_syntax.parse(source) != basic_syntax.parse(compile_policy(parent)):
            from independent_ir import extract as lift, lower
            recovered = lift(source)
            parts = lower(recovered["skill"])
            rules = {"account":"R0", "select":"R1", "pursue":"R2", "inventory":"E0",
                     "sustain":"E1", "equipment":"E2", "fallback":"R4"}
            marked = "\n".join(f"' @rule {rules[name]}\n{body}" for name,body in parts.items())
            if basic_syntax.parse(marked) != basic_syntax.parse(source):
                raise ValueError("independent lift changed the input structure")
            return extract(marked,parent)
        return deepcopy(parent)
    regions[-1][1].extend(current)
    result = deepcopy(parent)
    result["strategy"], result["skill"] = [], {}
    parent_rules = {r["id"]: r for r in parent["strategy"]}
    seen = set()
    for rule_id, lines in regions:
        if rule_id in seen:
            raise ValueError(f"duplicate rule region: {rule_id}")
        seen.add(rule_id)
        actual = basic_syntax.parse("\n".join(lines))
        matches = []
        for predicate, (condition, _, _) in PREDICATES.items():
            for operator, spec in CONTRACTS.items():
                template = spec.template if condition is None else guarded(condition, spec.template)
                parameters = {}
                if basic_syntax.match_template(basic_syntax.parse(template), actual, parameters):
                    spec.source(parameters)  # enforce parameter bounds, including repeated captures
                    matches.append((predicate, operator, parameters))
        if len(matches) != 1:
            raise ValueError(f"{rule_id}: expected one complete supported contract, found {len(matches)}; "
                             "extend the binding with a tested semantic operator for new control flow")
        predicate, operator, parameters = matches[0]
        old = parent_rules.get(rule_id)
        name = old["skill"] if old else f"skill_{rule_id}"
        skill = {"operator": operator, "parameters": parameters}
        if name in result["skill"] and result["skill"][name] != skill:
            raise ValueError(f"shared skill {name} diverged between rule instances; split it explicitly in IR")
        result["skill"][name] = skill
        if old:
            goals = old["for"]
        else:
            result["goal"][f"unknown_{rule_id}"] = {"preference": None, "provenance": "unknown"}
            goals = [f"unknown_{rule_id}"]
        result["strategy"].append({"id": rule_id, "when": predicate, "skill": name, "for": goals})
    refresh_grounding(result)
    changes = differences(executable(parent), executable(result))
    if changes:
        result["update"] = {
            "revision": parent["update"]["revision"] + 1, "parent": digest(parent),
            "change": {"origin": "symbolic_extraction", "behavior_changes": changes},
            "needs_review": sorted(set(parent["update"]["needs_review"]) |
                                   {"goal/" + g for g in result["goal"]} |
                                   {"belief/" + b for b in result["belief"]["claims"]}),
            "evidence": [],
        }
        for belief in result["belief"]["claims"].values():
            belief["status"] = "requires_review"
    validate(result)
    if basic_syntax.parse(compile_policy(result)) != basic_syntax.parse(source):
        raise ValueError("extraction failed full-program structural parity")
    return result


def bundle(policy, directory):
    """Freeze a reviewable research revision and both directions of the round trip."""
    source = compile_policy(policy)
    recovered = extract(source, policy)
    if executable(recovered) != executable(policy):
        raise ValueError("round-trip executable parity failed")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    write(directory / "policy.ir.json", policy)
    (directory / "policy.bas").write_text(source)
    write(directory / "extracted.ir.json", recovered)
    write(directory / "semantics.json", grounded(recovered))
    dependencies = [HERE / n for n in ("binding.py", "basic_syntax.py", "policy_ir.py", "independent_ir.py")]
    dependencies += [ROOT / "examples/gods_of_the_arena" / n for n in ("bots.nim", "sim.nim", "content.nim")]
    dependencies += [ROOT / "src/polyworld/basic.nim", ROOT / "coworld/dependencies.lock"]
    manifest = {
        "schema": SCHEMA, "policy_sha256": digest(policy), "executable_sha256": digest(executable(policy)),
        "source_sha256": digest(source.encode()), "structural_parity": True,
        "intent_parity": "authored claims require scenario and episode evidence; not inferred from BASIC",
        "dependencies": {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in dependencies},
        "artifacts": {p.name: digest(p.read_bytes()) for p in sorted(directory.iterdir())},
    }
    write(directory / "manifest.json", manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("compile", "bundle", "refresh"):
        command = commands.add_parser(name)
        command.add_argument("ir", type=Path)
        command.add_argument("output", type=Path)
    for name in ("extract", "check"):
        command = commands.add_parser(name)
        command.add_argument("source", type=Path)
        command.add_argument("--parent", type=Path, required=True)
        if name == "extract":
            command.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "compile":
            args.output.write_text(compile_policy(read(args.ir)))
        elif args.command == "refresh":
            policy = read(args.ir)
            refresh_grounding(policy)
            write(args.output, validate(policy))
        elif args.command == "bundle":
            print(json.dumps(bundle(read(args.ir), args.output), indent=2))
        else:
            parent = read(args.parent)
            recovered = extract(args.source.read_text(), parent)
            if args.command == "extract":
                write(args.output, recovered)
            else:
                changes = differences(executable(parent), executable(recovered))
                print(json.dumps({"parity": not changes, "behavior_changes": changes}, indent=2))
                return int(bool(changes))
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(f"IR error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
