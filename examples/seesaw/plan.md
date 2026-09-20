# Seesaw — a cooperative playground

## Context

The first Polyworld examples are about fighting, gathering, or parties that
still have a winner. Seesaw is a **two-player coworld** whose only score is
shared fun: two agents on one board, five minutes, no text, no hidden team
chat. If one rider is miserable, the pair loses.

It is designed backward from the coworld split used by Pudge Wars:

| Question | Owner | Used for |
| --- | --- | --- |
| Who played well together? | `results.scores` (identical on both seats) | Ladder / Elo |
| How was the fun made? | Graders + expression log | Optimizer attention |
| Where should I look? | Interest-range grader | Replay scrubbing |
| Can this policy even pump in rhythm? | Diagnoser scenarios | Mechanical competence |

Do not collapse those into one number. A policy that maxes its own bounce
while the partner goes green is not “better” on the ladder.

## The game

Two children, **Lila** (west seat) and **Nico** (east seat), start already on
the seesaw. A match is five real minutes at 24 Hz (`7200` ticks). Decisions
land every eight ticks. Lean and pump are sticky intents; an expression is a
short-lived signal.

The board is a plank on a fulcrum. Positive angle is Lila’s side down.
Pumping is the playground skill: add weight on the way down, lighten on the
way up. Equal masses sit still until someone leans. A side that is already
down wants to stay down, so reversing the board takes a partner who times
the pump instead of fighting the geometry.

### Hidden episode conditions

Every seed samples **playground weather** and **two inner lives**. The riders
do not get the numbers, only coarse bands and what it feels like.

Weather bands (public):

- Temperature: cold, cool, mild, warm, hot
- Wind: still, breeze, windy, gusty
- Wet: dry, damp, wet

Hidden magnitudes behind those bands change damping, pump slip, wind torque,
and heat fatigue.

Each rider independently samples:

- Energy: exhausted, tired, fresh, energized, wired
- Stomach: hungry, fed, overfull
- Vestibular: steady, queasy, nauseous
- Mood: grumpy, cheerful
- Thirst: thirsty, hydrated

Those traits set a **preferred intensity** (how wild a ride feels good) and a
**sickness threshold**. Energized wants a bigger arc. Tired wants a gentle
one. Nauseous gets sick on a ride the partner might still love. That mismatch
*is* the cooperation problem.

### What you can see

A rider feels the board (angle, angular velocity), their own lean/pump, their
own fun delta and nausea, and the weather bands. They can **see** the
partner’s body: lean and whether they are pumping. They cannot see the
partner’s fun, nausea, traits, or preferred intensity.

The only intentional language is a **face**: smile, frown, or one of fourteen
generated expression glyphs. No chat, no pings, no numbers sent across.

### Fun, sickness, and the combined score

Each tick awards comfort when `|omega|` is near that rider’s hidden
preference. Both-comfortable ticks pay a together bonus. A blast that leaves
the partner at zero comfort is discounted.

Nausea accumulates when intensity exceeds the vestibular threshold, faster
when the board is wet or the rider is already queasy. Crossing the sick line
is a large fun penalty. Sitting still recovers.

At the bell:

```
individual = max(0, rawFun - sickEvents * penalty - maxNausea * trickle)
pairScore  = 2 * min(individual) + (sum / 4)
```

Both seats receive `pairScore`. The less-happy rider is the binding
constraint. Optimal play is not “I had more fun”; it is **the highest fun
both of you can sustain**.

## Coworld packaging (later)

Engine truth stays in this folder: integer sim, action tape, BASIC host,
native spectator. A certifiable coworld (HTTP/WS game container, Docker
policies, platform ladder) should wrap this sim the way spec 0085 wraps
Pudge Wars — not fork the rules.

Suggested later pieces, none of which belong in the first Polyworld drop:

- `results.scores = [pairScore, pairScore]`
- Fog is unnecessary; both seats see the same board and the other’s face
- Graders: fairness (`min/max` fun), communication (did they express when
  nausea crossed a band), rhythm (pumps aligned with descent), sickness
  avoidance, together-bonus rate
- Diagnoser: “partner frowned — did you ease off?”, “nauseous seed —
  can you keep them under threshold?”, “wired vs exhausted — did you
  compromise?”
- Bundled baselines: `players/base.bas` (cooperative) and
  `players/selfish.bas` (own intensity, ignore faces)

Seating is two slots, `team_pair` with a single pair, or a cooperative
ladder that ranks the pair score. Clone seats must not be able to steal
credit by making the other sick.

## Files

```
seesaw.nim     entry, branches on -d:headless
content.nim    bands, expressions, tuning, contentHash
maps.nim       integer playground, sand pit, path, forest
sim.nim        board physics, fun, nausea, pair score
bots.nim       BASIC host surface
players/       cooperative and selfish scripts
game.nim       CLI, match setup, headless runner
replays.nim    POLYSEESAW action tape
graphics.nim   spectator: park, rotating plank, faces
decor.nim      benches, lamps, fence, flowers
ui.nim         fun/nausea, weather, expressions, transport
```

Dependency order is acyclic: `content → replays → maps → sim → bots →
controls → game → graphics`. Tests never import `game.nim`.

## Commands

```bash
nim r examples/seesaw/seesaw.nim --bot examples/seesaw/players/base.bas:2
nim r -d:headless examples/seesaw/seesaw.nim --seed 1988 --bot examples/seesaw/players/base.bas:2 --record examples/seesaw/replays/demo.replay
nim r examples/seesaw/seesaw.nim --replay examples/seesaw/replays/demo.replay
nim r tests/test_ssw_sim.nim
```
