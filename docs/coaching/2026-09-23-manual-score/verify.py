"""Verify preserved manual coaching and diagnostics; not a policy qualification."""
from pathlib import Path
import hashlib
import json
import runpy
import statistics
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
read = lambda path: json.loads(path.read_text())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

inputs = read(HERE / "input-manifest.json")
for row in inputs["images"]:
    assert sha(HERE / row["artifact"]) == row["sha256"]
assert sha(HERE / inputs["original_user_text"]) == inputs["original_user_text_sha256"]
model = read(HERE / "suggestions.ir.json")
assert runpy.run_path(str(HERE / "suggestions.py"))["MODEL"] == model
assert set(model) == {"schema", "id", "situation", "belief", "goal", "skill", "strategy", "execution", "update"}
assert model["schema"] == "gota-optimization-hypotheses/1"
assert model["execution"]["executable"] is False
assert model["execution"]["apply_to_live_policy"] is False
for path in model["update"]["evidence"]:
    assert (HERE / path).exists(), path

sys.path.insert(0, str(ROOT / "examples/gods_of_the_arena/players/ir"))
import policy_ir
try:
    policy_ir.validate(model)
except ValueError as error:
    assert "unsupported policy schema" in str(error)
else:
    raise AssertionError("Research suggestions must not be accepted as executable IR")

analysis = read(HERE / "evidence/current-engine-analysis.json")
assert analysis["complete"] and analysis["games"] == 200 and analysis["new_hosted_games"] == 0
assert len(analysis["rows"]) == 600
for label, summary in analysis["summary"].items():
    rows = [r for r in analysis["rows"] if r["label"] == label]
    assert len(rows) == len({r["episode"] for r in rows}) == 200
    assert statistics.mean(r["score"] for r in rows) == summary["overall"]["mean_score"]
    assert sum(v["n"] for v in summary["classes"].values()) == 200
    assert all(v["n"] == 50 for v in summary["contexts"].values())
    for key, value in summary["overall"]["means"].items():
        assert statistics.mean(r["counts"].get(key, 0) for r in rows) == value
proof = read(HERE / "engine-source-proof.json")
assert sha(ROOT / proof["reference_path"]) == proof["reference_source_sha256"]
autocast = read(HERE / "evidence/autocast-proof.json")
assert autocast["games"] == 200 and autocast["manual_spell_actions"] == 0
assert all(r["manual_spell_actions"] == 0 for r in autocast["rows"])
calibration = read(HERE / "evidence/calibration-proof.json")
assert calibration["passed"] and calibration["all10_xp_gold_kills_equal"]
assert calibration["all_state_hashes_equal"]
manifest = read(HERE / "manifest.json")
for path, digest in manifest["artifacts"].items():
    assert sha(HERE / path) == digest, path
print(json.dumps({"verified": True, "screenshots": 5, "audited_games": 200,
                  "new_hosted_games_for_diagnosis": 0, "executable": False,
                  "proposed_gameplay_benefits_validated": False}))
