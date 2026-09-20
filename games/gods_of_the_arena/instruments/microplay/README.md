# Gota microplay research instrument

Develop individual and cooperative combat skills against the real simulator and
BASIC host. The [completed study](../../../../docs/microplay/2026-09-20/README.md)
contains the results, limitations, rejected variants, and reusable IR artifacts.

The local qualified candidate is
[microplay/policy.ir.json](../../../../examples/gods_of_the_arena/players/ir/forks/microplay/policy.ir.json).
It retains the frozen Jordan268 policy's macro controller and inserts a local
target-refinement rule before its attack controller. A finishing-only ablation
is included. Neither artifact was uploaded or selected as a live champion.

## Representation

| Artifact | Purpose |
| --- | --- |
| `gota-semantic-policy/1` | Existing executable seven-layer policy IR; exact BASIC compile/extract round trip |
| `gota-microplay-research-ir/1` | Mechanics, claims, objectives, skill contract, results, limitations, and lineage |
| `gota-experiment-ir/1` | Frozen conditions, hypotheses, gates, policy hashes, results, and audit references |
| `gota-action-ir/1` | Public observation, grounded predicates, selected branch, original/selected targets, execution, and encounter outcome |

All use **situation → belief → goal → skill → strategy → execution → update**.
Research/action IR must not be passed to the executable policy compiler. Recorded
target intent and movement flags are effects after the decision, not complete
command logs or proof that an attack landed. Actual hit counters and encounter
outcomes are recorded separately. Full-game checks retain normal action replays.

`ir.py` loads the hash-verified compiler archive and original contracts from the
existing Jordan268 bundle. `ir_v2.py` through `ir_v4.py` add versioned operators.
Old operators and experiments remain reproducible. The final binding uses the
engine's **60,000 world units per tile**, explicitly retains the tested **60% of
attack reach**, and skips refinement above **48 visible objects** to bound cost.
The earlier range-unit explanation and the overstatement that manual casting
isolates basic attacks are explicitly corrected in the research IR.

## Use the evaluated policy

From the repository root:

```python
import json
import sys
from pathlib import Path

sys.path.insert(0, "games/gods_of_the_arena/instruments/microplay")
import ir_v4

path = Path("examples/gods_of_the_arena/players/ir/forks/microplay/policy.ir.json")
policy = json.loads(path.read_text())
ir_v4.compiler.validate(policy)
basic = ir_v4.compiler.compile_policy(policy)
assert ir_v4.compiler.extract(basic, policy) == policy
```

Changing any executable parameter requires new evidence. The final JSON records
local qualification, not universal superiority or successful live deployment.

## Reproduce

The tool defaults pin the clean `polyworld-gota-clean-20260916-r5` checkout at
`f2ab9598d8f8001b6beae3e66404e341770c803f` and its pinned dependency directory.
`study.prepare` refuses a modified engine or an existing frozen plan. Original
dirty-workspace game edits never enter the native executable.

```sh
# Use new directories: evidence is never overwritten by run commands.
python3 games/gods_of_the_arena/instruments/microplay/guarded_team.py tmp/gota-ir/new-microplay prepare
python3 games/gods_of_the_arena/instruments/microplay/guarded_team.py tmp/gota-ir/new-microplay discovery
# Permitted only when the prospective discovery gates pass:
python3 games/gods_of_the_arena/instruments/microplay/guarded_team.py tmp/gota-ir/new-microplay holdout
python3 games/gods_of_the_arena/instruments/microplay/guarded_team.py tmp/gota-ir/new-microplay audit --partition holdout

# Final bounded implementation: verify equivalence to the qualified v3 cases.
python3 games/gods_of_the_arena/instruments/microplay/finalize.py tmp/gota-ir/new-microplay-final prepare --previous tmp/gota-ir/new-microplay
python3 games/gods_of_the_arena/instruments/microplay/finalize.py tmp/gota-ir/new-microplay-final run

# Existing evaluated artifacts and focused real-VM tests:
python3 examples/gods_of_the_arena/players/ir/forks/microplay/verify.py
python3 -m unittest discover -s games/gods_of_the_arena/instruments/microplay -p 'test_*.py' -v
```

The tests use `GOTA_MICROPLAY_VM`, defaulting to the native observation-fixture VM
under `tmp/gota-ir/microplay-20260920/scenario-vm`. Build that VM from the pinned
checkout's `scenario_vm_public_target_v1.nim` with its normal headless Nim flags.
Fixtures test branch logic and cost; `encounter.nim` tests actual combat effects.

`qualify.py` additionally runs complete normal games, checks every VM's actual
budget, saves action tapes, and independently replays every tick. It uses the
native `integration` binary built from `integration.nim` in the pinned checkout.
The recorded full-game tests had no refinement opportunities and therefore
establish compatibility only. No synthetic fixture is called a hosted replay.

`report.py` exports the evaluated policy, semantic action records, provenance,
and experiment IR. Historical raw observations are compact gzip JSONL files in
the report's `evidence/` directory. Failed variants remain part of the record.

## Hosted counterfactual verification

`hosted.py` freezes the evaluated parent, finishing-only and combined policies
against nine real other players. The 2026-09-20 study used three 40-game XP
requests, covering every hero seat four times per arm. Creation goes through
the shared research allowance and concurrency lock. Uploading a version does
not select a league champion. Use the Metta virtualenv for authenticated tools.

The `harvest` command downloads all official artifacts and independently audits
every tick, action, score, and VM status. `probe` reruns the exact subject VM on
all 120 tapes. It also substitutes both controls on every combined-policy tape,
holding the other players' commands fixed and stopping at the first divergence.
These are 80 same-tape counterfactual checks; XP cohorts themselves have
different seeds. No counterfactual outcome is claimed after divergent actions.

`hosted_probe.nim` is staged in the clean pinned checkout's `tmp/microplay/` and
built with `-d:headless -d:release`. `hosted_report.py` checks complete coverage,
rosters, provenance and source parity before exporting semantic research and
evaluated policy IR. The [hosted report](../../../../docs/microplay/2026-09-20-hosted/README.md)
records zero field activation and exact counterfactual equivalence. This result
calls for redesigning the opportunity gate in a new fork, not more unchanged
policy batches.
