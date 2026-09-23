# Relh v169: source audit and useful transfers

**The distinctive change is drafting. Its battle controller is byte-for-byte
identical to Richard v174, whose earlier transfers into our policy did not pass
their score gates.** The useful lesson is to diagnose why a particular draft and
controller score poorly before importing another player's rules.

We recovered the exact source from the user-specified `../co-gas` repository,
reconstructed **142,715 commands in eight complete games**, and reviewed all
**200 existing current-engine controls** from our unit-farming experiment.
Every reconstructed world hash and source command matches. All 200 games have
clean ten-player VM audits, reconciled XP and integer scores. This is source and
behavior verification, not a competitive trial of a new own policy.

The live leaderboard read at **2026-09-23 18:23:10 UTC** has Andre/khors180 first
(2,048.64), Aaron second (1,773.63), relh169 third (1,638.32), Coach fourth
(1,572.57), Richard195 fifth (1,375.54). That is a snapshot, not a forecast of
the league winner. [Captured readback](live-readback.json).

## What v169 changed

The [exact source](source/relh-v169.bas) has SHA256
`6791bc8cab237d88225356efa03713e2dbbd875c2c42bb718f1cfc926b02f9ca`, policy UUID
`0f0c8e5a-a004-4c34-88ba-56bd2cca0dc1`. Its recorded introduction is co-gas commit
`be20720b4f493d50056d768af0d2cbcfe85edb1c`; source checkout was
`27fb04fabfda2f2731ab231bfb17d3daf3347462`.

V169 replaces a handwritten draft heuristic with a legal-masked linear selector:
10 available-class flags, 10 ally class flags, 10 enemy class flags and two team
pick counts. It uses public draft observations, not opponent names or hidden XP.
The extracted [fixed-point weights](draft-controller.json) reproduce all 200
observed relh picks. Its battle body, starting at line 405, exactly matches
Richard174 from line 55 through EOF. [Byte comparison](battle-body-comparison.json).

The co-gas [candidate record](source/candidate.yaml) reports that v161 selected
Vanguard/Death Knight in two zero-score games despite Crossbowman being available.
The head chose Crossbowman in those states. Four paired replay58 controls report
scores `0,0,0,0 → 2318,6969,0,2637`. These are **reported historical findings**:
the referenced co-gas `.runtime` captures are absent locally, so we did not
independently re-audit them. They are not evidence for our policy or replay59.

The head imitates leading players' draft choices. Its reported development
agreement is 78.43% versus 72.55% for a masked-frequency baseline; the same
development set selected the training epoch. It is neither an independent
holdout nor a model trained to predict our controller's XP return. V170/v171
follow-up fixes are separate rejected screens, not part of v169.

## What the current games show

All results below use **2026.9.23.1 / replay59**, including Ranger HP growth29,
Crossbow damage58, Chalice45 and Gale Slash65. Four contexts have 50 games each:
our red/blue lead and late seats. **Relh is our teammate and occupies team seat1
throughout.** “Late” describes our seat, not relh's. Classes, seats and controllers
differ; the table does not establish class-adjusted superiority or a head-to-head
win rate.

| Policy / observed classes | Games | Mean score | Nonzero games | Mean among nonzero |
| --- | ---: | ---: | ---: | ---: |
| Relh169: Arcanist/Lich | 200 | 2,027.89 | 95.0% | 2,134.62 |
| Ours: all four observed classes | 200 | 1,714.83 | 60.5% | 2,834.42 |
| Ours: Crossbowman/Ranger | 100 | 3,311.42 | 98.0% | 3,379.00 |
| Ours: Death Knight/Vanguard | 100 | 118.23 | 23.0% | 514.04 |

Relh has 96 Arcanist games averaging 2,187.27 and 104 Lich games averaging
1,880.77. Our 49 Crossbowman games average 4,041.22, 51 Ranger games 2,610.24,
86 Death Knight games 137.48 and 14 Vanguard games zero. Relh's score>=500
frequency is 90%; ours is 54.5%. Our strongest opportunity is the frequency of
productive games; replacing successful carry behavior has little support here.

Relh averages **15.46 hero kills / 2,319 hero XP** versus ours 10.505 / 1,575.75.
Creep XP is similar: 2,235.19 versus 2,271.86. It buys back 4.625 times per game
versus 2.49, spending 2,305 versus 1,235.50 gold on buybacks. It also dies more:
9.325 versus 7.53. These associations suggest testing productive return from
death, not assuming that extra deaths or unconditional buybacks improve score.

Relh uses only **4.335 consumables per game**, mostly poison, versus our 16.95
(including portals). It has **no portal purchase/use logic**. It is not evidence
for adding healing spam or deleting our safe portals. Its 517.15 rejected orders
per game include 338.66 inventory-full shopping failures. Rejection percentage is
especially misleading because it emits about 19,170 orders per game; our slower
decision schedule has a different denominator. Measure accepted spell/item effects
and score, not just fewer rejected commands.

## Why copying its draft head is insufficient

We applied the exact head to **our actual pre-pick public states**, without
continuing a replay after a hypothetical changed pick. Our existing draft
heuristic separately reproduced all 200 of our actual picks.

