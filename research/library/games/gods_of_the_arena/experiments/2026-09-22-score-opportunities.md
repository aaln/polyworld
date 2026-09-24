# Individual XP opportunity selection

Status: complete; 160 fresh hosted games audited. Candidate rejected; deployed portal policy retained on both players. Earlier design and launch entries below preserve their original timing.

User direction: individual score is the sole objective; improve hero-kill XP
and account for elapsed time. Parent is deployed portal source db71abb3, on
2026.9.22.2 / ffcedcd866c4d31924361ed4baff2b7a6d3aba67. Existing closed levers
were reviewed. This is a distinct target-allocation experiment, not a repeat
of the rejected mirrored movement or faster-attention bundles.

Hypothesis: explicitly comparing bounded, feasible hero engagements with creep
income will increase individual score. The parent gives forts a 500-point
target bonus, pursues visible targets up to18tiles, and only adds300 for a
hero below four raw basic hits. The new controller separates hero, creep and
structure opportunities before assessing complete nearby public force/tower
context. A nearby nearly defeated hero should outrank a creep last hit; a
healthy or dangerous distant hero should not draw the bot away from farming.
Buildings remain available when no better XP opportunity is visible.

The score is max(0, XP*1440 -200*world_ticks)//1440, including draft. A hero
kill rewards150XP, a creep has a shared15XP pool, and a building kill100XP.
This is not XP divided by duration. No unconditional stalling is proposed.
Live BASIC does not expose lifetime XP, so no invented rolling-XP feature is
used. Public HP/distance/basic damage and nearby levels are imperfect utility
proxies; armor, geometry, spell hits and fog can invalidate a predicted kill.

Predictions: close finishable heroes displace routine structure targets and
creep last hits; poor chases fall back to creeps; scan order no longer changes
the available force context used by the final hero-versus-farm choice. If the
hypothesis is wrong, hero XP fails to rise or extra deaths/time outweigh it.

Before hosted work, require real-host selection/negative/tower/retreat tests,
both colors and classes, dense-scene VM margins, preserved portal fixtures,
and complete native replay/hash/runtime checks. Native score is diagnostic
only. Existing160 portal games are historical evidence, not this candidate's
concurrent control.

Prospective hosted comparison:160 games,40per source/color, one subject and
nine exact pinned mixed-team policies, khors:v114 opposing on both sides.
Fresh db71abb3 controls; rotate both whole teams. Advancement requires zero
invalid games, at least10% aggregate mean integer-score gain and each color
at least95% of control. Report hero/creep/building XP, kills, deaths, duration,
outscore counts, duplicate streams and whole-game confidence intervals.
Team victory is diagnostic. This experiment cannot establish #1 or universal
opponent superiority. Coordinated changes are evaluated together; no claim
about a component's isolated causal contribution follows.

Critique: target utility is a heuristic, no guarantee of kill credit; nearby
ally levels are not exact effective power; one pinned first-pick roster limits
generalization;40games/cell may leave wide intervals. Each is reported rather
than hidden behind a win rate. Captured coaching inputs and parent pair stay
unchanged. Today's1760/1760 hosted budget is exhausted; finish a concrete,
locally checked pair before requesting any additional allowance.

## Live-version change before hosted work

The live GET check discovered2026.9.22.3, source1b708944, coworld2cb5d47d,
replay58. Source diff adds500XP for every teammate when the enemy god falls;
no other simulation/API/content change versus ffcedcd. Old r1/r2 candidates
remain preserved. R1 exceeded fixed-point conversion range on the synthetic
100000HP portal-threat fixture; integer division repairs that in r2. R2 passes
84portal fixtures on the old engine. Neither has hosted evidence.

R3 binds to the new engine and adds finishing priority for an exposed god
within basic reach and four raw hits. Healthy gods remain below productive
living targets. This accounts for500 own XP and saved time without turning
team wins into a separate acceptance gate. All new comparisons require fresh
controls and replay58 calibration. The original design above is preserved
as the pre-drift record.

## Local result on2026.9.22.3

Sourcef6a0dace passes180target/reward cases,84portal cases and126broader
all-class/runtime checks. Max instructions15927 and work22716 stay below
19000/50000. The initial target fixture let automatic acquisition happen
before the intended decision; its failed80rows are preserved. Corrected
fixtures force a due decision before simulation and require target plus actual
attack intent and realized kill XP. Deployed parent differs in60 intended
choices (finishing hero, hero over healthy god, finishing god).

Eight complete native matches (one subject, nine current host reference bots)
pass full hashes/XP/integer scores and runtime. Scores by source/red-blue:
parent2810/3832; candidate3170/5163.5. All four matched pairs improve. Pooled
mean3321→4166.75; heroXP2325→2550, creepXP2118.5→2323.5, kills15.5→17,
deaths1.5→1.5, minutes11.1083→10.5321. Hero XP falls on red and rises on blue.
These are mechanism/runtime diagnostics, not a competitive verdict.

The replay58 auditor exactly reconstructs ereq_b825c4d6-44a9-478d-baa0-dcd3f75cf7ca,
including total XP and integer scores. Other VM slot3failed in that game, so
it establishes decoder calibration only. All ten planned exact versions have
individual current-engine runtime admission. Before any hosted result, the
Games Bond listing returnedHTTP500; substitute currently active Julia with
healthy VM in the prespecified calibration replay, equally for both arms.
Khors114,Jordan411,Richard167 oppose both colors;relh161 is a teammate.

