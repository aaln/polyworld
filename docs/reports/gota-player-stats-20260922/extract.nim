## Per-hero behaviour stats from a Gods of the Arena replay.
## Adapted from andre_von_auto/games/gods-of-the-arena/tools/gota_stats.nim.
## Usage: extract PATH
## Prints one line per hero: "row <position> key=value key=value ..." so a
## collator can group heroes by the policy that sat in each position.
## Direct stats come from the hero's own orders and its state each tick,
## indirect stats from its purchases, downstream stats from rewards.
import
  std/[os, strformat, strutils, tables, math],
  polyworld/tapes,
  maps, replays, sim, events

const Scale = 60000

type HeroStats = object
  team: int
  class: int
  walks, attackMoves, attackOrders, casts, itemUses, levelUps: int
  orders, duplicates, rejected: int
  rejections: Table[string, int]
  targetHero, targetCreep, targetBuilding, targetGod: int
  aliveTicks, lowHpTicks, halfHpTicks, ownHalfTicks, enemyHalfTicks: int
  nearEnemyTowerTicks, nearOwnGodTicks, nearEnemyGodTicks: int
  hpSum: float
  distance: float
  walksLowHp: int
  goldEarned, goldSpent, buybacks, buybackGold: int
  bought: Table[string, int]
  consumed: int
  xpLastHit, xpShared, xpHeroKill, xpBuilding, xpGod: int
  kills, deaths, assists, buildingKills, towerKills, barracksKills: int
  targetTower, targetBarracks: int
  totalXp, level, goldEnd: int

let
  path = paramStr(1)
  replay = loadReplay(path)
  game = newGame(
    generateMap(replay.config.seed, replay.config.mapPreset),
    replay.config.spawnIntervalTicks,
    0,
    true,
    replay
  )
game.replayPlayer = initReplayPlayer(replay)
game.historyPlayback = true

var stats: Table[int32, HeroStats]
for h in game.world.heroes:
  stats[h.id] = HeroStats(team: h.team.ord, class: h.class.ord)
  stats[h.id].bought = initTable[string, int]()
  stats[h.id].rejections = initTable[string, int]()

proc itemGroup(id: int32): string =
  ## Groups item IDs by purchase purpose.
  case id
  of 1, 2:
    "heal"
  of 3, 22:
    "mana"
  of 21:
    "portal"
  of 4:
    "poison"
  else:
    "gear"

proc isHero(id: int32): bool =
  ## Identifies the ten stable hero entity IDs.
  id >= 100 and id < 110

## Orders are read straight from the replay's action stream.
var lastPos: Table[int32, (float, float)]
## Duplicate orders: an order identical to the hero's previous one (same
## kind, target and arguments) is spam, whether or not it was harmless.
var lastOrder: Table[int32, (uint8, int32, int32, int32, int32, int32)]
for action in replay.actions:
  if not stats.hasKey(action.heroId):
    continue
  inc stats[action.heroId].orders
  let sig = (action.kind, action.slot, action.first, action.second,
             int32(action.offset.x), int32(action.offset.y))
  if lastOrder.getOrDefault(action.heroId) == sig:
    inc stats[action.heroId].duplicates
  lastOrder[action.heroId] = sig
  case action.kind
  of ActionWalkTo:
    inc stats[action.heroId].walks
  of ActionAttackMove:
    inc stats[action.heroId].attackMoves
  of ActionAttackTarget:
    inc stats[action.heroId].attackOrders
    let t = action.first
    if isHero(t):
      inc stats[action.heroId].targetHero
    elif t >= 1000:
      inc stats[action.heroId].targetCreep
    elif t <= 2:
      inc stats[action.heroId].targetGod
    else:
      inc stats[action.heroId].targetBuilding
  of ActionCastTarget, ActionCastPoint:
    inc stats[action.heroId].casts
  of ActionUseItem, ActionUseItemAt:
    inc stats[action.heroId].itemUses
  of ActionLevelAbility:
    inc stats[action.heroId].levelUps
  else:
    discard

## Walk orders issued while low: a retreat proxy, filled in during the tick loop.
var walkTicks: Table[int32, seq[int]]
for action in replay.actions:
  if action.kind == ActionWalkTo and stats.hasKey(action.heroId):
    walkTicks.mgetOrPut(action.heroId, @[]).add int(action.tick)

var
  ownGod: array[2, (int, int)]
  enemyTowers: array[2, seq[(int, int)]]
for f in game.world.forts:
  ownGod[f.team.ord] = (int(f.center.x div Scale), int(f.center.z div Scale))
