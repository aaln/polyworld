## Current deployed optimizer — September16,2026

**Aaron's Optimizer:** `aaron-gota-ir-cadence-all-0916:v1`, confirmed215/400
wins versus waveguard175/400 and motion176/400; bothp<.004. Passed a separate
100game current-champion field check with58wins. Both owned ladder players are
active. [Research report](experiments/2026-09-16-autoresearch-result.md).

Current candidate/optimizer source of truth: [semantic IR](cadence_all.evaluated.ir.json)
and [generated BASIC](cadence_all.evaluated.bas), revision22 with exact round-trip
parity. This improves post-hit attack recovery; it does not establish safe escape
movement. Future research should start from this validated IR, while retaining
the immutable historical motion/waveguard controls.

# Gods of the Arena: semantic policy workspace

## Current work — September 15

**Kiting campaign complete: exact league v2 retained.**
Ten candidates were built through the IR↔BASIC loop and tested with40 matched
cases each, including full replay checks. None met both survival and fort-win
gates. The best current-release win result was23/40 vs v2's22/40, with deaths135
vs134. The short spellcasting variant had115deaths but only17/40wins.
[Interactive comparison](kiting-campaign-20260915.html) ·
[Complete results](kiting-campaign-20260915.json).

The canonical [v2 IR](waveguard_xp.evaluated.ir.json) now records the current
2026.9.15.3 contract, survival/Glory goals and failed-candidate evidence. It still
generates the exact selected [v2 BASIC](waveguard_xp.evaluated.bas), SHA
`c23c618705b74ec3154ba7614cdda6fd7bdc84e71ea55c3b0ef171438f0a91c3`.
No new policy was uploaded or promoted. Final league readback still selects
`aaron-gota-ir-waveguard-r4:v2`, nowrank3 at1585.103MMR.

Published2026.9.15.3(source`e127989`) exposes successful basic-hit counters,
attack cooldowns and observed enemy target IDs. The new operators support
confirmed-hit kiting, target-aware retreat, optional emergency escapes, and
explicit offensive spells while moving. All67 tests pass. Confirmed-hit variants
had100% of normal retreats follow an actual hit withinone tick; correct mechanics
alone did not establish competitive improvement. Each evaluated IR regenerates
its exact tested BASIC. Item buying remains the v2 implementation.

