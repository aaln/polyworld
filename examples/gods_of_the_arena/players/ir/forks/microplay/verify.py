"""Verify evidence hashes and exact native IR/BASIC parity for both policies."""
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT / "games/gods_of_the_arena/instruments/microplay"))
import ir_v4

manifest = json.loads((HERE / "manifest.json").read_text())
for reference in [manifest["research"], manifest["compiler_parent"], *manifest["contracts"]]:
    assert ir_v4.sha(ROOT / reference["artifact"]) == reference["sha256"], reference
for name, expected in manifest["policies"].items():
    policy = json.loads((HERE / (name + ".ir.json")).read_text())
    assert ir_v4.compiler.digest(policy) == expected["ir_sha256"]
    basic = ir_v4.compiler.compile_policy(policy)
    assert basic == (HERE / (name + ".bas")).read_text()
    assert hashlib.sha256(basic.encode()).hexdigest() == expected["basic_sha256"]
    assert ir_v4.compiler.extract(basic, policy) == policy
research = json.loads((ROOT / manifest["research"]["artifact"]).read_text())
for reference in research["execution"]["experiments"]:
    path = ROOT / reference["artifact"]
    assert ir_v4.sha(path) == reference["sha256"]
    experiment = json.loads(path.read_text())
    for artifact in experiment["execution"]["artifacts"]:
        assert ir_v4.sha(ROOT / artifact["artifact"]) == artifact["sha256"]
reference = research["strategy"]["decision_records"]
assert ir_v4.sha(ROOT / reference["artifact"]) == reference["sha256"]
count = 0
with gzip.open(ROOT / reference["artifact"], "rt") as records:
    for line in records:
        record = json.loads(line)
        assert record["schema"] == "gota-action-ir/1"
        assert set(ir_v4.compiler.LAYERS) <= record.keys()
        count += 1
assert count == research["strategy"]["refined_decisions"]
print(json.dumps({"verified": True, "policies": len(manifest["policies"]),
                  "semantic_decisions": count, "scope": "local encounter qualification"}))