for b in game.world.buildings:
  if b.kind == TowerBuilding:
    enemyTowers[1 - b.team.ord].add((int(b.position.x div Scale), int(b.position.z div Scale)))

var
  walkIndex: Table[int32, int]
  endTick = 0
  winner = -1
for tick in 0 .. replay.hashes.len:
  if tick > 0:
    game.tickWorld(nil)
    game.hashCheck.requireReplayComplete(uint32(game.world.tick), tick)
  let t = int(game.world.tick)
  endTick = t
  for event in game.world.events:
    case event.kind
    of PortalCompleted, EntityRespawned:
      lastPos.del(event.target.id)
      lastPos.del(event.actor.id)
    of Death:
      if event.target.kind == 2 and stats.hasKey(event.target.id):
        inc stats[event.target.id].deaths
        lastPos.del(event.target.id)
      if isHero(event.actor.id) and stats.hasKey(event.actor.id):
        if event.target.kind == 2:
          inc stats[event.actor.id].kills
        elif event.target.kind >= 4:
          inc stats[event.actor.id].buildingKills
          if event.target.kind == 5:
            inc stats[event.actor.id].barracksKills
          else:
            inc stats[event.actor.id].towerKills
    of Assist:
      if stats.hasKey(event.actor.id):
        inc stats[event.actor.id].assists
    of XpGained:
      if stats.hasKey(event.target.id):
        let a = int(event.amount)
        if event.cause == NearbyKill:
          stats[event.target.id].xpShared += a
        elif event.actor.kind == 2:
          stats[event.target.id].xpHeroKill += a
        elif event.actor.kind == 3:
          stats[event.target.id].xpLastHit += a
        elif event.actor.kind >= 4:
          stats[event.target.id].xpBuilding += a
        elif event.actor.kind == 1:
          stats[event.target.id].xpGod += a
    of GoldGained:
      if stats.hasKey(event.target.id):
        stats[event.target.id].goldEarned += int(event.amount)
    of GoldSpent:
      if stats.hasKey(event.target.id):
        stats[event.target.id].goldSpent += int(-event.amount)
        if event.cause == Buyback:
          inc stats[event.target.id].buybacks
          stats[event.target.id].buybackGold += int(-event.amount)
    of ItemPurchased:
      if stats.hasKey(event.target.id):
        let g = itemGroup(event.detail)
        stats[event.target.id].bought[g] = stats[event.target.id].bought.getOrDefault(g) + 1
    of ItemConsumed:
      if stats.hasKey(event.target.id):
        inc stats[event.target.id].consumed
    of ActionRejected:
      if stats.hasKey(event.actor.id):
        var s = stats[event.actor.id]
        inc s.rejected
        let name = $event.error
        s.rejections[name] = s.rejections.getOrDefault(name) + 1
        ## A rejected order is not a move: take it back out of the
        ## accepted-order counters filled from the action stream.
        case event.action
        of ActionWalkTo:
          dec s.walks
        of ActionAttackMove:
          dec s.attackMoves
        of ActionAttackTarget:
          dec s.attackOrders
          let t = event.first
          if isHero(t):
            dec s.targetHero
          elif t >= 1000:
            dec s.targetCreep
          elif t <= 2:
            dec s.targetGod
          else:
            dec s.targetBuilding
        of ActionCastTarget, ActionCastPoint:
          dec s.casts
        of ActionUseItem, ActionUseItemAt:
          dec s.itemUses
        of ActionLevelAbility:
          dec s.levelUps
        else:
          discard
        stats[event.actor.id] = s
    of MatchEnded:
      winner = int(event.amount)
    else:
      discard
  for hero in game.world.heroes:
    if tick == 0 or hero.hp <= 0:
      continue
    var s = stats[hero.id]
    inc s.aliveTicks
    let hpPct = hero.hp.float / max(1, hero.maxHp).float
    s.hpSum += hpPct
    if hpPct < 0.25:
      inc s.lowHpTicks
    if hpPct < 0.5:
      inc s.halfHpTicks
    let
      x = int(hero.position.x div Scale)
      y = int(hero.position.z div Scale)
      own = ownGod[hero.team.ord]
      enemy = ownGod[1 - hero.team.ord]
      dOwn = (x - own[0]) * (x - own[0]) + (y - own[1]) * (y - own[1])
      dEnemy = (x - enemy[0]) * (x - enemy[0]) + (y - enemy[1]) * (y - enemy[1])
    if dOwn <= dEnemy:
      inc s.ownHalfTicks
    else:
      inc s.enemyHalfTicks
    if dOwn <= 225:
      inc s.nearOwnGodTicks
    if dEnemy <= 400:
      inc s.nearEnemyGodTicks
    for tw in enemyTowers[hero.team.ord]:
      if (x - tw[0]) * (x - tw[0]) + (y - tw[1]) * (y - tw[1]) <= 144:
        inc s.nearEnemyTowerTicks
        break
    let
      fx = hero.position.x.float / Scale.float
      fy = hero.position.z.float / Scale.float
    if lastPos.hasKey(hero.id):
      let (px, py) = lastPos[hero.id]
      s.distance += sqrt((fx - px) * (fx - px) + (fy - py) * (fy - py))
    lastPos[hero.id] = (fx, fy)
    ## Walk orders issued at this tick while below 30% health.
    if walkTicks.hasKey(hero.id):
      var i = walkIndex.getOrDefault(hero.id)
      let ticks = walkTicks[hero.id]
      while i < ticks.len and ticks[i] <= t:
        if ticks[i] == t and hpPct < 0.3:
          inc s.walksLowHp
        inc i
      walkIndex[hero.id] = i
    stats[hero.id] = s