**Hosted request format:** use [hosted_batch.py](hosted_batch.py), one XP request
per policy arm with `--episodes N` (default40, maximum100). New per-game requests
are disabled in the historical matched runner. Each batch freezes incumbent
versions and rotates hero seats. Omit a fixed seed so the platform generates
distinct episode seeds. Separate arm requests have independent seeds and must
use an independent-cohort analysis, not a paired-seed test. Current40-episode
candidate request: `xreq_bfd62a49-10d3-4efe-94dc-e05ffebd5b42`;
[batch dashboard](http://localhost:8792).

```sh
../metta/.venv/bin/python examples/gods_of_the_arena/players/ir/hosted_batch.py \
  tmp/gota-ir/MY_FROZEN_RUN launch --episodes 40
```

The run directory must contain a frozen `plan.json`; the existing batch is under
`tmp/gota-ir/xp-batched-20260915/`. Reusing its launch command is idempotent.

The previous candidate is [wave-local IR](hypotheses/wave_local_balance.evaluated.ir.json),
which generates the exact [evaluated BASIC](hypotheses/wave_local_balance.evaluated.bas).
It incorporates the independent IR draft's six-tile wave-local targeting into v2,
preserving v2's item buying, healing and movement code. Its first local screen was
**27/40 wins versus v2 23/40 and default 20/40**; [results and limits](wave-local-20260915-screen.html).
Fresh120-seed local confirmation completed with68wins versus v2's57 and default60.
The paired p-values (.111 and .175) missed the .025 threshold, and the default
gain (+6.67points) missed the10-point requirement. All360 replay audits passed.
This is an experimental candidate with a failed local confirmation gate, not a
league replacement. [Validation report](wave-local-20260915-validation.html).

**Item buying is verified.** On pulled commit `1d7eb72`, all ten classes bought
equipment on tick 1. A complete 28,800-tick functionality game recorded 19 equipment
purchases, 47 consumable purchases and 3,860 gold spent; every replay state matched.
[Accepted-purchase evidence](item-buying-20260915.json) is attached to the IR's
`B_item_execution` belief. Subsequent win feedback preserves that evidence and the
exact tested BASIC. This verifies execution, not optimal item selection.

**Glory is now represented in the IR and evaluation tools.** The repository's
tournament definition is `win * (total_xp - 100 * ticks / 1440)`. It uses lifetime
XP, fractional simulated minutes, zero for defeats/draws, and preserves negative
winning values. [The grounded metric contract](glory-contract-20260915.json)
records the formula, live league distinction and optimization priority.
`G_glory` links productive last hits, equipment and movement to this secondary
objective; fort-win qualification remains primary. The calculator matches the
game's Nim scorer on300fixtures. All80 hosted paired replays and lifetime-XP
arrays are now verified: wave-local won4/40 versus v2's7/40 and mean Glory was
−26.26 versus113.74. Neither result supports promotion.
[Completed hosted comparison](wave-local-hosted-20260915.json),
[Glory analysis](glory-hosted-20260915.json). The separate40-episode field batch
has finished with all40 replays and XP arrays verified:6/40 wins,26timeouts, meanGlory61.76. It is an independent directional cohort and is not pooled into this A/B.

The earlier local balance studies used an isolated announcement simulation,
and their hosted comparisons pinned2026.9.15.1. They are historical evidence;
the kiting study pins the newly published2026.9.15.2. See
[current game contract](CURRENT_GAME.md).

The dated September 10 material below remains historical evidence.

**League selection updated:** at 2026-09-10T22:17:27Z, the user explicitly requested upgrading the linked v1 policy to the latest uploaded version. **`aaron-gota-ir-waveguard-r4:v2` is now the active champion** in Gods of the Arena. Its 4/10 versus v1's 2/10 hosted result is exploratory, not a passed statistical improvement gate. The studies below retain their original conclusions; no unconfirmed local candidate was substituted. See [the selection/readback record](submission-v2-latest-20260910.json) and [version log](VERSION_LOG.md). Future automatic selection remains disabled.

The workspace now has an executable seven-layer IR, a BASIC compiler, a reverse extractor, and a bounded research loop. Start with [base.ir.json](base.ir.json) for the faithful baseline or [waveguard_r4.ir.json](waveguard_r4.ir.json) for the isolated wave-following experiment. [layered.ir.json](layered.ir.json) is the next isolated change: wave-local targeting (6-tile escort disk) plus the existing join-wave fallback. It is VM-tested and untested on complete games. The optimizer-seed copy lives at `optimizer-seed/games/gods-of-the-arena/players/layered/`. The Markdown policies explain the baseline and the larger Waveguard design; **JSON is the executable semantic source**.

To inspect a recorded loss, compare the baseline, or control a hero yourself, see [Watch and play](WATCH_AND_PLAY.md).

The latest [HP Investment evaluation](hp-investment-20260910-report.html) tested a new policy generated from the reconciled IR: buy missing HP equipment before potions when injured without healing stock. On **120 independent seeds / 360 complete games**, it won **57/120**, versus Duelist **62/120** and default **55/120**. Both predeclared improvement gates failed, so it did not advance to hosted XP or league replacement. The intended behavior worked—113 accepted investments in 89 games, adding 6,320 current HP—but healing purchases fell and inventory-space rejections rose. All 360 replay state sequences and investment events were verified; two interrupted candidate attempts completed on exact-input retry. The [updated IR](hypotheses/hp_investment.ir.json) records mechanism evidence separately from unconfirmed superiority and regenerates the exact [tested BASIC](hypotheses/hp_investment.bas). All 36 tests pass. See the [experiment record](experiments/2026-09-10-hp-investment.md) for the fixed decision rules and limitations.

The latest [independent IR review](independent-20260910-report.html) reconstructed the base policy from source using a separate semantic model and lowering. It found **no baseline translation defect**: full AST equality, 500 real-VM scenarios and two paired complete games matched. The current IRs now record verified observation timing, command side effects and immediate equipment resource gains. The extractor also accepts checked unmarked baseline-family edits. All 34 tests pass; tested BASIC and league selection are unchanged. See the [fresh IR](independent/base.ir.json) and [reconciliation receipt](independent-20260910-reconciliation.json).

The previous [consumable-space study](reserve-20260910-report.html) tested an IR-generated four-equipment cap: **27/60 wins versus Duelist 24/60**. Three added wins missed the predeclared four-win discovery gate, so it did not advance to confirmation or league promotion. The capacity mechanism worked: rejected healing purchases fell 55,580→99, with all 120 replay state sequences verified. [Updated IR](hypotheses/reserve.ir.json) records this separately from the unconfirmed win hypothesis and regenerates the exact [tested BASIC](hypotheses/reserve.bas). All 30 tests pass. This study did not qualify a replacement and left v1 selected at its completion; the subsequent explicit version update is recorded above.

The previous [hypothesis study](hypotheses-20260910-report.html) tested three independently generated IR changes against the unchanged Duelist parent: pursuit recovery (34/60 wins), structure priority (25/60), and one healing purchase at a time (30/60), versus Duelist's 35/60 on the same seed/seat assignments. None qualified for fresh-seed confirmation. Recovery activated only once; structure targeting increased without improving wins. A real-purchase replay audit confirmed that single-heal eliminated double successful healing buys in the inspected seed, while exposing that purchase attempts are an inadequate spending metric. All outcomes and limitations are fed back into the [three hypothesis IR/BASIC pairs](hypotheses/). The parent and league selection are unchanged.

The study follows optimizer-seed's diagnosis, experiment and A/B skills, with the user's local-first preference. [hypothesis_study.py](hypothesis_study.py) records the plan before play, isolates one change per arm, checks activation, and supports hash-checked resume. [study_report.py](study_report.py) independently recomputes results, audits all tapes/traces, generates evidence-bearing IR bundles and renders the report. [audit_purchases.nim](audit_purchases.nim) reconstructs actual accepted purchases and spending from recorded commands while checking every state hash. Twenty-eight tests pass. These local experiments establish behavior and screen ideas; they do not establish live-field superiority.

## Working loop

`semantic IR → BASIC → extracted IR → parity/scenarios → complete games → evidence-updated IR`

The current campaign uses **local baseline gates before further hosted XP**. It screens semantic changes on discovery seeds, freezes one candidate, and tests every class on fresh seeds with nine default baseline teammates/opponents. Eligibility requires at least a 10-percentage-point paired win gain and an exact sign test across seed clusters. [campaign-20260910-plan.json](campaign-20260910-plan.json) fixes two possible validation attempts at `alpha=0.025` each; individual seats within a seed are never counted as independent samples. [local_gate.py](local_gate.py) runs the screen/freeze/validation sequence. A candidate that misses the local gate does not trigger another hosted batch.

The economy-only candidate failed validation: **112/240 wins versus baseline's 115/240**, after its 36/60 discovery result. [sustain_center.ir.json](sustain_center.ir.json) records this negative evidence and generates [sustain_center.generated.bas](sustain_center.generated.bas). [local-sustain-result-20260910.json](local-sustain-result-20260910.json) preserves the complete paired scores. The targeting candidate, [duelist.ir.json](duelist.ir.json), combines sustain-only spending with distance-weighted hero preference: a hero can be up to twice as far away as a footman and still be preferred. It scored 37/60 on discovery seeds; the stronger four-times-distance preference scored 35/60.

The moderate targeting candidate finished its separate 24-seed validation at **123/240 versus baseline's 100/240**: a **9.58-percentage-point paired gain**, with 12 positive, 7 negative and 5 tied seed clusters. The exact one-sided sign-test p-value is **0.1796**, above the predeclared 0.025 threshold; the mean gain also falls just below the required 10 points. It is a promising measured gain, **not a confirmed improvement**. Neither candidate qualified for more XP or league promotion. [local-duelist-result-20260910.json](local-duelist-result-20260910.json) contains all paired results; the [campaign report](campaign-20260910-result.json) covers all five discovery configurations and both frozen validations. In total the campaign ran **834 complete local games**, including shared baseline controls. The targeting result has been fed back into [duelist.ir.json](duelist.ir.json), which regenerates the exact evaluated [duelist.generated.bas](duelist.generated.bas). Further confirmation needs a new, explicitly planned set of seeds; these validation sets must not be reused for tuning or repeated gates.

The [post hoc diagnosis](local-duelist-diagnostics-20260910.json) distinguishes stalemates from decisive controls: 18 of the 23 additional wins came from four seeds whose all-baseline game timed out. On the other seeds the candidate won 105/200 versus 100/200. `B_stalemate` records this limitation in the IR; it does not identify the mechanism or change the failed gate. All 834 source/replay/trace hash checks passed. Maximum observed VM usage was 10,183 work units and 5,332 instructions, below the 50,000/20,000 limits.

[local_feedback.py](local_feedback.py) independently recomputes the reported gate, checks the generated source hash and paired totals, updates beliefs, then bundles both representation directions. A failed gate leaves hypotheses under review. A successful whole-policy result does not automatically prove each constituent hypothesis. These updates preserve the tested BASIC bytes; deliberate skill changes generate a new experiment. The suite currently passes 22 structural, real-VM and evidence tests.

```sh
python3 examples/gods_of_the_arena/players/ir/local_feedback.py \
  --ir examples/gods_of_the_arena/players/ir/sustain_center.ir.json \
  --report examples/gods_of_the_arena/players/ir/local-sustain-result-20260910.json \
  --belief B_equipment --output tmp/gota-ir/my-evidence-revision
```

The earlier two XP arms completed before this local-first workflow was established. Sustain-only spending won 4/10 versus v1's 2/10 against the same rotated, pinned field roster. Final equipment totaled 35 versus 16 items across ten heroes. These are exploratory results from one seed cluster. [xp-result-20260910.json](xp-result-20260910.json) records matched games and hashes; [waveguard_xp.evaluated.ir.json](waveguard_xp.evaluated.ir.json) incorporates this evidence and generates [waveguard_xp.evaluated.bas](waveguard_xp.evaluated.bas). Belief feedback preserves the tested BASIC bytes. [xp_feedback.py](xp_feedback.py) rejects incomplete, mismatched or unverified games before updating an IR bundle.

Hosted replay audits use [audit_replay.nim](audit_replay.nim) compiled against the exact published `27a8fd5` source (`2026.9.10.3`). This release changes replay/config metadata; its BASIC host and combat mechanics remain compatible with the local policy binding. All 20 hosted tapes consumed every action with zero state-hash mismatches. Candidate `aaron-gota-ir-waveguard-r4:v2` was uploaded for the exploratory evaluation. At the end of that campaign, v1 remained selected and the local gate did not authorize advancing a new candidate. The subsequent explicit selection of the existing v2 is recorded above.

[policy_ir.py](policy_ir.py) provides `compile`, `extract`, `check`, `refresh`, and `bundle`. [binding.py](binding.py) defines the supported semantic skills, their grounding, memory, parameters and complete executable contracts. There are no arbitrary BASIC payloads in the IR. New algorithms require a new tested binding operator; changing prose alone does not implement a behavior.

| Layer | What is represented | What parity can establish |
| --- | --- | --- |
| Situation | Host grounding, visibility, named predicates | Predicates and observation contract match the binding |
| Belief | Cross-decision memory, separately attributed hypotheses and evidence | Memory is implemented; hidden intent is never inferred from code |
| Goal | Authored or interpreted preferences | Rules retain explicit goal references; goal truth/fidelity requires evidence |
| Skill | Named semantic operator and bounded parameters | Complete parsed BASIC matches the operator contract |
| Strategy | Ordered guarded rules and goal references | Actual guard, skill, parameters and order are recovered |
| Execution | Game version, language and binding version | Version checks, structural parity and real-VM/full-game checks |
| Update | Parent hash, named change, review needs and episode evidence | Evidence revisions cannot silently change executable behavior |

The extractor parses real control flow, with the game's operator precedence. Generated `@rule` comments supply region identity only. Undeclared commands, changed tie-breaking, unknown control flow, inconsistent parameter occurrences and duplicate rule IDs fail closed. A supported symbolic edit updates the corresponding operator/parameters/guard/order and marks inherited goal and belief interpretations for review. An unmarked program can bootstrap only when its entire parsed behavior matches the supplied parent, as the original baseline does. This is a bounded bidirectional representation, not an arbitrary BASIC decompiler or a way to recover unique human intent.

From the repository root:

```sh
IR=examples/gods_of_the_arena/players/ir
python3 "$IR/policy_ir.py" compile "$IR/base.ir.json" /tmp/gota-base.bas
python3 "$IR/policy_ir.py" check /tmp/gota-base.bas --parent "$IR/base.ir.json"
python3 "$IR/policy_ir.py" bundle "$IR/waveguard_r4.ir.json" tmp/gota-ir/my-revision

# After editing the generated BASIC within a supported contract:
python3 "$IR/policy_ir.py" extract /tmp/gota-base.bas /tmp/gota-edited.ir.json --parent "$IR/base.ir.json"
python3 "$IR/policy_ir.py" compile /tmp/gota-edited.ir.json /tmp/gota-edited.bas
python3 "$IR/policy_ir.py" check /tmp/gota-edited.bas --parent /tmp/gota-edited.ir.json

# After deliberately changing IR skills/predicates, refresh derived grounding:
python3 "$IR/policy_ir.py" refresh /tmp/gota-edited.ir.json /tmp/gota-refreshed.ir.json
python3 -m unittest discover -s "$IR" -p 'test_*.py' -v
```

`check` exits 0 for behavioral parity, 1 for supported drift and 2 for unsupported/invalid input. Compilation allows pending rationale reviews so an experiment can be made concrete; it does not certify coaching fidelity. Bundles require a new directory and contain IR, generated BASIC, extracted IR, derived semantics and SHA-256 manifests for artifacts/compiler/binding/host sources.

## Implemented movement experiment

Only R4 changes: when the baseline finds **no eligible enemy**, replace the fixed center destination with an allied-footman anchor. All targeting, inventory use, purchase order and gold-snapshot behavior remain the baseline. This does **not** yet stop a hero from chasing a visible enemy; that belongs to the later obstruction/targeting experiment.

Retain the previously selected living allied footman if it is still observed; otherwise choose minimum `(squared distance, stable ID)`. Move two tiles toward the observed living allied fort, using `max(abs(dx), abs(dy))` normalization and BASIC integer division toward zero; when closer than the offset, use the fort point. If there is no escort, use `(64,64)`. Revalidate on each R4 decision, clear commitment and request center on rejected movement, and make one center request after 48 consecutive stationary R4 decisions. A gap in R4 decisions or position/escort change resets that progress counter. Return values are recorded; arrival is not assumed. The full draft's regroup/retreat/siege rules are separate future experiments.

[research.py](research.py) runs a predeclared offset sweep with one candidate seat and nine baseline seats, covering all ten classes on each seed. It freezes the selected offset before held-out games and reports five-versus-five separately. It saves complete replays, per-tick hashes, sparse actual-predicate/action traces, per-class results, VM budgets, a selection record and a new evidence-bearing IR bundle. Replays normalize only their creation timestamp for exact tape comparison. The final compile/extract check proves that feeding results into beliefs did not silently alter actions.

```sh
python3 examples/gods_of_the_arena/players/ir/research.py tmp/gota-ir/my-research \
  --offsets 0,2 --selection-seeds 2026,2027 --held-out-seeds 3026,3027 --workers 2
```

The loop validates scenarios before games, compares a complete original/generated baseline tape, and rejects VM failures. Seed sets must be disjoint. Results flag hypotheses for review; a small correlated sample never becomes a proved belief automatically. This local experiment tests the player and the update machinery. Testing the broader IR hypothesis requires a direct-code optimization control with equal evaluation budgets and independent held-out seeds.

## First completed experiment, 2026-09-10

**Keep the baseline as the reference; do not promote Waveguard from this result.** The implementation passed 14 structural/real-VM tests and the existing GOTA simulation suite. A complete original/generated baseline comparison matched all 122,880 actions and all per-tick state hashes, finishing at tick 13,548 with hash `000000007EE61CA9`.

The bounded sweep ran 69 games: 40 selection, 20 held-out, four five-versus-five, four baseline controls and one original-baseline parity run. Each single-seat condition covers all ten assigned classes on each seed. The two selection seeds chose offset 0 before the two held-out seeds were evaluated.

| Condition | Candidate wins | Matched baseline wins | Timeouts |
| --- | --- | --- | --- |
| Offset 0, selection | 9 / 20 | 10 / 20 | 0 |
| Offset 2, selection | 8 / 20 | 10 / 20 | 2 |
| Offset 0, held-out | 12 / 20 | 10 / 20 | 2 |
| Offset 0, five-versus-five | 2 / 4 games | 2 / 4 games | 0 |

There is no consistent improvement across selection and held-out results; two seed clusters per split are insufficient to establish generalization. All VMs stayed active. Maximum observed per-decision usage was 5,870 instructions / 11,041 work units against limits of 20,000 / 50,000. One candidate replay was independently played through all 110,231 actions with the expected final hash and no hash mismatches.

[experiment-20260910.json](experiment-20260910.json) contains the plan, per-seat/class comparisons, artifact hashes and compatibility evidence. Raw bundles, tapes and sparse decision traces are in `tmp/gota-ir/research-20260910-r2/`. [waveguard_r4.evaluated.ir.json](waveguard_r4.evaluated.ir.json) and [waveguard_r4.evaluated.bas](waveguard_r4.evaluated.bas) are the selected offset-0 candidate after feeding results back into its belief/update layers. `B_wave` explicitly remains `requires_review`. The original offset-2 IR remains available for reproduction.

## League submission, 2026-09-10

At the user's request, the evaluated offset-0 candidate was uploaded as [aaron-gota-ir-waveguard-r4:v1](https://softmax.com/observatory/v2?tab=uploads&detail=policy-version:7b5f3065-85b0-4abf-882e-a4ab95a136fe) under Aaron and placed in the Gods of the Arena Competition division. The initial submission used `auto_champion=never`, leaving it out of the league roster and scheduled rounds despite its `competing` status. This was corrected at 20:14 UTC by selecting this exact version as Aaron's champion. Readback now confirms `competing`, substatus `active`, `is_champion=true`, and inclusion in the champions roster. No hosted episodes had completed or leaderboard entry appeared at that check; the local results above remain the available performance evidence. Automatic promotion of future uploads remains disabled.

For this league, entry validation must include the champions-only roster: `GET /v2/league-policy-memberships?league_id=...&player_id=...&champions_only=true`. `placed` and `competing` alone do not establish scheduling eligibility. Select the intended existing version with `POST /v2/league-policy-memberships/{membership_id}/champion` when completing an authorized league entry, and verify its subsequent round attribution and results.

[submission-20260910.json](submission-20260910.json) records the immutable version, submission and membership IDs, exact BASIC/IR hashes, API readbacks and validation evidence. The uploaded 5,211-byte BASIC file is exactly `waveguard_r4.evaluated.bas`. A fresh complete game using those bytes reproduced the selected candidate's replay, decision trace and runtime metrics. The raw-file upload was completed and the same content-hash/size/metadata request resolved back to the same version. Transaction evidence and the immutable bundle are under `tmp/gota-ir/submission-20260910/`.

## Verified target, 2026-09-10

| Field | Value |
| --- | --- |
| League | `league_3c60897b-25cf-4b37-9d1a-8554c1198f28` |
| Division | Competition, `div_a4534073-c5d2-4193-a94a-93d9c5e2e443` |
| Coworld used for current XP | `cow_8186b473-d616-487f-8d42-386c0114f4b5` |
| Published version used for current campaign | `2026.9.10.3` |
| Published source commit used for current campaign | `27a8fd51eadf48d2f69591cca4287074e9058e8f` |
| Local checkout inspected | `76c477e5b88f04d82fa11444cdb196b6ec554573` |
| Baseline SHA-256 | `6af2a79e0c7815b41a00e824de897b1ab2a2f3057798c6c5395778e59d734ae9` |
| Competition configuration | Seed 2026, maximum 28,800 ticks, waves every 240 ticks |

The league advanced through `2026.9.9.4`, `2026.9.10.1`, and `2026.9.10.3` during implementation. The latest campaign pins `.3`; historical artifacts retain their evaluated versions. The `.3` BASIC host, VM, item catalog and dependency lock match this checkout; the simulation change adds a configuration accessor without changing combat. Replay/config metadata changed, so the local campaign runner and hosted audit use the isolated published-source checkout under `tmp/gota-ir/runtime-2026.9.10.3`. Updating the target did not change generated BASIC. This establishes source correspondence, not identity with the published container binary. Local evaluation uses local dependencies, not the published container.

Live league settings reported a 16-minute round interval and at least four episodes per entrant, with two teams, distinct teammates and filler policies. Its guide still says 30 minutes and two episodes. Three ranked entries were present when checked. These are a dated snapshot, not policy assumptions.

## Historical domain contract — September 10

For the current spell, terrain and poison contracts, use [CURRENT_GAME.md](CURRENT_GAME.md).

- One submitted raw `.bas` program controls one of ten heroes. Slots 0–4 are Red; 5–9 are Blue. Each team has five fixed, different classes, so a policy must handle its assigned class. A single entrant cannot assume that it controls its teammates.
- Destroy the enemy fort to win. Every winning teammate receives 1; other scores are 0. A timeout gives everyone 0. Gold, kills, survival and tower damage are useful diagnostics or intermediate objectives, not the terminal score.
- The simulation runs at 24 ticks per second; each living hero's persistent BASIC VM runs once per tick. The engine rotates execution order. Heroes respawn after death.
- The host exposes self identity, class, position, HP, mana, gold, level and tick; six inventory slots; and an object enumeration containing ID, kind, team, class, integer tile position, HP and `objectAlive`.
- All allied objects are observable. Enemy objects are filtered by team visibility. Missing means unobserved. No host query exposes enemy intentions, tower target, ability cooldowns or arbitrary simulator state.
- **Standing and attackable are different predicates.** For towers, `objectAlive` means exposed: all earlier towers in the lane have fallen. For forts it means at least one lane is fully cleared. `objectHp > 0` still identifies a standing, protected structure. All standing enemy towers can attack, including protected towers.
- Normal structure progression is outer tower → inner tower → gate tower → fort. Use the structure's exposed flag directly; a policy need not infer it from missing objects.
- Towers prefer footmen when acquiring a new target, but retain a valid current hero target. Footmen arriving later do not guarantee that a tower stops shooting the hero. Their target is hidden from the policy.
- The four commands are `walkTo(x,y)`, `attackTarget(id)`, `buyItem(id)` and `useItem(slot)`. Movement clears the current attack order. Attack orders trigger engine-controlled pursuit, attacks and automatic abilities. There is no BASIC `castAbility`, `attackMove`, chat or team-command API.
- Command return value 1 means accepted, not arrived, damaged or survived. A failed move can also clear the old attack order. Record intended commands, return values and later observations separately.
- Self host values are snapshots for the decision. Purchases and consumables change live inventory immediately. Several reads of `selfGold` within a decision do not update the budget. Generated policies must track accepted spending themselves if that is what their IR specifies.
- Purchases work without travelling to a shop. Equipment occupies one of six slots; duplicates are rejected. Consumables stack up to eight. There is no exported sell command.
- One engine quirk needs a separate regression case: poison applies damage to the current requested target through `applyUseItem` without the range/exposure checks used by normal combat target resolution. The baseline can use that path. Do not describe normal-combat affordances as universal engine invariants, or silently remove this behavior during a faithful extraction.

Sources: [BASIC interface](../../bots.nim), [simulation](../../sim.nim), [class and item catalog](../../content.nim), [baseline](../base.bas), [Coworld guide](../../../../coworld/gota/guide.md).

## Evidence already collected

The existing `test_gota_sim.nim` suite passed, including tower progression, footman targeting, BASIC tower attacks, purchases, automatic abilities, simulation/replay state and team/timeout scores.

An unmodified baseline-versus-baseline game, seed 2026, completed after **13,548 ticks / 564.50 simulated seconds**:

- Red won; fort HP Red 400, Blue 0; standing towers Red 2, Blue 0.
- All 10 BASIC VMs remained active; 121,989 decisions and 122,880 recorded actions.
- Final state hash `000000007EE61CA9`; map hash `000000003EDD1DDE`.

Replaying all 122,880 recorded actions reproduced the same outcome, final state hash and map hash, with no reported replay hash mismatches.

This is a reference run, not evidence that Waveguard works or that one policy outperforms another. Different team classes make the Red result unsuitable as a policy comparison by itself. Local raw API snapshots, logs and replay are under `tmp/gota-ir/` at the repository root.

Reproduce from the repository root with the installed dependency directories:

```sh
POLYWORLD_DEPS="$PWD" nim c -d:headless --hints:off -o:tmp/gota-ir/gota examples/gods_of_the_arena/gota.nim
tmp/gota-ir/gota --bot:examples/gods_of_the_arena/players/base.bas:10 --seed 2026 --ticks 28800 --record tmp/gota-ir/baseline.replay
POLYWORLD_DEPS="$PWD" nim c -r -d:headless --hints:off -o:tmp/gota-ir/test-gota-sim tests/test_gota_sim.nim --bot:examples/gods_of_the_arena/players/base.bas:10
```

## Further policy work

1. Use the recorded R4 decisions and first losing windows to choose the next independent change. Do not add all of the full Waveguard draft at once.
2. Add tested semantic operators for local wave obstruction, tower danger including protected towers, supported siege and bounded recovery. The existing extractor deliberately rejects these until their contracts exist.
3. Evaluate a budget-aware economy separately; the baseline intentionally does not decrement its gold snapshot. Never silently describe that baseline as having a fresh budget.
4. Expand the opponent/teammate roster beyond baseline fillers and run hosted league experience requests when live competitive evaluation is in scope.
5. Compare IR-guided and direct-code research with equal trials and held-out evaluation before claiming that the representation itself improves optimization.

Keep ontology changes distinct from belief updates. If the concept “wave screen” fails because tower targeting persists, revise the concept and its evidence requirements explicitly. Do not merely increase a confidence number. Human explanations remain authored rationale; decision traces record actual predicates and selected rules.

The Pudge Python backend cannot run inside this game's BASIC VM. Reuse the layered representation and evaluation discipline; add a game-specific binding. Realtime voice and policy replacement during a running hosted match are separate integration work: this Coworld currently stages BASIC at episode start and has no gameplay WebSocket channel.

## Read-only API access

The official helpers live in `metta/packages/coworld/src/coworld/api_client.py` and `metta/packages/softmax-cli/src/softmax/auth.py`. Use `CoworldApiClient.from_login(server_url=get_api_server())`; it reads the existing Softmax login without copying a credential into the policy or repository.

Routes used under `https://softmax.com/api/observatory`:

- `GET /v2/leagues/{league_id}`
- `GET /v2/divisions?league_id={league_id}`
- `GET /v2/divisions/{division_id}/leaderboard`
- `GET /v2/coworlds/{coworld_id}`
- `GET /v2/rounds?league_id={league_id}&limit=2`

The checked-out client's typed `list_rounds` expects offset-pagination fields missing from the live cursor-based response. Reading that endpoint as JSON through `client.get_text` worked. The snapshot helper is read-only. The separately authorized submission above used the live OpenAPI file-upload routes (`POST /stats/policies/files/upload`, presigned staging PUT, `POST /stats/policies/files/complete`) and `POST /v2/league-submissions`, because this Metta checkout's upload CLI supports only container policies.

Refresh the league/version/leaderboard snapshot through those official helpers:

```sh
../metta/.venv/bin/python examples/gods_of_the_arena/players/ir/league_snapshot.py tmp/gota-ir/my-league-snapshot
```
