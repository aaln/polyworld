## Controlled encounter runner using the unmodified release simulation and VM.
## Staged under PINNED_ROOT/tmp/microplay; imports resolve to that release only.
import std/[json, os, strutils]
import polyworld/[basic, cli, pathing]
import ../../examples/gods_of_the_arena/[bots, content, maps, replays, sim]

proc integer(node: JsonNode, key: string, fallback: int): int =
  if node.hasKey(key): node[key].getInt else: fallback

proc optional(runtime: Runtime, key: string): int32 =
  try: runtime.getGlobal(key)
  except BasicError: -1

proc point(x, y: int): WorldPoint =
  let tile = layers[GroundLayer].tiles[y * GridTiles + x]
  result = WorldPoint(x: int32(x - GridTiles div 2) * WorldScale + WorldScale div 2,
                      z: int32(y - GridTiles div 2) * WorldScale + WorldScale div 2)
  for height in tile.tops:
    result.y += height.int32 * WorldScale div 32

proc observe(world: World, hero: Hero): JsonNode =
  result = %*{"selfId": hero.id, "selfClass": hero.class.ord,
    "selfTeam": hero.team.ord, "selfX": mapCoordinate(hero.position.x),
    "selfY": mapCoordinate(hero.position.z), "selfHp": hero.hp,
    "selfMaxHp": hero.maxHp, "selfTarget": hero.attackObjectId,
    "selfAttackRange": heroAttackRange(hero.class),
    "selfAttackDamage": hero.heroAttackDamage,
    "selfAttackCooldown": world.heroAttackCooldown(hero),
    "selfAttacksLanded": hero.attacksLanded, "worldTick": world.tick}
  var objects = newJArray()
  for i in 0 ..< world.worldObjectCount(hero.id):
    var obj: WorldObject
    doAssert world.worldObjectAt(hero.id, i, obj)
    # Target IDs must also be visible to this observer, as in bots.objectProc.
    var target = 0'i32
    if obj.targetId != 0:
      for j in 0 ..< world.worldObjectCount(hero.id):
        var other: WorldObject
        if world.worldObjectAt(hero.id, j, other) and other.id == obj.targetId:
          target = obj.targetId
    objects.add(%*{"id": obj.id, "kind": obj.kind.ord, "team": obj.team.ord,
      "x": mapCoordinate(obj.position.x), "y": mapCoordinate(obj.position.z),
      "hp": obj.hp, "alive": obj.alive, "target": target})
  result["objects"] = objects

