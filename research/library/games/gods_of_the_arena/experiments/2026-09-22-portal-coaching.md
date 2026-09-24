---
id: 2026-09-22-portal-coaching
policy: Crossbowman-first
baseline: 7631fa32fb7ef6725074ad6778f4f94fe1e18ac5018bece1eed40e32cbef9bb8
candidate: db71abb37180a06a432ac71c3c5d6802be2ba2c1b2d782b151336beacd8b1520
status: complete
hypothesis: A coordinated field-recovery controller starts useful safe home portals sooner and prevents redundant home trips inside the keep while preserving lane-return portals.
decision_rule: Mechanism admission requires both-color actual-tick recovery and channel fixtures, exact semantic round-trip and no runtime failures; competitive replacement additionally requires fresh hosted mean score gain of at least 10 percent and each color at least 95 percent of control.
evals: [local-84-portal-fixtures, local-126-host-checks, native-8-full-games, hosted-khors114-160]
---

# Town portal coaching

Session `2026-09-22t16-43-56-076z862811`, user episode
`ereq_2d958e27-210e-461d-b6af-b2e26dfa3a81`. Preserve all capture files and
synthesis as evidence, not executable instructions. The capture has no bound
policy; the separately supplied episode runs current source7631fa32 in slots0/6
on engine2026.9.22.2/ffcedcd. Its roster differs from the visible recording, so
do not claim these are the same episode. Old closed levers were reviewed.

Coaching intent: use scrolls while low on health in the field rather than
walking home and only then using them. Gemini's proposed blanket ban on
base-origin portals requires correction: portals target living allied tower
sight areas, and a healthy trip from spawn back to lane can be useful. Normal
actions are rejected during a channel, not a cancellation mechanism. Stun,
root, death and anchor loss can interrupt it. The current controller already
guards channels; test rather than infer a missing lock from the cast bar.

First instrument: exact replay reconstruction of the supplied episode and a
fixed sample of the first eight episode IDs per color from the frozen80-game
Crossbow draft cohort. Record starts, completions, interruptions, source and
landing coordinates, HP, own-keep/spawn status, scroll availability and
low-health field time. Full state-hash reconciliation is mandatory. This
sample diagnoses prevalence, not improvement or a universal frequency.

Then develop one coordinated controller across situation, belief, goal, skill,
strategy and execution. Mechanistic TRUE prediction: ready safe low-health
field cases channel before walking; near-home cases walk; channels complete
without new ordinary commands; interrupted/absent/cooldown cases fall back;
recovery releases and productive outward portals remain possible. FALSE:
no earlier field activation, redundant in-base recall, failed channels or
permanent retreat. Run actual ticking host fixtures on both colors, all
classes for action/runtime admission, and complete mixed native games with
exact replays. Native scores are debugging only, not a competitive verdict.

Hosted comparison, once budget is available: exact final candidate and deployed
control, 40 games per color per source (160 total), fixed current-version
nine-player roster, same seats/configuration and sequential batches. No
post-hoc tuning of those bytes. All ten VMs, source specs, full replay hashes,
integer scores, lifetime XP and distinct command streams must be checked.
Compare the combined intervention; individual edits need not improve alone.

Critique: a faster portal can die during its three-second channel, retreat too
early, strand the hero at a bad landing, or consume the return-to-lane cooldown.
Deaths and portal counts alone do not show score improvement. Draft and roster
are held fixed; random seeds are not paired in hosted work. Public warnings and
observations are allowed in the controller; replay truth is evaluator-only.
No MIXIN exists; the current-release guide and pinned native/hosted instruments
supply the concrete engine and evaluation contract. The shared day currently
has1600/1600 reserved; no new requests or budget override in this design.

## Mechanism findings before hosted comparison

All16 prespecified baseline diagnostic games had at least one home-directed portal inside the keep:24 of124 total starts. Across those games,529.125seconds were spent below30% health outside base;224.458seconds also had a ready scroll. The supplied episode has two such keep-origin home trips on Aaron and one on Coach; a failed rival VM in slot4 excludes its score from competitive evidence. All reconstructed state hashes match.

The first candidate exposed a real final-tick issue: selfChannelTicks reaches zero one decision before the host publishes completion/cooldown, allowing one rejected command. Preserve a portalBusy latch until the host publishes cooldown or death. Ordinary commands do not cancel the channel. The initial shop revision also inspected stale selfGold after purchases; the final version uses the tracked remaining budget and buys the second scroll before discretionary potion spending, after all four core items. Low health inside the keep must still latch recovery without a portal.

