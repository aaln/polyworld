# Current Gods of the Arena policy work

Read `games/gods_of_the_arena/current.json`. The active engine is
**2026.9.23.1 / d6827a4bd3a55a46cf86f88e921f147137709c64**, published coworld
`cow_32f7afc6-78f6-49d5-990b-5b3c3619662c`. Verify the live league's source,
version and configuration before new hosted work. The research branch preserves
older engine files and studies; build the exact pinned engine through
`games/gods_of_the_arena/instruments/productive20260923/bootstrap59.py`.

The September 23 balance release uses replay game version **59**, game format **6**
and outer file version **2**. Ranger HP growth is now **29**, Crossbowman base
attack damage **58**, Gale Slash damage **65**, and Sanguine Chalice healing **45**.
The score formula, BASIC host and simulation controller code remain unchanged;
content stats and the replay envelope changed. Existing source29f6d7e6 champions
remain live; all competitive qualifications below belong to their recorded old
release until a fresh replay59 comparison passes. Andre's coached high-score episode uses khors v179; the subsequent trial
freezes v180 after an upgrade before submission.

The [khors179 audit](../opponents/khors-v179/score-audit-20260923/README.md)
explains the coached7,781game with full replay/XP reconciliation and a separate
seven-layer descriptive IR. It identifies recurring hero/creep XP,48%own building
attack commands, and lost farming sources after barracks destruction. Buildings
still award100XP and the enemy god500team XP. Twelve other recent games prevent
treating the selected high score as typical; other-player VM failures are explicit.

The [unit-farming trial](../../games/gods_of_the_arena/experiments/2026-09-23-unit-farming.md)
tests excluding buildings from deliberate target selection, retaining safety and
navigation observations. Source1238ec73 passed662candidate checks and16native games;
400fresh games compare it with incumbent29f6d7e6 againstkhors180/Richard195/Jordan411,
on both colors and draft contexts. All400games passed audits, but score fell27.58%
(95%interval−38.30%to−16.07%) and productive frequency fell54.5%to38%.
[The reviewed pair](../../examples/gods_of_the_arena/players/ir/forks/unit-farming20260923-hosted/README.md)
is rejected; source29f6d7e6 remains live. The user then requested selective short
finishes. Source08987348 passed802checks/16native games and completed a
[separate400-game comparison](../../games/gods_of_the_arena/experiments/2026-09-23-selective-finish.md)
with fresh controls. It permits nearby two-hit towers/god and one-hit barracks,
without long deliberate sieges. Mean score fell1.82% (95%interval−16.53%to+14.35%);
productive frequency fell53%to44.5%, despite a higher conditional productive mean.
It failed the frozen joint rule and was not deployed. The separately
prepared [outbound portal candidate](../../games/gods_of_the_arena/experiments/2026-09-23-productive-return.md)
is preserved and deferred before hosted spending, not combined with this test.

The [manual coaching IR](../coaching/2026-09-23-manual-score/README.md) preserves
five user screenshots and audits all200existing replay59 controls for resource,
spell and kill productivity. Andre's higher spending includes more buyback gold;
consumables include portals. Automatic casting is enabled, so rejected manual
casts alone do not prove lost spell effects. Half our cohort is melee, while
Andre always drafts Ranger/Crossbowman; our14Vanguard games all scorezero and
86DeathKnight games average137.48. Class/role context is required before choosing
an intervention. Proposed skills and their validation gates are non-executable
research IR, not a qualified policy replacement. Both live champions remain29f6d7e6.

The live game changed during individual-score research: replay version58 adds
**500XP to every teammate when the enemy god is destroyed**, including dead
and distant teammates, awarded once. Timeouts grant no god reward. The score
formula is unchanged. All completed portal/balance hosted numbers below are
from2026.9.22.2 and do not qualify a replacement under this patch. The deployed
source remains the byte-exact reference; fresh controls are required. Preserve
the old replay57 engine and datasets.

## Latest deployed reference: Druid lane recovery

