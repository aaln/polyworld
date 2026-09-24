## Real host observation/decision fixtures; no fabricated BASIC host return values.
import std/[os, json]
import bassy
import polyworld/[cli, tapes, pathing]
import ../[bots, content, maps, sim, replays]

let source = getEnv("AUDIT_POLICY")
let candidate = getEnv("AUDIT_CANDIDATE") == "1"
var rows = newJArray()
var maxInstructions, maxWork: int64

proc decide(g: Game) =
  g.runBotDecisions()
  for vm in g.heroVms:
    if vm != nil:
      doAssert not vm.failed, vm.lastError
      maxInstructions = max(maxInstructions, vm.lastInstructions)
      maxWork = max(maxWork, vm.lastWork)

proc placeTile(h: Hero, x, y: int32) =
  h.position = WorldPoint(x: (x - mapTiles().int32 div 2) * WorldScale + WorldScale div 2,
                    y: h.position.y,
                    z: (y - mapTiles().int32 div 2) * WorldScale + WorldScale div 2)
  h.navLayer = GroundLayer

for scenario in ["crowded", "near_home_unknown", "balanced", "low_hp", "enemy_close",
    "early", "expired", "already_chosen", "respawn", "blue_override"]:
  for team in Team:
    for initial in 0..2:
      let g = newGame(generateMap(54), 100000, 10, false, ReplayData(), drafting = false)
      g.loadBots([BotGroup(path: source, count: 10)])
      g.recorder = initReplayRecorder(g.currentSetup(10000), defaultConfig())
      let index = team.ord * 5
      for i, h in g.world.heroes:
        h.gold = 0
        if i != index:
          h.hp = 0; h.state = Dying
          g.heroVms[i] = nil
      let h = g.world.heroes[index]
      h.class = Ranger; h.refreshHeroStats(); h.hp = h.maxHp; h.mana = h.maxMana
      g.tickWorld(proc() = g.runBotDecisions())
      let vm = g.heroVms[index]
      vm.runtime.setGlobal("lane", initial.int32)
      vm.runtime.setGlobal("ordinal", 1'i32)
      let current = if scenario == "blue_override" and team == BlueTeam: 1 else: initial
      if scenario == "blue_override": vm.runtime.setGlobal("ordinal", 0'i32)
      let hx = vm.runtime.getGlobal("homeX")
      let hy = vm.runtime.getGlobal("homeY")
      for a in 1..3:
        let ally = g.world.heroes[index + a]
        ally.hp = ally.maxHp; ally.state = Marching
        let lane = if scenario == "balanced": a-1 else: current
        let ax = (if lane == 0: 11 elif lane == 2: 104 else: 58).int32
        let ay = ax
        let divisor = if scenario == "near_home_unknown": 30'i32 else: 3'i32
        ally.placeTile(hx + (ax-hx) div divisor, hy + (ay-hy) div divisor)
      if scenario == "low_hp": h.hp = h.maxHp div 4
      if scenario == "enemy_close":
        let enemy = g.world.heroes[(1-team.ord)*5]
        enemy.hp = enemy.maxHp; enemy.state = Marching
        enemy.placeTile(mapCoordinate(h.position.x, team)+1, mapCoordinate(h.position.z, team))
        g.world.rebuildVision()
      if candidate and scenario in ["already_chosen", "respawn"]:
        vm.runtime.setGlobal("laneAssigned", 1'i32)
        vm.runtime.setGlobal("laneChanged", 1'i32)
        vm.runtime.setGlobal("laneStored", initial.int32)
        if scenario == "respawn": vm.runtime.setGlobal("initialized", 0'i32)
      g.world.tick = (if scenario == "early": 120 elif scenario == "expired": 900 else: 300)
      g.decide()
      let selected = vm.runtime.getGlobal("lane")
      let changed = if candidate: vm.runtime.getGlobal("laneChanged") else: 0
      if candidate:
        if scenario in ["crowded", "blue_override"]:
          doAssert changed == 1 and selected != current, scenario & " " & $team & " " & $initial
          doAssert vm.runtime.getGlobal("laneKnown") == 3
          doAssert vm.runtime.getGlobal("crossed") == 0
          doAssert vm.runtime.getGlobal("forwardScore") == 1000000
        elif scenario in ["already_chosen", "respawn"]:
          doAssert selected == initial and changed == 1
        else:
          doAssert changed == 0 and selected == initial, scenario & " " & $team & " " & $initial
        # Reversing all observed commitments must not trigger a second switch.
        if changed == 1:
          for a in 1..3:
            let ally = g.world.heroes[index+a]
            let ax = (if selected == 0: 11 elif selected == 2: 104 else: 58).int32
            ally.placeTile(hx+(ax-hx) div 3, hy+(ax-hy) div 3)
          g.world.tick = 324
          g.decide()
          doAssert vm.runtime.getGlobal("lane") == selected
      rows.add(%*{"scenario": scenario, "team": team.ord, "initial": initial,
        "current_effective": current, "selected": selected, "changed": changed})

doAssert maxInstructions <= 19000 and maxWork <= 50000
echo $(%*{"passed": true, "rows": rows, "max_instructions": maxInstructions,
  "max_work": maxWork, "scope": "60isolated actual host decision fixtures per source; allied positions manipulated to create commitment contexts. Not gameplay efficacy evidence."})
