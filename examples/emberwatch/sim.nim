## Integer-only authoritative simulation, compiled unchanged for native and JS.
import std/[json, sequtils]
import content

type
  Tower* = object
    id*, owner*, kind*, x*, y*, level*, branch*, priority*, spent*: int
    cooldown*, shots*, target*, boostUntil*: int
  Enemy* = object
    id*, kind*, lane*, progress*, x*, y*, hp*, maxHp*: int
    slowUntil*, freezeUntil*, hitUntil*: int
  Effect* = object
    kind*, x*, y*, tx*, ty*, until*, owner*: int
  Command* = object
    actor*: int
    kind*: string
    x*, y*, value*, target*: int
  World* = object
    version*, seed*, difficulty*, tick*, wave*, phase*, core*, kills*: int
    nextId*, spawned*, spawnIn*, planningLeft*, waveLeaks*, bonus*, score*: int
    gold*, energy*, abilityUntil*, orders*, pingX*, pingY*, pingUntil*: array[2, int]
    ready*: array[2, bool]
    towers*: seq[Tower]
    enemies*: seq[Enemy]
    effects*: seq[Effect]

proc newWorld*(seed = 2026, difficulty = 1): World =
  result.version = GameVersion
  result.seed = clamp(seed, 0, 1_000_000)
  result.difficulty = clamp(difficulty, 0, 2)
  result.core = 30
  result.gold = [240, 240]
  result.energy = [100, 100]
  result.orders = [2, 2]
  result.nextId = 1
  result.planningLeft = TickRate * 30

proc terminal*(w: World): bool = w.phase >= 2

proc towerIndex*(w: World, id: int): int =
  for i, t in w.towers:
    if t.id == id: return i
  -1

proc occupied*(w: World, x, y: int): bool =
  for t in w.towers:
    if t.x == x and t.y == y: return true

proc upgradeCost*(t: Tower): int =
  if t.level >= 3: return 0
  TowerCosts[t.kind] * (if t.level == 1: 3 else: 5) div 4

proc towerRange*(t: Tower): int =
  TowerRanges[t.kind] + (t.level - 1) * 150 + (if t.branch == 2: 1200 else: 0)

proc linked*(w: World, t: Tower): bool =
  for other in w.towers:
    if other.owner != t.owner and
        distanceSq(t.x, t.y, other.x, other.y) <= 5: return true

proc supported*(w: World, t: Tower): bool =
  for other in w.towers:
    if other.kind == 4 and other.id != t.id and
        distanceSq(t.x * Unit, t.y * Unit, other.x * Unit, other.y * Unit) <=
          other.towerRange * other.towerRange: return true

proc effect(w: var World, kind, x, y, tx, ty, duration, owner: int) =
  if w.effects.len < 200:
    w.effects.add Effect(kind: kind, x: x, y: y, tx: tx, ty: ty,
      until: w.tick + duration, owner: owner)

proc startWave(w: var World) =
  inc w.wave
  w.phase = 1
  w.spawned = 0
  w.spawnIn = 0
  w.waveLeaks = 0
  w.ready = [false, false]
  if w.wave > 1:
    let reward = w.planningLeft div (TickRate * 3)
    w.bonus += reward * 2
    for seat in 0 .. 1: w.gold[seat] += reward