Source **29f6d7e6**, reviewed IR **d331ba09**, binding
`gota-bassy/druid-lane-recovery-2026-09-23-r1` is verified on both players.
[Pair and evidence](../../examples/gods_of_the_arena/players/ir/forks/druid-lane20260923-hosted/README.md)
record400fresh natural later-draft games:+44.17%pooled score,red+49.24%,blue+43.42%,
95%gainCI[+9.73,+92.18]. All audits and preset gates pass. Other hero commands
are unchanged with local complete-match equivalence. Fixed later-draft scope,
not a universal score gain or rank claim. Shopping and unsafe escape remain.
[Deployment receipts](../../examples/gods_of_the_arena/players/ir/forks/druid-lane20260923-deployment/README.md)
preserve blue-center rollback. Opaque names requested; the API has no privacy flag.

The all-class lane recovery attempt remains rejected:320games,−5.26%aggregate,
bluelead−12.15%. The later Druid-only source used its own frozen400fresh-game
comparison. Do not reinterpret the earlier rejection as passing.

The user permanently authorized **100,000 hosted episodes per UTC day** on
September23. The shared config no longer has an expiring daily override.
[Authorization](../../games/gods_of_the_arena/budget-authorizations/2026-09-23-permanent-100000.json)
preserves the request and previous allowance. Shared journals,400-game experiment
cycles, at most3active requests and current API batch ceilings remain in force.

## Completed analysis: khors v114 and low-score situations

The [seven-layer opponent IR and report](../opponents/khors-v114/score-audit-20260923/README.md)
cover 72 recent league games, with full replay hashes and XP/score reconciliation.
Khors source was unavailable; this is a descriptive model, not an executable proxy.
Other players failed in 63 games; all own and khors VMs were clean. Nine fully clean
games are reported separately, alongside 200 reused clean historical controls.

Ours scored zero in 14/75 appearances, including nine of 13 melee appearances;
Crossbowman/Ranger had none in 27. Khors also had eight zeroes in 39, but its nonzero
mean was 2,842.68 versus 2,068.67 for ours. Four authentic own-source reconstructions
match 5,826 submitted commands, exposing both repeated deaths and healthy,
unproductive advances. The counter IR prioritizes safer weak melee play, public
progress recovery, farming opportunity cost, outbound portals and legal cast reach.
These are proposed changes, not demonstrated improvements; preserve effective
ranged behavior and all earlier failed experiments.

The objective is `floor(max(0, XP - 200 * elapsed minutes))`, including draft.
At seven minutes, 1,400 XP scores zero. An added minute needs more than 200 extra XP
to raise the unclamped margin, and any existing deficit must be recovered first.
Raw XP is unavailable to BASIC; proposed live recovery must use public proxies.
No hosted games or policy changes were made for this analysis. Current champions
and the game budget remain unchanged.

## Completed research: Richard v174 source transfer

The [source-informed opponent IR](../opponents/richard-v174/source-audit-20260923/README.md)
reconstructs82,818commands and every replay hash across four Warlock games.
It preserves the neural selector and later overrides, without claiming an
executable semantic surrogate. The [coordinated guarded siege experiment](../../games/gods_of_the_arena/experiments/2026-09-23-richard174-transfer.md)
tests covered tower pressure together with retaliation against a reachable
attacker. Source **f7873bb2** passed662local checks and16native matches but failed its400-game
hosted rule:+7.58%aggregate,95%interval[−8.65,+27.05],redlate−53.15%.
The [blue-Druid-only source](../../examples/gods_of_the_arena/players/ir/forks/blue-druid-siege20260923-hosted/README.md)
completed its own400fresh games: −0.08% own score,95% interval[−17.43,+21.10].
It outscored Richard119/200 versus86/200 baseline, but worsened the mean khors gap
by718.49points. Both studies are unqualified; the scoped fork is saved for
Richard-focused research. The qualified Druid reference remains deployed to both
players. All800games passed audits, and no new jobs or league writes are pending.

## Prior deployed reference: blue central route

Source **c02f8cb6**, reviewed IR **88860443**, binding
`gota-bassy/blue-center-2026-09-23-r2` was deployed to both players before Druid lane recovery.
[Portable pair and evidence](../../examples/gods_of_the_arena/players/ir/forks/blue-center20260923-hosted/README.md)
record400fresh games: aggregate+15.68%,blue+40.74%,red−3.07%; all preset gates
and ten-source/VM/full-replay/XP audits pass. Blue mean gap versuskhors114 is
+1266.72,95%CI[648.84,1881.67],58/100outscored. Fixed first-team-seat roster;
no late-draft or lasting #1claim. Red executable behavior is unchanged.
Both champions were verified active/competing; current.json holds exact UUIDs.
[Deployment receipts](../../examples/gods_of_the_arena/players/ir/forks/blue-center20260923-deployment/README.md)
preserve core-buyback67fdcd5d as rollback.

