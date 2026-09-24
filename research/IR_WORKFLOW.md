# Working with semantic IR and executable policies

The three active references under `policies/` are complete portable pairs. Each contains `policy.py`, `policy.ir.json`, `policy.bas`, `extracted.ir.json`, `semantics.json`, `convert.py`, `verify.py`, a frozen binding/compiler tree and evidence. The BASIC bytes are authoritative for what was evaluated; the IR records intent, ordering, execution binding and evidence status.

## Seven layers and change scope

| Layer | What to change |
|---|---|
| situation | Public predicates, observation interpretation and current mechanics |
| belief | Persistent state, uncertainty, supported/rejected/untested claims |
| goal | Expected individual score; intermediate goals explain behavior |
| skill | Bound operator and its parameters; add a binding when the behavior is new |
| strategy | Ordered guards, skill calls and goal references |
| execution | Exact game release, BASIC language and binding version |
| update | Parent IR digest, evidence references, review state and provenance |

The [controller index](knowledge/controller.ir.json) maps every deployed skill to its BASIC region and original semantic operator. It is a navigation aid, not a second executable policy. Inherited compiler memory lists are incomplete: lane assignment and neutral pull globals also persist between decisions. Inspect their initialization/reset paths when changing stateful behavior.

The portable bindings compose templates through `dataclasses.replace`. For the deployed pair the entry is `tooling/neutralfarm20260923/camp_binding.py`; it imports lane occupancy, control tactics, Druid recovery, blue opening, buyback, portal and base bindings. `configure()` sets the active contracts and binding version. Do not assume an old directory date identifies the current behavior: the frozen composed source and game version determine that.

## Verify or reproduce a frozen pair

From the workspace root, with the Python environment in `environment.json`:

```sh
python research/policies/deployed/verify.py
python research/policies/deployed/convert.py compile --out /tmp/gota-deployed-roundtrip
python research/policies/deployed/convert.py extract --source research/policies/deployed/policy.bas --out /tmp/gota-deployed-extraction
```

Output directories must not already exist. `verify_workspace.py` runs compile/extract parity checks in temporary directories for all three active pairs. No hosted games are required for these checks.

The converter checks every executable statement, not just `@rule` comments. It supports exact extraction for its bound operators; arbitrary unbound BASIC rewrites need a corresponding binding change. `semantics.json` and the `grounded` IR fields are derived outputs. Regenerate them rather than editing them independently.

## Create and evaluate a new fork

1. Make a new experiment directory and copy the chosen portable pair into a `captured-parent/` directory. Keep the original reference untouched. Record parent BASIC/IR digests, engine and hypothesis.
2. Edit a separate working `policy.py` and binding tree. Change every required semantic layer and policy component together. A coordinated bundle may be useful even if its pieces do not improve alone.
3. Set a new policy ID, binding revision and update parent; mark score claims `requires_review` or `untested`. Keep original evidence as historical provenance. A copied `deployment_qualified` flag never qualifies new bytes.
4. Compile with the working converter to a new output directory. Extract the result using the same working binding and verify exact round-trip equality. Record full source and canonical IR SHA256 values.
5. Run meaningful current-engine fixtures and complete native replay checks. Diagnose the actual intended mechanism, including accepted commands and XP receipts. These establish behavior/runtime validity, not hosted superiority.
6. Freeze a current-engine paired hosted plan through the shared journal, using unique opaque upload names and exact policy UUIDs. Evaluate combined effect on expected individual score; report class/side/seat and mechanism diagnostics.
7. Reflect the observed result into belief/update and the manifest, while requiring the tested BASIC bytes to remain identical. Preserve the pre-review IR and failed candidates. If executable bytes change, the old results no longer validate that candidate.

The [reviewed weak-neutral pair](policies/weak-neutral) demonstrates evidence reflection: the IR changed after the 180-game study, but source `c2321ead` did not. Its `evidence/frozen-input.ir.json` preserves the original hypothesis. Its score claim remains unconfirmed and promotion is false.

## Historical snapshots and opponent IR

`library/manifest.json` indexes 16 additional historical IR/BASIC snapshots and their original bindings/releases. They intentionally are not alternate runnable campaigns. Their original manifests may reference evidence/tooling still at the preserved origin. Use their mechanics and negative results to design a current fork; use the active portable converter to implement it.

Richard/relh source models and khors observation models have different evidence strength. An observational motif is not a recovered controller, and authentic source reconstruction is not a competitive transfer result. Neither licenses hidden opponent memory, future replay truth, policy UUIDs or private XP as live controller inputs. See the copied [opponent-model guide](library/docs/guides/guide-opponent-model-ir.md).
