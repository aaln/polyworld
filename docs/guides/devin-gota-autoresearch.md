# Devin: continuous GotA research with semantic IR

Repository: **https://github.com/aaln/polyworld**. Mission: improve our GotA policy against the current league, especially Richard, Alex Smith and Jordan, and attain and retain #1. Check every **three hours**. A rank or a small winning screen is evidence to investigate, not a guarantee of future wins.

**September 21 release update:** the live game moved to **2026.9.21.5** at
`f776d5e55d439706a8d49878d17d7ba1f6a1f7ce`. See the
[new-week policy experiment](../../games/gods_of_the_arena/experiments/2026-09-21-week-policy.md)
and its [isolated runtime](../../games/gods_of_the_arena/instruments/week20260921/README.md).
The live score is now per-hero `max(0, lifetime XP - 200 * world ticks / 1440)`;
fort wins are a separate diagnostic. The old runtime, acceptance records and
deployment anchors below are historical and remain preserved. Read the new
experiment and resolve live champions before continuing research.

**September 22 microplay result:** the [practiced IR/BASIC pair](../../examples/gods_of_the_arena/players/ir/forks/microplay20260922/README.md)
`b82c3799` / `aaron-gota-micro0922:v1` completed 480 audited baseline/candidate
games on the new release. Candidate fort wins: relh161 **62/80**, Jordan306
**80/80**, Richard153 **63/80**, versus baseline 3/80, 10/80 and 2/80.
Own XP score improves in all six cells, but still trails relh and Richard on
red; each-color/absolute-score qualification remains unmet. Same-tick
walk+attack did not reset recovery in actual-tick drills; one physics tick
between them did. The bundle preserves the exact compiler, practice results,
all candidate sources and failed hypotheses. No league champion changed.
Follow-up micropractice remains separate; read the current ownership checkpoint
before any new hosted work.

This is the operational entry point. The September 20 handoff preserves local research, including failed candidates. It does **not** assert that a jointly winning counter exists or that the Devin automation has already been enabled. Historical documents contain original Mac paths; use the portable entry points below for a new installation.

## 1. Give Devin this mission

Paste [devin-gota-prompt.md](devin-gota-prompt.md) into the initial Devin session and the scheduled automation. Connect `aaln/polyworld`, grant its GitHub integration access, and use this fork as the code remote. Do not push research changes to `Metta-AI/polyworld`.

