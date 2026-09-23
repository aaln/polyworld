## Real-tick control legality fixtures; isolated visible combat plus natural-vision recovery.
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

for scenario in ["combat", "lane_heal", "portal", "potion"]:
  for team in Team:
    for class in HeroClass:
      if scenario != "combat" and class != DruidWarden: continue
      for effect in [NoControl, StunControl, SilenceControl, RootControl]:
        exposeThreat = false
        let g = newGame(generateMap(54), 100000, 10, false, ReplayData(), drafting = false)
        g.loadBots([BotGroup(path: source, count: 10)])
        g.recorder = initReplayRecorder(g.currentSetup(10000), defaultConfig())
        g.world.spawnTimerTicks = 100000
        let index = team.ord * 5
        for i, unit in g.world.heroes:
          unit.gold = 0
          if i != index:
            unit.hp = 0; unit.state = Dying; unit.deathTicks = -1000000
            g.heroVms[i] = nil
        let h = g.world.heroes[index]
        h.class = class
        h.refreshHeroStats()
        h.hp = h.maxHp; h.mana = h.maxMana
        g.step() # Capture authentic home before placing the field fixture.
        h.level = 6
        h.abilityLevels = [1'i32, 1, 1, 1]
        h.inventory = [CrimsonDagger, KnightArmor, BattleAxe, RuneCrossbow, NoItem, NoItem]
        h.itemCounts = [1'i32, 1, 1, 1, 0, 0]
        h.refreshHeroStats()
        h.spellsReady = true
        for slot in HeroAbilitySlot:
          h.charges[slot] = heroAbility(h.class, slot).abilitySpec(h.abilityLevels[slot]).charges
          h.cooldowns[slot] = 0; h.recharges[slot] = 0
        h.hp = h.maxHp; h.mana = h.maxMana
        let at = g.field(h)
        h.place(at)
        g.world.footmen.setLen(0)
        let enemy = g.world.heroes[(1-team.ord)*5]
        if scenario == "combat":
          exposeThreat = true
          enemy.hp = 10000; enemy.maxHp = 10000; enemy.state = Marching
          enemy.place(WorldPoint(x: at.x + WorldScale, y: at.y, z: at.z))
          # Inert but valid hostile body isolates own legal actions from retaliation.
          g.world.applyControl(enemy.id, StunControl, 1000)
        if scenario in ["lane_heal", "potion"]: h.hp = h.maxHp * 29 div 100
        if scenario == "potion":
          h.inventory[4] = HealthPotion; h.itemCounts[4] = 2
          h.cooldowns = [9999'i32, 9999, 9999, 9999]
        if scenario == "portal":
          h.portalEnds = g.world.tick + 72
          h.portalDestination = h.position
        g.world.applyControl(h.id, effect, 48)
        let controlEnd = g.world.tick + 48
        var trace, commands = newJArray()
        var castDuring, castAfter, rejectedSilence, attacksDuring, movesDuring,
          itemsDuring, releasedDuring, releasedAfter, healing: int
        let portalAfterControl = h.portalEnds
        for tick in 0..<120:
          let before = g.recorder.data.actions.len
          g.step()
          let held = g.world.tick < controlEnd and effect != NoControl
          for event in g.world.events:
            if event.actor.id == h.id:
              if event.kind == ActionRejected and event.error == ActionSilenced: inc rejectedSilence
              if event.kind == SpellReleased:
                if held: inc releasedDuring
                else: inc releasedAfter
              if event.kind == Healing and event.target.id == h.id: healing += event.amount
          for i in before..<g.recorder.data.actions.len:
            let action = g.recorder.data.actions[i]
            commands.add(%*{"tick": action.tick, "kind": action.kind, "slot": action.slot,
              "first": action.first, "second": action.second,
              "offset_x": int32(action.offset.x), "offset_y": int32(action.offset.y)})
            if action.kind == ActionCastTarget:
              if held: inc castDuring
              else: inc castAfter
            if held:
              if action.kind == ActionAttackTarget: inc attacksDuring
              if action.kind == ActionWalkTo: inc movesDuring
              if action.kind == ActionUseItem: inc itemsDuring
          trace.add(%*{"tick": g.world.tick, "hp": h.hp, "mana": h.mana,
            "xp": h.totalXp, "gold": h.gold, "deaths": h.deaths,
            "position": h.position, "enemy_hp": enemy.hp, "hits": h.attacksLanded,
            "target": h.attackObjectId, "cooldowns": h.cooldowns, "charges": h.charges,
            "inventory": h.inventory, "item_counts": h.itemCounts, "portal_ends": h.portalEnds})
        rows.add(%*{"scenario": scenario, "team": team.ord, "class": $class, "effect": $effect,
          "control_end": controlEnd, "cast_during": castDuring, "cast_after": castAfter,
          "silenced_rejections": rejectedSilence, "attacks_during": attacksDuring,
          "moves_during": movesDuring, "items_during": itemsDuring,
          "released_during": releasedDuring, "released_after": releasedAfter,
          "healing": healing, "portal_after_control": portalAfterControl,
          "trace": trace, "commands": commands})

doAssert maxInstructions <= 19000 and maxWork <= 50000
echo $(%*{"engine_replay": ReplayGameVersion, "vm_failures": 0, "rows": rows,
  "max_instructions": maxInstructions, "max_work": maxWork,
  "scope": "104 status fixtures per source,120 actual ticks each; combat visibility is deliberately exposed, other fixtures use natural vision. Not competitive evidence."})
