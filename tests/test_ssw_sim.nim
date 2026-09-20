## Seesaw simulation: determinism, board physics, and pair scoring.

import
  std/strformat,
  ../examples/seesaw/content,
  ../examples/seesaw/maps,
  ../examples/seesaw/sim

let gameMap = generateMap(DefaultSeed)
gameMap.validateMap()

proc leftPumps(w: World) =
  discard w.applyLean(0, 2)
  discard w.applyPump(0, 1)
  discard w.applyRest(1)

echo "Testing determinism: two identical games, one hash stream"
block twinWorlds:
  let
    first = newWorld(gameMap, 240)
    second = newWorld(gameMap, 240)
  while not first.over:
    first.tickWorld(leftPumps)
    second.tickWorld(leftPumps)
    if first.tick mod 40 == 0:
      doAssert first.stateHash() == second.stateHash(),
        &"twin worlds diverged at tick {first.tick}"
  doAssert second.over
  doAssert first.stateHash() == second.stateHash()
  doAssert first.scores[0] == first.scores[1],
    "both seats must receive the same pair score"

echo "Testing a one-sided lean drops that seat"
block leftGoesDown:
  var w = newWorld(gameMap, 200)
  w.windForce = 0
  while w.tick < 96:
    w.tickWorld(leftPumps)
  doAssert w.angleMilli > 40,
    &"expected the west seat to drop, angle was {w.angleMilli}"
  doAssert not w.riders[1].seated,
    "rest should take the east rider off the board"
  doAssert w.riders[0].seated
  doAssert w.riders[1].riderWeight(w.omegaMilli, 0) == 0

echo "Testing a rider can walk back onto the board"
block remount:
  var w = newWorld(gameMap, 400)
  proc getOff(world: World) =
    discard world.applyRest(0)
    discard world.applyRest(1)
  while w.tick < 40:
    w.tickWorld(getOff)
  doAssert not w.riders[0].seated
  proc hopOn(world: World) =
    discard world.applyLean(0, 1)
    discard world.applyRest(1)
  var seatedAgain = false
  while w.tick < 280:
    w.tickWorld(hopOn)
    if w.riders[0].seated:
      seatedAgain = true
      break
  doAssert seatedAgain, "leaning while off the board should walk back to the seat"
  doAssert w.riders[0].lean == 1

echo "Testing clone and restore"
block cloneRestore:
  let live = newWorld(gameMap, 120)
  while live.tick < 32:
    live.tickWorld(leftPumps)
  let snap = live.clone()
  while live.tick < 80:
    live.tickWorld(leftPumps)
  doAssert live.stateHash() != snap.stateHash()
  live.restore(snap)
  doAssert live.stateHash() == snap.stateHash()

echo "Testing command validation"
block commands:
  var w = newWorld(gameMap, 80)
  doAssert not w.applyLean(2, 1), "a third rider was accepted"
  doAssert not w.applyExpress(0, 99), "an unknown face was accepted"
  doAssert w.applyLean(0, 2)
  doAssert w.riders[0].lean == 2
  doAssert w.applyExpress(1, int32(FaceSmile.ord))
  doAssert w.riders[1].expression == int32(FaceSmile.ord)

echo "Testing felt fun never goes negative"
block funFloor:
  var w = newWorld(gameMap, 40)
  w.riders[0].rawFun = 10
  w.riders[0].sickEvents = 3
  w.riders[0].nausea = 800
  doAssert w.riders[0].feltFun == 0

echo "test_ssw_sim: all checks passed"
