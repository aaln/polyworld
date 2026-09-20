# Observable opponent IR instrument

New studies use the maintained [opponent IR guide, revision 2](../../../../docs/guides/guide-opponent-model-ir.md). `prepare_pair.py` snapshots it into each new study and records its hash. Publishers preserve existing study/published guide snapshots and refuse conflicting replacements; they no longer depend on a Downloads file. An already frozen study with no surviving guide must restore its historical snapshot rather than acquire the current guide at publication.

Build a counted semantic model from an opponent's visible trajectory, then test its choice predictions on a chronological holdout. The first completed study is [Jordan v268](../../../../docs/opponents/jordan-v268/opponent.ir.md).

The primary deliverable is an importable Python `MODEL` dictionary in [jordan_v268.py](../../../../examples/gods_of_the_arena/players/ir/opponents/jordan_v268.py), using the primary IR's seven layers and its `id / when / skill / for` strategy records. The observation binding has its own schema discriminator: inferred behavior cannot safely be compiled as if it were known BASIC. Its belief entries use the primary `claim / status / evidence` shape and pass the real primary validator. [Compatibility receipt](../../../../docs/opponents/jordan-v268/python-compatibility.json) confirms unchanged compiled BASIC on a test copy.

## Use the Python representation

From the repository root:

```python
from examples.gods_of_the_arena.players.ir.opponents.jordan_v268 import MODEL
from examples.gods_of_the_arena.players.ir.opponent_ir import (
    validate, predict, belief_patch,
)

validate(MODEL)
forecast = predict(
    MODEL,
    {"opportunity_mask": 7, "low_hp": False},
    ["target_hero", "target_creep", "target_structure",
     "advance", "withdraw", "lateral", "hold"],
)
# forecast: skill, probabilities, preference_id, context, usable_for_rollout=False
proposed_claims = belief_patch(MODEL)  # Returns a copy; no live-policy mutation.
```

`opportunity_mask` is the sum of hero=1, creep=2, exposed structure=4, relative to the opponent: these are *our* units. Each must be alive/exposed and within 12 integer tiles in the **previous** snapshot. `low_hp` is visible absolute HP≤100. Use `semantics.features` to construct these consistently from decoded observations. Do not treat the seven-skill example as an unconditional availability declaration.

The predictor forecasts a sustained motif at an inferred boundary. It does not predict when the boundary occurs, choose a target ID, execute a skill, or qualify as a simulator opponent. `belief_patch` includes provisional entries with `requires_review`; a consumer must check exact opponent version and evidence status before using them. No automatic belief or strategy adoption is implemented.

## Reproduce this study

Python for network/auth and plotting: `../metta/.venv/bin/python`. Statistical extraction itself uses the standard library. Commands below assume the existing frozen selection/evidence directory. `fetch.py` downloads existing episodes with GET only; it never creates an XP request or uploads a policy.

```sh
STUDY=tmp/gota-ir/opponent-jordan-v268-20260919
INSTRUMENT=games/gods_of_the_arena/instruments/opponent_ir
PYTHON=../metta/.venv/bin/python

# Inputs: existing eligible.json and study-plan.json, preserved under STUDY.
$PYTHON "$INSTRUMENT/fetch.py" "$STUDY"

# Build the observer probe against exactly the published source checkout.
CLEAN=/Users/aaln/experiments/softmax/polyworld-gota-clean-20260916-r5
cp "$INSTRUMENT/replay_observer.nim" "$CLEAN/examples/gods_of_the_arena/players/ir/replay_opponent_observer.nim"
POLYWORLD_DEPS=/Users/aaln/experiments/softmax/gota-research-20260916/deps \
  nim c -d:headless -d:release --hints:off \
  -o:"$PWD/$STUDY/observer-probe" \
  "$CLEAN/examples/gods_of_the_arena/players/ir/replay_opponent_observer.nim"

$PYTHON "$INSTRUMENT/decode.py" "$STUDY"
$PYTHON "$INSTRUMENT/segment.py" "$STUDY"
# On a NEW study only: fit.py refuses to overwrite an existing freeze.
# $PYTHON "$INSTRUMENT/fit.py" "$STUDY"
$PYTHON "$INSTRUMENT/decode.py" "$STUDY" --heldout
$PYTHON "$INSTRUMENT/segment.py" "$STUDY" --heldout
$PYTHON "$INSTRUMENT/evaluate.py" "$STUDY"
$PYTHON "$INSTRUMENT/build.py" "$STUDY"
$PYTHON "$INSTRUMENT/verify.py"
$PYTHON "$INSTRUMENT/plot.py"
$PYTHON -m unittest discover -s "$INSTRUMENT" -p 'test_*.py' -v
```

