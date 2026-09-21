# GotA checkpoint — Devin host

Cycle `20260920T2340Z-devin-01` · written 2026-09-20T23:58Z · owner state: **observer only** (see ownership.json)

## Live (checked 2026-09-20T23:41:17Z, release 2026.9.16.5)
Richard #1 v135 `7c370daf` · Alex #2 g002:v1 `a30542cb` · Coach #3 `2bb94c84` · Jordan #6 v268 `207ffaf9` · Aaron #7 `61148477`.
Live episodes for the current Aaron/Coach versions since 22:41Z: 5W 0L 1D (Jordan ×2, g003v2 ×2, g002v1 ×1, nancy draw); no Richard pairing yet.

## Reconciliation
- Archive `docs/handoff/gota-20260920` captured 20:11Z; account made XP requests until 22:14Z → a later writer existed; its ledger/checkpoint not transferred. No purchases, uploads or membership changes from this host.
- Active requests: 0/0/0. Account spend today 4,328 episodes (limit 1,600) → hosted budget exhausted for 2026-09-20 UTC regardless of ownership.
- Deployed source sha256 `c708970d…436a4` (formation-adaptive-20260920/policy.bas). Verify: parity OK, basic `be6affd3…`.

## This cycle (local only)
Local responsive matches, pinned engine f2ab959, deployed source vs authentic Richard v135.bas `f48bb005…5a30`, seeds 54/101/202: red 0W 3L 0D 0 invalid (1 distinct stream), blue 3W 0L 0D 0 invalid. Max instr 18,410 (<19,000 gate), no VM failures. Structure probe replayed with 0 hash mismatches.

## Hypothesis H-RED-OPEN-SPLIT-01 (proposed, untested)
Layer strategy/skill, red opening. Slots 2–3 reach the centre structure alone by tick ~1085 while 3 Richard heroes are there; both die (first blood), then 101/104 die at (56–58,25–27) by 1540. Predicted mechanism: early XP transfer → Richard L7 heroes → faster structure race. Falsifier: a variant that keeps ≥3 red heroes grouped before contesting centre that still loses with ≤1 death by tick 1800 refutes "early split" as cause. Runtime cost: expected ≤ +300 instructions (one belief predicate + rule).

## Next exact command
Compile `replay_semantic_episode_probe.nim` in `.gota/engine`, run on `.gota/cycles/20260920T2340Z-devin/local-richard/red-54.replay` for slots 2,3 to extract matched rules ticks 0–1150. No hosted spend until ownership transfer is confirmed and a new UTC day begins.

## Standing instruction (Aaron, 2026-09-21 ~00:15Z, offline ~27h)
Monitor the league; fork/improve only on evidence a rival is majorly beating us. Trigger (any):
- current Aaron or Coach version loses ≥3 of last 5 head-to-heads vs one rival across ≥2 checks, or
- either player drops ≥2 ranks vs the previous check and stays down at the next, or
- a new rival version appears above both of ours with ≥2 wins over us.
Otherwise: local research only, no hosted spend. Ownership: claim single-writer if no foreign XP requests since last check (last foreign: 22:14:20Z). Deploy to Coach first; Aaron = rollback.

## Cycle 02 — check 2026-09-21T00:23:31Z (engine 2026.9.16.5, no drift)
Live: Richard #1 1956.3 v135 `7c370daf`; Alex #2 1700.5 g002:v1 `a30542cb`; Coach #4 1669.8 `2bb94c84`; Jordan #6 1626.0 v268 `207ffaf9`; Aaron #8 1614.6 `61148477`.
Exact-current-version live H2H since deploy (completed): Coach — W vs Richard(blue), W vs Alex(blue), W vs Jordan(blue), W vs Scott g003(red), D vs macromackie v4(red). Aaron — W vs Jordan(red), 2W vs Scott(blue), D vs NanosaurusX(red), **L vs relh v159 (blue)** — relh v159 is a NEW version, watch it. No red game vs Richard yet (known 0/40 hosted).
Trigger: NOT met (ranks −1 each vs 23:41Z, first check of slippage; no repeated H2H losses). No hosted spend.
Ownership: claimed single-writer (no foreign XP requests since 22:14:20Z over two checks; 0 active). Spent today 0/1600.
Local step: observer-trajectory probes (hash-validated, 5898 ticks, 73861 actions) on red-54 slot2 and blue-54 slot7 → H-RED-TRANSIT-01 (see progress.json): red-only caster-transit sends slots 2–3 alone to centre at tick ~850 into 3 Richard heroes; blue has no such lone pair. Next discriminating test: fork with transit gated on ≥3 nearby allies, screen red vs Richard and red vs Alex/Jordan (risk: transit is part of tested Alex/Jordan red package).