Hosted verdict pending. The completed historical portal cohort cannot replace
fresh controls after the500XP rule changed. No new games requested and no
league selection performed in this iteration.

## Hosted authorization and launch

User explicitly answered the prepared-comparison budget question: "raise cap
to10000". At2026-09-22T21:11:52UTC the dated effective cap changed1760→10000,
with the shared1760already reserved retained and the normal1600limit unchanged
for later dates. Cycle400and at-most-three-active-request limits remain.
Authorization and the prior config are preserved under raw budget/.

The exact prepared160-game plan is now running; its original budget-pending
text remains as a frozen preregistration. The current allowance is recorded
separately. First request: xreq_785f2cfc-ce49-485e-a091-894e732047fb. Dashboard
http://127.0.0.1:8852. No acceptance threshold or source changed.

## Completed hosted result — reject candidate

All four requests completed with 40 valid, distinct command streams each:

| Arm | Color | Request |
|---|---|---|
| Baseline | Red | xreq_785f2cfc-ce49-485e-a091-894e732047fb |
| Baseline | Blue | xreq_5a46e045-c27b-492c-be42-1548b241fcd3 |
| Candidate | Red | xreq_4e44fd54-0dc9-4faf-b449-8ae5d81e6834 |
| Candidate | Blue | xreq_20e206bb-3ae3-4ef0-a46b-30d354fe6f12 |

Every game's ten source hashes and VM exits, complete replay hashes, XP-source
sum and integer score passed. All 160 are included; no replacement seeds,
invalid exclusions or reused historical controls. Both whole teams rotated.

| Mean per subject | Baseline red | Baseline blue | Candidate red | Candidate blue |
|---|---:|---:|---:|---:|
| Score | 1955.20 | 2990.85 | 2155.25 | 2313.65 |
| Total XP | 4871.375 | 5881.725 | 4997.725 | 5050.000 |
| Hero XP | 1781.25 | 2242.50 | 1728.75 | 1695.00 |
| Creep XP | 2587.625 | 2921.725 | 2876.475 | 2812.500 |
| Building XP | 402.50 | 542.50 | 330.00 | 430.00 |
| God XP | 100.00 | 175.00 | 62.50 | 112.50 |
| Hero kills | 11.875 | 14.950 | 11.525 | 11.300 |
| Deaths | 6.500 | 5.975 | 6.450 | 5.700 |
| Level | 10.825 | 12.075 | 10.900 | 11.150 |
| Minutes, including draft | 14.720 | 14.452 | 14.723 | 13.679 |

Aggregate mean score **2473.025 → 2234.45 (−9.647%)**, with red **+10.232%**
and blue **−22.642%**. The side-stratified, independent whole-game bootstrap
95% gain interval is **[−25.649%, +9.743%]**. Neither the aggregate +10% gate
nor blue's 95% retention gate passes. This exact candidate is **not deployed**.
No claim of a universal negative effect follows from this fixed roster.

Red's improvement comes mainly from +288.85 creep XP; hero XP fell 52.5.
Blue lost 547.5 hero XP and 831.725 total XP. Its games were 0.773 minutes
shorter, saving about 154.6 time-penalty points, which did not offset the lost
XP. Fewer raw deaths and fewer out-of-range actions accompanied lower score;
these are diagnostics, not substitute objectives. Team wins also fell, but do
not determine this decision. XP and time means do not exactly reconstruct mean
score because the final score is clipped at zero and rounded per game.

Draft mix does not explain away blue's loss: Crossbowman picks rose 17→26 out
of 40, yet within-class mean scores fell 27.72% for Crossbowman and 34.03% for
Ranger. Descriptive standardization to pooled class frequencies gives blue
−30.00%, red +11.40%. Small conditional cells and other seeded composition
differences prevent causal attribution. This exploratory check does not change
the preregistered unadjusted acceptance rule.

The candidate outscored khors114 in 13/40 red and 20/40 blue (33/80), versus
baseline 38/80. Candidate mean own-minus-khors gaps were −542 red and −399.4
blue; both paired difference intervals cross zero. It outscored Jordan411 in
67/80 and Richard167 in 53/80. Those counts do not override the failed score
gate; relh161 was a teammate, so no opposing-relh claim is made.

The reviewed pair is
`examples/gods_of_the_arena/players/ir/forks/score-opportunities20260922-hosted`:
source f6a0dace unchanged, reviewed IR e3786265. CompetitiveGain is marked
contradicted for this exact bundle; host-mechanism claims remain supported.
Compile/extract round-trip, local evidence and all hosted result hashes are
preserved. The prior local pair, failed r1/r2, original coaching inputs and
baseline pair remain untouched. Both owned champions remain db71abb3.

After the authorized 160 games, the shared September 22 journal records
**1,920 / 10,000 reserved; 8,080 remaining**. No pending comparison request or
league write remains. The inert candidate upload is retained for provenance.

Next research should test a distinct mechanism that recovers reachable hero
kills without losing farming or survival. Audit rejected hero opportunities,
spell reach and realized damage, then freeze a new coordinated candidate and
new prospective comparison. Red's result alone does not validate splicing this
controller into a color-conditional policy. Preserve the current exact bundle
as a failed experiment rather than rerunning it unchanged.
