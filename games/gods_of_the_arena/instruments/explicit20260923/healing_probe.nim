## Diagnose the unchanged incumbent's explicit healing on replay60.
import std/[os, json, math]
import bassy
import polyworld/[cli, tapes, pathing]
import ../[bots, content, maps, sim, replays]

let source = getEnv("AUDIT_POLICY")
doAssert source.len > 0
var rows = newJArray()
var maxInstructions, maxWork: int64

proc step(g: Game) =
  g.tickWorld(proc() =
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

for team in Team:
  for class in HeroClass:
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
    h.spellsReady = false
    h.hp = h.maxHp*29 div 100; h.mana = h.maxMana
    let at = g.field(h)
    h.place(at)
    g.world.footmen.setLen(0)
    let hp = h.hp
    let mana = h.mana
    var heals, casts, walkHome: int
    for tick in 0..<180:
      let before = g.recorder.data.actions.len
      g.step()
      doAssert g.heroVms[index].runtime.getGlobal("bestId") == 0,
        "No-enemy fixture exposed a selected hostile target"
      for event in g.world.events:
        if event.kind == Healing and event.actor.id == h.id and
          event.target.id == h.id and event.cause == AbilityEffect:
          heals += event.amount
        if event.kind == SpellReleased and event.actor.id == h.id:
          inc casts
      for i in before..<g.recorder.data.actions.len:
        let action = g.recorder.data.actions[i]
        if action.kind == ActionWalkTo:
          let sx = g.heroVms[index].runtime.getGlobal("spawnX").int32
          let sy = g.heroVms[index].runtime.getGlobal("spawnY").int32
          if action.first == sx and action.second == sy: inc walkHome
    rows.add(%*{"team": team.ord, "class": $class,
      "initial_hp": hp, "final_hp": h.hp, "max_hp": h.maxHp,
      "initial_mana": mana, "final_mana": h.mana,
      "self_healing": heals, "accepted_spell_releases": casts,
      "home_walks": walkHome, "retreat": g.heroVms[index].runtime.getGlobal("retreat").int64})

echo $(%*{"engine_replay": ReplayGameVersion, "scene": "No visible enemy;29%HP;full mana;all abilities rank1;four core items;no consumables;180real ticks", "vm_failures": 0, "rows": rows, "max_instructions": maxInstructions, "max_work": maxWork, "scope": "Diagnostic fixtures, not a league score comparison."})