proc apply*(w: var World, c: Command): string =
  ## Empty string means accepted. Rejections leave the entire world unchanged.
  if c.actor < 0 or c.actor > 1: return "Unknown defender."
  if w.terminal: return "This expedition has ended."
  let a = c.actor
  case c.kind
  of "build":
    if c.value < 0 or c.value >= TowerNames.len: return "Unknown tower."
    if not buildable(c.x, c.y): return "Build on the grass beside a path."
    if w.occupied(c.x, c.y): return "That tile already has a tower."
    if w.towers.len >= 40: return "The island supports 40 towers."
    if w.gold[a] < TowerCosts[c.value]: return "Not enough embers."
    w.gold[a] -= TowerCosts[c.value]
    w.towers.add Tower(id: w.nextId, owner: a, kind: c.value, x: c.x,
      y: c.y, level: 1, spent: TowerCosts[c.value], target: -1)
    inc w.nextId
    w.effect(5, c.x * Unit, c.y * Unit, 0, 0, 18, a)
  of "upgrade", "sell", "priority":
    let i = w.towerIndex(c.target)
    if i < 0: return "Select an existing tower."
    if w.towers[i].owner != a: return "Only its owner can change this tower."
    if c.kind == "upgrade":
      if w.towers[i].level >= 3: return "This tower is fully upgraded."
      if w.towers[i].level == 2 and c.value notin 1 .. 2:
        return "Choose power or reach for the final upgrade."
      let cost = w.towers[i].upgradeCost
      if w.gold[a] < cost: return "Not enough embers."
      w.gold[a] -= cost
      w.towers[i].spent += cost
      inc w.towers[i].level
      if w.towers[i].level == 3: w.towers[i].branch = c.value
    elif c.kind == "sell":
      w.gold[a] += w.towers[i].spent * 3 div 4
      w.towers.delete(i)
    else:
      if c.value notin 0 .. 2: return "Unknown targeting priority."
      w.towers[i].priority = c.value
  of "ready":
    if w.phase != 0: return "A wave is already underway."
    if w.ready[a]: return "You are already ready."
    w.ready[a] = true
    if w.ready[0] and w.ready[1]: w.startWave()
  of "gift":
    if w.gold[a] < 50: return "You need 50 embers to share."
    w.gold[a] -= 50
    w.gold[1 - a] += 50
  of "order":
    if c.value notin 0 .. 2: return "Choose north, south, or adapt."
    w.orders[1 - a] = c.value
  of "ping":
    if c.x notin 0 ..< GridWidth or c.y notin 0 ..< GridHeight:
      return "Ping a tile on the island."
    w.pingX[a] = c.x
    w.pingY[a] = c.y
    w.pingUntil[a] = w.tick + TickRate * 12
  of "overdrive", "freeze":
    if c.x notin 0 ..< GridWidth or c.y notin 0 ..< GridHeight:
      return "Aim on the island."
    if w.phase != 1: return "Abilities become available during a wave."
    if w.abilityUntil[a] > w.tick: return "Your ability is recharging."
    let cost = if c.kind == "overdrive": 45 else: 60
    if w.energy[a] < cost: return "Not enough energy."
    w.energy[a] -= cost
    w.abilityUntil[a] = w.tick + TickRate * 8
    let x = c.x * Unit
    let y = c.y * Unit
    if c.kind == "overdrive":
      for t in w.towers.mitems:
        if distanceSq(x, y, t.x * Unit, t.y * Unit) <= 9_000_000:
          t.boostUntil = w.tick + TickRate * 5
      w.effect(6, x, y, 0, 0, TickRate * 5, a)
    else:
      for e in w.enemies.mitems:
        if distanceSq(x, y, e.x, e.y) <= 9_000_000:
          e.freezeUntil = w.tick + TickRate * 2
          e.slowUntil = w.tick + TickRate * 5
      w.effect(7, x, y, 0, 0, TickRate * 2, a)
  else: return "Unknown command."
  ""

proc position*(e: var Enemy) =
  let path = route(e.lane)
  let i = min(e.progress div Unit, path.high)
  let j = min(i + 1, path.high)
  let part = e.progress mod Unit
  e.x = path[i].x * Unit + (path[j].x - path[i].x) * part
  e.y = path[i].y * Unit + (path[j].y - path[i].y) * part

proc spawn(w: var World, lane, index: int) =
  let kind = waveKind(w.wave, index)
  # Seed changes timing and lane health slightly, without hiding the roster.
  let variation = (w.seed * 13 + index * 7 + lane * 11) mod 17 - 8
  let scaling = (75 + w.wave * 19 + w.wave * w.wave * 2 + variation) *
    [78, 100, 135][w.difficulty] div 100
  let hp = EnemyHealth[kind] * scaling div 100
  var e = Enemy(id: w.nextId, lane: lane, kind: kind, hp: hp, maxHp: hp)
  e.position()
  inc w.nextId
  w.enemies.add e

proc damage(w: var World, index, amount, towerKind: int) =
  if w.enemies[index].hp <= 0: return
  var dealt = amount
  if w.enemies[index].kind == 2 and towerKind in [0, 2]:
    dealt = dealt * 45 div 100
  if towerKind == 2 and w.enemies[index].slowUntil > w.tick:
    dealt = dealt * 180 div 100
  w.enemies[index].hp -= max(1, dealt)
  w.enemies[index].hitUntil = w.tick + 4
  if w.enemies[index].hp <= 0:
    inc w.kills
    let bounty = EnemyBounty[w.enemies[index].kind]
    for a in 0 .. 1: w.gold[a] += bounty
    w.effect(8, w.enemies[index].x, w.enemies[index].y, 0, 0, 10, 0)

proc fire(w: var World, i: int) =
  let t = w.towers[i]
  if t.kind == 4: return
  let range = t.towerRange
  var best = -1
  var bestValue = -1
  for j, e in w.enemies:
    if e.hp <= 0 or distanceSq(e.x, e.y, t.x * Unit, t.y * Unit) > range * range:
      continue
    let value = case t.priority
      of 1: e.hp
      of 2: EnemySpeed[e.kind] * 1000 + e.progress div 1000
      else: e.progress
    if value > bestValue:
      bestValue = value
      best = j
  if best < 0: return
  let target = w.enemies[best]
  var power = TowerDamage[t.kind] * (100 + (t.level - 1) * 65 +
    (if t.branch == 1: 70 else: 0)) div 100
  if w.linked(t): power = power * 115 div 100
  if w.supported(t): power = power * 135 div 100
  w.towers[i].cooldown = TowerPeriods[t.kind]
  w.towers[i].target = target.id
  inc w.towers[i].shots
  w.effect(t.kind, t.x * Unit, t.y * Unit, target.x, target.y, 7, t.owner)
  case t.kind
  of 1:
    w.damage(best, power, t.kind)
    w.enemies[best].slowUntil = w.tick + TickRate * (2 + t.level)
  of 2:
    w.damage(best, power, t.kind)
    var hits = 1
    for j, e in w.enemies:
      if j != best and e.hp > 0 and hits < 3 + (if t.branch == 1: 2 else: 0) and
          distanceSq(e.x, e.y, target.x, target.y) <= 4_000_000:
        w.effect(2, target.x, target.y, e.x, e.y, 7, t.owner)
        w.damage(j, power * 3 div 4, t.kind)
        inc hits
  of 3:
    let radius = if t.branch == 1: 2200 else: 1600
    for j in 0 ..< w.enemies.len:
      if distanceSq(w.enemies[j].x, w.enemies[j].y, target.x, target.y) <= radius * radius:
        w.damage(j, power, t.kind)
  else: w.damage(best, power, t.kind)

