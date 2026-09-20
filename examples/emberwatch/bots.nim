## The partner sees public state and issues exactly the same commands as a human.
import content, sim

proc decide*(w: World, actor: int, expert = true): seq[Command] =
  if w.terminal or actor notin 0 .. 1: return
  template command(name: string, px = 0, py = 0, val = 0, id = 0) =
    result.add Command(actor: actor, kind: name, x: px, y: py, value: val, target: id)
  var counts: array[5, int]
  var own = 0
  for t in w.towers:
    if t.owner == actor:
      inc counts[t.kind]
      inc own
  var wanted = if actor == 0: 0 else: 1
  if w.orders[actor] < 2: wanted = w.orders[actor]
  elif expert:
    var coverage: array[2, int]
    for t in w.towers:
      if t.kind == 4: continue
      for lane in 0 .. 1:
        for p in route(lane):
          if distanceSq(t.x * Unit, t.y * Unit, p.x * Unit, p.y * Unit) <=
              t.towerRange * t.towerRange:
            coverage[lane] += t.level * 10
    if coverage[0] + 80 < coverage[1]: wanted = 0
    elif coverage[1] + 80 < coverage[0]: wanted = 1
  if expert and w.phase == 1 and w.abilityUntil[actor] <= w.tick:
    var bestCount = 0
    var bestX, bestY: int
    for e in w.enemies:
      var count = 0
      for other in w.enemies:
        if distanceSq(e.x, e.y, other.x, other.y) < 9_000_000:
          count += (if other.kind == 4: 6 else: 1)
      if e.progress > 20_000: count += 3
      if count > bestCount:
        bestCount = count
        bestX = e.x div Unit
        bestY = e.y div Unit
    if bestCount >= 6 and w.energy[actor] >= 60:
      if w.pingUntil[1 - actor] > w.tick:
        bestX = w.pingX[1 - actor]
        bestY = w.pingY[1 - actor]
      command("freeze", bestX, bestY)
      return
  if expert and own >= 4:
    var upgrade = -1
    var best = -1
    for i, t in w.towers:
      if t.owner != actor or t.level >= 3 or w.gold[actor] < t.upgradeCost: continue
      let score = (if t.kind in [2, 3]: 40 else: 0) +
        (if t.level == 1: 30 else: 0) + t.shots div 10
      if score > best:
        best = score
        upgrade = i
    if upgrade >= 0 and (own >= 7 or w.wave mod 3 != 0):
      command("upgrade", val = 1, id = w.towers[upgrade].id)
      return
  var kind = 0
  if expert:
    if own == 0: kind = (if actor == 0: 0 else: 2)
    elif counts[1] == 0: kind = 1
    elif counts[2] == 0: kind = 2
    elif counts[3] == 0: kind = 3
    elif own >= 5 and counts[4] == 0: kind = 4
    else: kind = (if counts[3] < counts[2]: 3 else: 2)
  if w.gold[actor] >= TowerCosts[kind] and w.towers.len < 40:
    var best = -1
    var bx, by: int
    for x in 2 ..< GridWidth - 2:
      for y in 1 ..< GridHeight - 1:
        if not buildable(x, y) or w.occupied(x, y): continue
        var score = 0
        for lane in 0 .. 1:
          for index, p in route(lane):
            if distanceSq(x * Unit, y * Unit, p.x * Unit, p.y * Unit) <=
                TowerRanges[kind] * TowerRanges[kind]:
              score += (if lane == wanted: 12 else: 5) + (if index > 10: 2 else: 0)
        if expert:
          for t in w.towers:
            let d = distanceSq(x, y, t.x, t.y)
            if d <= 5:
              if t.owner != actor: score += 15
              if (kind == 1 and t.kind == 2) or (kind == 2 and t.kind == 1): score += 20
              if kind == 4 and t.kind != 4: score += 50 * t.level
              if kind == t.kind: score -= 20
          if w.pingUntil[1 - actor] > w.tick and
              distanceSq(x, y, w.pingX[1 - actor], w.pingY[1 - actor]) <= 9:
            score += 65
        else:
          # A deliberately limited benchmark: single-type defenses at the entrances.
          score = 50 - abs(x - 3) * 5 - abs(y - (if wanted == 0: 2 else: 12)) * 5
        if score > best:
          best = score
          bx = x
          by = y
    if best >= 0:
      command("build", bx, by, kind)
      return
  if w.phase == 0 and not w.ready[actor] and (own >= 2 or w.tick > TickRate * 12):
    command("ready")
