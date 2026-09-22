---
id: 2026-09-21-week-policy
status: complete
---

# New-week policy: productive lanes and safe objectives

Pinned live game: 2026.9.21.5, upstream f776d5e55d439706a8d49878d17d7ba1f6a1f7ce,
cow_e5445477-d55e-432d-ac38-bd1eae66e6d3. The old research engine and policy
archives remain unchanged. Latest source is in a separate checkout because the
research fork contains divergent human-play changes. No league selection is
part of this experiment.

Hypothesis: a coordinated Bassy-compatible policy can acquire XP and equipment
through lane farming, spend ability points promptly, recover at spawn, and
convert allied creep pressure into tower damage. It should avoid wasting gold
on immediate early buybacks and avoid standing under untanked doubled towers.
Draft and routing must work for either color and any of ten hero classes.
The old inventory signatures and fixed class-to-color assumptions are invalid.

Closed levers reviewed: September 19–20 negative grouping and defense-release
results remain scoped to the previous game. This is a new contract migration;
the bundled behavior is tested together, with no claim of individual causality.

Native admission: actual game VM, both colors, all classes; drafting terminates
with ten unique picks; legal skill spending, stack/shop/channel guards, finite
defense release, and decimal/bitwise semantics. Complete responsive matches
must finish without VM failure, at <=19,000 instructions and <=50,000 work per
decision. Replays must resimulate with every state hash matching.

Initial local comparison: eight seeded games per source against the latest
upstream baseline, four per color. These are debugging and directional evidence,
not a hosted competitive verdict. Keep candidate only if it passes admission
and increases aggregate wins without losing wins on either color; otherwise
record the failure and freeze a distinct refinement before another comparison.

Before any hosted request, the live manifest and two captured league result
records revealed a further contract change: scores are per-hero lifetime XP
minus 200 times elapsed world ticks / 1440, floored at zero. Draft time counts.
The original proposed win-based hosted gate is therefore superseded before
spending or observing a hosted candidate result. Native wins remain diagnostic.

Hosted comparison after runtime admission and budget reconciliation: exact
candidate and incumbent versions, against the same fixed new-week roster,
40 games per arm/color. Pass iff mean per-hero score improves by at least 10%
on each color and 20% overall, all subject VMs finish without error, and every
replay resimulates exactly. Report fort outcomes separately. Subject score must
be computed from platform results and checked against audited XP and duration.
Keep failed opponent VMs explicitly labeled; a clean-opponent comparison is
required for a clean competitive claim. Repeat trajectories are correlated.
A separate mixed-team field evaluation is required for a league promotion claim.
No reinterpretation of old-week wins as new-week evidence.

Adversarial critique: spreading can lose team fights; tower caution can stall;
buyback conservation can expose the god; late convergence can starve XP; the
opponent baseline is only one opponent. Measure full fort outcomes alongside
XP, ability ranks, deaths, actual accepted actions and runtime limits. Any
changed source restarts its prospective evaluation.

Raw evidence: `tmp/gota-week-20260921`. Reproducible instruments:
`games/gods_of_the_arena/instruments/week20260921`.

## Completed uniform comparison

The frozen candidate is `aaron-gota-week0921-lane:v1`, version
`9fc7f72e-0489-48f5-a5d3-c53fca44cff4`, BASIC SHA256
`ad3f1d5ca719491cc3e34a76a0bcdf7434aed45b4fb1a707a65ecdcf65f030f9`.
The exact compatibility control is `c2785cd4-433b-46d1-a454-dd29147383ec`.
Each faced the same upstream baseline version
`6559c395-82f9-4fa4-8f7e-6f3481d9f169` with five identical policies per team.

| Source | Color | Mean per-hero score | Wins | Losses | Draws | Distinct streams |
|---|---|---:|---:|---:|---:|---:|
| Candidate | Red | 553.4651 | 40 | 0 | 0 | 16 |
| Candidate | Blue | 584.7613 | 34 | 0 | 6 | 17 |
| Compatibility control | Red | 26.0933 | 0 | 40 | 0 | 19 |
| Compatibility control | Blue | 90.3153 | 40 | 0 | 0 | 17 |

All 160 games completed with ten valid VMs and exact replay/score audits.
The prospective score gate passed. Blue fort-win frequency regressed despite
the score improvement; wins and league score are distinct outcomes here.
Repeated action streams limit independence. Native diagnostics separately
passed eight candidate wins, 126 actual-host checks and six compiler tests.
All 400 candidate hero-games ended with learned ability ranks. Candidate
terminal mean XP/level were 2,718.5/8.10 on red and 3,246.7/8.74 on blue;
the control reached 1,740.9/6.39 and 1,025.2/4.85. Blue candidate deaths
averaged 6.99 versus 3.20 for the control, so the bundle has a survival cost
despite its score gain. Match duration and drafted classes differ; these
diagnostics do not isolate a causal effect of any individual component.

## Prospective mixed-team holdout

Before its first request, `field-plan.json` froze 160 additional games: one
subject hero in slot 2 on red or slot 7 on blue, with nine distinct current
players filling the other slots. This tests the third pick on each team.
Richard v152, Jordan v304, relh v161, Andre von Auto/khors v33, both daveey
players, Scott Smith, BeWellBot and Andrew Brower are exact UUIDs in the plan.
Candidate and incumbent use the identical other nine versions per color.

The gate requires no subject VM failures, all replay/score audits passing,
at least 30 games with all ten VMs valid per cell, candidate clean mean score
at least the control on each color and at least 1.20 times the control overall.
Tainted games are retained and reported separately. Passing two fixed rosters
would support this bounded mixed-team claim, not universal leaderboard rank.
The complete 320-game study shares the campaign ledger and stays within its
400-game cycle and 1,600-game UTC-day limits. No league selection is performed.

## Completed mixed-team holdout and decision

All 160 holdout games were harvested and replay/score audited. Every subject
VM was valid, including all 80 candidate games, but every game contained at
least one other failed VM. BeWellBot v12 and Andrew Brower/red-kite v34
reported `BASIC VM disabled`; exact counts, versions and examples are in
`field-errors.json`. There are zero clean games in each cell, below the
prospective minimum of 30. The mixed-team gate is **unqualified**, and the
performance hypothesis remains unresolved.

| Source | Color | Mean score, all tainted games | Subject errors | Clean games |
|---|---|---:|---:|---:|
| Candidate | Red | 389.6118 | 0 | 0 |
| Candidate | Blue | 930.8632 | 0 | 0 |
| Compatibility control | Red | 0.0000 | 0 | 0 |
| Compatibility control | Blue | 173.7701 | 0 | 0 |

Retain the new-week candidate as a runtime-admitted policy with a supported
uniform score improvement. Save the exact tested BASIC with semantic evidence
annotations, preserving its source hash. No champion or formal accepted-state
change was made. The next competitive study should first verify clean rosters,
then freeze a new mixed-team comparison; it must not relabel this failed
cleanliness gate as confirmation. No component-specific causal claim is made.

Saved bundle: `examples/gods_of_the_arena/players/ir/forks/week20260921`.
Final live readback still resolved game 2026.9.21.5 and the original Aaron/Coach
compatibility champions. All 320 requested games are terminal and audited.
