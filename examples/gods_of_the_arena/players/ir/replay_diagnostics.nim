## Read-only, complete action-tape diagnostics for published GOTA 2026.9.15.3.
## Copy into the pinned checkout before compiling. GOTA_SLOT selects the hero;
## GOTA_FRAME_STEP (default 24, 0 disables) controls schematic viewing samples.
## stdout JSONL: header, frames, final summary. Every replay hash is checked.
import std/[json, strutils, os, math]
import polyworld/[metrics, fixed]
import ../../[game, sim, replays, content, terrains, maps]

if not run.replayMode:
  raise newException(ValueError, "--replay is required")
let slot = getEnv("GOTA_SLOT", "0").parseInt
let frameStep = getEnv("GOTA_FRAME_STEP", "24").parseInt
let frameStart = getEnv("GOTA_FRAME_START", "0").parseInt
let frameEnd = getEnv("GOTA_FRAME_END", "28800").parseInt
if slot notin 0 .. 9:
  raise newException(ValueError, "GOTA_SLOT must be 0..9")
let hero = run.world.heroes[slot]
proc point(p: WorldPoint): JsonNode =
  %*[p.x.float64 / WorldScale.float64 + 58,
     p.z.float64 / WorldScale.float64 + 58]
proc distance(a, b: WorldPoint): float64 =
  let x = (a.x.float64 - b.x.float64) / WorldScale.float64
  let z = (a.z.float64 - b.z.float64) / WorldScale.float64
  sqrt(x*x + z*z)
