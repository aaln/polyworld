---
id: 2026-09-21-targets-microplay
policy: week20260921
baseline: ad3f1d5ca719491cc3e34a76a0bcdf7434aed45b4fb1a707a65ecdcf65f030f9
candidate: b82c379953831b719776ba4faf3ab21a5ac2d1d383ed7f93c5f70df26fc81098
status: complete
hypothesis: Better attack timing, XP position, equipment spending and purposeful portals can improve growth and wins against the current three targets.
decision_rule: Freeze each executable before hosted tests; require valid VMs and exact audits, and report fort-win and league-score gates separately on both colors.
evals: []
---

# Hypothesis

User explicitly requests practicing last hitting, XP optimization, equipment
and town portals for defense and growth. Treat these as a coordinated bundle;
do not attribute a full-game improvement to a single component without an
isolating practice test. The new-week baseline already has an exact seven-layer
IR; extend it through versioned skills and preserve its tested source.

Current exact targets: relh v161 `6b72f83b-6623-458c-add3-85ec0ef6e38b`,
Jordan v306 `c51035c0-65f4-48cc-b8a7-23b743797110`, Richard v153
`d774f970-7699-4478-acb3-3fb99a6627cb`. Game 2026.9.21.5, engine
`f776d5e55d439706a8d49878d17d7ba1f6a1f7ce`. Previous v135/268 grouping
failures in closed_levers.md do not establish new-release mechanisms.

# Design and critique

First inspect existing target VM exits, then freeze a 240-game baseline panel:
40 games per target/color, five identical policies on each team, exact UUIDs.
The baseline is lane:v1 `9fc7f72e-0489-48f5-a5d3-c53fca44cff4`, not the
live compatibility champion. Inspect all ten VMs and resimulate every replay.
Measure mean per-hero league score for both teams and fort outcomes separately.
Track repeated complete command streams; generated seeds are not independent
trials. Uniform teams establish this matchup only, not mixed-team rank.

Practice in the actual engine: measure accepted attacks and last-hit gold,
shared XP inside/outside range, useful inventory purchases, portal destination,
successful channel completion, and defense release. Local practice establishes
mechanics and directional changes, not competitive success. New mechanics may
increase exposure, starve teammates, waste portal cooldowns or spend too much
on travel; include boundary/negative fixtures and complete responsive games.
Never feed retrospective hidden replay truth to the executable policy.

# Predictions and decision rule

Baseline matchup gates, fixed before results: zero invalid VMs or replay/score
failures; fort gate at least 30 wins out of 40 on every target/color; score gate
strictly higher mean per-hero score and at least 1.10 times rival mean in every
cell. A source can pass one and fail the other. No #1 or promotion claim follows
from one-seed, local, tainted or merely created results.

If micropractice helps, its native measured effect must activate, runtime must
remain <=19,000 instructions / <=50,000 work per decision, and subsequent
frozen hosted comparisons must improve the failing matchup without relabeling
earlier outcomes. If it does not, keep the baseline and record the failed fork.
Refinement selection and confirmation plans will be frozen before their own
results. Normal shared budget: 400 episodes per research cycle, 1,600 per UTC
day, at most three active requests. The baseline panel uses 240 of this cycle.

# Practiced mechanisms and revision

The first timing fork issued walk and attack in the same decision. Actual-tick
practice falsified its recovery claim: Ranger remained at 20 hits/360 ticks.
The simulator retains the swing if the target is reacquired before physics.
Revision 2 moves for one physics tick, then reacquires. Ranger reaches 39 hits
in 360 ticks (9-tick intervals instead of 18); every class improves in this
stationary drill. The Crossbowman XP guard originally inherited a stale
24-tick navigation throttle. Removing that throttle from the proximity skill
changes the same-floor 6.25-tile kill from 0 to 15 XP on both colors.