The native probe checks **every** original state hash, complete tick count, and complete command consumption. It reconstructs replay commands internally but emits only host-visible snapshots before the observer acts. It excludes dead-observer ticks. Hidden state enters only aggregate visibility denominators. Targets outside the observer's object list become zero; zero remains ambiguous. Inventory enum names represent the same public item identities exposed as IDs by the host.

`fit.py` deduplicates by SHA-256 of the complete observer stream, freezes model counts, thresholds and source hashes, and reserves the last 4/20 Jordan games. Heldout decoding requires the freeze file. `evaluate.py` refuses changed segmentation or semantic code. Heldout novelty is exact-stream novelty, not a claim of statistically independent seeds. Raw tapes differ even where visible trajectories repeat.

## Interpretation and limits

- A motif must persist for ≥6 ticks (0.25 seconds at 24 Hz); shorter runs are residual. First appearances are left-censored, not observed choices. Every sustained start has a complete annotation block.
- Targeting motifs include pursuit and retained targets. Movement remains a simultaneous qualifier. Stationary motion may be turning or collision; inferred `hold` preferences stay provisional.
- Every choice predictor uses the previous tick. No newly selected target, subsequent damage, hidden HP maximum, private cooldown, gold or VM memory becomes a feature.
- Affordances are conservative local estimates, not successful execution guarantees. The model cannot identify source branches, all ability use, or enemy beliefs.
- Predictions are scored only where continuity and named affordances are established; coverage/exclusions are reported alongside accuracy. No missing tick is filled from ground truth.
- Population sampling is one earlier game per opponent version and our side. Its composition is explicit and is not a random sample of the entire league. Same-context, visible-class and side-conditioned baselines are reported.
- A supported forecast is not an exploited weakness. Strategy candidates remain proposals; proxy rollout count is zero, divergence is unmeasured, and `usable=False`.

## Artifacts

[Individual report](../../../../docs/opponents/jordan-v268/opponent.ir.md), [population report](../../../../docs/opponents/jordan-v268/population.ir.md), [evidence](../../../../docs/opponents/jordan-v268/evidence.json), [observation blocks](../../../../docs/opponents/jordan-v268/observations.jsonl.gz), [predictions](../../../../docs/opponents/jordan-v268/heldout-predictions.jsonl.gz), [provenance manifest](../../../../docs/opponents/jordan-v268/artifact-manifest.json).

Raw replays and full predecision observations remain in the study directory. Do not discard them before subsequent review or validation.

## Richard v135 and Alex g002:v1

The [joint analysis](../../../../docs/opponents/richard-alex-20260920/analysis.md) links the two primary-format Python models, counted preferences, own-policy failure traces and proposed repairs. Each uses 20 exact-version games against the currently deployed Jordan counter, with 16 training / 4 chronological heldout games and 14 earlier population games. These are independent studies, with independent freezes; no Jordan study semantics or artifacts were changed.

For an existing frozen study, use `tmp/gota-ir/opponent-richard-v135-20260920` or `tmp/gota-ir/opponent-alex-g002-v1-20260920` as `STUDY`:

```sh
$PYTHON "$INSTRUMENT/run_target.py" "$STUDY"
$PYTHON "$INSTRUMENT/macro_observations.py" "$STUDY"
$PYTHON "$INSTRUMENT/publish_target.py" "$STUDY"
$PYTHON "$INSTRUMENT/verify_target.py" "$STUDY"
$PYTHON "$INSTRUMENT/plot_pair.py"
```