## Completed coaching study: retain blue-center

The [field-sustain IR/policy pair](../../examples/gods_of_the_arena/players/ir/forks/field-sustain20260923-hosted/README.md)
completed 240 fresh games against blue-center after 558 local checks and 12
complete native games. All audits pass, but mean score falls 10.73% and every
context misses the 95% preservation floor. It is saved for research and is
**not deployed**. Both champions retained blue-center `c02f8cb6` at that decision;
the later Druid-only study above subsequently replaced it.

The [verified coaching replay](../coaching/2026-09-23-field-sustain/README.md)
confirms that automatic healing already worked: a recovered Druid continued its
base route for about 45 seconds. The tested bundle improves route interruption
and field healing, without a qualified score gain. Preserve this negative result
and all captured inputs. A narrower intervention needs a separately frozen test;
do not repeat the same bundle or select a favorable post-hoc class slice.

## Prior deployed reference: core buyback


Source **67fdcd5d**, reviewed IR **c1a5839b**, binding
`gota-bassy/core-buyback-2026-09-23-r1` was deployed to both players before blue-center.
The [portable pair and report](../../examples/gods_of_the_arena/players/ir/forks/core-buyback20260923/README.md)
passed400fresh held-out games on the active2026.9.22.3 engine: mean score
**2270.46→2955.775(+30.18%)**, red+22.97%,blue+39.79%,95%gain interval
**[+16.10%,+46.54%]**. All ten source/VM, replay hashes, XP and integer-score
checks pass; the field stayed stable. There are100games/source/color, with
one duplicate stream in control red and candidate blue. Fixed first-team
seat and roster; no late-draft or permanent#1claim.

After completing four core items, the policy buys back with>5seconds remaining
and price+100gold; without complete core it retains>25seconds/price+200.
Respawn grows with death count, not level. All390host fixtures and8native
matches pass; only the lifecycle executable body changes. The score increase
comes with more hero/creep XP and more deaths; it is not a survival claim.
Richard174 is outscored160/200,Jordan411166/200,khors114100/200.
Andre's blue mean still leads by161.49; both-color superiority remains unmet.

Aaron `30a0e469-8c2f-450c-b3bc-4a687a6c74e3` and Coach
`2013aad3-a754-4e31-8cea-727aa6c3a6b1` were verified active competing champions
at2026-09-23T01:35:32Z. [Deployment and rollback receipts](../../examples/gods_of_the_arena/players/ir/forks/core-buyback20260923-deployment/README.md)
preserve old portal versions and exact source identity. New league-round
performance remains unmeasured. Re-resolve opponents before new experiments;
prior studies below retain their original decisions and engine scope.

## Current contract

- BASIC supports decimals and fractional action coordinates. Public position
  observations are global integer cells with complementary team border rules.
  Mirrored movement, navigation, vision, targeting and seeded last-hit ties are
  implemented in the host. Both bundled reference policies use team coordinates;
  that is a controller design, not a restriction on legal global-coordinate bots.
- One shared object/warning frame is frozen for the decision phase. Accepted own
  inventory and ability operations update immediately. Movement plans use the
  same starting state, then move together; collected damage resolves before
  deaths and rewards. Mutual kills and simultaneous fort draws are legal.
- Faction draft bonuses are gone. Ranger HP growth is **29**, Crossbowman base
  damage **58**, and Warlock Dread Totem damage **87**. Read actual stats, ability
  ranks, costs and ranges from the host; do not import an old hero stat table.
- Explicit draft picks and skill-point spending remain required. Keep the public
  availability fallback and ten-second pick deadline. Abilities start locked.
- Shopping requires the friendly keep. Inventory has six slots; consumables
  stack. There is no sell/equipment-upgrade operation. Portals channel for three
  seconds with a 60-second cooldown. Spawn recovery is fast; buyback exists.
- Towers retain updated HP/damage; barracks waves have three melee and one caster.
  Creep XP requires same-floor proximity within six tiles. An eligible last
  hitter receives the 15% reserve; the remainder is shared. Crossbowman attacks
  reach beyond this XP radius, so its practiced farming step remains relevant.
