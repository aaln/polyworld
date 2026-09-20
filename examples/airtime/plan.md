# Airtime — a theme-park overlord

## Context

The shipped examples fight, gather, or throw dinner parties. Airtime is the
first **construction economy**: one BASIC overlord runs a park, guests are a
native crowd, and the thing that scores is not a kill or a bite. It is
whether the machines you built are a good time for the people who showed up.

RollerCoaster Tycoon is the reference, not the code. The signature of that
game is not "place a fun building." A ride's stats come from its **geometry**.
A square of flat track with a lift hill is a different ride from the same
budget spent on a drop, an airtime hill, and a helix. Guests have hidden
intensity preferences, so the same circuit can be a masterpiece for one
visitor and a sick bag for the next.

That is the new control shape. Light vs Dark commands an army. Heartleaf
walks a body. Airtime draws paths, appends track verbs, sets prices, and
assigns staff zones. Guests are never scripted.

## What is different from the other examples

| | Light vs Dark | Heartleaf | Airtime |
|---|---|---|---|
| Agents | one VM per side, two of them | nine VMs, one villager each | **one VM, the manager** |
| Conflict | damage | garden races, dinner seats | guest taste, cash, breakdowns |
| Map | mirrored 128 | village ring, no symmetry | one fenced park, no symmetry |
| Walkability | changes (build, fell) | fixed at generation | **changes** (paths, rides, shops) |
| Clock | cosmetic | the mechanic | the mechanic: days, weather, ledger |
| Who is scripted | every unit | every villager | **only the manager** |
| Position | tile / body | tile | guests on path tiles; cars on track |

Do not collapse the park into a Theme Park catalog. If a coaster is a
footprint with hardcoded excitement, this example has nothing to say that
`build` in Light vs Dark does not already say.

## The game

A match is **twelve park days** in the shared twenty-minute default
(`28800` ticks at `24` Hz). Each day is `2400` ticks of park time, 10:00 to
22:00, then a five-second daily ledger, then the next morning. Decisions
land every eight ticks. Path, price, and research intents are sticky;
building a track is a sequence of accepted verbs.

The manager starts with a south gate, a three-by-three cobble plaza, cash,
and a loan. Everything else is grass, a pond, a ridge, and trees that cost
money to clear. Guests only walk on path and queue tiles that flood-fill
from the gate. A ride with no path from the plaza is scenery.

### Hidden guest lives

Every guest independently samples, at the gate, four inner numbers the
manager never sees:

- Intensity preference: timid `200`, average `500`, thrill `800`
- Nausea tolerance: queasy, steady, iron
- Patience: how long a queue they will join
- Wealth: wallet size and price sensitivity

Weather and rating change the **mix**, not the individual. A sunny Saturday
with a 700 rating brings more thrill-seekers. Rain brings fewer guests and
a timid shift. The manager sees the weather band and the thought histogram,
never the preference of guest 184.

That mismatch *is* the design problem. A steel loop that maxes excitement
will empty the park on a timid day and print money on a thrill day.

### What you can see

The manager sees cash, loan, rating, date, weather, and aggregates:
guest count, average happiness / hunger / thirst / nausea, thought counts
over a short window, ride and shop stats, staff, and the tile under a
query. They cannot list four hundred guests. They cannot see a preference.

Rides report excitement, intensity, nausea, queue length, riders, profit,
reliability, and whether the last test run completed. A live construction
reports the turtle: tile, facing, height, and how far a `finishTrack`
would miss.

### Fun, sickness, and the score

A guest on a ride banks happiness from how close the ride's intensity is
to their hidden preference, plus the ride's excitement, minus nausea they
cannot tolerate. A blast that leaves them sick is a thought and a walk to
the exit. Sitting, eating, and a working bathroom recover them. Litter,
rain, and a broken ride spend happiness. An empty wallet, a lost path, or
a long run of bad thoughts sends them home.

At the bell:

```
parkValue = cash
          + (buildCost of standing rides and shops) * 4 / 5
          + sceneryValue
          - loanRemaining
score     = parkValue
```

The default scenario, **Greenfield**, also records a binary goal: park
value at least `$50_000`, rating at least `600`, and at least `80` guests
on the grounds at once, before the tick limit. Bankruptcy (cash below zero
with the loan maxed) closes the park and freezes construction.