| Our actual choice | Relh head in the same state | Games |
| --- | --- | ---: |
| Crossbowman | Crossbowman | 49 |
| Ranger | Ranger | 51 |
| Death Knight | Death Knight | 56 |
| Death Knight | Vanguard | 30 |
| Vanguard | Vanguard | 14 |

All 100 late states offer **only melee heroes**. Available sets are subsets of
Vanguard, Demon Hunter, Death Knight and Berserker; no mage, carry or support is
legal. Relh's 30 changed choices therefore do not fix our lack of a ranged hero.
Our 14 actual Vanguard games all scored zero, which is a warning about our
controller, not a prediction that the 30 hypothetical games would also fail.

## Controller behavior worth understanding

The [seven-layer semantic IR](relh_v169.source.ir.json) preserves ordering,
timing, remembered state, exact draft weights and links to the identical battle
network. It is descriptive and **not an executable semantic surrogate**.

1. Draft explicitly, then end the invocation. Dead heroes immediately buy back
   when affordable, without our reserve or minimum respawn wait.
2. Spend up to four legal skill upgrades, prioritizing R > W > E > Q.
3. Recompute a 25-input, 16-hidden, 18-output battle selector every four living
   invocations. Select a combat mode and a gear mode together.
4. Issue the main target/navigation order, then the Lich's special point cast,
   inventory uses and keep-only purchases.
5. Apply mode corrections, tower-attacker retaliation, eligible nearest-home
   defender behavior, then a final movement order after a newly landed basic.

On the eight full current-engine paths, 87,026 living decisions select the
objective-build mode8 and 49,650 the normal nearest-enemy mode0. No retreat-mode1
or nearest-home defense activation was observed. There are 95 eligible siege
retaliations and 1,566 post-hit movement guards. These are activation counts,
not kills or an attribution of score. Mode8 prioritizes exposed towers/god
within squared distance300, then heroes within700; it does not skip buildings
or explicitly maximize XP-minus-time. Source last-hit target selection is nearest
enemy, not a learned last-hit predictor.

Automatic casting remains enabled. Source branch names do not tell us which
spells landed. Existing host-based resource/economy audits supply accepted
effects; failed casts do not consume mana/charges/cooldown merely by being tried.

## What to use and test

The [transfer hypotheses IR](transfer-hypotheses.ir.json) connects this analysis
to the [manual coaching](../../../coaching/2026-09-23-manual-score/README.md).
These are proposed experiments, not validated policy changes.

| Priority | Transfer | Concrete test / falsifier |
| --- | --- | --- |
| 1 | Improve forced-melee income and hero engagement | Coordinate melee approach, legal spell reach, reachable hero finishes, chase termination and safe creep-XP positioning. Test both late seats/colors while preserving successful carry commands. Reject if mean or productive frequency falls. |
| 2 | Class-specific equipment and return readiness | Our relaxed buyback rule requires dagger+armor+axe+crossbow for every class. Test a melee-appropriate affordable core and its return threshold together. Measure time-to-core, field time after return and XP-minus-time; more buybacks alone do not pass. |
| 3 | Context-aware drafting trained for our controller | Reuse legal masking, team-composition features and timestamp-clean examples. Learn from our own class/controller returns and validate on future rounds; do not treat imitation accuracy as score gain. |

Retain our already validated explicit drafting/upgrades, attack-recovery movement,
portal channel locks, core-aware buybacks and Druid lane recovery. Do not blindly
copy relh's no-portal omission, stale potion affordability checks, broad tower
pursuit or always-buyback rule.

The previous Richard174 [broad transfer](../../richard-v174/source-audit-20260923/transfer-review.json)
and [blue-Druid transfer](../../richard-v174/source-audit-20260923/scoped-transfer-review.json)
failed their respective gates across 800 games. Relh's identical battle bytes
provide no basis for rerunning those unchanged interventions. The first useful
new intervention must discriminate by our class, reach, income and economy.

## Evidence and reproduction

- [Frozen selection plan](plan.json): all 200 existing controls; eight source
  reconstructions selected as the first two lexical episode IDs per context,
  without filtering on relh score/class. 200 distinct replay hashes.
- [Full derived data](evidence/analysis.json): all actor rows, pre-pick observations,
  class/context summaries and source activations. Score is
  `max(0,XP*1440 - 200*ticks)//1440`, including drafting.
- [Input manifest](evidence/input-manifest.json) and [runtime provenance](runtime-provenance.json):
  pinned engine `d6827a4bd3a55a46cf86f88e921f147137709c64`, locked dependencies,
  native instrument/source hashes and frozen local replay locations.
- [Buff context](buff-context.json): the fetched player page mixes replay58/59;
  the hero page is older still. Captured HTML/JSON and visit times are preserved.
  Neither pooled page is used as an exact-patch causal comparison.
- [Instrument correction](evidence/instrument-correction/): initial draft probe
  failed to compile due to a private error type; corrected instrumentation and
  rebuilt. Captured policy bytes were never edited.

Run from the research checkout:

```sh
python3 docs/opponents/relh-v169/source-audit-20260923/verify.py --inputs
```

The [instrument README](../../../../games/gods_of_the_arena/instruments/relh16920260923/README.md)
documents full replay reconstruction. No new hosted games or league writes were
made. Both incumbent policy/IR pairs remain unchanged; their last successful
membership readback remains the separately recorded 17:48 UTC check. This audit's
later leaderboard read succeeds but does not supply missing own-policy labels.