- Fresh actual-engine practice still finds a full movement tick after a landed
  hit shortens Ranger recovery to nine ticks. Same-decision walk+attack is not
  equivalent. This mechanic does not establish a hero's competitive strength.
- Primary league score is integer
  `max(0, lifetime_xp * 1440 - 200 * world_ticks) // 1440`, including draft time.
  Fort outcomes are separate diagnostics. Standings average scores, not win Elo.

## Current IR and completed evidence

The `balance20260922` bundle preserves the complete 400-game screen and all five
IR/BASIC pairs. Every cell has 40 clean games, exact source/VM/replay/XP/integer
score checks and 40 distinct command streams. All four coordinated mirrored
alternatives failed the prospective replacement gate. Geometric symmetry alone
was not retained as a gameplay improvement; blue score regressed.

The previous reference is **`balance-draft20260922`**, source **7631fa32**, binding
`gota-bassy/balance-draft-2026-09-22-r1`. It changes only draft priority to
Crossbowman and retains the deployed post-draft controller. If Crossbowman is
unavailable, it uses the existing public ranged-first fallback. A separate
80-game follow-up scored **2888.975 red / 3273.5 blue**, versus the reused exact
current-engine control's **2337.4 / 2701.975**: **+22.3%** overall, passing both
frozen conditions. All 480 games were valid and fully audited.

This is a fixed first-pick-roster result, not independent confirmation or a
universal hero ranking. The follow-up reuses earlier controls explicitly.
It outscored opposing relh on both colors and Jordan411/Richard153 on red;
Jordan and Richard were teammates in the blue roster, so no opposing blue claim
follows. Check newer opponent versions separately. The source-preserving
current-engine control remains in `balance20260922/control` as rollback.

Do not force team-relative movement merely because it passes mirrored-action
tests, and do not treat the retained global-coordinate behavior as permanently
required. A future controller can change either approach with current evidence.

Use IR as the editing medium. Change current host bindings and policy components
as needed; old tactical rules, opponent v135 identities, old integer-only
compilers and old win gates do not constrain new research. Preserve historical
studies under their original engine and decision rules. Never relabel an old
outcome as a new-engine result, or feed hidden replay truth/policy UUIDs into the
live controller. Failed alternatives remain available with their evidence.

## Evaluation and operations

Freeze exact executable bytes, IR, engine/configuration, opponent UUIDs, seats
and prospective decisions. Use mixed teams and one subject seat for claims about
this league. Compare matched side/roster controls. Default advancement requires
zero invalid games/audit failures, strict aggregate score improvement of at
least 10%, and each cell retaining at least 95% of control. Rival score
superiority, late-draft strength and #1 rank are separate claims. A reused
control cohort must be labeled explicitly; it is not fresh concurrent evidence.

Shared journal limits are 400 new games/cycle, 100,000/UTC day, at most three
active requests, 40–100 games/request under the captured current API. Do not reset a ledger or change limits to
make an experiment pass. Runtime, ownership and evidence safeguards remain even
when historical tactical IR is obsolete. Read the campaign FOCUS/ownership
record before taking the writer; the prior worker is paused during interactive
work. The user's root checkout moved to upstream main and the old LaunchAgent
script path is absent: do not blindly restart an obsolete or missing runner.

Historical portal registrations were Aaron `b65ccf7b-d7a1-4681-b57f-a55f5ace43c7`
and Coach `088c0fed-b536-4777-9f7a-14abee21e5b8`, both **db71abb3**.
Both portal registrations were verified competing, active and champion through normal
`auto_champion=always` placement. The [deployment receipts](../../examples/gods_of_the_arena/players/ir/forks/portal-coaching20260922-deployment/README.md)
preserve source hashes, readback and rollback identities. Placement does not
establish later league-round performance. Resolve live versions before new work.
Manual champion selection previously returned HTTP500; normal placement worked.
Do not retire a live champion before its replacement is verified.

## Preserved portal coaching parent