`results.scores = [parkValue]` for a later coworld seat. The goal flag,
happiness, uniqueness, and bankruptcy live on graders, not in that number.
A policy that prints one sickening coaster and milks the first week is not
"better" if the graders are looking at sustained rating.

## The integer rule

**No float ever enters `World`.** Guest tiles, cash, needs, and ratings are
`int32`. Track geometry is tiles plus height in the same `1/8`-tile steps
`pathing.pack` uses. Ride physics is millitiles and milli-g. Map generation
is integer value noise, the same family Light vs Dark and Heartleaf use.

The renderer interpolates cars along the track polyline and stands guests
on `surfaceHeight`. `surfaceHeight` is called in the viewer, and its result
never flows back. `sim.nim` must not import anything that returns a float.

`polyworld/fixed` is available if the test-car integrator is cleaner in
Q16.16. Either way the inputs and the published ride stats stay integers.

## Paths, queues, and the one-path-network rule

Guests walk only on **path** and **queue** tiles. Path tiles are undirected.
Queue tiles are a directed chain that must end at a ride's queue slot.
Shops and the gate sit on path. A bench occupies a path-adjacent tile and
does not break the network.

Walkability for guests is a derived grid, rebuilt when a path, queue, ride,
or shop is accepted, not by calling `computeWalkable`. The terrain bake
happens once. The park's circulatory system is this path grid.

Disconnected path is dead. `reachableFromGate(x, y)` is a host function.
Guests never path outside the gate flood fill. If a ride's queue head is
unreachable, nobody queues.

Cap `256` guests. Path searches are budgeted like Heartleaf: a handful of
A* expansions per tick, tile-index tiebreak, abandon after a stuck
threshold, `orderFailed` is not a guest concept because guests are not
commanded. A guest who cannot reach a chosen destination picks another or
leaves.

## Track as a turtle

BASIC cannot run a 3D CAD tool. A coaster is a **closed verb tape** the
overlord appends one piece at a time.

`beginTrack(kind, x, y, facing)` spends the station cost and places a
station on the circuit: four tiles long, one tile wide. The queue slot is
the side of the first tile. The turtle starts at the last tile, facing
out, height zero.

`track(verb, arg)` appends one verb, occupies tiles at the turtle's
height, and advances the cursor. `undoTrack` pops. `clearTrack` refunds
the construction and deletes the tape. `finishTrack` accepts only when
the turtle arrives at the first station tile, facing in, at height zero,
and a test car completes a lap without stalling or exceeding the kind's
speed cap.

### Verbs

Cardinal only. No 45-degree track in the first drop. Diagonals make
closing a circuit a BASIC nightmare and buy nothing the research needs.

| Verb | Arg | Footprint | Wooden | Steel |
|---|---|---|---|---|
| `Straight` | length 1..4 | `arg` tiles forward | yes | yes |
| `Left90` | unused | 2×2, ends facing left | yes | yes |
| `Right90` | unused | 2×2, ends facing right | yes | yes |
| `Lift` | height steps 4..24 | forward, powered climb | yes | yes |
| `Climb` | height steps 1..8 | forward, unpowered | yes | yes |
| `Drop` | height steps 1..16 | forward, unpowered | yes | yes |
| `Brake` | unused | one tile, caps speed | yes | yes |
| `Airtime` | unused | three tiles, camelback | yes | yes |
| `HelixL` / `HelixR` | unused | 3×3 descending spiral | no | yes |
| `Loop` | unused | three tiles, inversion | no | yes |

Self-intersection at the same height is illegal. Crossing above a path
or another rail is legal. Supports are automatic and have no sim cost.
Underground track is out of scope.

`tracks.nim` is pure: verb tape in, node list and occupancy out, plus
whether the tape is a closable circuit. It does not touch `World`.

### Ride physics and the three numbers

`rides.nim` runs one test car over the nodes. No guests. The published
stats are the only thing guests and the HUD read.

Each tick the car integrates:

```
slope     = riseSteps / lengthMilli
speed     = speed + gravity * slope - friction - brake
if lift:    speed = clamp(speed, liftMin, liftMax)
lateralG  = speed² / radiusMilli
verticalG = 1000 + speed² * curvature   # 1000 = 1 g
```

The lap is a histogram. The three numbers, `0..1000`, displayed as
`0.00..10.00`:

