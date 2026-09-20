# Replay findings: turn cost, tower traps, and late escapes

[Watch the three selected replays](replay-review-20260915.html) · [Machine-readable evidence](replay-findings-20260915.json)

The highest-priority policy change is to make retreat completion depend on
**actual separation**, with turn time and route safety included. The ten-tick
kiting controller often resumes fighting just as its hero starts moving.

This diagnosis covers **160 complete, hash-verified replays** on published
`2026.9.15.3`, source `e1279894d10a7684f303e7a9f1ea2f84c1d14253`.
They represent the same **40 seed/hero cases across four arms**, with nine
default policies in each match. These are previously observed discovery cases,
not new independent validation or evidence of improved league strength.

## 1. Short retreats spend most of their time turning

The engine finishes turning before it moves. Its turn rate is 0.35 radians per
tick, so a reversal can consume about nine ticks. Attack animations face the
target, making that reversal particularly relevant immediately after a hit.

| Recorded retreat measurement | Short + spells | Long, no explicit spells |
|---|---:|---:|
| Configured duration | 10 ticks | 32 ticks |
| Complete hit-adjacent walk segments examined | 409 | 444 |
| Median ticks turning without movement | **8** | 12 |
| Median ticks with displacement | **2** | 20 |
| Median net displacement | 0.21 tiles | 1.95 tiles |
| Segments with tracked enemy still alive at end | 334 | 309 |
| Gained more than 0.25 tiles of separation | **32 / 334 (9.6%)** | 206 / 309 (66.7%) |
| Lost more than 0.25 tiles of separation | 108 / 334 | 65 / 309 |

These are command-derived segments, not reconstructed private VM variables.
Each starts immediately after a basic hit, lasts exactly the controller's
configured duration, and begins within seven real tiles of the nearest visible
enemy. Separation tracks that same enemy at both boundaries. Dead/missing
enemies are excluded from the separation denominator. Events within a game
are correlated; no statistical significance is claimed from event counts.

**Watch:** `crossbow-short`, seed 721028, **08:33.63**, tick 12327. The Crossbowman
barely moves during its short retreat while the Demon Hunter closes in.
Also watch `lich-long`, seed 721018, **14:09.46**, tick 20387: a longer retreat
still follows an ineffective route and loses health.

**Proposed IR change:** distinguish `turning`, `creating distance`, and
`ready to re-engage`. Keep a destination long enough to make progress; evaluate
measured separation and enemy closing speed before resuming attacks. Bound the
retreat so it cannot abandon objectives indefinitely. Preserve spell use while
moving, and reassess routes when progress fails. A fixed longer timer alone is
not established as an improvement: long kiting won 23/40 versus v2's 22/40,
but deaths increased from 134 to 135. The short variant won only 17/40.

## 2. Heroes can become trapped beside their own towers

V2 has two cases with more than 30 seconds of uninterrupted immobility without
a basic hit or active offensive spell:

- **Arcanist, seed 721023:** 344.7 seconds, starting at tick 698 (**00:29.08**).
  Finished with one basic-hit event, zero XP, and a team loss.
- **Warlock, seed 721001:** 78.5 seconds, also ending in a team loss.

Both have a first path waypoint inside a friendly tower's required collision
clearance. Every other ≥30-second stall found in the default and two candidate
arms also has a waypoint overlapping a friendly tower footprint.

For the Arcanist, the waypoint is `(7.5, 77.5)`. It is only 0.434 tiles from
tower 14, where the combined tower/hero clearance is 0.83 tiles. The hero stops
on that boundary. `followHeroPath` keeps steering toward the blocked waypoint
and reports that it followed a path, even though the end-of-tick position
does not change. Changing distant attack targets does not resolve this.

**Controlled replay probe:** restore the exact, hash-verified state at tick
1200; retain everyone else's recorded commands; test eight directions at
distances one, two, and four tiles for 96 ticks. **All 24 nearby movement
commands produce zero displacement.** The unchanged control reproduces every
hash. In a separate **engine-only diagnostic**, replacing that first waypoint
with the hero's current position allows 4.60 tiles of movement. That intervention
is not a legal policy or a competitive evaluation, and was not deployed.

Earlier probes matter: by tick 650, changing destinations still leads to the
same trap; at tick 500, nearby movement commands can divert the hero. This
supports investigating prevention before contact, not treating movement retries
after contact as a sufficient recovery mechanism.

**Proposed IR change:** avoid tower collision clearance before entering it,
and monitor progress independently of target identity. `terrainWalkable` and
an accepted `walkTo` are insufficient evidence of a traversable route. A robust
game-side fix also needs collision-aware hero paths or failed-progress handling.
No game mechanics were changed in the evaluated runtime.

## 3. Critical-HP escape is often too late

Across v2's **134 deaths**, the final six-second window contains a median of
only **one second of samples below 35% HP**. Eighteen deaths have no such sample.
Sampling is every half-second: this is an estimate of opportunity, not an exact
continuous time-to-death measurement.

- 132/134 deaths have a visible enemy hero or creep targeting us in that window.
- 65/134 include a sample with at least three more nearby enemies than allied
  mobile units, within six tiles. This counts units, not their combat strength.
- 25/134 include tower targeting. Towers are not the only danger to model.

**Proposed IR change:** compare escape time against recent damage, multiple
attackers, nearby allies, and visible spell warnings before HP becomes critical.
Choose an escape corridor toward useful support, considering turn cost and
pursuer speed. Do not simply repeat the rejected unconditional 35%-HP retreat.
Both survival and fort wins must improve in fresh evaluations.

## Lower-priority observations and limits

- V2 spends 53.9% of alive ticks with its selected target more than 12 tiles
  away, and 77.6% outside basic-attack range. This includes legitimate travel;
  it is not all wasted time. A local-radius targeting policy was already tested
  without confirmed superiority. Reopening targeting needs route/value evidence,
  not the same radius test again.
- Only 4/134 v2 deaths occur with a full inventory. Reserving more slots is
  therefore less directly supported by these deaths than fixing movement.
- Published `.3` does not populate `DamageMetric`. Its zeros were excluded
  from damage conclusions. Inactivity instead requires no displacement, no
  basic-hit event, and no active offensive spell effect.
- No new hosted XP, uploads, or league promotion were made. The selected v2
  executable remains unchanged. These findings update its IR beliefs and the
  next experiment plan; proposed behaviors are not claimed as implemented.

## Reproduce and inspect

The native 3D capture failed because the local asset checkout lacks
`courtyard-stone-1.rgb.png`. The supplied viewer renders real recorded positions,
visibility-filtered objects, and engine paths schematically. It has play/pause,
speed, timeline, hero-following, and whole-map controls.

Reusable instruments in this directory:

- `replay_diagnostics.nim`: complete replay verification, per-tick counters,
  movement segments, death context, tower-overlap evidence, optional frames.
- `replay_escape_probe.nim`: bounded checkpoint interventions with an unchanged
  replay control and an explicitly separated engine-only diagnostic.
- `replay_review.py`: batch decode, input hashes, and independent checks against
  original death/hit/XP/final-state totals.
- `replay_findings.py`: aggregate the descriptive evidence.
- `replay_viewer.py`: build the self-contained interactive viewer.

Inputs and complete outputs are retained under
`tmp/gota-ir/replay-diagnosis-20260915/`. `cohort-v2/` contains the final analysis.
The initial `cohort/` is retained but superseded: the revised instrument aligns
separation boundaries exactly and excludes active offensive spells from stalls.
The 96-tick probes are open-loop for other players and support only local
mechanistic conclusions.
