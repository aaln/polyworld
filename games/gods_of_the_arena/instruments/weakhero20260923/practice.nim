## Real-tick positive/negative sustain fixtures on the exact replay60 engine.
import std/[os, json, math]
import bassy
import polyworld/[cli, tapes, pathing]
import ../[bots, content, maps, sim, replays]

let source = getEnv("AUDIT_POLICY")
doAssert source.len > 0
var rows = newJArray()
var maxInstructions, maxWork: int64
var exposeThreat = false

proc step(g: Game) =
  g.tickWorld(proc() =
    if exposeThreat:
      # Danger fixtures isolate a visible threat guard, independent of terrain
      # occlusion. All recovery fixtures and full matches use normal vision.
      g.world.thawObservations()
      for cells in g.world.teamVisible.mitems:
        for cell in cells.mitems: cell = 255
      discard g.world.freezeObservations()
    g.runBotDecisions())
  for vm in g.heroVms:
    if vm != nil:
      doAssert not vm.failed, vm.lastError
      maxInstructions = max(maxInstructions, vm.lastInstructions)
      maxWork = max(maxWork, vm.lastWork)

proc distance(a, b: WorldPoint): float =
  sqrt(float((int64(a.x)-b.x)*(int64(a.x)-b.x) +
    (int64(a.z)-b.z)*(int64(a.z)-b.z))) / WorldScale.float

proc field(g: Game, h: Hero): WorldPoint =
  let home = h.position
  var best = 1e9
  const Unit = WorldScale div PathUnitsPerTile
  for z in 1..<115:
    for x in 1..<115:
      if not navigationOpen(GroundLayer, x, z): continue
      let q = pathPoint(GroundLayer, x, z)
      let at = WorldPoint(x: q.x*Unit, y: q.y*Unit, z: q.z*Unit)
      h.place(at)
      if h.canShop or h.inOwnSpawn: continue
      var safe = true
      for b in g.world.buildings:
        if b.team != h.team and b.kind == TowerBuilding and
          distance(at, b.position) < 16: safe = false
      if not safe: continue
      let score = abs(distance(at, home) - 42)
      if score < best: best = score; result = at
  h.place(home)
  doAssert best < 5

