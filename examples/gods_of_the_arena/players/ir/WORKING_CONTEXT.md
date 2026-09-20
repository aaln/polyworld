Active work moved to the clean `.3` workspace: `/Users/aaln/experiments/softmax/polyworld-gota-clean-20260916-r3`. Read its WORKING_CONTEXT.md. Original game edits remain preserved.

# Current research moved to a clean workspace

Use `/Users/aaln/experiments/softmax/polyworld-gota-clean-20260916/examples/gods_of_the_arena/players/ir/WORKING_CONTEXT.md` for current work.
Live2026.9.16.2/source5c701f9; isolated clean engine and pinned dependencies.
Current artifacts: `/Users/aaln/experiments/softmax/gota-research-20260916`.
Original local gameplay changes are preserved. The report below describes the preceding release.

# Gods of the Arena autoresearch — completed September16,2026

User's latest autoresearch request completed:16 IR variants,880 local games,
2100 new hosted games. A better policy passed fresh confirmation and field
validation and was deployed on Aaron's Optimizer. No new permission needed for
future authorized evaluation/improvement/deployment; keep two owned players.

## Current active players (API verified)

League`league_3c60897b-25cf-4b37-9d1a-8554c1198f28`; division
`div_a4534073-c5d2-4193-a94a-93d9c5e2e443`.

- Optimizer`ply_594ec24d-d7f3-4370-a000-468354ec41c9`: **aaron-gota-ir-cadence-all-0916:v1**,
  version`c5711f9d-6248-4843-ae39-bc13a4911b79`, membership
  `lpm_365995fe-5793-4098-959a-c211f850b8c0`; active competing champion.
- Aaron`ply_630a768f-d623-44b2-80fa-36968d6fa75a`: waveguard-r4:v2,
  version`6d0ff780-652f-47a8-82b3-336cb7a10a56`, membership
  `lpm_c32ccc98-8cba-451f-9b81-52fb05e88478`; active competing champion.

Exactlytwo owned champions verified; auto_championnever. Do not use OptimizerJr.
No first-place claim or post-deployment rank improvement measured yet.

## Validated source and evidence

Canonical **cadence_all.evaluated.ir.json/.bas**, IRrevision22. This is the
parent for future optimization; motion/cadence candidate factories still encode
historical studies and should not silently restart from the old deployed motion.
BASIC SHA`d44442652129be56516e6ef675bd338d05a0a7863e2372958d2da8fece348c8e`.
Exact compiled bytes and reverse-extracted IR match. Feedback includes authored
cadence goal and rule rationale, measured mechanism, confirmation, field and
deployment. No safe-escape claim: one-tick walks mostly turn the hero.

RUN=`tmp/gota-ir/autoresearch-20260916/cadence-cycle`.
Read `completed.json`, `deployed-feedback/`, and
`experiments/2026-09-16-autoresearch-result.md` for complete results.

Fresh400games/arm: cadence215, waveguard175, motion176. Gains+10pp/+9.75pp,
Fisherp=.002886/.003579; all frozen gates passed, no adverse-class flag.
Deathrate.39800 versus.65400/.48925; meanGlory989.37 vs389.51/365.32. All1200
full tapes, VM outcomes, configs, seeds, rosters, scores and XP verified. Previous
discovery excluded. No dropped/replaced cases. Gearinall400candidategames.
Field:58/100,13otherchampion versions/59opponentsets, gearall100/fullaudits;
excludedbothownedplayers. Request`xreq_98443e6b-3124-4449-84ba-4af4e06aa594`.
All research XP and audit processes completed. Dashboard remains atlocalhost8798.

First iteration failed:520local/400hosted; farm46/100,center41 vs motion54/v252.
Second discovery:360local/400hosted; cadence54/100 vs v246/motion37; guard36.
Old motion1200game recovery passed340/600vs304/600 on an older roster. Those
already-played games are not counted as new or pooled with current confirmation.
Failed settings remain in closed_levers.md; do not retry unchanged for luck.

## Mechanics and next research

Published2026.9.15.3, sourcee1279894d10a7684f303e7a9f1ea2f84c1d14253,
coworld`cow_fdd365d8-57ba-4e3f-8c06-f0b87cd6d870`. Exact runtime under
`tmp/gota-ir/runtime-2026.9.15.3`. Rootgamefilesuserdirty: preserve them.
One confirmed-hit movement decision shortens recovery;300discovery tapes showed
21.28basic hits/alive-minute vs12.58motion/12.78waveguard. Repeated hit intervals
shortened acrossallclasses. Median walk displacement0; no effective escape claim.
Two candidate discovery games still had long friendly-tower pathing stalls.
Previously tested continuous tower detours failed; a new destination-persistence
hypothesis needs its own evidence. See hypotheses/2026-09-16-followups.md.

## Operational rules and tools

Use../metta/.venv/bin/python and hosted_wave.client/get; never print credentials.
100episode XP requests, stable per-study keys, serial game batches with streaming
harvest+audits. Independent request-derived seeds are not paired. Fresh controls,
predeclared gates, no outcome peeking/optional stopping. Current helpers:
economy_screen, economy_hosted, hosted_queue, economy_field, economy_deploy.
Deployment helper defaults read-only; --apply is authorized only after validation.
It hardcodes both old player/control identities for this completed transition;
update those deliberately before a future deployment study.

One pod-log capture failure used official structured player-status proof:
ten distinct slots exited0/Completed. Published source ties it to the same sticky
BASIC-failure flag as headless status. Keep originalmarker; missing/failed/duplicate
or contradictory status is rejected. APIcompleted alone is not VM proof.
recover_hosted_vm_status.py backfills this proof for explicit capture markers.
Do not run duplicate audit writers for the samefolder (shared temporary paths).
Queue now waits all collectors before raising an earlier error; originalcontroller
exit killed one collector, which was resumed on the same request successfully.
100full-suite tests plus3roster+1queue checks passed. Recovery records and hashes
are in RUN. Complete historical context archived in RUN/working-context-history.md
and working-context-before-completion.md; scientific records/receipts retained.

Raw BASIC uploads only. Stored-content409 -> files/complete; versions bind to a
player. Upload != submission != champion. Explicit champion selection and
champions_only=true&mine=true readback are required to verify two ladder players.
