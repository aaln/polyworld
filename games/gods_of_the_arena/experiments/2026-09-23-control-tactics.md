# Reviewed control-tactics policy / engine61

Candidate `morrow-ibis-61c2:v1` is uploaded inertly. Both league champions remain
the incumbent source29f6d7e6; this directional pilot does not qualify deployment.

The coordinated fork targets hero control before retreat stops, avoids long
overlap, reserves mana for imminent healing and retains legal basic/item channels
under silence or root. Managed control casts are arbitrated separately from the
generic spell loop. The level2E guard has no demonstrated benefit in standard
level2 fixtures. Control can cost damage, mana and XP; it is not automatically safe
for score.

## Evidence

120paired real-tick fixtures /240executions pass (max5986instructions/9410work).
Warlock silence prevents a scripted enemy spell and saves42HP, both colors.
Vanguard stun saves38HP in the retreat-attacker drill. Sixteen complete native
games contain eight matched comparisons: twoWarlock score deltas+502/+949 and
six unchanged. These are mechanism/reference-opponent evidence only.

Hosted:80fresh baseline games and80responsive counterfactual games, four frozen
side/seat contexts,20pairs each. Every game has ten valid VMs, all replay hashes,
all XP and integer scores checked. Pair seed/config/manifest, own source and all
nine other sources agree. Unique full command streams:
baseline80/80, candidate80/80.

Mean score **2429.51 → 2493.62**;
paired mean delta **+64.11**,95%interval
**[+2.06, +135.04]**.
Higher/equal/lower individual score:13/56/11.
These counts are score comparisons, not match victories.
Frozen pilot advancement:True. No established verdict-size
floor; no deployment from this pilot. Natural subjects are Ranger/Crossbowman/
Druid; Warlock, Vanguard and Lich hosted effects remain unmeasured.

`evidence/statistics.json` includes exact score decomposition, paired uncertainty,
hero/side/seat summaries, control impacts, disjoint time/XP states and victim-to-
recipient XP graphs. Extra telemetry requested during the run is exploratory,
not a changed gate. The user's subsequent score-only objective governs future
studies and is preserved in `evidence/score-objective-steering.json`.

Raw tapes, original inputs and upload receipts remain in
`polyworld/tmp/gota-control-tactics61-20260923`; hashes and all160episode IDs are
in `evidence/artifact-index.json`. Original IR is preserved in that capture.
Reviewed IR annotations regenerate **byte-identical** tested BASIC.
Run `python verify.py`, or `convert.py compile --out <new-dir>` and
`convert.py extract --source policy.bas --out <new-dir>`.

Portable pair: `examples/gods_of_the_arena/players/ir/forks/controltactics20260923-hosted/control-tactics`.

## What the score aggregation shows

| Subject hero | Paired games | Baseline mean | Control-policy mean | Mean difference |
| --- | ---: | ---: | ---: | ---: |
| Ranger |18|3262.06|3262.06|0|
| Crossbowman |22|3569.68|3569.68|0|
| Druid |40|1427.78|1556.00|+128.23|

These are the complete natural classes in the frozen cohort. The Druid slice
explains the aggregate improvement; it is a descriptive slice, not a newly
selected candidate. Red mean delta is+75.73 and blue+52.50; their individual
95%intervals cross zero. Overall mean improves2.64%, with a narrow positive
lower paired bound of+2.06points. This passes the pilot's advancement rule,
not deployment qualification or a guarantee against lower scores.

Exact overall score accounting, per game:

| Component | Score difference |
| --- | ---: |
| Extra XP |+115.1375|
| Additional elapsed time |−29.7014|
| Zero-floor effect |−21.3361|
| Integer rounding |+0.0125|
| Total |+64.1125|

Druid hero-control impacts rise1.75→2.625 per game. Its hero XP rises963.75→1072.50,
creep XP3123.85→3205.38 and structure/other XP437.50→477.50. XP per elapsed minute
rises280.52→289.47; fewer dead seconds accompany the gain. These outcomes support
the coordinated candidate within this fixed cohort, not separate causal effects
for each cast/guard. Warlock silence still has fixture/native evidence only.

The finite-state accounting also shows about225 baseline Druid living seconds
per game beyond a30-second XP drought. This is a diagnostic flag, including
post-death recovery; it does not prove every such second is avoidable. In the
candidate it rises to233seconds despite higher score, illustrating why downtime
or death counts must not replace the actual XP-minus-time objective.

## Separate XP-harvesting prototype

User steering during this run asked for XP harvesting at all costs and discrete
math. The separate `harvest-value` fork ranks visible target rewards per integer
hit/travel-work estimate and retains reward-bearing structures. Eight matched
local pairs yield19367→19376 total score, with three increases/five decreases;
red+5750 and blue−5741 nearly cancel. It is prepared and saved, not uploaded or
qualified. Refine the opportunity proxy with actual reach/finish evidence and
fresh paired tests; do not promote it because selected red games look strong.

New research optimizes expected individual score only. The old pilot's frozen
rule remains unchanged; team wins have no role in either analysis. See
[the method](../../../docs/guides/guide-gota-score-analysis.md) and the
[prepared harvesting pair](../../../examples/gods_of_the_arena/players/ir/forks/harvest-value20260923-local/harvest-value/README.md).