- **Intensity** — peak speed, peak |G|, drop length
- **Nausea** — lateral G, inversions, long duration, drops after a loop
- **Excitement** — airtime (vertical G under `1000`), drop count, G
  variety, length, inversions, a small scenery bonus from nearby flower
  and tree tiles, then a penalty when nausea and intensity dwarf
  excitement

A four-tile square with a lift is a valid wooden circuit and a bad ride:
low excitement, modest intensity, near-zero nausea. The golden wooden
tape in `tests/test_air_rides.nim` (lift, drop, airtime, four lefts)
must land in fixed bands so a physics edit fails by name.

Operating trains reuse the same integrator. One train per ride in the
first drop, eight seats on wooden, twelve on steel. Guests vanish from
the path while seated, the way Heartleaf hides a villager indoors, and
reappear on the station's exit path with their needs updated.

Throughput is the layout puzzle. Queue tiles are capacity. A full queue
is a thought, "too long," and the guest walks away. Extending the queue
is a real verb, not flavour.

## Flat rides and shops

Not everything is a turtle. Flat rides are footprints with **catalog
stats**, because the interesting design is still "where, how much, and
who can reach it," and because the overlord needs something to build
before research unlocks wood.

Starting unlocks: carousel, bathroom, burger stall, dirt path.

Research is one slot, four topics. Ticks accumulate. The first thrill
unlock is the wooden coaster. The second is steel. Gentle and shop
topics unlock teacups, drinks, ice cream, souvenirs, an info kiosk.

| Kind | Footprint | Role |
|---|---|---|
| Carousel | 3×3 | gentle, low intensity |
| Teacups | 3×3 | gentle, nausea if they ride twice |
| Wooden coaster | station + tape | the first real machine |
| Steel coaster | station + tape | loops, helixes, higher cap |
| Bathroom | 1×2 | bathroom need |
| Burger | 2×2 | hunger, then litter |
| Drink | 2×2 | thirst |
| Ice cream | 2×2 | hunger, more on hot days |
| Souvenir | 2×2 | optional cash, happiness drip |gi
| Info kiosk | 1×1 | reduces "I'm lost" thoughts nearby |
| Bench | 1×1 | sit, energy, nausea recover |
| Lamp | 1×1 | rating, night visibility (cosmetic night) |
| Flower bed | 1×1 | scenery bonus to nearby ride excitement |

`clearLand(x, y)` removes a generated tree for a fee. Water is
unbuildable. No bridges in the first drop.

## Staff are zones, not micro

Staff are not Light vs Dark units. The overlord hires a kind and paints a
rectangle. The body walks the rectangle on its own.

- **Handyman** — sweeps litter and vomit in the zone
- **Mechanic** — inspects rides in the zone; reliability decays; at zero
  the ride closes, queues dump, thoughts fire
- **Entertainer** — happiness aura while walking the zone

Security and vandalism wait. Wages tick every day. An unassigned hire
idles at the gate and still gets paid.

## Economy and rating

Cash starts at `$15_000` plus a `$10_000` loan. Interest is a daily
ledger line. The loan can be grown to `$20_000` or repaid.

Park entrance is a price. Each ride and shop has a price. Guests refuse
with "I'm not paying that" when price exceeds wealth. Running cost is
staff wages plus a small per-ride upkeep. A closed ride costs less and
earns nothing.

Rating is `0..999`, rebuilt on a slow period, not every tick:

```
happinessTerm = avgHappiness * 2 / 5          # 0..400
crowdTerm     = min(guestCount, 200)          # 0..200
rideTerm      = uniqueOpenRides * 25
              + avgExcitement / 20            # modest
cleanTerm     = max(0, 150 - litterTiles * 5)
uptimeTerm    = max(0, 100 - 25 * brokenRides)
lostTerm      = min(lostToday * 2, 150)
rating        = clamp(sum - lostTerm, 0, 999)
```

Spawn rate is rating, weather, and a time-of-day curve (lunch and
evening peaks). The world RNG makes the draws reproducible. Night is a
ledger, not a second simulation: remaining guests flush toward the gate,
mechanics finish inspections, the day counter advances.

## Days, weather, ledger

Weather is a public band sampled each morning: clear, overcast, rain,
storm. Magnitudes behind the band change spawn and a little nausea. The
manager sees the band, not the magnitudes.

