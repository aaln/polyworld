"""Additive, executable microplay IR using the frozen incumbent's compiler.

No live campaign modules are modified. The parent bundle carries the complete
compiler and its original contracts; this module adds one versioned contract.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import runpy
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[4]
PARENT = ROOT / "examples/gods_of_the_arena/players/ir/forks/jordan268"
COMPILER_WORKSPACE = tempfile.TemporaryDirectory(prefix="gota-microplay-compiler-")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_compiler():
    manifest = json.loads((PARENT / "manifest.json").read_text())
    assert sha(PARENT / "compiler.zip") == manifest["compiler_zip_sha256"]
    assert sha(PARENT / "contracts.py") == manifest["contracts_sha256"]
    with zipfile.ZipFile(PARENT / "compiler.zip") as archive:
        assert set(archive.namelist()) == set(manifest["compiler_files"])
        for name, expected in manifest["compiler_files"].items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == expected
        archive.extractall(COMPILER_WORKSPACE.name)
    sys.path.insert(0, COMPILER_WORKSPACE.name + "/examples/gods_of_the_arena/players/ir")
    runpy.run_path(str(PARENT / "contracts.py"))
    import policy_ir
    import binding
    return policy_ir, binding


compiler, binding = load_compiler()

# Each scratch field resets on every decision. No enemy identity survives fog.
# Conservative reach: sqrt(dx²+dy²) + sqrt(2) <= true range; two tiles bounds
# integer-cell uncertainty without assuming the two units occupy tile centers.
binding.CONTRACTS["microplay_local_target_v1"] = binding.contract(
    """
    mpOriginal = bestId
    mpKind = 0
    mpLeader = selfId
    mpAssist = 0
    mpPick = 0
    mpScore = 2147483647
    mpRange = selfAttackRange / 100000 - 2
    if mpRange < 0 then
      mpRange = 0
    end if
    mpIndex = 0
    while mpIndex < objectCount() and mpIndex < 64
      if objectId(mpIndex) = bestId then
        mpKind = objectKind(mpIndex)
      end if
      if param_assist = 1 and objectKind(mpIndex) = 2 then
        if objectTeam(mpIndex) = selfTeam and objectAlive(mpIndex) and objectHp(mpIndex) > 0 then
          mpDx = objectX(mpIndex) - selfX
          mpDy = objectY(mpIndex) - selfY
          if mpDx * mpDx + mpDy * mpDy <= param_ally_tiles * param_ally_tiles then
            if objectId(mpIndex) < mpLeader and objectTarget(mpIndex) <> 0 then
              mpLeader = objectId(mpIndex)
              mpAssist = objectTarget(mpIndex)
            end if
          end if
        end if
      end if
      mpIndex = mpIndex + 1
    wend
    if mpKind = 2 or mpKind = 3 then
      mpIndex = 0
      while mpIndex < objectCount() and mpIndex < 64
        if objectKind(mpIndex) = 2 and objectTeam(mpIndex) <> selfTeam then
          if objectAlive(mpIndex) and objectHp(mpIndex) > 0 then
            mpDx = objectX(mpIndex) - selfX
            mpDy = objectY(mpIndex) - selfY
            mpDistance = mpDx * mpDx + mpDy * mpDy
            if mpDistance <= mpRange * mpRange then
              mpRank = 0
              if param_assist = 1 and objectId(mpIndex) = mpAssist then
                mpRank = 1
              end if
              if param_finish = 1 and objectHp(mpIndex) <= selfAttackDamage then
                mpRank = 2
              end if
              if mpRank > 0 then
                mpValue = (2 - mpRank) * 1000000 + objectHp(mpIndex) * 100 + mpDistance
                if mpValue < mpScore or (mpValue = mpScore and objectId(mpIndex) < mpPick) then
                  mpPick = objectId(mpIndex)
                  mpScore = mpValue
                  mpChosenDistance = mpDistance
                end if
              end if
            end if
          end if
        end if
        mpIndex = mpIndex + 1
      wend
      if mpPick <> 0 then
        bestId = mpPick
        bestDistance = mpChosenDistance
      end if
    end if
    """,
    {"finish": (1, 0, 1), "assist": (1, 0, 1), "ally_tiles": (8, 2, 12)},
    ("candidate",), ("candidate",), (),
    "Refine an existing unit engagement only. Prefer a living visible enemy hero "
    "whose current HP is at most one own basic hit, then a living visible enemy "
    "hero currently targeted by the lowest-ID nearby lower-ID ally. Require "
    "conservative own basic-attack reach; otherwise retain the original target. "
    "Lower-ID leadership prevents reciprocal following loops. Revalidate both "
    "ally and target each decision. Structures and no-target macro decisions "
    "are preserved. objectTarget is intent, not evidence of an ally hit. HP is "
    "current, not predicted at impact. No threat redirection or saved-ally claim. "
    "The first 64 public objects are scanned; missing opportunities fall back "
    "to the parent. No movement, cast, inventory or private-state access."
)


def make_policy(name, finish, assist):
    parent = json.loads((PARENT / "policy.ir.json").read_text())
    assert compiler.compile_policy(parent) == (PARENT / "policy.bas").read_text()
    if name == "parent":
        return parent
    policy = deepcopy(parent)
    policy["id"] = "gota_microplay_" + name
    policy["goal"]["G_microplay"] = {
        "preference": "Improve individual damage conversion and local allied "
        "combat survival in matched short encounters. Fort wins are not the "
        "experiment selection objective.", "provenance": "authored"}
    policy["skill"]["microplay"] = {
        "operator": "microplay_local_target_v1",
        "parameters": {"finish": finish, "assist": assist, "ally_tiles": 8}}
    attack = next(i for i, rule in enumerate(policy["strategy"]) if rule["skill"] == "attack")
    policy["strategy"].insert(attack, {
        "id": "M0", "when": "always", "skill": "microplay", "for": ["G_microplay"]})
    for claim in policy["belief"]["claims"].values():
        claim["status"] = "requires_review"
    policy["belief"]["claims"]["B_microplay"] = {
        "claim": "Reach-bounded finishing and acyclic ally assistance may improve "
        "short combat exchanges; test individual components and their composition.",
        "status": "untested", "evidence": []}
    policy["update"] = {
        "revision": parent["update"]["revision"] + 1,
        "parent": compiler.digest(parent),
        "change": "Isolated local target refinement; microplay objective.",
        "needs_review": ["B_microplay"], "evidence": []}
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
        result[name] = {"ir_sha256": compiler.digest(policy),
                        "basic_sha256": sha(directory / (name + ".bas")),
                        "roundtrip": True}
    return result


if __name__ == "__main__":
    print(json.dumps(build(sys.argv[1]), indent=2))
