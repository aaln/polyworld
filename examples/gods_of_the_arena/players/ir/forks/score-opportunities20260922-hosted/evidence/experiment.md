# Individual XP opportunity selection

Status: local development; no hosted request or deployment.

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
