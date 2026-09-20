"""Version two: tight axis-wise bounds on unknown within-tile positions.

Version one is preserved with its inactive discovery evidence. Each cell
difference dx permits true |delta_x| < |dx|+1, independently for y. Range is
rounded down to hundredths of a tile; no floating-point or private positions.
"""
from dataclasses import replace
import json
from pathlib import Path

import ir
from ir import ROOT, PARENT, binding, compiler, sha

old = binding.CONTRACTS["microplay_local_target_v1"]
source = old.template.replace(
    "mpRange = selfAttackRange / 100000 - 2\nif mpRange < 0 then\n  mpRange = 0\nend if",
    "mpRange = selfAttackRange / 1000")
source = source.replace(
    "if mpDistance <= mpRange * mpRange then",
    """mpBoundX = mpDx
        mpBoundY = mpDy
        if mpBoundX < 0 then
          mpBoundX = -mpBoundX
        end if
        if mpBoundY < 0 then
          mpBoundY = -mpBoundY
        end if
        mpBoundX = (mpBoundX + 1) * 100
        mpBoundY = (mpBoundY + 1) * 100
        if mpBoundX * mpBoundX + mpBoundY * mpBoundY <= mpRange * mpRange then""")
assert source != old.template and "mpBoundX =" in source
binding.CONTRACTS["microplay_local_target_v2"] = replace(
    old, template=source, meaning=old.meaning +
    " V2 reach uses the squared upper bound (abs(tile_dx)+1)^2 + "
    "(abs(tile_dy)+1)^2, with range rounded down to hundredths of a tile. "
    "This supersedes v1's unnecessarily coarse two-tile radial subtraction. "
    "A safe bound at observation time cannot guarantee a moving target remains in range.")


def make_policy(name, finish, assist):
    policy = ir.make_policy(name, finish, assist)
    if name != "parent":
        policy["id"] += "_v2"
        policy["skill"]["microplay"]["operator"] = "microplay_local_target_v2"
        policy["update"]["change"] += " Axis-wise integer-cell reach bound v2."
        compiler.refresh_grounding(policy)
        compiler.validate(policy)
    return policy


def build(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    result = {}
    for name, finish, assist in [("parent", 0, 0), ("finish", 1, 0),
                                 ("assist", 0, 1), ("combined", 1, 1)]:
        policy = make_policy(name, finish, assist)
        source = compiler.compile_policy(policy)
        assert compiler.extract(source, policy) == policy
        (directory / (name + ".ir.json")).write_text(json.dumps(policy, indent=2) + "\n")
        (directory / (name + ".bas")).write_text(source)
        result[name] = {"ir_sha256": compiler.digest(policy), "basic_sha256": sha(directory / (name + ".bas")),
                        "roundtrip": True}
    return result
