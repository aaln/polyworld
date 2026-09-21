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

## Cycle 07 — 2026-09-21T10:23:48Z (engine 2026.9.16.5, no drift)
Ranks: Richard #1 7c370daf (1870.98), relh #2 ce5bfbfa v159 (1832.9), Coach #3 2bb94c84 (1679.44), Aaron #4 61148477 (1651.97), Alex #5 a30542cb (1639.37), Jordan #6 207ffaf9 (1622.30).
H2H window (current versions): Aaron/Richard red 0-1; Coach/Richard red 0-4; Coach/relh blue 0-3, red 0-1. relh trigger sustained. Ownership unchanged (Aaron incumbent, Coach challenger, a-aron retired). Reconciliation: 0 pending/submitted/running requests from cycle 06.
H-RED-TRANSIT-01: two zero-new-global forks of skill.transit_state (group: gate on mAllies>=6; off: mAllies>=99). Both compiler-exact (79 modules). Local (seeds 54/101/202, pinned f2ab959): identical results for group and off -> guard reads mAllies before the object scan populates it (stale), so both == transit disabled. Red vs Richard v135 0W/1L/2D (draws to 28800 ticks; parent 0W/3L), red vs parent 0W/3L, blue hash-identical to parent, 0 invalid, 3 streams/colour, max instr 18871.
Hosted (journaled study gota-ab-transit-off-relh159-20260921, version 69fac10f inert): candidate red vs relh v159 40 eps -> 0W/40L/0D/0 INVALID (cycle-06 control red 0-40). FALSIFIED. Nothing deployed, no membership change.
Spend: 40 this cycle, 160/1600 today, 0 active. Next: scenario-vm trace hero108@1418 (why v3 retarget not emitted); red lane-assignment probe (dispersal not caused by transit alone).

