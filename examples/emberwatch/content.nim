## Authoritative tuning. Coordinates use 1,000 integer units per tile.
const
  GameVersion* = 1
  TickRate* = 24
  GridWidth* = 19
  GridHeight* = 15
  Unit* = 1000
  WaveCount* = 12
  MaxTicks* = TickRate * 900
  TowerNames* = ["Bolt", "Frost", "Arc", "Mortar", "Beacon"]
  TowerCosts* = [70, 85, 105, 120, 90]
  TowerDamage* = [19, 6, 17, 58, 0]
  TowerPeriods* = [13, 23, 21, 52, 24]
  TowerRanges* = [3100, 2700, 2900, 3900, 2500]
  EnemyNames* = ["Cinderling", "Runner", "Ironclad", "Mender", "Colossus"]
  EnemyHealth* = [65, 47, 240, 135, 1800]
  EnemySpeed* = [61, 110, 39, 52, 30]
  EnemyBounty* = [7, 8, 18, 16, 100]
  EnemyLeaks* = [1, 1, 3, 2, 10]
  WaveNames* = ["First embers", "Quick feet", "A gathering storm",
    "Iron procession", "The healing choir", "Convergence",
    "Running wild", "Heavy weather", "Ash and iron",
    "The long night", "One last stand", "The extinguishers"]

type Point* = object
  x*, y*: int

const Waypoints*: array[2, array[8, Point]] = [
  [Point(x: 0, y: 3), Point(x: 5, y: 3), Point(x: 5, y: 6),
   Point(x: 9, y: 6), Point(x: 9, y: 3), Point(x: 14, y: 3),
   Point(x: 14, y: 7), Point(x: 17, y: 7)],
  [Point(x: 0, y: 11), Point(x: 5, y: 11), Point(x: 5, y: 8),
   Point(x: 9, y: 8), Point(x: 9, y: 11), Point(x: 14, y: 11),
   Point(x: 14, y: 7), Point(x: 17, y: 7)]
]

proc distanceSq*(ax, ay, bx, by: int): int =
  (ax - bx) * (ax - bx) + (ay - by) * (ay - by)

proc route*(lane: int): seq[Point] =
  var p = Waypoints[lane][0]
  result.add p
  for i in 1 ..< Waypoints[lane].len:
    let dest = Waypoints[lane][i]
    while p != dest:
      if p.x != dest.x: p.x += (if dest.x > p.x: 1 else: -1)
      else: p.y += (if dest.y > p.y: 1 else: -1)
      result.add p

proc road*(x, y: int): bool =
  for lane in 0 .. 1:
    for p in route(lane):
      if p.x == x and p.y == y: return true

proc buildable*(x, y: int): bool =
  x > 0 and x < GridWidth - 1 and y > 0 and y < GridHeight - 1 and
    not road(x, y) and distanceSq(x, y, 17, 7) > 2

proc waveKind*(wave, index: int): int =
  if wave == WaveCount and index == 0: return 4
  if wave >= 5 and index mod 7 == 3: return 3
  if wave >= 4 and index mod (if wave >= 8: 3 else: 5) == 0: return 2
  if wave >= 2 and index mod (if wave == 7: 2 else: 4) == 1: return 1
  0

proc waveSize*(wave: int): int = 6 + wave * 2

proc waveRoster*(wave: int): array[5, int] =
  if wave < 1 or wave > WaveCount: return
  for i in 0 ..< waveSize(wave): result[waveKind(wave, i)] += 2
