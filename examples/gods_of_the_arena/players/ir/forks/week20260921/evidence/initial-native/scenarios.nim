## Real host fixtures for the policy; copy to pinned engine tools/ before build.
import std/[os, json]
import bassy
import polyworld/[cli, tapes, pathing]
import ../[bots, content, maps, sim, replays]

let policy = getEnv("WEEK_POLICY")
doAssert policy.len > 0
var maximumInstructions, maximumWork: int64
var checks = 0

proc quiet(team: Team, class: HeroClass): Game =
  result = newGame(generateMap(54), 100_000, 10, false,
    ReplayData(), drafting = false)
  result.loadBots([BotGroup(path: policy, count: 10)])
  result.recorder = initReplayRecorder(result.currentSetup(1000), defaultConfig())
  for i, hero in result.world.heroes:
    hero.manualSpells = true
    if i != team.ord * 5:
      hero.hp = 0
      hero.state = Dying
      result.heroVms[i] = nil
  let hero = result.world.heroes[team.ord * 5]
  hero.class = class
  hero.refreshHeroStats()
  hero.hp = hero.maxHp
  hero.mana = hero.maxMana
  for cells in result.world.teamVisible.mitems:
    for cell in cells.mitems: cell = 255

proc decide(game: Game): seq[ReplayAction] =
  game.world.tick += 6
  let before = game.recorder.data.actions.len
  game.runBotDecisions()
  for vm in game.heroVms:
    if vm != nil:
      doAssert not vm.failed, vm.lastError
      maximumInstructions = max(maximumInstructions, vm.lastInstructions)
      maximumWork = max(maximumWork, vm.lastWork)
      doAssert vm.lastInstructions <= 19000
      doAssert vm.lastWork <= 50000
  result = game.recorder.data.actions[before ..< game.recorder.data.actions.len]

proc has(actions: seq[ReplayAction], kind: uint8): bool =
  for a in actions:
    if a.kind == kind: return true

proc middle(): WorldPoint =
  let point = lanePathPoints[1][lanePathPoints[1].len div 2]
  const Unit = WorldScale div PathUnitsPerTile
  WorldPoint(x: point.x * Unit, y: point.y * Unit, z: point.z * Unit)

for team in Team:
  for class in HeroClass:
    let game = quiet(team, class)
    let hero = game.world.heroes[team.ord * 5]
    hero.gold = 1000
    let first = game.decide()
    doAssert first.has(ActionLevelAbility)
    doAssert first.has(ActionBuyItem)
    doAssert hero.abilityLevels[PrimaryAbility] == 1
    doAssert CrimsonDagger in hero.inventory
    doAssert KnightArmor in hero.inventory
    inc checks
    hero.portalEnds = game.world.tick + PortalChannelTicks
    doAssert game.decide().len == 0
    hero.portalEnds = 0
    hero.portalCooldownEnds = game.world.tick + PortalCooldownTicks
    doAssert not game.decide().has(ActionUseItemAt)
    inc checks
    hero.place(middle())
    hero.gold = 2000
    doAssert not hero.canShop()
    doAssert not game.decide().has(ActionBuyItem)
    inc checks
    hero.level = 20
    hero.refreshHeroStats()
    for i in 0 ..< 5: discard game.decide()
    doAssert hero.abilityLevels == [4'i32, 4, 4, 3]
    inc checks
    hero.hp = 0
    hero.state = Dying
    hero.deaths = 1
    hero.deathTicks = 0
    hero.gold = 150
    doAssert not game.decide().has(ActionBuyback)
    hero.deaths = 10
    hero.gold = 2000
    doAssert game.decide().has(ActionBuyback)
    doAssert hero.hp == hero.maxHp
    inc checks

    hero.place(middle())
    game.world.footmen.setLen(0)
    for i in 0 ..< 600:
      game.world.footmen.add(Footman(id: int32(1000+i), team: Team(1-team.ord),
        hp: FootmanHp, position: middle(), state: Marching))
    discard game.decide()
    inc checks

echo $(%*{"passed": true, "checks": checks,
  "max_instructions": maximumInstructions, "max_work": maximumWork,
  "scope": "All ten classes on both colors: real host upgrades, shop, portal guards, death/buyback and 600-creep stress."})