let request = parseJson(stdin.readAll())
for fixture in request["cases"]:
  var preset = defaultConfig()
  preset.mapSize = 128
  preset.roadWidth = 62
  let game = newGame(generateMap(int32(fixture["seed"].getInt), preset),
                     100_000, 10, false, ReplayData())
  let world = game.world
  world.spawnTimerTicks = 100_000
  world.heroTurnTicks = 0
  for building in world.buildings.mitems:
    building.hp = 0
  for hero in world.heroes:
    hero.hp = 0
    hero.state = Dying
    hero.deathTicks = -100_000
  loadBots(game, @[BotGroup(path: fixture["policy"].getStr, count: 10)])
  for vm in game.heroVms:
    vm.failed = true
  var active: seq[int]
  var subjects: seq[int]
  for actor in fixture["actors"]:
    let slot = actor["slot"].getInt
    active.add slot
    let hero = world.heroes[slot]
    hero.class = HeroClass(actor["class"].getInt)
    hero.level = int32(actor.integer("level", 1))
    hero.refreshHeroStats()
    hero.hp = int32(actor.integer("hp", int(hero.maxHp)))
    hero.mana = int32(actor.integer("mana", int(hero.maxMana)))
    hero.gold = 0
    hero.state = Marching
    hero.swingTicks = -1
    hero.manualSpells = not fixture["automatic_spells"].getBool
    hero.place(point(actor["x"].getInt, actor["y"].getInt))
    hero.navLayer = GroundLayer
    if actor["controller"].getStr == "subject":
      subjects.add slot
      game.heroVms[slot].failed = false
    elif actor.hasKey("target"):
      discard world.applyAttackTarget(hero.id, world.heroes[actor["target"].getInt].id)
  var hashes = newJArray()
  var previousHp, previousHits, damageTaken, hitCount, deaths: array[10, int]
  var firstDeath, firstHit, lastTarget, switches, maxWork, maxInstructions: array[10, int]
  var alive: array[10, bool]
  for slot in active:
    previousHp[slot] = int(world.heroes[slot].hp)
    alive[slot] = true
  var traces = newJArray()
  for tick in 1 .. fixture["ticks"].getInt:
    game.tickWorld(proc() =
      var observations = newJObject()
      for slot in subjects:
        if world.heroes[slot].state != Dying:
          observations[$slot] = observe(world, world.heroes[slot])
      # Deterministic, legal public API controls for non-subject participants.
      for actor in fixture["actors"]:
        let slot = actor["slot"].getInt
        if actor["controller"].getStr == "fixed" and world.heroes[slot].hp > 0:
          let target = actor["target"].getInt
          if world.heroes[target].hp > 0:
            discard world.applyAttackTarget(world.heroes[slot].id, world.heroes[target].id)
        elif actor["controller"].getStr == "passive":
          # Walking in place suppresses auto-acquisition; acceptance is measured
          # by the same engine. This is a stationary target, not an adversary.
          discard world.applyWalkTo(world.heroes[slot].id,
            int32(actor["x"].getInt), int32(actor["y"].getInt))
      runBotDecisions(game)
      for slot in subjects:
        let vm = game.heroVms[slot]
        if vm.failed:
          raise newException(ValueError, vm.lastError)
        maxWork[slot] = max(maxWork[slot], int(vm.lastWork))
        maxInstructions[slot] = max(maxInstructions[slot], int(vm.lastInstructions))
        if observations.hasKey($slot):
          let hero = world.heroes[slot]
          traces.add(%*{"tick": world.tick, "slot": slot,
            "observation": observations[$slot],
            "decision": {"original": optional(vm.runtime, "mpOriginal"),
              "selected": optional(vm.runtime, "bestId"),
              "refinement": optional(vm.runtime, "mpPick"),
              "ally_intent": optional(vm.runtime, "mpAssist"),
              "motion": optional(vm.runtime, "motionActive")},
            "execution": {"target_after_decision": hero.attackObjectId,
              "moving_after_decision": hero.hasMoveTarget},
            "instructions": vm.lastInstructions, "work": vm.lastWork})
    )
    for slot in active:
      let hero = world.heroes[slot]
      let hp = max(0, int(hero.hp))
      damageTaken[slot] += max(0, previousHp[slot] - hp)
      if hero.attacksLanded > int32(previousHits[slot]):
        hitCount[slot] += int(hero.attacksLanded) - previousHits[slot]
        if firstHit[slot] == 0: firstHit[slot] = tick
      if hero.hp <= 0 and alive[slot]:
        inc deaths[slot]
        if firstDeath[slot] == 0: firstDeath[slot] = tick
        alive[slot] = false
      if hero.attackObjectId != 0:
        if lastTarget[slot] != 0 and lastTarget[slot] != int(hero.attackObjectId):
          inc switches[slot]
        lastTarget[slot] = int(hero.attackObjectId)
      previousHp[slot] = hp
      previousHits[slot] = int(hero.attacksLanded)
    hashes.add(%($game.stateHash()))
  var metrics = newJArray()
  for slot in active:
    metrics.add(%*{"slot": slot, "class": world.heroes[slot].class.ord,
      "team": world.heroes[slot].team.ord, "subject": slot in subjects,
      "damage_taken": damageTaken[slot], "basic_hits": hitCount[slot],
      "deaths": deaths[slot], "first_death": firstDeath[slot],
      "first_hit": firstHit[slot], "hp_remaining": max(0, world.heroes[slot].hp),
      "target_switches": switches[slot], "max_work": maxWork[slot],
      "max_instructions": maxInstructions[slot]})
  echo $(%*{"id": fixture["id"], "metrics": metrics, "state_hashes": hashes,
    "decisions": traces, "ticks": world.tick, "vm_valid": true})