## Cycle 08 — 2026-09-21T12:23:43Z (engine 2026.9.16.5, no drift)
Ranks: **relh #1** ce5bfbfa v159 (1868.12), Richard #2 7c370daf (1828.62), Coach #3 2bb94c84 (1700.85), Aaron #4 61148477 (1661.85), Jordan #5 207ffaf9, Alex #6 a30542cb, macromackie #7, Andrew Brower #8.
H2H window: Aaron 14W/11L/4D (relh blue 0-2 red 0-1; Andrew Brower red-kite:v34 red 0-4 NEW WATCH; Richard red 0-1; nancy-goa:v2 red 0-1-2), Coach 18W/9L/3D (Richard red 0-4 blue 3-0; relh blue 0-2; Aaron red 0-2). relh trigger sustained (now above both and #1). Ownership unchanged. Hosted: cycle-07 request harvested/closed, 0 active; no new spend.
Mechanism finding (v3 null result): rule R2 (richard_formation_combat_v1) skips the whole threat/kite/assist scan when objectCount() > motion_object_limit (80) or > defense_motion_limit (40) during shared defense. Hosted relh observer trajectory (ereq_cf6a3dd5) counts 64-94 objects at ticks 600-2400 -> controller degrades to plain attackTarget in team fights, which is where the v3 assist lived.
H-MOTION-GATE-01 (parameter-only forks, frozen compiler, zero new globals, contract ranges respected):
 - def80 (defense_motion_limit 40->80, src 2305c0e9…): vs Richard red 0-3 (5971 ticks, 1 outcome), blue 2W/1L (parent 3-0) -> blue regression, FALSIFIED; vs parent red 0-2-1, blue 3-0; max instr 18791.
 - mol120 (+motion_object_limit 80->120, src f4ebc0ec…): vs Richard red 0-3 (same), blue 3-0 in 11433 ticks (faster than parent); vs parent red 0-3, blue 3-0; 0 INVALID; max instr 19023 of 20000 (977 headroom) -> too thin for hosted 5v5 object counts; not qualified, no hosted spend.
Red vs Richard remains 0-3 with identical 5971-tick collapse under every fork so far (transit, assist, motion gate): the red failure is upstream of combat control (opening lane/formation), next target.
Next: probe red-54 ticks 0-1200 matched rules for lane assignment/formation (R_lane*, gaActive) to name the rule that produces the 1/2/2 split; consider mol100 if a red repair needs the scan.

## Cycle 09 — 2026-09-21T14:23:52Z (engine 2026.9.16.5, no drift)
Ranks: relh #1 ce5bfbfa v159 (1888.9), Richard #2 7c370daf (1810.4), Coach #3 2bb94c84 (1686.5), Aaron #4 61148477 (1662.3), Alex #5 a30542cb (1628.4), Jordan #6 207ffaf9 (1623.2), macromackie #7, NanosaurusX #8.
H2H window: Aaron 15W/10L/5D (relh red 0-1 blue 0-2; Andrew Brower red-kite:v34 red 0-3 blue 2-0; Richard red 0-1), Coach 17W/10L/4D (Richard red 0-1 latest slice, prior red 0-4; relh blue 0-2). relh trigger sustained. Ownership unchanged (Aaron incumbent, Coach challenger, a-aron retired). Hosted: 0 active, no new spend (160/1600 today).
Red-opening probe (cycle-02 hash-validated red-54 trajectory): red spawns ~(107,5); slot 0 (class 5) spawn (110,9) is nearest the right-lane creep wave and escorts it alone (R1 observe: waveChosen = nearest friendly kind-3 creep, retained via escortId); slots 1-4 go left along the top; caster transit (R_profile_transit) then splits 2-3 off -> 1/2/2. Blue geometry yields 3/2.
H-RED-LANE-01 (skill.observe contract fork formation_profile_observe_red_lane_bias_v1: red-only +4096 squared-distance penalty for non-retained waves at x >= selfX; zero new globals; frozen compiler 79 modules, compiler-exact):
 - lane (src 07b4e383…, ir 07980301…): vs Richard v135 red 0-3 (6088 ticks vs parent 5971 -> trajectory changed, same collapse), blue 3-0 (unchanged); vs parent red 0-3, blue 2-0-1; 0 INVALID; 3 streams/colour; max instr 17844.
 - notransit (lane + transit_min_allies 99; src 3a36dbbe…, ir eb000320…): vs Richard red 0-3 (5282 ticks), blue 3-0; vs parent red 0-3, blue 2-0-1; 0 INVALID; max instr 18149.
 FALSIFIED: formation/lane assignment is not the red mechanism. Nothing deployed, no membership change.
Mechanism evidence (per-hero end stats, seed 54): Richard's heroes out-farm ours on BOTH colours — Richard red-side heroes 38/111/48/94/117 basic hits, levels 2-9 vs ours 3-32 hits, levels 1-5 (red slot 0 class 5: 3 hits, level 1, 4 deaths over 6088 ticks = inert tank); even in our blue WIN Richard has 102/83 hits vs our max 37. The ~6000-tick red collapse coincides with a level/XP deficit, not the opening shape.
Next: H-FARM-01 — probe why our heroes take so few basic hits (attackTarget acceptance vs creep selection in R2/R4; is the class-5 tank stuck in defensive fallback?) with an instrumented red-54 trace of per-tick attackTarget calls and hits for slot 0; then one farm-rate fork. No hosted spend until a candidate beats the parent red locally.

## Cycle 10 — 2026-09-21T16:23:47Z (engine 2026.9.16.5, no drift)
Ranks: relh #1 ce5bfbfa v159 (1904.0), Richard #2 7c370daf (1800.8), Coach #3 2bb94c84 (1682.4), Aaron #4 61148477 (1671.7), Alex #5 a30542cb (1630.2), Jordan #6 207ffaf9 (1612.3), macromackie #7, NanosaurusX #8. Unchanged order.
H2H window: Aaron/Richard red 0-2, Coach/Richard red 0-1; relh trigger sustained (#1 above both). Ownership unchanged (Aaron incumbent, Coach challenger, a-aron retired). Hosted: 0 active, no new spend (160/1600 today).
H-FARM-01 → H-RED-DEFREL-01 (skill.observe contract fork formation_profile_observe_red_def_release_v1: the far-from-home shared-defense release `dist(defHome) > 28 and adMode<>1 and worldTick>=criticalUntil -> defActive=0` was blue-only (`selfTeam = 1`); extended to red. Zero new globals; frozen compiler 79 modules, compiler-exact; src 6ffbede7…, ir 373258c4…; diff vs parent = 1 condition line + header):
 - vs Richard v135 red 0-3 (5898 ticks vs parent 5971 -> release activated, trajectory changed, same collapse; our lvl 15 vs 21, deaths 7 vs 1), blue 3-0 (4824 ticks, unchanged from parent); vs parent red 0-2-1 (loss 13419, draw 28800), blue 2-0-1; 0 INVALID; 3 streams/colour; max instr 18410.
 FALSIFIED: red defActive stickiness is not the farm-rate mechanism. Nothing deployed, no membership change.
Next: H-FARM-01 continued — instrumented per-tick trace of red slot 0 (class 5) attackTarget calls vs hits in ticks 0-1500 (is it targeting anything? is R4 fallback/route overriding R2 each tick?); compare with a Richard red hero's attack cadence. No hosted spend until red beats parent locally.