The daily ledger is a Heartleaf scorecard, shorter. Five real seconds
regardless of playback speed: guests in, guests lost, profit, top
thoughts, ride income. Pause holds it. The final day shows standings,
then a file replay loops.

## The overlord surface

One VM. The captured `playerId` is `0`. Every command that names an
entity is refused unless the manager owns it. There is no fog. The map
is the park.

Observations are a snapshot taken once per decision, in a canonical
order: own rides, own shops, own staff, then a capped thought window.
Guest bodies are not in the list. Aggregates sit on host data slots.

Host functions take and return scalars. `and` is logical, so every
condition is its own reader, never a bitfield.

The budget is the Light vs Dark shape (`300k` instructions, `400k`
work) with cheaper movement and more expensive track work: `track` and
`finishTrack` price the occupancy walk and the test-car lap. A script
that tries to invent a steel circuit by brute-forcing verbs will blow
the budget. That is the pressure that pushes authors onto `canClose`,
`cursorMiss`, and a planned tape.

### Host data

```
worldTick day dayCount minuteOfDay weather
cash loan rating parkValue guestCount
avgHappiness avgHunger avgThirst avgNausea
litterTiles brokenRides lostToday
obsCount ownRides ownShops ownStaff
gateX gateY mapSize decisionPeriod
researchTopic researchTicks
buildingId          # live turtle, or 0
```

### Snapshot readers

Rides, shops, staff, in identifier order.

```
obsId obsKind obsSub obsX obsY
obsOpen obsQueue obsRiders
obsExcitement obsIntensity obsNausea
obsProfit obsReliability obsPrice
obsFailed
```

`obsKind`: `1` ride, `2` shop, `3` staff. Flat rides and tracked rides
share `1`; `obsSub` is the catalog ordinal.

Thoughts are not snapshot rows. They are counters:

```
thoughtCount(kind) → guests who fired that thought this window
```

### Queries

```
distance(x1, y1, x2, y2)
tileKind(x, y)              # grass, path, queue, water, tree, ride, shop
tilePassable(x, y)          # guest-walkable
reachableFromGate(x, y)
canPlace(kind, x, y, facing)
canClear(x, y)
tileLitter(x, y)
tileTraffic(x, y)           # recent guest steps, capped
rideByIndex(i)              # id, or 0
cursorX cursorY cursorFacing cursorHeight
cursorMiss                  # tiles from a legal finish, or 0 if closable
canClose
canBuild(kind)
buildCost(kind)
trackCost(verb, arg)        # next piece, 0 if illegal
researchTicksLeft
```

`nearestHungry`, `nearestLitter`, `longestQueue` exist so a script does
not scan the park. Ties break on tile index.

### Commands

One accepted command is one replay action. Decide and record before
mutating. Return `1` or `0`.

```
placePath(x, y)
placeQueue(x, y, rideId)
placeLine(x1, y1, x2, y2, queueFlag, rideId)
  # orthogonal only; one action, many tiles; work-priced by length
bulldoze(x, y)
clearLand(x, y)
placeFlat(kind, x, y, facing)
placeScenery(kind, x, y)
beginTrack(kind, x, y, facing)
track(verb, arg)
undoTrack()
clearTrack()
finishTrack()
setPrice(id, price)
setEntranceFee(price)
openId(id)
closeId(id)
hire(kind)
assignZone(staffId, x0, y0, x1, y1)
setResearch(topic)
borrow(amount)
repay(amount)
```

`placeLine` is how a plaza gets paved without burning a day of
decisions. The replay stores the line, not the expanded tiles; the sim
expands it the same way on playback.

## Determinism

`stateHash` is FNV-1a over a canonical walk of everything that can
influence a later tick, computed every tick and stored in the replay.
Every `World` field carries a `# HASH: include` or `# HASH: derived`
comment.

Included but easy to miss: guest path remaining, the track verb tape
(not just the baked nodes), the test-car stats (they change who rides),
staff zone rectangles, research ticks, thought window counters, and the
daily weather magnitudes. Animation ticks on guests and trains are
included so the viewer and a headless build do not drift visually.

Guest spawn, preference rolls, and vomit checks use the world RNG.
`orderFailed` does not exist. The manager's refused commands are not
world state.

