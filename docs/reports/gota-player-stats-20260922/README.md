# Player statistics: where to improve

Source: [Gods of the Arena player statistics](https://metta-ai.github.io/polyworld-buff/GOTA/players/).
Captured snapshot generated **2026-09-22T19:58:52.371756+00:00**, covering **360 replays**
between **2026-09-22T11:49:51.687951+00:00** and **2026-09-22T19:49:51.687951+00:00**.
Use exact policy versions. Aaron/Coach's deployed source and khors:v114/Jordan411
below all use replay engine57 (current patched game). Richard153 and relh161
combine engines51/56/57 in this snapshot; their rows in the CSV are descriptive
history and are not a clean current-patch comparison.

| Metric | Aaron (70) | Coach (71) | khors:v114 (13) | Jordan:v411 (97) |
|---|---:|---:|---:|---:|
| Recorded score | 1,510.0 | 1,315.2 | 1,978.9 | 649.7 |
| Game minutes | 11.5 | 11.1 | 13.2 | 13.1 |
| Lifetime XP | 3,728.9 | 3,339.6 | 4,513.1 | 3,008.2 |
| XP at creep last hits | 1,656.3 | 1,531.0 | 2,110.8 | 1,954.8 |
| XP from nearby creep deaths | 187.6 | 189.6 | 179.2 | 522.9 |
| Hero-kill XP | 1,433.6 | 1,240.1 | 2,215.4 | 490.2 |
| Building XP | 451.4 | 378.9 | 7.7 | 40.2 |
| Hero kills | 9.6 | 8.3 | 14.8 | 3.3 |
| Deaths | 3.9 | 3.5 | 7.1 | 3.2 |
| Final level | 9.4 | 8.8 | 10.1 | 8.3 |
| Building-target order share | 36.5% | 35.1% | 0.0% | 8.3% |
| Hero-target order share | 16.7% | 16.9% | 31.0% | 12.3% |
| Unspent end gold | 1,501.4 | 1,308.9 | 1,391.2 | 760.4 |
| Scrolls purchased | 5.8 | 5.2 | 7.3 | 5.8 |
| Buybacks | 0.6 | 0.4 | 1.4 | 1.8 |
| Accepted casts/min alive | 2.1 | 2.2 | 2.0 | 1.7 |
| Out-of-range rejections | 591.4 | 523.5 | 6.0 | 5.3 |
| Rejected order share | 34.1% | 33.8% | 1.8% | 1.2% |
| Alive time near own god | 20.6% | 21.4% | 23.9% | 16.4% |

## Primary opportunity: productive targets

Our current controller allocates about36% of accepted attack-target orders to
buildings; khors:v114 allocates essentially none. Its higher score accompanies
more hero-kill and creep XP, despite more deaths and fewer team wins. The
comparison suggests testing lower structure priority when a productive creep
wave or safe hero fight is available. Preserve emergency defense and structures
that open useful access. Barracks destruction can remove future enemy creep
income, so objective timing belongs in this test too. Order share is a proxy for
attention, not time or damage, and does not prove that structure targeting caused
the score difference.

## Longer games: evaluate marginal XP, not duration alone

Current score is `max(0, floor(lifetime XP - 200 * world minutes))`, including
draft. Each extra minute must earn more than200 XP to raise unclamped score.
For example, another minute earning400 XP adds about200 points; one earning100
XP loses about100 points before clamping. Zero-XP waiting costs200 per minute.

Khors averages **1.69 more minutes** and **784.2 more XP**
than Aaron. Extra time costs **337.7 points**, leaving an
unclamped difference of **446.5**. The recorded gap
is **468.9**; per-game clamping/rounding explains the residual.
Pooled XP per recorded minute is **323.9 for Aaron**,
**302.1 for Coach**, and **341.9 for khors**.
These are ratios of totals, not average per-game rates or estimates of future
marginal income. Longer games may result from stronger farming or weaker
objectives; this snapshot cannot separate cause and consequence.

## Direct-control cleanup

Aaron records about591 out-of-range rejections per game, versus6 for khors.
In pinned `sim.nim`, the explicit `ActionOutOfRange` return is object-targeted
spell range validation. Our generated `R_combat` tries damaging spells against
the chosen target without a range guard. `attackTarget` itself does not return
that range error. Prioritize effective spell usage and positioning, rather than
assuming these are missed basic attacks. Suppressing failed attempts alone can
improve the dashboard without improving score; measure landed effects and XP.
Current BASIC lacks an ability-range query, so a future guard needs a
current-engine, class/rank-aware binding or conservative public geometry test.

The portal A/B already tests field recall, reserves and the final channel-tick
lock. The new stats do not change the executable being evaluated. Track avoided
home-to-home channels, failed channels, recovery duration and XP after return.

## Indirect economy and survival

Aaron ends with about1501 unspent gold; Coach1309 and khors1391. Spending more is
not automatically useful: six inventory slots and no sell/upgrade operation
limit conversion. Test stacked useful consumables and buyback only when their
expected productive time exceeds the purchase/return cost. Extra shopping trips
can erase the benefit. Our lower deaths and high average HP are strengths, but
could also coexist with missed profitable fights; target net XP, not minimum
deaths or maximum HP. Jordan illustrates the limit: very low rejections and
high survival accompany much less hero-kill XP and lower score.

## Scope and proposed tests

The13 khors:v114 games come from one round; Aaron70 and Coach71 span a longer
window. Draft, side, teammates and failed VMs differ. Website statistics exclude
replay hash failures but do not certify all participants' VMs succeeded. This
is hypothesis generation, not causal or independent competitive validation.

`optimization.ir.json` records seven research layers and the proposed priorities.
It is deliberately non-executable; current accepted IR stays unchanged until
combined changes are practiced and compared against frozen fresh controls.
`all-players-latest.csv` retains every observed player's latest-version values,
including explicit engine coverage. Original downloaded files are byte-preserved.
Definitions and limitations follow the [site's extractor guide](https://github.com/Metta-AI/polyworld-buff/blob/main/tools/PLAYERS.md).