## Cycle 03 — check 2026-09-21T02:23:39Z (engine 2026.9.16.5, no drift)
Live: Richard #1 1941.5 `7c370daf`; **relh #2 1703.5 v159 `ce5bfbfa`**; Alex #3 1689.7; Coach #4 1673.1 `2bb94c84`; Aaron #5 1632.4 `61148477` (+3); Jordan #6.
H2H current versions (completed since deploy): Coach 9W 3L 2D (L: relh blue, Richard red, Aaron red); Aaron 8W 5L 4D (L: relh blue, relh red, macromackie blue, Coach red x2). Invalid/incomplete: 3 (Aaron–Alex, Aaron–Richard, Coach–Richard, Coach–Jordan not completed).
**TRIGGER MET: relh v159 — 3 losses/0 wins vs us over two checks, both colours, ranked above both our players.** Richard red loss is the known 0/40 pattern (no new information).
Ownership: single-writer (this host); 0 active XP requests; spend today 0/1600. No hosted spend this cycle (no candidate yet).
Diagnosis (3 hosted replays, all hash-validated): see docs/opponents/relh-v159/inferred-20260921/model.json. Blue-loss = ONE distinct stream (Aaron/Coach replays identical). Mechanism: relh focus-fires one hero at a time + caster burst; our other two stack members keep hitting creeps for ~60 ticks while the teammate dies (episode IR, ticks 1470-1560). Red-loss: relh 5-stack lane push vs our 1/2/2 dispersal.
Coach hypothesis H-ALLY-UNDER-ATTACK-01 (progress.json). Next discriminating test: fork + activation test at ereq_ea546a70 tick 1470 + local screen vs Richard/Alex/Jordan, then hosted A/B vs relh v159.

## Cycle 04 — check 2026-09-21T04:23:44Z (engine 2026.9.16.5, no drift)
Live: Richard #1 1922.5 `7c370daf`; relh #2 1733.4 v159 `ce5bfbfa`; Coach #3 1683.2 `2bb94c84` (+1); Alex #4 1674.6; Aaron #5 1648.8 `61148477`; Jordan #6.
Trigger: relh v159 trigger from cycle 03 still active. No new foreign XP requests; single-writer retained; 0 active requests; spend 0/1600. No hosted spend, no deploy.
H-ALLY-UNDER-ATTACK-01 tested locally: v1 (fork ally-under-attack-20260921, src 28a33472…) FALSIFIED — blue vs Richard 0W/3L (parent 3W/0L), 20–32 deaths. v2 (ally-under-attack-v2-20260921, src 5608d806…) NOT QUALIFIED — zero activation vs Richard (state hashes identical to parent), +2,101 instr blue, 3 INVALID red-vs-parent games (VM instruction limit). Both forks verify.py-exact. Details: docs/reports/2026-09-21-devin-cycle-04/. Incumbent retained.
Next: belief-layer memoised assist predicate + activation test on relh replay ereq_ea546a70 tick 1470 before any screen; keep H-RED-TRANSIT-01 as alternative. Hosted A/B vs relh only after local gates pass.

## Cycle 05 — check 2026-09-21T06:23:45Z (engine 2026.9.16.5, no drift)
Live: Richard #1 1903.2 `7c370daf`; relh #2 1768.9 v159 `ce5bfbfa`; Coach #3 1670.5 `2bb94c84`; Aaron #4 1661.2 `61148477` (+1); Alex #5; Jordan #6.
H2H exact current versions: Aaron 20W/10L/2D, Coach 16W/12L/3D; relh 0W/9L vs us (trigger sustained). Watch: daveey-2 side-aware-team-secondary v1 3W/0L vs us; macromackie v4 0W/3L/4D vs us.
XP: 0 active, no foreign writers, spend 0/1600; no hosted spend. No deploy.
Local step: offline activation test of the ally-under-attack predicate on hosted relh observer trajectories — fires at tick 1418/1436 for 108/107 in the blue loss (61/59 ticks), 0 in the red loss. Mechanism belief confirmed observable; repair blocked only by runtime/globals (parent at 256/256 globals). Report: docs/reports/2026-09-21-devin-cycle-05/.
Next: v3 single-pass, zero-new-globals fold into main scan; local gates; then hosted A/B vs relh v159 through the journal.

## Cycle `20260921T0823Z-devin-06` · written 2026-09-21T08:58Z · single-writer held
Monitor 08:23Z: Richard #1, relh #2 v159, Coach #3, Aaron #4, Alex #5, Jordan #6 (no engine drift). relh trigger sustained (Aaron blue 0-3, Coach blue 0-4 red 0-1 in window).
H-ALLY-UNDER-ATTACK-01 v3 (`d60f9626…`, zero new globals) passed local gates (0 invalid, no regression vs Richard/parent, +661 instr) but hosted A/B vs relh v159 fixed seats: candidate red 0-40, blue 0-40, control (deployed Aaron) red 0-40; hosted blue trajectory hero-state identical to the parent loss → predicate true but no effective retarget. **Falsified. Incumbent retained; Coach unchanged; nothing deployed.** Spend 120/1600 today, 0 active. Tooling: tools/gota_autoresearch/hosted_ab.py (frozen plan, idempotent, journaled). Report: docs/reports/2026-09-21-devin-cycle-06/.
Next (10:23Z): H-RED-TRANSIT-01 red fork (transit gated on ≥3 nearby allies, zero globals) + scenario-vm single-tick trace of hero 108 @1418 on the hosted observer snapshot.