proc resolve(id: int32): tuple[found: bool, pos: WorldPoint, hp, kind, layer: int32] =
  for h in run.world.heroes:
    if h.id == id: return (h.hp > 0, h.position, h.hp, 2'i32, h.navLayer)
  for f in run.world.footmen:
    if f.id == id: return (f.hp > 0, f.position, f.hp, 3'i32, f.navLayer)
  for t in run.world.towers:
    if t.id == id: return (t.hp > 0, t.position, t.hp, 4'i32, -1'i32)
  for f in run.world.forts:
    if f.id == id: return (f.hp > 0, f.center, f.hp, 1'i32, -1'i32)

var terrain = newJArray()
if frameStep > 0:
  for y in 0 ..< mapTiles():
    var row = ""
    for x in 0 ..< mapTiles():
      row.add(if terrainValue(x.int32, y.int32, 0, TerrainWalkableField) != 0: '.' else: '#')
    terrain.add(%row)
echo $(%*{"type":"header", "slot":slot, "hero_id":hero.id,
  "class": $hero.class, "team":hero.team.ord, "tick_rate":24,
  "frame_step":frameStep, "terrain_layer":0, "terrain":terrain,
  "replay":options.replayPath, "version":"2026.9.15.3"})

var
  idleStart = -1
  idleStartTarget, idleStartHp: int32
  idleStartDamage: int64
  idlePath, idleTower: JsonNode
  idleTicks, longestIdle, aliveTicks, remoteTargetTicks, outOfRangeTicks: int
  lowHpThreatTicks, towerAggroTicks, mobileAggroTicks: int
  deaths = newJArray()
  stalls = newJArray()
  walks = newJArray()
  casts = newJArray()
  hits = newJArray()
  walkStart = -1
  walkStartPosition: WorldPoint
  walkStartHp, walkStartHits, walkThreat: int32
  walkStartDamage: int64
  walkStartDistance: float64
  walkEndDistance: float64
  walkMovedTicks, walkTurnOnlyTicks, walkStillTicks: int
  walkHitAdjacent: bool
  lastHitTick = -100
  lastWalkTick = -100
  startWalkDest: JsonNode
  lastActionKind = 0
  minWalkDistance: float64
  previousPos = hero.position
  previousHp = hero.hp
  previousHits = hero.attacksLanded
  previousDamage = run.world.stats.values[slot][DamageMetric]
  previousDying = false
  recent = newJArray()

proc finishIdle() =
  if idleStart >= 0:
    let n = run.world.tick.int - idleStart
    if n >= 72:
      idleTicks += n
      longestIdle = max(longestIdle, n)
      let target = resolve(hero.attackObjectId)
      stalls.add(%*{"start":idleStart,"end":run.world.tick,"ticks":n,
        "position":point(previousPos),"start_target":idleStartTarget,
        "end_target":hero.attackObjectId,"start_hp":idleStartHp,
        "end_hp":previousHp,"target_distance":(if target.found: distance(previousPos,target.pos) else: -1),
        "target_layer":target.layer,"hero_layer":hero.navLayer,
        "first_waypoint":idlePath,"waypoint_tower_overlap":idleTower,
        "damage_metric_unavailable":true})
    idleStart = -1

proc finishWalk() =
  if walkStart >= 0:
    walks.add(%*{"start":walkStart,"end":run.world.tick,"ticks":run.world.tick.int-walkStart,
      "hit_adjacent":walkHitAdjacent,"start_position":point(walkStartPosition),
      "end_position":point(previousPos),"destination":startWalkDest,
      "displacement":distance(walkStartPosition,previousPos),"threat_id":walkThreat,
      "start_separation":walkStartDistance,
      "end_separation":walkEndDistance,
      "min_separation":minWalkDistance,"start_hp":walkStartHp,"end_hp":previousHp,
      "moved_ticks":walkMovedTicks,"turn_only_ticks":walkTurnOnlyTicks,"stationary_ticks":walkStillTicks,
      "basic_hits":previousHits-walkStartHits})
    walkStart = -1

while run.world.tick < run.replayData.hashes.len and not run.world.gameOver:
  let firstAction = run.replayPlayer.actionIndex
  let prePos = hero.position
  let preHp = hero.hp
  let preHits = hero.attacksLanded
  let preDamage = run.world.stats.values[slot][DamageMetric]
  let preFacing = hero.body.facing
  var preThreat = 0'i32
  var preSeparation = 1.0e9
  for i in 0 ..< run.world.worldObjectCount(hero.id):
    var o: WorldObject
    if run.world.worldObjectAt(hero.id,i,o) and o.hp > 0 and o.team != hero.team and o.kind in [2'i32,3'i32,4'i32]:
      let d = distance(prePos,o.position)
      if d < preSeparation: preSeparation = d; preThreat = o.id
  advanceGame()
  let tick = run.world.tick.int
  let emitFrame = frameStep > 0 and tick mod max(1,frameStep) == 0 and tick >= frameStart and tick <= frameEnd
  let dying = hero.state == Dying or hero.hp <= 0
  let damage = run.world.stats.values[slot][DamageMetric]
  let target = resolve(hero.attackObjectId)
  let targetDistance = if target.found: distance(hero.position,target.pos) else: -1
  var orderedWalk = false
  var walkDest = newJNull()
  for i in firstAction ..< run.replayPlayer.actionIndex:
    let a = run.replayData.actions[i]
    if a.heroId == hero.id and a.kind in [ActionWalkTo, ActionAttackTarget]:
      orderedWalk = a.kind == ActionWalkTo
      lastActionKind = a.kind.int
      if orderedWalk: walkDest = %*[a.first,a.second]
  var
    objects = newJArray()
    attackers = newJArray()
    nearestThreat = 0'i32
    nearestDistance = 1.0e9
    enemyNear, allyNear, towerAggro, mobileAggro = 0
  # Visibility-filtered observations at the post-tick boundary. Policy decisions
  # occur earlier in the tick; exact decisions come from the recorded action tape.
  for i in 0 ..< run.world.worldObjectCount(hero.id):
    var o: WorldObject
    if not run.world.worldObjectAt(hero.id,i,o): continue
    let d = distance(hero.position,o.position)
    if o.hp > 0 and o.id != hero.id:
      if o.team != hero.team and o.kind in [2'i32,3'i32,4'i32]:
        if d < nearestDistance:
          nearestDistance = d; nearestThreat = o.id
        if d <= 6: inc enemyNear
        if o.targetId == hero.id:
          attackers.add(%*{"id":o.id,"kind":o.kind,"distance":d})
          if o.kind == 4: inc towerAggro
          else: inc mobileAggro
      elif o.team == hero.team and o.kind in [2'i32,3'i32] and d <= 6:
        inc allyNear
    if emitFrame:
      objects.add(%*[o.id,o.kind,o.team.ord,point(o.position),o.hp,o.maxHp,o.targetId,o.alive])
  if not dying:
    inc aliveTicks
    if targetDistance > 12: inc remoteTargetTicks
    var attackRange = heroAttackRange(hero.class).float64 / WorldScale.float64
    if target.kind == 4: attackRange = max(attackRange,TowerSiegeRange.float64 / WorldScale.float64)
    # Private sim constant FortRange=255000 in the pinned e127989 source.
    if target.kind == 1: attackRange = 255000.0 / WorldScale.float64
    if targetDistance > attackRange: inc outOfRangeTicks
    if hero.hp * 100 < hero.maxHp * 35 and attackers.len > 0: inc lowHpThreatTicks
    if towerAggro > 0: inc towerAggroTicks
    if mobileAggro > 0: inc mobileAggroTicks
  var activeOffense = false
  for c in run.world.casts:
    if c.heroId == hero.id and c.ability.abilitySpec.kind == Strike and c.ends >= run.world.tick:
      activeOffense = true
  # Published .3 never increments DamageMetric. Exclude ongoing offensive
  # casts instead; this is a conservative inactivity measure, not damage.
  let unproductive = not dying and not previousDying and hero.position == prePos and hero.attacksLanded == preHits and not activeOffense
  if unproductive:
    if idleStart < 0:
      idleStart = tick; idleStartTarget = hero.attackObjectId
      idleStartHp = hero.hp; idleStartDamage = damage
      idlePath = newJNull(); idleTower = newJNull()
      if hero.movePathIndex < hero.movePath.len:
        let wp = hero.movePath[hero.movePathIndex]
        idlePath = point(wp)
        for t in run.world.towers:
          let radius = 0.28 + [0.42,0.55,0.70][t.tier.ord]
          if t.hp > 0 and distance(wp,t.position) < radius:
            idleTower = %*{"id":t.id,"team":t.team.ord,"waypoint_distance":distance(wp,t.position),
              "clearance_required":radius,"hero_distance":distance(hero.position,t.position)}
  else: finishIdle()
  if orderedWalk and not dying:
    if walkStart < 0:
      walkStart = tick; walkStartPosition = prePos; walkStartHp = preHp
      walkStartHits = preHits; walkStartDamage = preDamage
      walkThreat = preThreat; walkStartDistance = preSeparation
      minWalkDistance = preSeparation; startWalkDest = walkDest
      walkHitAdjacent = tick - lastHitTick <= 1
      walkMovedTicks = 0; walkTurnOnlyTicks = 0; walkStillTicks = 0
    let tracked = resolve(walkThreat)
    walkEndDistance = if tracked.found: distance(hero.position,tracked.pos) else: -1
    if tracked.found: minWalkDistance = min(minWalkDistance,walkEndDistance)
    if hero.position != prePos: inc walkMovedTicks
    else:
      inc walkStillTicks
      if hero.body.facing != preFacing: inc walkTurnOnlyTicks
    lastWalkTick = tick
  elif walkStart >= 0: finishWalk()
  if hero.attacksLanded > preHits:
    lastHitTick = tick
    hits.add(%*{"tick":tick,"target":hero.attackObjectId,"kind":target.kind,"hp":hero.hp,"distance":targetDistance})
  for c in run.world.casts:
    if c.heroId == hero.id and c.started == run.world.tick:
      casts.add(%*{"tick":tick,"ability": $c.ability,"kind": $c.ability.abilitySpec.kind,"target":c.targetId,"impact":c.impact})
  let context = %*{"tick":tick,"position":point(hero.position),"hp":hero.hp,"max_hp":hero.maxHp,
    "target":hero.attackObjectId,"target_distance":targetDistance,"attackers":attackers,
    "enemy_near":enemyNear,"ally_near":allyNear,"action":lastActionKind,
    "swing":hero.swingTicks,"hit_count":hero.attacksLanded,"damage":damage}
  if tick mod 12 == 0:
    recent.add(context)
    if recent.len > 12: recent.elems.delete(0)
  if dying and not previousDying:
    deaths.add(%*{"tick":tick,"context":context,"preceding_6_seconds":recent.copy()})
  if emitFrame:
    var path = newJArray()
    for i in hero.movePathIndex ..< hero.movePath.len: path.add(point(hero.movePath[i]))
    echo $(%*{"type":"frame","tick":tick,"hero":context,"objects":objects,
      "path":path,"layer":hero.navLayer,"has_move_target":hero.hasMoveTarget,
      "path_index":hero.movePathIndex,"path_length":hero.movePath.len,
      "xp":hero.totalXp,"mana":hero.mana,"inventory":hero.inventory})
  previousPos = hero.position; previousHp = hero.hp; previousHits = hero.attacksLanded
  previousDamage = damage; previousDying = dying
finishIdle()
finishWalk()
if run.hashCheck.mismatches != 0 or run.replayPlayer.actionIndex != run.replayData.actions.len or run.world.tick != run.replayData.hashes.len:
  raise newException(ValueError,"incomplete or mismatched replay")
echo $(%*{"type":"summary","slot":slot,"class": $hero.class,"ticks":run.world.tick,
  "alive_ticks":aliveTicks,"idle_ticks_in_runs_ge72":idleTicks,"longest_idle_ticks":longestIdle,
  "remote_target_ticks":remoteTargetTicks,"out_of_range_ticks":outOfRangeTicks,
  "low_hp_threat_ticks":lowHpThreatTicks,"tower_aggro_ticks":towerAggroTicks,
  "mobile_aggro_ticks":mobileAggroTicks,"deaths":deaths,"stalls":stalls,"walks":walks,
  "casts":casts,"hits":hits,"xp":hero.totalXp,"damage_metric_available":false,
  "hash_mismatches":run.hashCheck.mismatches,"actions_consumed":run.replayPlayer.actionIndex,
  "state_hash":run.stateHash().toHex(16)})