`prepare_pair.py` freezes new selections from archived round metadata. `run_target.py` preserves the fit-before-heldout order and uses `evaluate_target.py`; it never overwrites a fit freeze. `macro_observations.py` is post-fit, training-only descriptive analysis, excluded from prediction features. The separate `own-decision-analysis.json` records four audited own-policy VM traces; raw proofs remain under each episode artifact directory. `publish_target.py` requires that analysis rather than inventing it.

`verify_target.py` checks source hashes, exact episode rosters, runtime logs, native reconstruction proofs and every heldout Python forecast. It tests merging **both** opponent belief patches into a copy of the archived deployed primary IR, requiring byte-identical BASIC. It writes the compatibility receipt and artifact manifest. Re-run verification after republishing artifacts. The forecast models have `proxy.usable=False`: no live proxy or jointly winning counter was validated. Every Alex heldout observer stream repeats training, so transfer to novel trajectories is unproven.

## Source reveal: Richard v135

The [source comparison](../../../../docs/opponents/richard-v135/source-audit-20260920/README.md), [counter handoff](../../../../docs/opponents/richard-v135/source-audit-20260920/counter-policy-guide.md), and [Ranger economy audit](../../../../docs/opponents/richard-v135/source-audit-20260920/ranger-economy.md) are separate from the original observation-only model. All original published artifacts and Python models retain their hashes. The source-audit schema is descriptive and cannot be compiled by the primary policy compiler.

Run from the repository root. These commands use already downloaded replays and the pinned clean game checkout; they do not create XP requests. `source_audit.py` caches per-game receipts bound to binary/source/replay hashes. A changed binary requires a new receipt directory or explicit archival of the previous receipts.

```sh
PYTHON=/Users/aaln/experiments/softmax/metta/.venv/bin/python
NIM=/Users/aaln/.local/bin/nim
INSTRUMENT=games/gods_of_the_arena/instruments/opponent_ir
CLEAN=/Users/aaln/experiments/softmax/polyworld-gota-clean-20260916-r5
DEPS=/Users/aaln/experiments/softmax/gota-research-20260916/deps
RUN="$PWD/tmp/gota-ir/richard-v135-source-audit-20260920"
mkdir -p "$CLEAN/tmp/opponent-source-audit" "$RUN"
cp "$INSTRUMENT/source_audit_probe.nim" "$INSTRUMENT/source_fixture_vm.nim" "$CLEAN/tmp/opponent-source-audit/"
POLYWORLD_DEPS="$DEPS" "$NIM" c -d:headless -d:release --hints:off --out:"$RUN/source-probe" "$CLEAN/tmp/opponent-source-audit/source_audit_probe.nim"
POLYWORLD_DEPS="$DEPS" "$NIM" c -d:headless -d:release --hints:off --out:"$RUN/fixture-vm" "$CLEAN/tmp/opponent-source-audit/source_fixture_vm.nim"
$PYTHON "$INSTRUMENT/source_audit.py"
$PYTHON "$INSTRUMENT/source_audit_fixtures.py"
$PYTHON "$INSTRUMENT/build_economy_probe.py" --mechanics-root "$CLEAN" --deps-root "$DEPS" --output-dir "$RUN/economy" --nim "$NIM"
$PYTHON "$INSTRUMENT/economy_audit.py"
$PYTHON "$INSTRUMENT/publish_source_audit.py"
$PYTHON "$INSTRUMENT/verify_source_audit.py"
```

The source probe executes all five authentic opponent VMs and requires every command and full state hash to match. Its private-memory guards are retrospective source evidence, not permitted observer features. The fixture VM accepts supplied observations/host returns without simulating combat; a passing branch test is not a winning counter. The economy probe copies pinned mechanics to an isolated logging overlay, records accepted purchases and lethal-hit rewards, verifies every replay hash and reconciles XP/gold/levels for all ten heroes. It leaves canonical game source unchanged.

The revised guide requires event timing, target identity, action composition, override order and conditional intervention tests before using an inferred model as a rollout proxy. It also distinguishes purchase attempts from accepted purchases and first-visible items from exact acquisition times. The existing seven-motif predictor retains its original narrower contract.
