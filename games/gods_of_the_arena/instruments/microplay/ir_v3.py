"""Threat-aware assistance: do not abandon self-defense for a healthier ally."""
from dataclasses import replace
import json
from pathlib import Path

import ir_v2
from ir_v2 import ROOT, PARENT, binding, compiler, sha

old = binding.CONTRACTS["microplay_local_target_v2"]
source = old.template.replace("mpOriginal = bestId", "mpOriginal = bestId\nmpSelfThreat = 0\nmpLeaderHp = 0")
source = source.replace("mpKind = objectKind(mpIndex)", """mpKind = objectKind(mpIndex)
    if objectTarget(mpIndex) = selfId then
      mpSelfThreat = 1
    end if""")
source = source.replace("mpAssist = objectTarget(mpIndex)",
                        "mpAssist = objectTarget(mpIndex)\n          mpLeaderHp = objectHp(mpIndex)")
source = source.replace("mpRank = 1", """if mpSelfThreat = 0 or mpLeaderHp * 2 < selfHp then
            mpRank = 1
          end if""")
binding.CONTRACTS["microplay_local_target_v3"] = replace(
    old, template=source, meaning=old.meaning +
    " V3 assistance additionally checks whether the original selected enemy "
    "publicly targets self. If so, assistance is allowed only when the allied "
    "leader has less than half self's current HP. Otherwise preserve self-defense. "
    "Finishing still has priority. This compares observed absolute HP, not "
    "unavailable enemy maximum HP or predicted survival. A zero observed target "
    "is ambiguous; it is not proof of safety. Reset both threat and ally HP each decision.")


def make_policy(name, finish, assist):
    policy = ir_v2.make_policy(name, finish, assist)
    if name not in ("parent", "finish"):
        policy["id"] = "gota_microplay_" + name + "_v3"
        policy["skill"]["microplay"]["operator"] = "microplay_local_target_v3"
        policy["update"]["change"] += " V3 observed self-threat and relative ally HP guard."
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
