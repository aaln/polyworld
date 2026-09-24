# Lane selection and neutral farming / release62

User coaching: farm less crowded lanes and account for the new neutral camps.
Primary objective is expected individual `floor(max(0, XP −200×minutes))`.
Team wins, deaths, nonzero frequency and conditional means are diagnostics.

Fresh parent mean **2706.07**. Forty paired seeds per arm,
four fixed color/seat contexts, nine responsive pinned opponents. Treatments
reuse the same40controls:120valid hosted games in total.
The parent is control-tactics sourceb3f0c124, a research fork; this is not a fresh
comparison against deployed incumbent29f6d7e6.

| Treatment | Mean score | Delta versus parent | 97.5% paired interval | Pilot advance |
|---|---:|---:|---:|---|
| lane-only | 2353.15 | -352.93 | [-787.23, +91.10] | False |
| lane-neutral | 3220.45 | +514.38 | [+22.73, +972.20] | True |

Adding camps to lane selection changes score by **+867.30**,
exploratory95%interval **[+348.65, +1368.25]**.
This is discovery, with no established verdict sample floor or independent
confirmation. No deployment qualification and no league writes.

## Version and mechanics

Exact engine `2c8db6ebe1dc785ce1eea87496505d1244ee4c44`, game2026.9.23.4,
replay62/format6/outer2, coworld `cow_a472c872-2b97-4b81-9961-e171304e5d63`.
The earlier lane61+11.14% result remains separate; it is not this study's control.

Fourteen camp clearings form seven mirrored pairs. Tier1/2/3 mobs award20/35/50XP
and10/20/30gold; leaders double HP and rewards. Neutral XP goes to eligible
nearby heroes on the last-hitting unit's team, with15%reserved for an eligible
hero last hitter and85%shared. Gold requires a hero last hit. Thus allied lane
creeps can help generate neutral XP without granting the hero last-hit gold.
Returning mobs are immune. The leash is12tiles; full clears respawn after60sec
unless a living hero remains within10tiles. Static geometry is public; hidden
mob life and respawn state are not. Source: exact engine `sim.nim`, `bots.nim`,
and `players/puller.bas`; upstream neutral-camp suite passes.

The candidate retains lane/hero combat priority. With sufficient level and HP,
it farms visible nearby neutrals during gaps instead of choosing a structure
or an empty advance. If an idle allied wave is nearby, it can enter camp aggro
and move beyond the wave, within the leash. Pulls require safety and two nearby
allied creeps; they stop on handoff, danger, root, low HP, missing wave/sight,
invalid route or15sec timeout, then wait20sec before retrying. These are
heuristics, not an optimal XP planner. Direct farming and pulling are tested as
a coordinated bundle; the experiment does not isolate those two components.
The parent already admits neutrals through its generic target scan, and
attack-move can also engage them. This tests more selective neutral behavior,
not the first ability to gain neutral XP.
The new guards control explicit neutral selection and pulling; inherited
attack-move can still engage other camps incidentally.

## Validation and invalid batch

48host fixtures pass; maximum4591instructions/7621work. Twelve complete native
games pass exact replay and runtime checks. Native totals10479parent,
10701lane-only,11648combined are a small reference-bot screen only.
The first pull-cancellation prototype is archived separately; finalr62b fixes
cleanup when an earlier retreat skill has already claimed movement.

The first10hosted controls all failed Jordan411 BASIC compilation in slot7.
The other nine reported exit0. That complete batch is preserved and is invalid,
not zero-score evidence. A prospective amendment replaced Jordan with BeWellBot
and uploaded a distinct baseline clone before requesting any replacement games.
No successful or failed score was selected out of the replacement cohort.
Total new reservations:130, including10invalid; requests contain10or40games.