The [portal coaching experiment](../../games/gods_of_the_arena/experiments/2026-09-22-portal-coaching.md)
and [validated portable pair](../../examples/gods_of_the_arena/players/ir/forks/portal-coaching20260922-hosted/README.md)
add safe field recall, a complete channel lock, scroll reserves and keep-local
walking recovery. All 84 portal fixtures, 126 broader host checks and eight
full native matches pass mechanism/runtime checks; native scores are mixed.
The local snapshot and hosted-reviewed pair remain preserved as the parent and rollback for core buyback.

Before any request was created, the user authorized 160 additional September 22
games and named khors:v114 as a target. The revised A/B uses exact v114 in the
opposing first-pick seat on both colors, with whole teams rotated together.
Jordan411 and Richard153 also oppose both colors. relh161 is a teammate, so this
comparison cannot establish opposing relh superiority. The original unlaunched
plan remains preserved. Primary score advancement and khors superiority are
separate prospective tests; a fixed roster does not establish #1 league rank.

All160 fresh-control games passed full audits. Source **db71abb3**, binding
`gota-bassy/portals-2026-09-22-r3`, passes the prospective score gate: mean
2472.84→2758.59 (+11.56%), red+27.46%, blue+0.60%. The95% bootstrap aggregate
interval is[-7.75%,34.75%], so generalization remains uncertain. Candidate blue
contains39 distinct command streams in40games; keep duplicate evidence visible.

It outscores khors:v114 in21/40red and24/40blue, with positive mean gaps on both.
Both difference intervals includezero, so confident khors superiority is still
unqualified. Jordan411 is outscored73/80 and Richard15376/80 in this fixed
roster. Fort outcomes are separate; candidate team wins27/80.

Keep-origin home-directed portal starts fall107→1 in80games per source. The
remaining event is a full-health21.4-tile hop to a near-home tower; preserve the
classification and test destination utility separately. Candidate low-health
field ticks increase, so the evidence does not show less overall low-health
exposure. Safe recall timing and scoreboard gains are distinct measurements.

The [player-statistics report](../reports/gota-player-stats-20260922/README.md)
and its non-executable `optimization.ir.json` prioritize productive target
selection, marginal XP above the200/minute time cost, spell reach/effectiveness
and useful gold conversion. These are research hypotheses, not new accepted
controller rules. The [khors descriptive IR](../opponents/khors-v114/replay-audit-20260922/README.md)
is retrospective and not a validated proxy. Old source/engine tactics remain
historical; none overrides current-version evidence.

## Completed individual-score comparison

The [hosted score pair](../../examples/gods_of_the_arena/players/ir/forks/score-opportunities20260922-hosted/README.md)
records **rejection** of source f6a0dace, reviewed IR e3786265. All 160 fresh
hosted games passed source, all-VM, full-replay, XP and integer-score audits;
each 40-game cell has 40 distinct command streams. Mean score fell
2473.025 → 2234.45 (**−9.65%**), red +10.23%, blue −22.64%. The 95% bootstrap
gain interval is [−25.65%, +9.74%]. The frozen +10% aggregate / 95% each-color
rule failed. **Both players retained the portal reference at that decision.**

This coordinated candidate separates hero/creep/structure opportunities,
checks public threat context, favors reachable hero finishes and values a
near-dead exposed god's 500 XP reward. Its 390 host fixtures and eight complete
native games pass, but their positive native score did not predict competitive
improvement. The original local pair and failed alternatives are preserved.

Red gained creep XP while hero XP declined slightly. Blue hero XP fell
2242.5 → 1695; shorter games saved about 155 score points but lost about 832 XP.
Blue underperformed within both Ranger and Crossbowman groups despite more
Crossbowman picks. This is descriptive, not per-component causal attribution.
Do not rerun the exact failed bundle unchanged. Useful next hypotheses concern
missed hero opportunities and realized spell damage, measured against productive
creep income and survival on both colors.

Khors114, Jordan411 and Richard167 opposed both colors; relh161 was a teammate.
The candidate outscored them 33/80, 67/80 and 53/80 respectively. These counts
neither pass the primary replacement rule nor establish #1 or general strength.

The user authorized **10,000 hosted games for September 22 UTC**, superseding
the earlier 1,760 cap. After this comparison the preserved shared journal has
1,920 reserved, leaving 8,080. The dated override retains the normal 1,600 limit
for later dates; cycle 400, parallel 3 and batch 40–200 limits remain. Do not
reset the journal. The prior background researcher remains paused and its old
game configuration must not be resumed unchanged. All four requests completed.
