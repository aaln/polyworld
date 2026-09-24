"""Source-derived baseline IR and an independent, narrow BASIC lowering.

Does not import binding.py, policy_ir.py, or any existing policy IR. The shared
syntax reader checks structure; real-VM and complete-game comparisons check
execution independently. This is an independent derivation, not a blinded study.
Only the documented baseline family is recognized; unknown code fails closed.
"""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from textwrap import dedent

import basic_syntax

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SCHEMA = "gota-causal-policy/1"
PHASES = ["account", "select", "pursue", "inventory", "sustain", "equipment", "fallback"]
CONFIG = {
    "target": {"eligible": "observed_alive_enemy", "metric": "squared_tile_distance", "ties": "first_in_enumeration"},
    "inventory": {"slots": 6, "presence": "before_use_per_slot", "heal_ratio": [3, 5], "mana_ratio": [2, 5], "poison": "candidate_exists"},
    "sustain": {"budget": "decision_start_gold", "healing": [[2, 50], [1, 30]], "healing_ratio": [1, 2],
                "mana": [3, 45], "mana_ratio": [1, 2], "poison": [4, 40], "ordering": "independent_attempts"},
    "equipment": {"gate": "earlier_scan_saw_empty", "starter_gate": "earlier_scan_saw_no_gear",
                  "groups": [
                      {"name": "melee", "classes": [0, 4, 5, 9], "items": [[7,70],[5,80],[11,110],[13,150],[18,180]]},
                      {"name": "ranged", "classes": [1,6], "items": [[8,100],[14,150],[19,180]]},
                      {"name": "magic", "classes": [2,3,7,8], "items": [[12,140],[10,120],[17,170],[20,190]]}],
                  "shared": [[6,90],[9,120]], "replacement": "none", "permanent_cap": "inventory_capacity"},
    "fallback": {"guard": "no_eligible_enemy", "point": [64,64]},
}
# Typed, editable behavior parameters. Other semantics remain the baseline
# family and are validated rather than silently ignored by the compiler.
PARAMETERS = [
    ("inventory", "heal_ratio", 0), ("inventory", "heal_ratio", 1),
    ("inventory", "mana_ratio", 0), ("inventory", "mana_ratio", 1),
    ("sustain", "healing_ratio", 0), ("sustain", "healing_ratio", 1),
    ("sustain", "mana_ratio", 0), ("sustain", "mana_ratio", 1),
    ("fallback", "point", 0), ("fallback", "point", 1),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def temporal_facts(game_version=None):
    facts = {
        "self_data": "self* and worldTick are set once before each hero's VM decision; use/buy do not refresh them.",
        "queries": "object* and item* query current engine state at the call; visibility still filters objects.",
        "inventory_flags": "Presence and empty-slot flags accumulate before useItem for each slot. They are earlier observations, not current post-use/post-buy inventory.",
        "gold": "All affordability guards read starting selfGold; each buyItem checks and spends the remaining live balance.",
        "equipment": "Successful purchases refresh stats: increases in maximum HP/mana also add that increase to current HP/mana. Resource gear therefore has immediate sustain effects as well as permanent capacity.",
        "attack": "attackTarget stores an engine pursuit target if valid; accepted does not prove path reachability or damage.",
        "walk": "walkTo clears attack intent before pathfinding, including when pathfinding subsequently returns false.",
        "poison": "useItem on poison strikes the engine's current attackObjectId, not a policy-local bestId variable.",
        "failures": "A command return of zero does not universally mean no state changed. Failed walkTo can clear attack intent.",
        "memory": "Policy globals persist; baseline resets its decision-local scan variables. Engine attack/movement intent is separate persistent state.",
    }
    if game_version in ("2026.9.15.1", "2026.9.15.2", "2026.9.15.3"):
        facts.update(
            poison="Poison uses the current engine attackObjectId and checks normal attack range, visibility and structure exposure before consumption.",
            spells="Explicit castTarget/castPoint inspect live mana, charges and cooldowns. Bot automatic spells remain enabled; explicit casts share the same resources.",
            terrain="Map dimensions are exposed; static terrain is queryable through fog. Script coordinates use the current map size (116 tiles in the competition preset).",
        )
    if game_version == "2026.9.15.3":
        facts.update(combat_timing="selfAttacksLanded counts successful basic hits for the lifetime of this hero, across respawns. selfAttackCooldown is ticks to next basic hit assuming uninterrupted range, including windup/recovery; movement can cancel the swing.", combat_units="selfAttackRange and selfMoveSpeed use world units; one tile is60000 units. Object targets and velocities are visibility-filtered.")
    return facts


def derive():
    sources = [HERE.parent / "base.bas", HERE.parents[1] / "bots.nim", HERE.parents[1] / "sim.nim"]
    return {
        "schema": SCHEMA, "id": "gota_base_independent",
        "situation": {"temporal_facts": temporal_facts(), "coordinates": "integer tiles 0..127",
                      "structure_eligibility": "objectAlive includes exposure, not merely positive structure HP"},
        "belief": {"observations": "Source-derived execution facts; no recovered beliefs about opponent intent.",
                   "hypotheses": [
                       {"id":"H_timing", "claim":"Earlier inventory flags can delay replacement after the last item in a slot is consumed.","status":"untested"},
                       {"id":"H_capacity", "claim":"Permanent equipment can exhaust consumable capacity; access and win value require separate evidence.","status":"untested"}]},
        "goal": {"terminal":{"value":"destroy enemy fort; team win=1, timeout=0", "provenance":"game_contract"},
                 "interpretations":["engage a nearby eligible enemy", "sustain below fixed resource thresholds", "spend surplus on class equipment", "move toward center without an eligible enemy"],
                 "provenance":"behavioral_interpretation_not_recovered_author_intent"},
        "skill": deepcopy(CONFIG),
        "strategy": {"phases": PHASES.copy(), "arbitration":"ordered cumulative actions, not a single chosen action",
                     "dependencies":[["select","pursue"],["pursue","inventory.poison"],["inventory.presence","sustain"],
                                     ["sustain.live_spending","equipment.live_budget"],["inventory.empty_observation","equipment.gate"]]},
        "execution": {"language":"BASIC", "binding":"independent-baseline/1", "game_version":"2026.9.10.3", "command_returns":"ignored"},
        "update": {"derivation":"Manually derived from base.bas and its host/simulator; no parent IR or existing lowering templates used.",
                   "scope":"Independent construction in the same research session; not a blinded independent agent.",
                   "sources":{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sources}, "needs_review":[]},
    }


def validate(policy):
    if set(policy) != {"schema","id","situation","belief","goal","skill","strategy","execution","update"}:
        raise ValueError("independent IR requires all seven semantic layers")
    if policy["schema"] != SCHEMA or policy["execution"] != derive()["execution"]:
        raise ValueError("unsupported independent execution contract")
    if policy["strategy"] != derive()["strategy"] or policy["situation"] != derive()["situation"]:
        raise ValueError("unsupported phase, dependency or host-semantics edit")
    normalized = deepcopy(policy["skill"])
    for a,b,i in PARAMETERS:
        value = normalized[a][b][i]
        maximum = 127 if a == "fallback" else 100
        minimum = 1 if b != "point" and i == 1 else 0
        if type(value) is not int or not minimum <= value <= maximum:
            raise ValueError(f"invalid parameter {a}/{b}/{i}")
        normalized[a][b][i] = CONFIG[a][b][i]
    if normalized != CONFIG:
        raise ValueError("unmodeled baseline-family behavior; extend and test the independent binding first")


def condition(test, *body):
    return f"if {test} then\n" + "\n".join("  "+line for part in body for line in part.splitlines()) + "\nend if"


def purchase(item):
    identity, guard = item
    return condition(f"selfGold >= {guard}",f"buyItem({identity})")


def lower(config):
    """Independent lowering of semantic axes, with explicit ordered effects."""
    parts = {}
    parts["account"] = "decisions = decisions + 1"
    parts["select"] = dedent("""
        bestId = 0
        bestDistance = 2147483647
        index = 0
        while index < objectCount()
          id = objectId(index)
          if objectAlive(index) and objectTeam(index) <> selfTeam then
            dx = objectX(index) - selfX
            dy = objectY(index) - selfY
            distance = dx * dx + dy * dy
            if distance < bestDistance then
              bestDistance = distance
              bestId = id
            end if
          end if
          index = index + 1
        wend
    """).strip()
    parts["pursue"] = condition("bestId <> 0", "attackTarget(bestId)")
    inventory = config["inventory"]
    flags = [("hasHeal", [1,2]),("hasMana",[3]),("hasPoison",[4])]
    body = ["id = itemId(slot)",condition("id = 0","emptySlot = 1")]
    for name,items in flags:
        body.extend(condition(f"id = {item}",f"{name} = 1") for item in items)
    body.append(condition("id > 4","hasGear = 1"))
    for resource,group in [("Hp","heal"),("Mana","mana")]:
        numerator,denominator = inventory[group+"_ratio"]
        ids = "id = 1 or id = 2" if group == "heal" else "id = 3"
        body.append(condition(ids,condition(f"self{resource} * {denominator} < selfMax{resource} * {numerator}","useItem(slot)")))
    body.extend([condition("id = 4",condition("bestId <> 0","useItem(slot)")),"slot = slot + 1"])
    prefix = "\n".join(f"{flag} = 0" for flag in ["hasHeal","hasMana","hasPoison","hasGear","emptySlot","slot"])
    parts["inventory"] = prefix+"\nwhile slot < 6\n"+"\n".join("  "+line for part in body for line in part.splitlines())+"\nwend"
    buying = config["sustain"]
    hn,hd = buying["healing_ratio"]
    mn,md = buying["mana_ratio"]
    # Numerator 1 is rendered explicitly so the AST has a uniform editable
    # parameter position; extract() also accepts the original simplified form.
    hp_rhs = "selfMaxHp" if hn == 1 else f"selfMaxHp * {hn}"
    mp_rhs = "selfMaxMana" if mn == 1 else f"selfMaxMana * {mn}"
    parts["sustain"] = "\n".join([
        condition(f"selfHp * {hd} < {hp_rhs}",condition("hasHeal = 0",*(purchase(i) for i in buying["healing"]))),
        condition("selfMaxMana > 0",condition(f"selfMana * {md} < {mp_rhs}",condition("hasMana = 0",purchase(buying["mana"])))),
        condition("bestId <> 0",condition("hasPoison = 0",purchase(buying["poison"]))),
    ])
    gear = config["equipment"]
    groups = gear["groups"]
    body = [f"{g['name']} = 0" for g in groups]
    body.extend(condition(" or ".join(f"selfClass = {c}" for c in g["classes"]),f"{g['name']} = 1") for g in groups)
    for group in groups:
        items = group["items"]
        body.append(condition(f"{group['name']} = 1",condition("hasGear = 0",purchase(items[0])),*(purchase(i) for i in items[1:])))
    body.extend(purchase(i) for i in gear["shared"])
    parts["equipment"] = condition("emptySlot <> 0",*body)
    x,y = config["fallback"]["point"]
    parts["fallback"] = condition("bestId = 0",f"walkTo({x}, {y})")
    return parts


def compile_policy(policy):
    validate(policy)
    return "' Independent source-derived baseline; gota-causal-policy/1\n\n" + "\n\n".join(lower(policy["skill"])[name] for name in PHASES) + "\n"


def extract(source):
    """Lift unmarked baseline-family BASIC without any parent IR.

    Complete AST matching prevents accepting snippets while dropping unknown
    statements. Algebraic normalization is intentionally limited to x*1.
    """
    def explicit_one(node):
        if not isinstance(node,tuple):
            return node
        if len(node)==4 and node[:2]==("binary","<") and node[3] in [("var","selfmaxhp"),("var","selfmaxmana")]:
            return (node[0],node[1],explicit_one(node[2]),("binary","*",node[3],("int",1)))
        return tuple(explicit_one(v) for v in node)
    profile = derive()
    config = deepcopy(CONFIG)
    for index,(a,b,i) in enumerate(PARAMETERS):
        config[a][b][i] = f"param_p{index}"
    pattern = basic_syntax.parse("\n".join(lower(config).values()))
    captures = {}
    if not basic_syntax.match_template(pattern,explicit_one(basic_syntax.parse(source)),captures):
        raise ValueError("source does not completely match the independently modeled baseline family")
    if set(captures) != {f"p{i}" for i in range(len(PARAMETERS))}:
        raise ValueError("incomplete semantic parameter recovery")
    for index,(a,b,i) in enumerate(PARAMETERS):
        profile["skill"][a][b][i] = captures[f"p{index}"]
    validate(profile)
    profile["update"]["lifted_source_sha256"] = sha(source.encode())
    profile["update"]["needs_review"] = ["belief/hypotheses","goal/interpretations"]
    if explicit_one(basic_syntax.parse(compile_policy(profile))) != explicit_one(basic_syntax.parse(source)):
        raise ValueError("independent round-trip structural mismatch")
    return profile


if __name__ == "__main__":
    directory = HERE / "independent"
    directory.mkdir(exist_ok=True)
    policy = derive()
    source = compile_policy(policy)
    original = (HERE.parent / "base.bas").read_text()
    if basic_syntax.parse(source) != basic_syntax.parse(original):
        raise ValueError("independently generated baseline differs structurally")
    recovered = extract(original)
    if recovered["skill"] != policy["skill"]:
        raise ValueError("independent source recovery differs")
    (directory / "base.ir.json").write_text(json.dumps(policy,indent=2)+"\n")
    (directory / "base.generated.bas").write_text(source)
    (directory / "base.extracted.ir.json").write_text(json.dumps(recovered,indent=2)+"\n")
    print(json.dumps({"baseline_sha256":sha(original.encode()),"generated_sha256":sha(source.encode()),"full_ast_parity":True,"parent_free_extraction":True}))