Validators follow the Light vs Dark rule: **decide and record before
touching anything.** A `track` that mutates then returns `0` will
reproduce a perfect final park and diverge at the verb that failed.

## Files

```
airtime.nim     entry, branches on -d:headless
content.nim     enums, prices, ride table, thought list, contentHash
maps.nim        integer park, fence, gate, pond, ridge, trees, mapHash
tracks.nim      turtle, occupancy, closable test — no World
rides.nim       test car, operating trains, the three numbers
sim.nim         World, guests, staff, economy, rating, stateHash
bots.nim        BASIC host surface, one VM, observation snapshot
game.nim        CLI, match setup, headless runner, replay wiring
replays.nim     POLYAIR action tape
graphics.nim    spectator: park, ribbon track, trains, guests
decor.nim       fence, lamps, flowers, pond edge; seed-only
ui.nim          cash, rating, thoughts, turtle, daily ledger
controls.nim    human manager: path brush, verb keys, zones
democamera.nim  follow one guest through a ride, Heartleaf shot rules
players/base.bas      reference manager
players/miser.bas     cheap tickets, no staff, one carousel
players/showman.bas   one steel attempt, ignore shops
```

Dependency order is acyclic:

```
content → tracks → rides → replays → maps → sim → bots → controls → game → graphics
```

`tracks` and `rides` do not import `sim`. Tests never import `game.nim`.
Nothing below `game` knows the command line exists.

Replay magic is the game name `airtime`. Actions use `entityId` plus
`first, second, third` the way Light vs Dark does. `placeLine` and
`assignZone` pack the extra integers into those three plus `entityId`
(`rideId` or `staffId`). If a later verb needs a fourth scalar, bump
the replay game version and add a field; do not overload with `div`.

## The scripted manager

`players/base.bas` is a reference, not a good designer.

It paves a plaza out from the gate with `placeLine`, drops a bathroom
and a burger on the edge, plants a carousel with a short queue, hires
one handyman on that rectangle, and researches thrill. When cash
clears a threshold it begins a wooden station on a reserved patch
east of the plaza and emits a **hardcoded golden tape**, the same
sequence the ride test locks. It prices by published intensity, extends
any queue that sits full, and opens a drink stall when thirst thoughts
dominate.

It does not invent track. Inventing track is the research problem.
`miser.bas` never researches and never hires. `showman.bas` skips shops
and tries steel as soon as it unlocks, which on a timid weather roll
is a disaster.

## Demo camera

The spectator starts on the gate. After the first guest enters, it
follows that guest the way Heartleaf follows a villager: interpolated
body, no extra damping, shot clocks in real seconds. A ride in progress
keeps the shot. Three seconds idle allow a handoff after sixty real
seconds; at ninety seconds any activity permits one. The next guest is
the least recently followed outdoor guest, excluding the current
thought-bubble cluster. Clicking a guest or the minimap takes manual
control; `C` resumes.

This is how you watch the game. A park from orbit is a diagram. A guest
from arrival through the wooden drop is the design.

## Human play

A human manager issues the same commands through silky: path brush,
flat palette, track verbs on keys, zone drag, price fields. Needed to
author the golden tape and to debug a bot that cannot close a circuit.
Replay playback is always the action tape, never the live UI.

## Map

`maps.nim` generates the park from one seed.

- Ground layer `128×128`, matching `pathing.GridTiles`
- Fence rectangle roughly `80×64`, gate on the south edge, plaza
  already pathed
- Gentle integer hills, a ridge that makes a bad station site if you
  ignore it, a pond that blocks a naive eastern expansion
- Noise-gated trees inside the fence, a solid forest wall outside
- A flood fill from the gate must reach every plaza tile, or the
  generator retries the seed deterministically

No symmetry. There is one player. The renderer dresses the fence,
gatehouse, and pond from the seed alone in `decor.nim`, so a replay
dresses like the live game and nothing it places has any bearing on
the simulation.

## Graphics notes

Guests reuse an existing kit at about `0.7` world units, tinted per
spawn so a followed guest is identifiable. Flat rides kitbash from
toon props plus a rotating platform. Track is a generated ribbon from
the node list, the old path-ribbon idea, with simple support posts.
The station is a platform module. Thoughts are small world-space icons,
not chat.

Fog of war is unnecessary. The 3D ground does not darken.