The coordinated potion variant buys dagger, armor, axe and crossbow, preserving
potion and portal slots. At 1000 shop gold, Ranger damage rises 47 to 61 with
unchanged 320 HP. A fifth-equipment alternative reaches 71 damage but was less
consistent on the native XP comparison. There is no sell/equipment-upgrade
host action. Both item variants and their frozen sources remain preserved.

Contested creep drills gain 240 instead of 210 gold but earn 285 instead of
300 shared XP per color. This is a real caveat, not a universal XP improvement.
Defensive portal practice completes channels and releases to offense after
threat removal; safe-base controls spend no scroll. Full-game portals can still
be interrupted by newly arriving threats. Scope: fixed stationary targets,
clamped creeps and normalized HP/mana for attack drills, not ranked matches.

The initial practice instrument failed to find an XP boundary among sparse
lane waypoints; it now selects an open same-floor ground segment. The old
scenario assertion requiring walk+attack in the same decision was replaced
with separate movement and later reacquisition checks. Original sources/logs
are retained; these are instrument revisions, not hidden VM failures.

All 126 revised runtime fixtures passed (max 13,428 instructions / 20,377 work).
The final source won four responsive native games against lane:v1 with exact
replays. Those two-seed cases include repeated trajectories. Final source
b82c3799 was uploaded inert as aaron-gota-micro0922:v1 / f3f8baab-d02a-4f7f-8fc9-e1f050f967a7.

# Confirmation design

The baseline discovery cycle closed at 240 games with both qualification gates
failed. The new one-physics-tick recovery / pre-throttle XP hypothesis then
started a separate frozen 240-game cycle, `interactive-microplay-r2-20260922`,
using the same shared journal and normal limits. No allowance or ledger reset.
The six exact targets/colors, 40 games/cell and absolute rival gates are unchanged.
The source is frozen through every arm; all ten VMs, full replay hashes, actions,
XP and server scores are audited. Each arm drains before the next starts.

Typed-event diagnosis selects the median own-score game separately within each
observed W/L/D group per cell. This is retrospective explanation, not independent
validation. It reconciles all XP to creep/hero/other sources and records accepted
purchases, completed/interrupted portals and rejected actions. Initial relh
replays show low-income heroes still buying consumables while missing armor;
that is an unresolved economic priority concern, not a claimed causal cure.

# Result

| Target | Color | Baseline W/L/D | Practiced W/L/D | Practiced / rival XP score | Distinct streams |
|---|---|---|---|---:|---:|
| relh | red | 0/40/0 | 33/7/0 | 322.44 / 381.16 | 18 |
| relh | blue | 3/37/0 | 29/0/11 | 411.02 / 310.23 | 18 |
| jordan | red | 9/0/31 | 40/0/0 | 781.65 / 436.60 | 15 |
| jordan | blue | 1/0/39 | 40/0/0 | 591.43 / 278.61 | 18 |
| richard | red | 0/40/0 | 29/11/0 | 327.99 / 436.26 | 19 |
| richard | blue | 2/38/0 | 34/0/6 | 484.70 / 237.28 | 17 |

All 480 baseline/candidate games are terminal, all ten VMs valid, and every
replay/action/XP/score audit passed. Practiced wins rise from 15/240 to 205/240.
Mean own XP score improves in all six target/color cells versus the baseline.

# Verdict


Keep b82c3799 as an improved research fork: both forts and own score improve
against each pinned target/color. The full frozen qualification still fails:
relh blue and Richard red each have 29 wins, below 30; own mean score remains
below the rival on relh red and Richard red. No #1, mixed-team, future-successor
or formal acceptance claim follows. No league champion was changed.

Final pair: `examples/gods_of_the_arena/players/ir/forks/microplay20260922`.
The parent and coaching captures remain untouched. The user's subsequent
"keep going" starts a separate armor-reserve micropractice hypothesis against
this exact improved parent; its outcomes cannot relabel this completed panel.
