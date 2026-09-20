"""Explicit engine units and bounded VM cost for the qualified local skills.

Erratum: WorldScale is 60,000, not 100,000. The v2/v3 arithmetic happened to
use 60% of true attack reach. Retain that measured behavior explicitly, rather
than silently expanding reach and attributing old evidence to a new policy.
"""
from dataclasses import replace
import json
from pathlib import Path

import ir_v3
from ir_v3 import ROOT, PARENT, binding, compiler, sha

old = binding.CONTRACTS["microplay_local_target_v3"]
body = old.template.replace("mpRange = selfAttackRange / 1000",
                            "mpRange = selfAttackRange * param_range_percent / 60000")
source = "mpOriginal = bestId\nmpPick = 0\nmpAssist = 0\nif objectCount() <= param_object_limit then\n"
source += "\n".join("  " + line for line in body.splitlines()) + "\nend if"
binding.CONTRACTS["microplay_local_target_v4"] = replace(
    old, template=source,
    parameters=old.parameters | {"range_percent": (60, 60, 100), "object_limit": (48, 16, 64)},
    meaning="Refine an existing hero/creep engagement, preserving structures and no-target "
    "macro choices. WorldScale=60000 engine units per tile. With range_percent=60, "
    "use the empirically tested inner60percent of basic reach, rounded down to hundredths "
    "of a tile. Candidate position uncertainty is bounded by abs(tile_delta)+1 on each axis. "
    "Prefer a visible living enemy HERO at most one own basic hit from death; otherwise "
    "consider the visible target of the lowest-ID nearby lower-ID ally. If the original "
    "enemy visibly targets self, assist only when that ally has less than half self's HP. "
    "Finishing precedes assistance; HP is current, not an impact prediction. objectTarget "
    "is intent, not a landed hit; zero can be ambiguous. Revalidate each decision, no memory "
    "through fog. If public object count exceeds object_limit, preserve parent selection to "
    "bound additional VM cost. Within that gate scan at most64objects. No actions, movement, "
    "spells, inventory changes, taunt, predicted damage or private data. Selected bestId "
    "and squared tile bestDistance feed the existing attack controller. Range60/object48 "
    "are the qualified configuration; changed parameters require new evidence. The earlier "
    "range-unit explanation was wrong; its raw observations and executable arithmetic are "
    "preserved as historical evidence with this explicit erratum.")


def make_policy(name, finish, assist):
    policy = ir_v3.make_policy(name, finish, assist)
    if name != "parent":
        policy["id"] = "gota_microplay_" + name + "_v4"
        policy["skill"]["microplay"]["operator"] = "microplay_local_target_v4"
        policy["skill"]["microplay"]["parameters"].update(range_percent=60, object_limit=48)
        policy["update"]["change"] += " Explicit 60percent reach and48object VM budget gate; units corrected."
        compiler.refresh_grounding(policy)
        compiler.validate(policy)
    return policy


def build(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    result = {}
    for name, finish, assist in [("parent", 0, 0), ("finish", 1, 0), ("combined", 1, 1)]:
        policy = make_policy(name, finish, assist)
        source = compiler.compile_policy(policy)
        assert compiler.extract(source, policy) == policy
        (directory / (name + ".ir.json")).write_text(json.dumps(policy, indent=2) + "\n")
        (directory / (name + ".bas")).write_text(source)
        result[name] = {"ir_sha256": compiler.digest(policy), "basic_sha256": sha(directory / (name + ".bas")),
                        "roundtrip": True}
    return result
