## Isolated real-tick CC opportunity fixtures; source-pinned mechanics, both colors.
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

for scenario in ["hero_ready", "retreat_attacker", "retreat_caster", "held_long", "held_expiring",
    "held_finish", "no_enemy", "silenced", "stunned", "rooted", "heal_reserve",
    "cooldown", "no_mana", "channel", "unlock"]:
  for team in Team:
    for class in [VanguardKnight, Warlock, DruidWarden, Lich]:
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
      h.class = class; h.refreshHeroStats()
      h.hp = h.maxHp; h.mana = h.maxMana
      g.step()
      h.level = 6
      h.abilityLevels = [1'i32, 1, 1, 1]
      h.inventory = [CrimsonDagger, KnightArmor, BattleAxe, RuneCrossbow, NoItem, NoItem]
      h.itemCounts = [1'i32, 1, 1, 1, 0, 0]
      h.refreshHeroStats(); h.spellsReady = true
      for slot in HeroAbilitySlot:
        h.charges[slot] = heroAbility(h.class, slot).abilitySpec(h.abilityLevels[slot]).charges
        h.cooldowns[slot] = 0; h.recharges[slot] = 0
      h.hp = h.maxHp; h.mana = h.maxMana
      let
        slot = if class in [VanguardKnight, DruidWarden]: UltimateAbility else: SecondaryAbility
        ability = heroAbility(class, slot)
        spec = ability.abilitySpec
        at = g.field(h)
      h.place(at)
      g.world.footmen.setLen(0)
      let enemy = g.world.heroes[(1-team.ord)*5]
      if scenario notin ["no_enemy", "unlock"]:
        exposeThreat = true
        enemy.class = Arcanist; enemy.refreshHeroStats()
        enemy.hp = 5000; enemy.maxHp = 5000; enemy.mana = 100
        enemy.state = Marching
        enemy.place(WorldPoint(x: at.x + WorldScale, y: at.y, z: at.z))
        if scenario in ["held_long", "held_expiring", "held_finish"]:
          g.world.applyControl(enemy.id, spec.control, (if scenario == "held_expiring": 6 else: 96))
        if scenario == "held_finish": enemy.hp = spec.damage
      if scenario in ["retreat_attacker", "retreat_caster"]:
        h.hp = h.maxHp * 29 div 100
        enemy.attackObjectId = h.id
        enemy.targetHeroId = h.id
      if scenario == "silenced": g.world.applyControl(h.id, SilenceControl, 96)
      if scenario == "stunned": g.world.applyControl(h.id, StunControl, 96)
      if scenario == "rooted": g.world.applyControl(h.id, RootControl, 96)
      if scenario == "heal_reserve":
        h.hp = h.maxHp * 50 div 100
        h.mana = spec.manaCost
      if scenario == "cooldown": h.cooldowns[slot] = 1000
      if scenario == "no_mana": h.mana = 0
      if scenario == "channel":
        h.portalEnds = g.world.tick + 96; h.portalDestination = at
      if scenario == "unlock":
        h.level = 2; h.abilityLevels = [0'i32, 1, 0, 0]
        h.refreshHeroStats()
      var casts, controls, damage, firstControl, manaAtCast, enemySpellAccepted: int
      enemy.abilityLevels = [1'i32, 1, 1, 1]
      enemy.spellsReady = false
      var orders = newJArray()
      let duration = if scenario == "unlock": 6 else: 48
      for tick in 0..<duration:
        # Keep the hostile body close for a controlled opportunity, but leave our
        # movement and the engine's real spells/attacks/control phases intact.
        if scenario != "retreat_attacker":
          enemy.attackObjectId = 0; enemy.hasMoveTarget = true
        if scenario == "retreat_caster" and g.world.tick == 32:
          if g.world.applyCastTarget(enemy.id, PrimaryAbility.ord.int32, h.id):
            inc enemySpellAccepted
        let before = g.recorder.data.actions.len
        g.step()
        for i in before..<g.recorder.data.actions.len:
          let action = g.recorder.data.actions[i]
          orders.add(%*{"tick": action.tick, "kind": action.kind, "slot": action.slot,
            "first": action.first, "second": action.second})
        for event in g.world.events:
          if event.actor.id == h.id:
            if event.kind == SpellReleased and event.detail == ability.ord:
              inc casts
              if firstControl == 0: firstControl = g.world.tick; manaAtCast = h.mana
            if event.kind in {Stunned, Silenced, Rooted} and event.detail == ability.ord:
              inc controls
            if event.kind == Damage and event.detail == ability.ord and event.cause == AbilityEffect:
              damage += event.amount
      rows.add(%*{"scenario": scenario, "team": team.ord, "class": $class,
        "enemy_spell_accepted": enemySpellAccepted, "control_releases": casts, "control_impacts": controls, "control_damage": damage,
        "first_release": firstControl, "mana_at_first_release": manaAtCast,
        "hp": h.hp, "enemy_hp": enemy.hp, "mana": h.mana,
        "ranks": h.abilityLevels, "orders": orders, "xp": h.totalXp,
        "hits": h.attacksLanded, "deaths": h.deaths})

doAssert maxInstructions <= 19000 and maxWork <= 50000
echo $(%*{"engine_replay": ReplayGameVersion, "vm_failures": 0, "rows": rows,
  "max_instructions": maxInstructions, "max_work": maxWork,
  "scope": "120real-tick opportunity fixtures per source; isolated hostile body and exposed combat visibility. No score claim."})
