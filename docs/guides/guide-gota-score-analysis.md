# Individual score research: discrete accounting and statistical aggregation

User direction, September 23: use discrete math and statistics like the
[player dashboard](https://metta-ai.github.io/polyworld-buff/GOTA/players/), and
prepare policies that harvest XP rather than optimize match wins.

The sole performance objective for **new studies** is expected individual
`floor(max(0, XP - 200 * elapsed_minutes))`. Draft time counts. Team victory,
survival, low deaths, positive-score frequency and conditional positive mean are
diagnostics, not independent acceptance constraints. More deaths or a team loss
can be acceptable when individual score improves. Runtime validity and evidence
quality remain required. Preserve prior frozen experiment rules and decisions.
The control-tactics pilot was frozen before this clarification; do not rewrite it.

## Exact accounting

At 24 ticks/second, use integer numerator `M = 1440 * XP - 200 * ticks`.
Score is `(M + max(0, -M) - (max(0, M) mod 1440)) / 1440`. For a matched
candidate/baseline pair, the score change therefore decomposes exactly into:

- Additional XP.
- The change in elapsed-time penalty.
- The effect of the zero floor.
- Integer rounding.

This exposes hidden gains in zero-score games and prevents mistaking longer
games or more kills for better score. Never subtract death/travel penalties
again; they are already included in elapsed time. Use their time budgets to
locate potential interventions, not as extra terms in the actual reward.

Mean score is also exactly `P(score>0) * E[score | score>0]`. Report both terms
and a three-part mixture (zero, 1–499, 500+) to explain changes, while optimizing
their aggregate. A higher conditional mean on a shrinking survivor subset is
not necessarily an improvement.

## Stratification and comparisons

Keep exact policy UUID, engine, side, draft seat, hero and roster identities.
Report raw sample sizes, missing/failed telemetry, and canonical command-stream
duplicates. A player with early carry picks is not a causal control for a late
melee player. Do not mix old balance or auto-cast engines into current estimates.

Primary A/B evidence uses responsive paired counterfactuals: same seed,
configuration, roster and subject seat; replace only our policy. Whole games are
the sampling units. Bootstrap matched pairs within frozen side/seat contexts,
preserving the planned context weights; never bootstrap ten heroes or thousands
of ticks as independent games. Fixed-roster results do not establish the league
mixture. If duplicate streams occur, report clustered sensitivity or collect
novel contexts before a precision claim.

Report score delta and paired 95% interval, higher/equal/lower score counts,
per-side/class/seat diagnostics, XP per elapsed minute, source XP, and frequency
of zero/productive games. Wilson intervals show uncertainty in those rates.
Class slices and extra telemetry are exploratory unless separately frozen;
do not choose a favorable slice after seeing results. Freeze a fresh confirmation
and its numerical threshold before outcomes. No finite result guarantees future
score preservation as opponents or engine versions change.

## Finite state and graph diagnostics

The replay61 decoder assigns each **pre-tick** state, in priority order:
draft, dead, stunned, portal channel, own keep, moving in field, other field.
These disjoint counts sum exactly to elapsed ticks. XP awarded that tick is
assigned to its starting state and sums exactly to lifetime XP. Movement means
an active move target, not proof of distance traveled or retreat intent.
Silence, root, low HP and 10/30-second XP droughts are overlapping annotations.
An XP drought clock includes previous dead time, but drought occupancy counts
only living battle ticks. Transition counts/sojourn occupancy describe play;
they do not establish a Markov process or the effect of changing a transition.

Construct a directed weighted graph from victim policy to XP recipient, using
reconstructed hero-death reward events. It identifies recurring XP sources and
which opponents farm us. Repeated victim/player rows remain within one game;
do not treat graph edges as independent evidence.

Control timers are intervals: refreshing an already controlled target gives
only the extension beyond its current expiry. Landing a stun/silence/root is
a mechanism metric; lost damage, mana and farming can outweigh it. Preserve
basic attacks and compatible action channels under root/silence.

## Prepared XP harvesting hypothesis

The separate `harvest-value` binding ranks public, visible attackable targets
by `reward / (ceil(HP/basic_damage) + travel_tiles_beyond_reach)`, with a small
current-target preference. Pinned release61 rewards: hero150, structure100,
god500 personal XP, creep15 shared-pool upper bound. It retains buildings as
opportunities: excluding all of them already failed a previous study.

This is a discrete **work proxy**, not calibrated expected XP per second.
It omits obstacles, spell burst, enemy response, allied sharing and competition
for last hits. Test its combined effect with exact responsive games; do not
interpret the arithmetic alone as evidence of better play. Future refinements
can estimate last-hit probabilities and spell/attack schedules from held-out
events, provided deployable inputs remain public.

Implementation: `tools/gota_autoresearch/score_statistics.py` and
`games/gods_of_the_arena/instruments/controltactics20260923/{telemetry.nim,statistics_report.py}`.
The captured dashboard snapshot (generated16:01UTC) has360 replays on engines58/59;
it informs vocabulary only. Our current cohort is engine61.