for scenario in ["heal", "mana", "full", "cooldown", "empty", "channel", "unlock", "danger", "shopping", "last_hit", "outside_threat"]:
  for team in Team:
    for class in HeroClass:
      exposeThreat = false
      let g = newGame(generateMap(54), 100000, 10, false,
        ReplayData(), drafting = false)
      g.loadBots([BotGroup(path: source, count: 10)])
      g.recorder = initReplayRecorder(g.currentSetup(10000), defaultConfig())
      g.world.spawnTimerTicks = 100000
      for i, h in g.world.heroes:
        h.gold = 0
        if i != team.ord*5:
          h.hp = 0; h.state = Dying; h.deathTicks = -1000000
          g.heroVms[i] = nil
      let index = team.ord*5
      let h = g.world.heroes[index]
      h.class = class
      h.refreshHeroStats()
      h.hp = h.maxHp; h.mana = h.maxMana
      g.step() # Let the real policy capture its original home.
      h.level = 6
      h.abilityLevels = [1'i32, 1, 1, 1]
      h.inventory = [CrimsonDagger, KnightArmor, BattleAxe,
        RuneCrossbow, NoItem, NoItem]
      h.itemCounts = [1'i32, 1, 1, 1, 0, 0]
      h.refreshHeroStats()
      h.spellsReady = true
      for slot in HeroAbilitySlot:
        h.charges[slot] = heroAbility(h.class, slot).abilitySpec(h.abilityLevels[slot]).charges
        h.cooldowns[slot] = 0
        h.recharges[slot] = 0
      h.hp = h.maxHp*29 div 100; h.mana = h.maxMana
      if scenario == "mana": h.hp = h.maxHp; h.mana = h.maxMana div 5
      if scenario == "full": h.hp = h.maxHp
      if scenario == "cooldown": h.cooldowns = [9999'i32, 9999, 9999, 9999]
      if scenario == "empty": h.charges = [0'i32, 0, 0, 0]; h.recharges = [9999'i32, 9999, 9999, 9999]
      if scenario == "unlock":
        h.level = 2
        h.abilityLevels = [0'i32, 1, 0, 0]
        h.refreshHeroStats()
        h.hp = h.maxHp
      if scenario == "shopping":
        h.inventory[3] = NoItem
        h.itemCounts[3] = 0
        h.gold = 500
      let at = g.field(h)
      h.place(at)
      g.world.footmen.setLen(0)
      if scenario == "channel":
        h.portalEnds = g.world.tick + 72
        h.portalDestination = h.position
      if scenario in ["danger", "last_hit", "outside_threat"]:
        exposeThreat = true
        let enemy = g.world.heroes[(1-team.ord)*5]
        enemy.class = Ranger
        enemy.level = 12
        enemy.refreshHeroStats()
        enemy.hp = enemy.maxHp
        enemy.state = Marching
        let gap = if scenario == "outside_threat": 7 else: 4
        enemy.place(WorldPoint(x: at.x + gap.int32*WorldScale, y: at.y, z: at.z))
        h.hp = h.maxHp*50 div 100
      if scenario == "last_hit":
        g.world.footmen = @[Footman(id: 9500, team: Team(1-team.ord), hp: 1, state: Marching, swingTicks: -1)]
        g.world.footmen[0].place(WorldPoint(x: at.x + WorldScale, y: at.y, z: at.z))
      let hp = h.hp
      let mana = h.mana
      var heals, restores, casts, walkHome, spacing, creepAttacks: int
      let duration = if scenario in ["heal", "mana"]: 180 else: 6
      for tick in 0..<duration:
        let before = g.recorder.data.actions.len
        g.step()
        if scenario notin ["danger", "last_hit", "outside_threat"]:
          doAssert g.heroVms[index].runtime.getGlobal("bestId") == 0, "Unexpected hostile target"
        for event in g.world.events:
          if event.kind == Healing and event.actor.id == h.id and
            event.target.id == h.id and event.cause == AbilityEffect:
            heals += event.amount
          if event.kind == ManaChanged and event.actor.id == h.id and event.amount > 0 and event.cause == AbilityEffect:
            restores += event.amount
          if event.kind == SpellReleased and event.actor.id == h.id:
            inc casts
        for i in before..<g.recorder.data.actions.len:
          let action = g.recorder.data.actions[i]
          if action.kind == ActionAttackTarget and action.first == 9500: inc creepAttacks
          if action.kind == ActionWalkTo:
            let sx = g.heroVms[index].runtime.getGlobal("spawnX").int32
            let sy = g.heroVms[index].runtime.getGlobal("spawnY").int32
            if action.first == sx and action.second == sy: inc walkHome
            else: inc spacing
      rows.add(%*{"scenario": scenario, "team": team.ord, "class": $class,
        "initial_hp": hp, "final_hp": h.hp, "max_hp": h.maxHp,
        "initial_mana": mana, "final_mana": h.mana,
        "self_healing": heals, "mana_restored": restores, "local_moves": spacing, "creep_attack_orders": creepAttacks, "ranks": h.abilityLevels, "accepted_spell_releases": casts,
        "home_walks": walkHome, "retreat": g.heroVms[index].runtime.getGlobal("retreat").int64,
        "xp": h.totalXp, "best_kind": g.heroVms[index].runtime.getGlobal("bestKind").int64,
        "hero_distance": g.heroVms[index].runtime.getGlobal("recallHeroDistance").int64,
        "enemy_power": g.heroVms[index].runtime.getGlobal("enemyPower").int64,
        "friend_power": g.heroVms[index].runtime.getGlobal("friendPower").int64})
echo $(%*{"engine_replay": ReplayGameVersion, "vm_failures": 0, "rows": rows, "max_instructions": maxInstructions, "max_work": maxWork})