let minutes = endTick.float / 1440.0
for hero in game.world.heroes:
  var s = stats[hero.id]
  s.totalXp = hero.totalXp
  s.class = hero.class.ord
  s.level = hero.level
  s.goldEnd = hero.gold
  let
    score = max(0.0, hero.totalXp.float - 200.0 * minutes)
    alive = max(1, s.aliveTicks).float
    aliveMin = alive / 1440.0
    seat = int(hero.id - 100)
    cpu =
      if seat < replay.metrics.final.len:
        int(replay.metrics.final[seat].cpu)
      else:
        -1
  var line = &"row {seat} team={s.team} class={s.class} minutes={minutes:.6f} won={(if winner == s.team: 1 else: 0)} cpu_pct={cpu}"
  line.add &" walks_pm={s.walks.float / max(0.1, aliveMin):.6f} attackmoves_pm={s.attackMoves.float / max(0.1, aliveMin):.6f} attacks_pm={s.attackOrders.float / max(0.1, aliveMin):.6f} casts_pm={s.casts.float / max(0.1, aliveMin):.6f} itemuses_pm={s.itemUses.float / max(0.1, aliveMin):.6f}"
  line.add &" attack_targets={s.attackOrders} alive_ticks={s.aliveTicks}"
  let targets = max(1, s.attackOrders).float
  line.add &" target_hero={s.targetHero.float / targets:.6f} target_creep={s.targetCreep.float / targets:.6f} target_building={s.targetBuilding.float / targets:.6f} target_god={s.targetGod.float / targets:.6f}"
  line.add &" hp_mean={s.hpSum / alive:.6f} time_below25={s.lowHpTicks.float / alive:.6f} time_below50={s.halfHpTicks.float / alive:.6f} time_enemy_half={s.enemyHalfTicks.float / alive:.6f} time_near_enemy_tower={s.nearEnemyTowerTicks.float / alive:.6f} time_near_own_god={s.nearOwnGodTicks.float / alive:.6f} time_near_enemy_god={s.nearEnemyGodTicks.float / alive:.6f} tiles_pm={s.distance / max(0.1, aliveMin):.6f} lowhp_walks={s.walksLowHp} alive_share={alive / max(1, endTick).float:.6f}"
  line.add &" gold_earned={s.goldEarned} gold_spent={s.goldSpent} gold_end={s.goldEnd} buybacks={s.buybacks} buyback_gold={s.buybackGold} items_consumed={s.consumed} buy_heal={s.bought.getOrDefault(\"heal\")} buy_mana={s.bought.getOrDefault(\"mana\")} buy_portal={s.bought.getOrDefault(\"portal\")} buy_poison={s.bought.getOrDefault(\"poison\")} buy_gear={s.bought.getOrDefault(\"gear\")}"
  let orders = max(1, s.orders).float
  line.add &" orders_pm={s.orders.float / max(0.1, aliveMin):.6f} dup_share={s.duplicates.float / orders:.6f} dup_pm={s.duplicates.float / max(0.1, aliveMin):.6f} rejected_share={s.rejected.float / orders:.6f} rejected_pm={s.rejected.float / max(0.1, aliveMin):.6f}"
  for name, count in s.rejections:
    line.add &" rej_{name}={count}"
  line.add &" xp={s.totalXp} xp_lasthit={s.xpLastHit} xp_shared={s.xpShared} xp_herokill={s.xpHeroKill} xp_building={s.xpBuilding} xp_god={s.xpGod} kills={s.kills} deaths={s.deaths} assists={s.assists} building_kills={s.buildingKills} tower_kills={s.towerKills} barracks_kills={s.barracksKills} level={s.level} score={score:.0f}"
  echo line