## Coworld packaging (later)

Engine truth stays in this folder: integer sim, action tape, BASIC
host, native spectator. A certifiable coworld should wrap this sim the
way the other examples do, not fork the rules.

Suggested later pieces, none of which belong in the first drop:

- One seat, `results.scores = [parkValue]`
- Graders: goal met, min/mean happiness, unique ride count, bankruptcy,
  nausea events, queue refusals, timid-day steel (did you close it?)
- Diagnoser: "can you close the golden wooden tape?", "rain seed —
  did spawn collapse?", "queue overflow — did you extend?", "loan
  maxed — did you stop building?"
- Interest-range: first `finishTrack`, first breakdown, first
  bankruptcy warning, a guest vomiting at the station

A two-gate town that shares one guest pool is a second game. Do not
sneak it into Greenfield.

## Implementation order

1. `content.nim` and `maps.nim` — empty fenced park, gate, plaza,
   screenshot of the grounds.
2. Paths and guests — spawn at the gate, wander reachable path, leave
   at night. No rides. A flood-fill test.
3. Carousel, queue, sit-down ride cycle. One thought: "I want to go
   home."
4. Burger, bathroom, needs, litter. Handyman zone.
5. `tracks.nim` turtle, occupancy, closable. Unit tests only.
6. `rides.nim` test car and the golden wooden bands.
7. `beginTrack` / `track` / `finishTrack` in the sim, operating train,
   guests ride.
8. Rating, loan, research, daily ledger, Greenfield goal.
9. BASIC host, `base.bas`, replay record/verify.
10. Graphics, ribbon track, demo camera, human controls, miser/showman.

## Verification

```bash
nim r tests/test_air_content.nim
nim r tests/test_air_tracks.nim
nim r tests/test_air_rides.nim
nim r tests/test_air_maps.nim
nim r tests/test_air_replays.nim
nim r tests/test_air_sim.nim
```

```bash
nim r examples/airtime/airtime.nim --bot examples/airtime/players/base.bas:1
```

```bash
nim r -d:headless examples/airtime/airtime.nim --seed 1988 \
  --bot examples/airtime/players/base.bas:1 \
  --record examples/airtime/replays/demo.replay
```

```bash
nim r examples/airtime/airtime.nim --replay examples/airtime/replays/demo.replay
```

```bash
SIM_SECONDS=40 CAM_DIST=48 CAM_X=64 CAM_Z=20 \
  SCREENSHOT_PATH=/tmp/airtime.png \
  nim r -d:takeScreenshot examples/airtime/airtime.nim -- \
  --bot examples/airtime/players/base.bas:1
```

Headless record then replay must be bit-exact on `stateHash`. The
golden wooden tape must finish and land in the locked stat bands.
`test_air_sim.nim` sends a timid guest and a thrill guest through that
tape and requires opposite happiness signs. A disconnected carousel
must stay at zero riders.

## Risks

- **Closing a circuit in BASIC is hard.** Host `cursorMiss` / `canClose`,
  and keep the baseline on a hardcoded tape. If authors cannot get a
  legal finish without those queries, the example is a compiler puzzle,
  not a park.
- **Guest pathing on a growing network.** Rebuild the gate flood fill
  on every accepted path edit. Cache paths by (start, dest, generation).
  A full A* from every guest every tick will miss the realtime target
  that Light vs Dark hit at ~130 units.
- **Walkability changes.** Same class of bug Light vs Dark already
  paid for. Guest grid is derived. Terrain `computeWalkable` runs once.
- **Test-car stalls.** Refuse `finishTrack` rather than open a ride
  that strands guests. The golden tape must complete.
- **Integer loops.** A steel loop with a bad radius will explode
  milli-g. Cap curvature per kind and lock a golden steel tape before
  unlocking the verb in content.
- **Ribbon track looking like a snake.** Height variation is the whole
  visual. A flat circuit should look cheap, because it is cheap.
- **Catalog flats stealing the design.** Keep their stats boring. The
  wooden tape is the load-bearing mechanic.

## Known cuts

Land purchase, bridges, underground track, 45-degree rail, transport
rides as actual transit, marketing campaigns, security, custom colours,
multiple trains, water rides, scenery that is not bench/lamp/flower,
and a second competing gate. Several of those are lakes. Two parks
sharing a town is an ocean.