proc step*(w: var World) =
  if w.terminal: return
  inc w.tick
  w.effects.keepItIf(it.until > w.tick)
  if w.tick mod 12 == 0:
    for a in 0 .. 1: w.energy[a] = min(100, w.energy[a] + 1)
  if w.tick >= MaxTicks:
    w.phase = 3
  elif w.phase == 0:
    if w.wave > 0:
      dec w.planningLeft
      if w.planningLeft <= 0: w.startWave()
  else:
    dec w.spawnIn
    if w.spawned < waveSize(w.wave) and w.spawnIn <= 0:
      for lane in 0 .. 1: w.spawn(lane, w.spawned)
      inc w.spawned
      w.spawnIn = max(10, 32 - w.wave) + (w.seed + w.spawned * 7) mod 6
    for e in w.enemies.mitems:
      if e.hp <= 0: continue
      if e.freezeUntil <= w.tick:
        var speed = EnemySpeed[e.kind]
        if e.slowUntil > w.tick: speed = speed * 55 div 100
        e.progress += speed
        e.position()
      if e.progress >= (route(e.lane).len - 1) * Unit:
        w.core = max(0, w.core - EnemyLeaks[e.kind])
        w.waveLeaks += EnemyLeaks[e.kind]
        e.hp = 0
    # Menders heal live allies only. Stable iteration and capped health.
    if w.tick mod TickRate == 0:
      for healer in w.enemies:
        if healer.hp <= 0 or healer.kind != 3 or healer.freezeUntil > w.tick: continue
        for e in w.enemies.mitems:
          if e.hp > 0 and e.id != healer.id and
              distanceSq(e.x, e.y, healer.x, healer.y) <= 4_000_000:
            e.hp = min(e.maxHp, e.hp + e.maxHp div 16)
    for i in 0 ..< w.towers.len:
      w.towers[i].cooldown -= (if w.towers[i].boostUntil > w.tick: 2 else: 1)
      if w.towers[i].cooldown <= 0: w.fire(i)
    w.enemies.keepItIf(it.hp > 0)
    if w.core <= 0: w.phase = 3
    elif w.enemies.len == 0 and w.spawned >= waveSize(w.wave):
      if w.wave >= WaveCount: w.phase = 2
      else:
        w.phase = 0
        w.planningLeft = TickRate * 30
        for a in 0 .. 1:
          w.gold[a] += 25 + w.wave * 3 + (if w.waveLeaks == 0: 15 else: 0)
  w.score = w.wave * 1000 + w.kills * 10 + w.core * 100 + w.bonus * 5

proc stateHash*(w: World): int =
  ## Portable polynomial checksum: products stay below 2^53 on JS and native.
  var h = 5381'i64
  for c in $(%w): h = (h * 33 + ord(c)) mod 2_147_483_647
  int(h)

proc observation*(w: World): JsonNode =
  result = %w
  result["nextRoster"] = %waveRoster(min(WaveCount, w.wave + (if w.phase == 0: 1 else: 0)))
  result["paths"] = %*[route(0), route(1)]
  result["towerInfo"] = newJArray()
  for kind in 0 ..< TowerNames.len:
    result["towerInfo"].add %*{"name": TowerNames[kind], "cost": TowerCosts[kind],
      "damage": TowerDamage[kind], "period": TowerPeriods[kind], "range": TowerRanges[kind]}

proc parseCommand*(n: JsonNode): Command =
  if n.kind != JObject or not n.hasKey("kind") or n["kind"].kind != JString:
    raise newException(ValueError, "Expected a command object with a kind string.")
  result.kind = n["kind"].getStr
  result.actor = -1
  for key, value in n:
    if key == "kind": continue
    if key notin ["actor", "x", "y", "value", "target"]:
      raise newException(ValueError, "Unknown command field: " & key)
    if value.kind != JInt or value.getBiggestInt < -1_000_000 or value.getBiggestInt > 1_000_000:
      raise newException(ValueError, "Command fields must be bounded integers.")
    case key
    of "actor": result.actor = value.getInt
    of "x": result.x = value.getInt
    of "y": result.y = value.getInt
    of "value": result.value = value.getInt
    of "target": result.target = value.getInt
    else: discard