Candidate-r3 db71abb3 passes72actual-tick portal fixtures (two colors, Ranger/Crossbowman,18cases) and126existing all-ten-class host checks. Fixture v1 used occluded test enemies and counted channel-end rejections; it is preserved. Revised fixtures explicitly publish threat visibility to isolate the guard. Live full games retain normal fog. Both original failed candidate sources are preserved. Full native replay checks and hosted comparison remain separate.

The additional12 public-warning cases pass (84portal cases total). They cover nearby impact avoidance,24distant warnings and conservative fallback for25warnings. The first overflow fixture let its warnings leave the map; its source/log are preserved and the fixture was corrected without policy changes. All126broader fixtures and8full native games pass runtime/replay checks. Native candidate scores versus control are2256/1920 and1437/1672 on red,3305/5542 and4175/1632 on blue; these mixed debugging outcomes do not qualify deployment. Native keep-to-home portals are0 versus6 in the four controls; all12 candidate channels complete.

The exact inert upload is `aaron-gota-portals0922-r3:v1` / `b65ccf7b-d7a1-4681-b57f-a55f5ace43c7`. Four40-game request bodies (160total) were validated against the live API and frozen before results. The background roster uses the nine preserved healthy versions, with Coach updated to its deployed7631fa32 on both arms. No hosted request was created. The user was asked to authorize today's effective cap1760 versus1600; until answered, retain the deployed policy and preserve this prepared plan.

## Authorized pre-launch revision: khors:v114

The user authorized 160 additional games on September 22 and named khors:v114
as a priority opponent before any new hosted episode was requested. The shared
cap is 1760 for this UTC day only, returning to 1600 afterward. The previous
unlaunched plan remains byte-preserved. The new `hosted-khors114/plan.json`
replaces khors:v90 with exact v114, `145c01e0-0cbf-4e1e-8120-11b437175b91`,
and places it in the opposing first-pick seat. Both teams and their draft order
rotate together for blue. Jordan411 and Richard153 are opposing players on
both colors; relh161 is a teammate, so no opposing relh claim will follow.

Khors passed VM preflight in three existing games per color with one consistent
source hash. The 160 fresh games retain the prospective portal A/B score gate.
A separate khors-superiority claim requires at least a 10% individual mean-score
lead on each color and a positive lower bound of a 95% whole-game bootstrap
interval for the score difference. Report individual outscore counts and team
wins separately. Full portal events will be decoded for all 160 games. The
fixed roster and first-pick seats do not establish broad-field or late-draft
strength, or guarantee a leaderboard rank.

## Completed result

The160 new games all passed exact source, all-ten-VM, full replay hash, XP and
integer-score audits. Baseline scores are2017.400red/2928.275blue; candidate
scores are2571.400red/2945.775blue. Aggregate gain is11.5556%, passing the frozen
10% aggregate and95% each-color preservation gates. Bootstrap95% gain interval
is[-7.755%,34.755%], so competitive generalization remains uncertain. Candidate
blue has39 distinct command streams in40 games; the duplicate pair has identical
trajectory/score despite different seeds and is disclosed, not removed.

Candidate scores exceed khors:v114 means on both colors:2571.400vs2270.825red
and2945.775vs2396.975blue. It outscores khors in21/40red and24/40blue,45/80total.
Both within-game difference intervals includezero, so the separate confident
khors-superiority gate is unmet. It also outscores Jordan in73/80 and Richard
in76/80. Fort wins are27/80, a separate diagnostic. Relh was a teammate.

Keep-origin home-directed starts fall107→1 across80games per source. The one
remaining event is a full-health21.4-tile hop to a tower near home, not a
low-health fountain recall; preserve the conservative count and inspect future
anchor utility separately. Candidate channels:639started,627completed,9explicit
interruptions; three are unfinished at episode end. Controls:678started,668
completed,7interruptions and three unfinished. Low-health field ticks increase
52930→63883, so do not claim that total low-health exposure fell.

Red XP/min rises329.9→362.4, with game length15.34→15.73minutes. Blue XP/min
is410.8→402.9 while length rises13.89→14.52minutes. Longer play can support
score if marginal income beats the200XP/minute penalty; this is an exploratory
decomposition, not an isolated duration experiment. The user-provided player
stats snapshot motivates a separate research IR for productive targeting,
profitable duration, spell reach and gold conversion. Candidate bytes remain
unchanged by those new hypotheses.