All120replacement games have ten valid VMs, exact full replay hashes, XP and
integer-score reconciliation, matching seeds, configs, manifests, slots and
nine unchanged opponent source hashes. Stratified whole-pair bootstrap uses
10000draws, seed9236102. Two baseline contrasts use97.5%intervals (Bonferroni);
incremental and class/context comparisons are exploratory. Canonical command
stream uniqueness is recorded in statistics.json. No game-win gate is used.
All40combined-candidate own-source reconstructions match every command and
world-state hash through the complete games: 85822commands,
39games with neutral target decisions, and
74pull starts across32games. Retrospective
source reconstruction is separate from the responsive score counterfactuals.

## Descriptive XP and time attribution

| Per-game mean | Parent | Lane only | Lane + camps |
|---|---:|---:|---:|
| Total XP | 5668.65 | 5037.52 | 6314.38 |
| Lane-creep XP | 2952.03 | 2663.50 | 3530.43 |
| Neutral XP | 1027.88 | 1120.28 | 681.45 |
| Hero XP | 1488.75 | 1046.25 | 1717.50 |
| Structure/other XP | 200.00 | 207.50 | 385.00 |
| Camp engagements | 9.90 | 9.10 | 5.25 |
| Hero kills | 9.93 | 6.97 | 11.45 |
| Deaths | 8.40 | 7.67 | 8.00 |
| Minutes | 15.49 | 14.25 | 15.50 |
| Alive XP drought ≥30sec | 126.43 | 115.22 | 123.47 |

| Context | Parent score | Lane only | Lane + camps |
|---|---:|---:|---:|
| side0-seat0 | 5008.50 | 4124.60 | 5057.50 |
| side0-seat3 | 577.20 | 577.20 | 1236.70 |
| side1-seat0 | 2963.60 | 2435.80 | 4976.90 |
| side1-seat3 | 2275.00 | 2275.00 | 1610.70 |

The combined policy earns **less neutral XP** (1027.88→681.45) and engages
fewer camps (9.90→5.25), while lane-creep XP rises2952.03→3530.43 and hero XP
1488.75→1717.50. The supported result is improved selective behavior as a bundle,
not a benefit from maximizing camp clears. The lane-only arm increases neutral
XP but loses more lane/hero XP and fails its pilot rule.

Druid's pooled mean is nearly unchanged (1426.10→1423.70), hiding red-seat3
delta+659.50 and blue-seat3−664.30. Blue first-seat ranged improves+2013.30;
red first-seat ranged changes+49.00. These are10-pair diagnostic slices, not
separate advancement gates or confirmed subgroup effects. Investigate the blue
Druid regression before broad confirmation; preserve the aggregate result.

All XP sources and disjoint time-state budgets reconcile. Neutral XP proves
reward exposure; it does not prove that wave pulls caused every neutral kill.
Route changes also alter combat exposure and travel, so the tables describe
mechanisms without assigning isolated causality. Outcomes from the frozen field
do not guarantee improvement against later opponent versions.

Parent `a0e6226e-b9e5-4c2d-8090-56d4365862dc`, lane-only `4d55ef4d-cfa2-485d-a048-a81c35b8acd3`,
combined `3ddff6be-799c-4cb7-a592-6c73471b456e` are inert research versions.
Both league champions retain source29f6d7e6. Reviewed semantic annotations compile
to byte-identical tested source2fbd789b; `python verify.py` verifies the portable
IR/policy pair, converter, evidence and hashes. Original IR, raw captures,
failed prototypes and complete hosted artifacts remain at
`polyworld/tmp/gota-lane-neutral62-20260923`.

Portable pair: `examples/gods_of_the_arena/players/ir/forks/neutralfarm20260923-hosted/lane-neutral`.

## Subsequent user-directed publication

After the study, the user instructed “publish the better policy”. Both players were verifiedactivecompetingchampions onsource2fbd789b at2026-09-24T01:30:58.496876+00:00. This does not change the frozen pilot evidence or supply independentconfirmation. See `examples/gods_of_the_arena/players/ir/forks/neutralfarm20260923-deployment` for authority,readbacks androllback.