In Devin, create an **Automation → Schedule → Custom schedule** with a three-hour interval (RRULE `FREQ=HOURLY;INTERVAL=3`). Prefer **Message session** to wake the same durable research session; if creating new sessions, establish the single-writer and durable-state arrangement in §3 first. The current documentation uses automations for new schedules; the older Scheduled Sessions UI is legacy. Verify the displayed next-run time and timezone. [Devin scheduling](https://docs.devin.ai/product-guides/scheduled-sessions), [automation triggers and actions](https://docs.devin.ai/product-guides/automations#schedule-triggers).

Store a Softmax bearer credential as a Devin secret and expose it to the process as `SOFTMAX_TOKEN`. It needs permission to read league/artifacts and, after ownership transfer, operate our players and XP. Never paste it into a prompt, commit it, print it, or put presigned upload URLs in public evidence. GitHub access and Softmax access are separate. Missing/expired auth means report a stale check and repair access, not infer a rank. [Devin Secrets](https://docs.devin.ai/product-guides/secrets).

Configure the repository environment with Python 3.12+, Git, a C compiler/build tools, and Nim **2.2.10** for the pinned research build. Repository setup is documented in [Devin repository setup](https://docs.devin.ai/onboard-devin/repo-setup). Build artifacts are native: rebuild them on Linux; do not copy Mac executables.

## 2. Portable startup

Run from the fork root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r tools/gota_autoresearch/requirements-remote.txt
.venv/bin/python tools/gota_autoresearch/remote.py init
.venv/bin/python tools/gota_autoresearch/remote.py verify
.venv/bin/python tools/gota_autoresearch/remote.py build
.venv/bin/python tools/gota_autoresearch/remote.py monitor
```

`init` creates ignored `.gota/` with a separate worktree at published engine commit `f2ab9598d8f8001b6beae3e66404e341770c803f`, restores the hash-checked compiler/probe snapshot, and installs explicitly recorded portability adapters. It refuses to overwrite an initialized campaign. `build` fetches the engine's exact dependency-lock revisions, rejects dirty/wrong dependencies, and builds the responsive ten-VM runner, replay auditor, scenario VM and observer probe. It saves source, compiler, dependency and binary hashes in `.gota/build.json`. `monitor` uses GET requests only, writes `.gota/LEAGUE_STATUS.{json,md}`, and never uploads, buys games or promotes.

Use `--root /persistent/path/gota` **before** the subcommand to put runtime state on a durable volume. Set `GOTA_RESEARCH_ROOT` to that same path for direct monitor calls. An initialized worktree is tied to its repository checkout: recreate the runtime after moving to another machine and restore campaign evidence separately. Do not reinitialize a ledger to evade a budget.

The research engine is **2026.9.16.5**. Main also contains newer human-play/game changes; they are intentionally preserved in this fork. **Do not build main and call its results published-game parity.** If the live game/version/source changes, freeze current work, pin the new source/configuration, rebuild, calibrate the auditor with known hosted replays and obtain fresh controls before resuming comparative conclusions.

`verify` checks the archived Jordan fork's exact Python/JSON/BASIC/compiler bundle, the saved Richard coaching/transition pairs and opponent-model tests without network access. It does not prove competitive superiority. The old `install.py`/LaunchAgent/Codex supervisor are Mac orchestration archives; Devin is the researcher and should not launch another Codex researcher.

## 3. Transfer ownership once; keep one durable writer

At handoff capture, a local continuous worker and a separate interactive coaching study were active. The repository archive is **not** a live transfer of their locks, pending jobs or budget. Devin may immediately monitor, inspect IR, develop isolated hypotheses, and run local tests. Before new hosted requests or membership changes:

1. Coordinate a checkpoint and pause of the old research writer(s) at the source host. The local controller supports `researcher.py --root <old-campaign> pause`; verify the worker actually stopped. Already submitted XP keeps running and must be harvested. Do not interrupt another study's pending promotion halfway through.
2. Transfer the **latest** `state.json`, `config.json`, `xp-ledger.json`, frozen plans, upload receipts, created-request receipts, policy/compiler bundles and checkpoints to durable private storage. Preserve original idempotency keys and reconcile every pending request with the API. Capture fresh memberships. The checked-in September 20 snapshots cannot substitute for this step.
3. Record owner/session, transfer timestamp, source checkpoint/hash, inherited pending requests, original→remote path mapping, spend to date and rollback versions in `ownership.json`. Only one session may own research and deployment. Do not auto-steal an apparently stale owner; reconcile running jobs first.
4. Use one durable state volume and a process lock spanning the **whole research cycle**, including uploads/promotions. Local `flock` prevents overlap only for processes sharing that filesystem. Separate ephemeral Devin machines require an external transactional lease and shared ledger; until implemented, use the same session or remain read-only. A Git file that merely says “locked” is not a cross-machine mutex.
5. Preserve original archived plans and manifests. Put relocated working paths in a separate mapping; do not rewrite history and still claim its old hashes. Recompute new runtime provenance on Linux.

Normal limits: **400 new hosted episodes per research cycle**, **1,600 per UTC day**, at most **3 active XP requests**, batches **40–200**. The capture includes a **100,000 allowance for September 20 only**, with a dated authorization and a 1,600 normal limit; it is not a standing remote budget increase. Count inherited and interactive spending, not just this process's requests. Continue useful local analysis when budget is exhausted. Never modify limits to make an experiment pass.

The existing `researcher.py reserve`/`xp_create` logic demonstrates durable reservation, body hashes, idempotency, active-request accounting and separate formal acceptance. Its historical `win_hosted.live()` dependency expects the old sibling research tree. **Do not invoke the legacy writer unchanged on Devin.** Before remote XP, port this preflight to the portable runtime/config, preserve its tests, and prove dry-run/no-POST behavior and crash recovery. `portable/eval_request.py` supplies live OpenAPI request validation; set `GOTA_EVAL_HELPER` to its absolute path for `hosted_wave.helper()`. Do not bypass the journal by calling a historical helper's auto-create path. Never create a fresh idempotency key after a network timeout without reconciling the original request.

## 4. Identity and evidence index

Latest deployment record (September 20, 22:41 UTC): both Aaron and Coach use the
[adaptive formation3600 fork](../../examples/gods_of_the_arena/players/ir/forks/formation-adaptive-20260920/README.md),
BASIC SHA256 `c708970db2c1be838d6d38b726cbc1b94b73c88f7c5b20c0adfd4d02666436a4`.
Aaron version is `61148477-1928-43c6-a881-8daea0e8f6c2`; Coach version is
`2bb94c84-fc32-4a81-9e6d-46666bc0315f`. Both were verified active, competing and
champion; [deployment and rollback receipts](../../examples/gods_of_the_arena/players/ir/forks/formation-adaptive-deployment-20260920/README.md)
record the user's authorization. Discovery and confirmation each produced Alex
and Jordan 40/40 wins per color, Richard blue 40/40 and red 0/40. Repeated
trajectories limit generalization; broad-field qualification and formal research
acceptance remain unmet. This supersedes the deployed-policy anchors below,
which preserve the earlier handoff capture. Resolve live champions before acting.

Resolve the actual current champions on **every cycle** and immediately before promotion. These UUIDs are historical anchors, not “latest” aliases:

| Role | Player UUID | Policy-version UUID at capture |
|---|---|---|
| Aaron, incumbent | `ply_630a768f-d623-44b2-80fa-36968d6fa75a` | `4cdbbf36-3d70-4ea3-8aed-c92ee0e024be` |
| Aaron's Co-play Coach, challenger | `ply_594ec24d-d7f3-4370-a000-468354ec41c9` | `00cd9483-0309-4613-bf61-89f3f4a33d01` |
| Richard v135 | `ply_ded11f40-3e30-4921-b019-f7f6bc3e9c83` | `7c370daf-3c5f-42f8-870b-54b79c495a44` |
| Alex Smith, gota-g002:v1 | `ply_4e9a2db0-dbc2-4283-b4cc-3ce79e9f8d40` | `a30542cb-54de-4109-92e6-bcabca7db4d8` |
| Jordan v268 | `ply_bcb80069-fb0c-4ba5-a45c-06b647870aeb` | `207ffaf9-0d1e-4d92-a15d-4352f1bddec2` |

League `league_3c60897b-25cf-4b37-9d1a-8554c1198f28`; division `div_a4534073-c5d2-4193-a94a-93d9c5e2e443`; game `cow_126f2fcb-80a0-4b6e-8166-eb6163576db5`, variant `competition`. **Do not reactivate a-aron.** Prefer retaining Aaron as the incumbent and using Coach for a qualified challenger; check the most recent explicit deployment scope.

At the archived 19:55 UTC September 20 check, Richard ranked #1, Alex #2, Coach #3, Jordan #5 and Aaron #7. Treat this as dated context; a new monitor run supersedes it.

| What to read | Repository location |
|---|---|
| Deployed primary Python IR, compiler archive, evaluation, rollback receipts | [Jordan268 fork](../../examples/gods_of_the_arena/players/ir/forks/jordan268/README.md) |
| Same seven-layer policy representation | `policy.py` exposing `POLICY`, paired `policy.ir.json`, `policy.bas`, binding contracts and manifests |
| Formal accepted ancestor, **different from deployed** | [accepted-0000-b2693715459d](../handoff/gota-20260920/accepted-0000-b2693715459d/) |
| Latest captured worker state and selected active-fork policies/plans/results | [handoff archive](../handoff/gota-20260920/README.md) |
| Tested repairs and failures | [repair ledger](../experiments/gota-repairs-20260920/README.md), [coaching bundles](../../examples/gods_of_the_arena/players/ir/forks/richard135-coaching-20260920/README.md), [closed levers](../../games/gods_of_the_arena/closed_levers.md) |
| Own episode IR, including original requested episode | [episode archive](../episodes/), [multi-rule episode guide](guide-episode-semantic-ir.md) |
| Opponent IR method | [opponent guide revision 2](guide-opponent-model-ir.md), [instrument commands/limits](../../games/gods_of_the_arena/instruments/opponent_ir/README.md) |
| Primary-format inferred opponent Python models | [opponents](../../examples/gods_of_the_arena/players/ir/opponents/) |
| Joint Richard/Alex observation study | [analysis](../opponents/richard-alex-20260920/analysis.md) |
| Authentic Richard source, source IR and proposed counters | [source audit](../opponents/richard-v135/source-audit-20260920/README.md), [counter guide](../opponents/richard-v135/source-audit-20260920/counter-policy-guide.md), [economy audit](../opponents/richard-v135/source-audit-20260920/ranger-economy.md) |

Deployed BASIC hash at capture: `be6affd3b3b9516a15dc8b32687c29b728adc4aa367fc651ba5c0fcefb9cbf73`. Formal accepted ancestor: `b2693715459d0de7283ba6f45440c0084ea5c7781c2305e163976a6572246ca9`. Never silently substitute one for the other in an A/B test.

## 5. The three-hour loop

1. **Reconcile before acting.** Fetch fork updates without discarding work, read ownership/checkpoint/ledger, resume existing requests, run `remote.py monitor`. Record successful UTC check time, game source, ranks, all champion UUIDs, recent exact-version results and source hashes. Inspect current leaders beyond the three named targets too. A failed request must leave the previous successful timestamp visibly stale.
2. **Choose one failure mechanism.** Sample recent losses, draws, a contrasting win and boundary cases across colors/classes. Bind the exact policy that actually played, not today's policy. Start with the earliest consequential divergence, not the last core hit. Create an episode IR and identify the implicated layer.
3. **Update the opponent model.** Add fresh observable episodes, preserve old freezes, test competing explanations and record unknowns. When a version changes, create a new model/evidence partition. Do not carry v135 confidence into v136 automatically.
4. **Ask the coach for a falsifiable repair.** Input: exact own IR, opponent model/source status, decision blocks, runtime budget, failures/closed levers and paired controls. Output: stable hypothesis ID, layer/rule/skill, public trigger, expected command/effect change, alternatives, falsifier, runtime cost and a minimal experiment. The coach proposes; measured evidence selects. Coordinated changes may be necessary, but record the interaction and use ablations before claiming component causality.
5. **Fork, compile and screen.** Preserve the parent and all seven layers. Add versioned binding contracts rather than silently redefining old operators. Check Python=JSON, compile→exact BASIC and extraction→original IR. Test activation, negative cases, target validity, death/reset, side/classes and dense-scene budget. Then run complete matches with every policy responding.
6. **Confirm prospectively.** Freeze candidate bytes/IR/compiler, controls, opponent versions, configuration, rosters, seeds where supported, all arms, metrics and numerical decision rule **before** heldout results. Upload inertly, verify uploaded content/owner, reserve/journal XP, submit once, harvest and audit every purchased game. Discovery games cannot be relabeled confirmation. Any executable edit starts new confirmation.
7. **Decide and record.** Mark supported, refuted, inconclusive or invalid; retain null results. Add measured evidence to belief/update with byte-identical tested BASIC when merely annotating. Promote only within the verified authority and gate. Commit the useful source/models/reports to the fork; retain raw evidence privately with hashes and retrieval IDs.
8. **Checkpoint.** Save tested hashes, numerical per-color results, unique-stream counts, requests/spend, current owner, next exact command and pending blockers. Before the session ends, ensure the next scheduled invocation can recover this state. Report actual live rank after any promotion; keep researching and monitoring even when #1 is reached.

Suggested cycle allocation: first 15 minutes for reconciliation/monitoring, next 30 for focused episode/opponent analysis, remaining time for one repair and its local/hosted pipeline. Checkpoint before the 160-minute cycle limit, leaving time before the next three-hour wake. Do not purchase more games just to fill the time window.

## 6. IR discipline for our policy and episodes

Use the primary seven-layer Python dictionary: `situation`, `belief`, `goal`, `skill`, `strategy`, `execution`, `update`. Preserve stable `id / when / skill / for` rules. Semantic claims need evidence/status; new ideas start as proposed. The executable lives in explicit bindings, not untracked patches to generated BASIC.

For each important decision point, record episode/tick/actor/side, available observation, prior memory, all evaluated and matched rules, affordances, goal, **ordered action bundle**, host acceptance, execution span/termination and observable consequence. Tag missing vocabulary `[unglossed]`. Keep ground truth in separately labeled scoring/retrospective fields. “Unseen” is unknown; zero target may be masked; structure `objectAlive` means exposed, positive HP means standing. Distinguish attempted buy/cast, accepted operation and actual damage/healing/movement.

**Multiple rules can fire per tick.** Apply §11 of the episode guide. Track arbitration per channel and cross-channel host side effects. Preserve writer order, overwritten commands, guards, suppression and preemption; record independent navigation/attack/spell/economy actions. Do not reduce the tick to one “winning rule.” A movement command may cancel an attack even though the commands look like separate channels. The archived episode runner's sparse `tactical_rule` summaries are insufficient for full rule-fidelity judgments; use the detailed semantic probes and matching IR.

A reconstructed trace must match **all commands and every state hash**, and be labeled reconstructed. Internal states are the reconstruction's states unless authentic execution establishes them. Fidelity without rule evaluation records is unresolvable. A missing simulator/source makes a suspected bad decision a candidate for testing, not a “dominated” verdict.

Route findings: ontology gap→situation; wrong inference→belief; objective ordering→goal; initiation/termination fault→skill; wrong choice or uncovered case→strategy; correct interface but poor action implementation→execution/binding; insufficient or stale evidence→update/research design. An embedding fidelity defect belongs in the compiler/binding, not a fabricated strategic explanation.

## 7. Opponent IR discipline

Read revision 2 of the opponent guide. Keep observation-derived `MODEL` dictionaries in the same seven-layer Python medium with their **observer schema discriminator**. The primary action compiler must reject them. Do not pretend inferred intent is known source code.

Fit from one specified observer's **predecision** visible history. Do not pool teammate vision unless the runtime permits it. Lag features; exclude subsequently chosen targets/outcomes. Separate our visibility from the opponent's. Freeze selection, segmentation, feature definitions, population baseline and chronological holdout. Group duplicate streams; report novelty, coverage and censoring alongside accuracy. Preserve short events as well as sustained motifs, exact targets, decision clocks, memory hypotheses and override order.

The original Richard model predicted heldout motifs at 75.2% versus 54.4% population; Alex 73.2% versus 67.9%. These are conditional motif forecasts, not action/timing or closed-loop guarantees. **Every Alex heldout observer stream repeated training.** Both models have `proxy.usable=False`; zero proxy rollouts were validated. Better prediction alone does not prove an exploitable weakness.

The subsequent authentic Richard v135 source audit matched **915,098 commands across 20 games** with all five Richard VMs and replay hashes. Use the hashed `v135.bas` for responsive local opponents, bound to its manifest/hosted UUID. Keep source-derived private guards separate from deployable public predicates. Its tower retaliation branch activated zero times in the old corpus: source existence plus a synthetic fixture does not show game reachability or a winning counter. Later source reveal does not retroactively improve the original observation-only model.

A rollout opponent must predict relevant event timing, target IDs, arguments, simultaneous channels, memory and reactions to interventions, then pass closed-loop divergence checks. Future opponent commands replayed from a tape are not a reacting opponent after our action changes their observation. Replay reconstruction proves fidelity; VM fixtures prove guard semantics; full responsive games and fresh hosted tests prove a bounded competitive claim. Keep those stages separate.

## 8. Experiments and promotion

First read the existing failures. The Jordan counter confirmed 40/40 per color against v268 but later lost to Richard. Broad critical recall damaged the field; one-time red caster transit improved local/ancestor matches but went **0/40 Richard red**. Two support repairs changed **no commands** in the six-case local screen. Later blue critical-defense/coaching components achieved **40/40 Richard blue**, while the final bounded coaching combination remained **0/40 red**. A cohort variant exhausted the instruction cap in 40 red games: those are invalid, not ordinary losses. Different sources/stages explain the apparently conflicting recall results.

The subsequent [transition coaching study](../../examples/gods_of_the_arena/players/ir/forks/richard135-transition-20260920/README.md) completed during this handoff: both final variants remained Richard red 0/40 and blue 40/40. The selected unchanged `transition_freshhit` then scored Alex red 2/40, Alex blue 0/40, and Jordan 0/40 on both colors. All 400 hosted games were audited. Its narrower conditional promotion gate **also failed**, so it is not an eligible challenger. Preserve these final results as well as the earlier captured worker checkpoint.

The final [Alex historical-policy comparison](../reports/2026-09-20-alex-policy-history.md) recovered the formal ancestor at `53f15b12-2198-41d1-bb99-df4bdb1ff7fd`: a highlighted historical cohort scored Alex red 30/40 and blue 40/40, while red varied from 19–30/40 across recovered cohorts. This supplies a valuable comparison for objective-specific early alarms. It is not a fresh retest or joint-target qualification; do not promote it from historical wins alone.

The worker's captured tower-handoff source also failed target gates; its color-composed fusion was still under local investigation at capture. Read the archived progress and obtain the latest checkpoint before continuing it. Historical wins over Richard v78 or Jordan v186 do not establish wins over current versions. Do not rerun an unchanged failed source without a new discriminator.

Default **joint-target** qualification for a new final executable:

| Gate | Requirement |
|---|---|
| Richard | ≥30/40 valid wins on **each** color and ≥8 additional total wins over fresh deployed control |
| Alex | ≥30/40 on each color; no per-color regression versus fresh deployed control |
| Jordan v268/current successor | ≥38/40 on each color; if version changes, prospectively bind fresh confirmation and keep old-version evidence separate |
| Field | Candidate/control, 8 per color against pinned relh154, g002v1, black-kite16, macro4, red-kite34 and vanguard1; ≤2 lost wins per rival/color and no aggregate regression; enlarge ambiguous cells |
| Validity | Same final bytes across all claims; exact game/config/rosters/versions; all ten VMs valid; full replay hashes/actions, terminal score and total-XP reconciliation |
| Runtime | Hard limits 20,000 instructions / 50,000 work per decision; maintain the existing ≤19,000 local instruction-margin gate and test complete dense/late-game episodes |

Resolve/pin actual rival UUIDs prospectively; do not substitute a similarly named policy. Keep candidate/control matching of seed/config/rosters explicit. Report W/L/D/invalid separately, draws score zero, and count distinct canonical command/observation streams. Forty deterministic repeats do not supply forty independent trials. Quarantine infrastructure/VM failures and explain recovery; never silently drop losses or replace seeds until the desired result appears.

Formal advancement of the **research accepted snapshot** has additional gates in [researcher README](../../tools/gota_autoresearch/README.md): ≥60% versus immediate parent on both colors with ≥40 per side; no per-rival/side regression against at least five field and two historical rivals; ≥200 mixed ten-player games **per policy**, ≥5 paired rosters, ≥80 per side and two subject classes per side. Distinct player IDs are required. Uniform five-copy teams cannot stand in for this generalization test.

An archived [narrow conditional authorization](../handoff/gota-20260920/conditional-promotion-gate.json) permits a particular already-built fresh-hit candidate to be promoted to **Coach only** after ≥30/40 each color against Alex and Jordan, even if the original Richard gate fails. It specifies two source candidates and a frozen selection rule. Its completed transition study failed the gate (results above); preserve this record and the failed decision. It provides no current deployment eligibility. **Do not generalize that exception to arbitrary future candidates, overwrite Aaron, or relabel failed Richard/broad gates as passed.** New user instructions can change promotion scope; record the precise authority and continue reporting unchanged scientific results.

Promotion protocol: verify current ownership, game and rival versions; compare exact candidate bytes to the fully audited source; save current membership/source/rollback version; apply only the authorized player's membership update using the live API schema; read back competing/active/champion and content identity. On partial failure, reconcile before retrying. Retain the incumbent on Aaron when using Coach as challenger. Observe new league rounds, not just the upload receipt. Roll back the changed player on confirmed runtime invalidity or a predeclared sustained regression; save both the failed deployment and recovery receipts. Do not churn champions over a single noisy loss.

## 9. Local runs, API and portable evidence

A responsive local match after `build` (repeat on both colors and frozen cases):

```python
from pathlib import Path
import subprocess
root = Path('.gota').resolve()
ours = Path('examples/gods_of_the_arena/players/ir/forks/jordan268/policy.bas').resolve()
rival = Path('docs/opponents/richard-v135/source-audit-20260920/v135.bas').resolve()
cmd = [str(root/'bin/episode'), '--config', str(root/'game-config.json'),
       '--seed', '54', '--record', str(root/'trial.replay')]
cmd += ['--bot:' + str(ours if i < 5 else rival) for i in range(10)]
with (root/'trial.json').open('w') as out:
    subprocess.run(cmd, stdout=out, check=True, timeout=900)
with (root/'trial-audit.json').open('w') as out:
    subprocess.run([str(root/'bin/audit-hosted'), '--replay', str(root/'trial.replay')],
                   stdout=out, check=True, timeout=900)
```

The engine may print a replay-save message before the JSON result; parse the final stdout line as JSON and retain the complete log. Check all ten hero summaries, ticks/actions consumed, state hashes, scores, total XP, limits and source/config hashes. This generic runner intentionally does not access policy-private `bestId` variables; it can run authentic opponents with different variable names. Add specific probes for mechanism/rule analysis. Cross-platform native builds need replay calibration before using them as hosted auditors.

Base API: `https://softmax.com/api/observatory`. Useful read routes, already used by the monitor:

- `/v2/divisions/<division>/leaderboard?include_recent_rounds=false`
- `/v2/league-policy-memberships?league_id=<league>&champions_only=true&limit=100`
- `/v2/coworlds/<coworld>`; check manifest source URL and release
- `/v2/rounds?division_id=<division>&limit=12`, then `/v2/rounds/<round>/episodes?limit=1000`
- `/v2/experience-requests/<xreq>/episodes`
- `/v2/episode-requests/<ereq>/artifacts/{results,replay,logs,player-status}`
- `/v2/policy-versions?mine=false&q=<name>` for rivals; `mine=true` for owned versions
- `/openapi.json` for current write schemas; never guess a mutation payload

The monitor covers the latest twelve rounds, completed exact-current-champion uniform 5v5 matchups. These observational scores are **not** full experimental audits. Check pagination/truncation and expand retrieval for deeper history. There is no assumed global episode-list endpoint. Fetch replay artifacts by saved episode IDs; decode gzip when returned. Preserve missing-log markers and use structured player-status where available, rather than inventing successful execution logs.

Historical instruments often contain Mac absolute paths and implicit study directories. Inspect before running; parameterize a **new** study and pass the portable engine/tooling/binary paths. Do not rewrite archived manifests to disguise relocation. Store future study paths relative to repository or campaign roots; use an artifact manifest with SHA-256, episode/request IDs, game/source, compiler/bindings, policy parent, roster, side and seeds. Put full raw tapes, credentials and upload URLs in private durable storage; publish sanitized summaries, source, receipts without signed URLs, and hashes. The fork contains source, IR bundles and selected evidence, not every multi-gigabyte replay/cache from the Mac.

## 10. Required output from each research cycle

Maintain `CHECKPOINT.md`, `progress.json`, `LEAGUE_STATUS.json`, `xp-ledger.json`, `ownership.json` and experiment folders in durable campaign storage. Publish useful research to `docs/experiments/` and `games/gods_of_the_arena/experiments/` using the existing template; update `closed_levers.md` and affected policy/opponent belief/update records. Never erase a failed experiment.

Report: successful check time; live ranks/champion versions; game drift; exact parent/candidate hashes; hypothesis and changed rule/skill; observed mechanism versus prediction; complete per-color W/L/D/invalid and distinct-stream counts; local versus hosted evidence; frozen gate outcomes; budget/pending request IDs; deployment/readback or reason retained; next discriminating test. A “no improvement; retained incumbent” cycle is valid. A missing credential or runtime parity failure should name the exact blocker and leave other independent work progressing.

The research objective remains a stronger, measured policy and sustained leaderboard results. Never claim that the schedule, an inferred opponent model, one promoted policy, or a finite test suite ensures permanent #1.
