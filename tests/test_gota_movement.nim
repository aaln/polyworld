import
  polyworld/[bodies, fixed],
  ../examples/gods_of_the_arena/[locomotion, maps, replays, sim]

proc openGround(pos: FixedVec2): bool = true
proc northWall(pos: FixedVec2): bool = pos.y <= 0.3'fx

const Speed = 0.08'fx

echo "Testing immediate reversals and exact arrival without overshoot"
block:
  var hero = Body(pos: FixedVec2Zero, facing: FixedZero, radius: 0.28'fx)
  doAssert walkAround(hero, fixedVec2(-2'fx, FixedZero), Speed, 0.35'fx,
    [], openGround)
  doAssert hero.pos.x < -0.07'fx, "walking waited for the model to turn"
  let target = fixedVec2(0.33'fx, 0.17'fx)
  for tick in 0 ..< 100:
    discard walkAround(hero, target - hero.pos, Speed, 0.35'fx, [], openGround)
  doAssert length(hero.pos - target) < 0.001'fx
  let arrived = hero.pos
  for tick in 0 ..< 20:
    discard walkAround(hero, target - hero.pos, Speed, 0.35'fx, [], openGround)
  doAssert hero.pos == arrived

echo "Testing heroes walk around a stationary unit without pushing or jittering"
for blockedSide in [false, true]:
  var hero = Body(pos: fixedVec2(-2'fx, FixedZero), radius: 0.28'fx)
  let
    enemy = Body(pos: FixedVec2Zero, radius: 0.28'fx)
    target = fixedVec2(2'fx, FixedZero)
  var maximumDetour = FixedZero
  for tick in 0 ..< 100:
    let before = hero.pos
    discard walkAround(hero, target - hero.pos, Speed, 0.35'fx, [enemy],
      if blockedSide: northWall else: openGround)
    doAssert length(hero.pos - enemy.pos) >= hero.radius + enemy.radius
    doAssert length(hero.pos - before) <= Speed + 0.001'fx
    doAssert hero.pos.x >= before.x - 0.005'fx, "avoidance reversed progress"
    if blockedSide: doAssert northWall(hero.pos)
    maximumDetour = max(maximumDetour, abs(hero.pos.y))
  doAssert maximumDetour > 0.55'fx
  doAssert length(hero.pos - target) < 0.01'fx, $blockedSide

echo "Testing two oncoming units pass instead of blocking each other"
block:
  var
    a = Body(pos: fixedVec2(-2'fx, FixedZero), radius: 0.28'fx)
    b = Body(pos: fixedVec2(2'fx, FixedZero), radius: 0.28'fx)
  for tick in 0 ..< 100:
    discard walkAround(a, fixedVec2(2'fx, FixedZero) - a.pos,
      Speed, 0.35'fx, [b], openGround)
    discard walkAround(b, fixedVec2(-2'fx, FixedZero) - b.pos,
      Speed, 0.35'fx, [a], openGround)
    doAssert length(a.pos - b.pos) >= a.radius + b.radius
  doAssert a.pos.x > 1.9'fx and b.pos.x < -1.9'fx

echo "Testing a group of enemies can be passed without crossing their bodies"
block:
  var hero = Body(pos: fixedVec2(-2'fx, FixedZero), radius: 0.28'fx)
  let
    target = fixedVec2(2'fx, FixedZero)
    enemies = [
      Body(pos: fixedVec2(FixedZero, -0.6'fx), radius: 0.28'fx),
      Body(pos: FixedVec2Zero, radius: 0.28'fx),
      Body(pos: fixedVec2(FixedZero, 0.6'fx), radius: 0.28'fx)
    ]
  for tick in 0 ..< 160:
    discard walkAround(hero, target - hero.pos, Speed, 0.35'fx, enemies, openGround)
    for enemy in enemies:
      doAssert length(hero.pos - enemy.pos) >= hero.radius + enemy.radius
  doAssert length(hero.pos - target) < 0.01'fx

echo "Testing an occupied destination settles without orbiting"
block:
  var hero = Body(pos: fixedVec2(-2'fx, FixedZero), radius: 0.28'fx)
  let enemy = Body(pos: FixedVec2Zero, radius: 0.28'fx)
  for tick in 0 ..< 100:
    discard walkAround(hero, -hero.pos, Speed, 0.35'fx, [enemy], openGround)
  let stopped = hero.pos
  doAssert length(stopped) >= hero.radius + enemy.radius
  for tick in 0 ..< 20:
    doAssert not walkAround(hero, -hero.pos, Speed, 0.35'fx, [enemy], openGround)
    doAssert hero.pos == stopped

proc movementGame(): Game =
  result = newGame(generateMap(2026), 240, 10, false, ReplayData())
  result.world.spawnTimerTicks = 100_000
  result.world.heroTurnTicks = 100_000
  for hero in result.world.heroes:
    hero.manualSpells = true
    hero.state = Dying
    hero.hp = 0
    hero.deathTicks = -100_000
  for tower in result.world.towers.mitems:
    tower.hp = 0
  let hero = result.world.heroes[0]
  hero.state = Marching
  hero.hp = hero.maxHp
  hero.place(hero.spellAimPoint(56, 18))

echo "Testing click redirects start walking and can reverse without a new command delay"
block:
  let
    game = movementGame()
    hero = game.world.heroes[0]
  var point = hero.position
  point.x += 35_000
  hero.place(point)
  doAssert game.world.applyWalkTo(hero.id, 62, 18)
  var movedEast = false
  for tick in 0 ..< 40:
    game.tickWorld(nil)
    if hero.position.x > point.x:
      movedEast = true
  doAssert movedEast
  doAssert mapCoordinate(hero.position.x) >= 56
  let before = hero.position
  doAssert game.world.applyWalkTo(hero.id, 54, 18)
  var movedWest = false
  for tick in 0 ..< 40:
    game.tickWorld(nil)
    if hero.position.x < before.x:
      movedWest = true
  doAssert movedWest, "right-click reversal never started walking west"

echo "Testing live navigation still reaches a clicked tile past other heroes"
block:
  let
    game = movementGame()
    hero = game.world.heroes[0]
    enemy = game.world.heroes[5]
    start = hero.position
  enemy.place(hero.spellAimPoint(58, 18))
  enemy.state = Marching
  enemy.hp = enemy.maxHp
  doAssert game.world.applyWalkTo(hero.id, 60, 18)
  for tick in 0 ..< 120:
    game.tickWorld(nil)
  doAssert mapCoordinate(hero.position.x) == 60
  doAssert abs(hero.position.x - start.x) > WorldScale

echo "Testing corpses and other floors do not block a walk command"
for obstacleKind in [1, 2]:
  let
    game = movementGame()
    hero = game.world.heroes[0]
    enemy = game.world.heroes[5]
  enemy.place(hero.spellAimPoint(58, 18))
  enemy.state = if obstacleKind == 1: Dying else: Marching
  enemy.hp = if obstacleKind == 1: 0 else: enemy.maxHp
  if obstacleKind == 2: enemy.navLayer += 1
  doAssert game.world.applyWalkTo(hero.id, 60, 18)
  for tick in 0 ..< 100:
    game.tickWorld(nil)
  doAssert mapCoordinate(hero.position.x) == 60

echo "GOTA movement tests passed"
