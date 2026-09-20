## Seesaw map generation.
##
## A meadow playground from one seed: a flattened lawn, a sand box under the
## board, a packed path ring, and a forest wall. Walkability is fixed at
## generation. The simulation never reads the terrain layers; the renderer
## may sample heights and must not write simulation state.

import
  std/strformat,
  polyworld/[hashes, noises, pathing, profiles],
  content

static:
  doAssert GridSide.int == GridTiles,
    "content and pathing disagree about the size of the map"

const
  MapCenter* = GridSide div 2
  TerrainAmplitudeSteps = 5'i32
  PlayFlatRadius = 18'i32
  PlayFadeRadius = 28'i32
  PitRadius* = 5'i32
  PathInner* = 6'i32
  PathOuter* = 8'i32
  ForestEdgeRadius* = 38'i32
  ForestWallRadius* = 56'i32
  FulcrumReach* = 1'i32
  GroundNoiseStream = 0xA0761D6478BD642F'u64
  GroundDetailStream = 0xE7037ED1A0B428DB'u64
  ForestNoiseStream = 0xD1B54A32D192ED03'u64
  CornerSide = GridSide + 1
  PitTileKind* = MarshTile
  PathTileKind* = RoadTile
  PadTileKind* = StoneTile

type
  MapData* = object
    seed*: int32
    passable*: seq[uint8]
    kinds*: seq[uint8]
    heights*: seq[int16]
    hash*: uint64

const StepOffsets* = [
  (0'i32, -1'i32), (1'i32, -1'i32), (1'i32, 0'i32), (1'i32, 1'i32),
  (0'i32, 1'i32), (-1'i32, 1'i32), (-1'i32, 0'i32), (-1'i32, -1'i32)
]

proc centerDistance(x, y: int32): int32 =
  max(abs(x - MapCenter), abs(y - MapCenter))

proc centerDistanceSquared(x, y: int32): int32 =
  (x - MapCenter) * (x - MapCenter) + (y - MapCenter) * (y - MapCenter)

proc generateMap*(seed: int32): MapData {.measure.} =
  ## Builds the playground for one seed. Writes `pathing.layers` once.
  proc ground(cx, cz: int): int32 =
    let value =
      valueNoise(seed, GroundNoiseStream, cx, cz, 24) * 3 +
      valueNoise(seed, GroundDetailStream, cx, cz, 9)
    int32(roundDivision(
      int64(value) * TerrainAmplitudeSteps,
      int64(MapBlendScale) * 4
    ))

  proc playFlatten(cx, cz: int32): int32 =
    let ring = centerDistance(cx, cz)
    smoothstep(
      int32(PlayFadeRadius - ring) * MapBlendScale div
        max(PlayFadeRadius - PlayFlatRadius, 1'i32)
    )

  proc makeCorner(cx, cz: int32): int32 =
    blendHeight(ground(int(cx), int(cz)), 0, playFlatten(cx, cz))

  var cornerHeights = newSeq[int16](CornerSide * CornerSide)
  for cz in 0 .. GridSide.int:
    for cx in 0 .. GridSide.int:
      cornerHeights[cz * CornerSide + cx] =
        int16(makeCorner(int32(cx), int32(cz)))
  template corner(cx, cz: int32): int32 =
    int32(cornerHeights[int(cz) * CornerSide.int + int(cx)])

  var groundLayer = QuadLayer(
    originX: 0, originZ: 0,
    width: GridSide, depth: GridSide,
    slab: false,
    tiles: newSeq[Tile](GridCells)
  )
  template groundTile(x, y: int32): var Tile =
    groundLayer.tiles[int(y) * GridSide.int + int(x)]

  for y in 0'i32 ..< GridSide:
    for x in 0'i32 ..< GridSide:
      groundTile(x, y) = Tile(
        flags: TileExists or TileConnectedEast or TileConnectedSouth,
        kind: GrassTile,
        tops: packedHeights([
          corner(x, y), corner(x + 1, y),
          corner(x, y + 1), corner(x + 1, y + 1)])
      )

  for y in 0'i32 ..< GridSide:
    for x in 0'i32 ..< GridSide:
      let d2 = centerDistanceSquared(x, y)
      if d2 <= PitRadius * PitRadius:
        groundTile(x, y).kind = PitTileKind
      elif d2 >= PathInner * PathInner and d2 <= PathOuter * PathOuter:
        groundTile(x, y).kind = PathTileKind

  for y in MapCenter - FulcrumReach .. MapCenter + FulcrumReach:
    for x in MapCenter - FulcrumReach .. MapCenter + FulcrumReach:
      groundTile(x, y).kind = PadTileKind
      groundTile(x, y).impassable = true

  proc inGridContent(x, y: int32): bool =
    x >= 0 and x < GridSide and y >= 0 and y < GridSide

  proc nearPath(x, y: int32): bool =
    for dy in -2'i32 .. 2'i32:
      for dx in -2'i32 .. 2'i32:
        let
          nx = x + dx
          ny = y + dy
        if not inGridContent(nx, ny):
          continue
        if groundTile(nx, ny).kind == PathTileKind or
            groundTile(nx, ny).kind == PadTileKind or
            groundTile(nx, ny).kind == PitTileKind:
          return true
    false

  for y in 0'i32 ..< GridSide:
    for x in 0'i32 ..< GridSide:
      let ring = centerDistance(x, y)
      if ring <= ForestEdgeRadius:
        continue
      if groundTile(x, y).kind != GrassTile:
        continue
      let
        forest = valueNoise(seed, ForestNoiseStream, int(x), int(y), 12)
        gate = MapBlendScale -
          (ring - ForestEdgeRadius) * MapBlendScale div
            (ForestWallRadius - ForestEdgeRadius)
      if forest > gate or ring >= ForestWallRadius:
        if nearPath(x, y):
          continue
        groundTile(x, y).kind = TreeTile
        groundTile(x, y).impassable = true

  layers = @[groundLayer]
  computeWalkable()

  result = MapData(
    seed: seed,
    passable: newSeq[uint8](GridCells),
    kinds: newSeq[uint8](GridCells),
    heights: newSeq[int16](GridCells)
  )
  for y in 0'i32 ..< GridSide:
    for x in 0'i32 ..< GridSide:
      let index = y * GridSide + x
      result.passable[index] = uint8(isWalkable(0, int(x), int(y)))
      result.kinds[index] = uint8(groundLayer.tiles[index].kind)
      let tops = groundLayer.tiles[index].tops
      result.heights[index] = int16(
        (int32(tops[0]) + int32(tops[1]) +
          int32(tops[2]) + int32(tops[3])) div 4
      )

  var hash = HashySeed
  hash.addHashy(seed)
  hash.addHashy(layers.len)
  for layerIndex, layer in layers:
    for index, tile in layer.tiles:
      hash.addHashy(uint32(tile.flags))
      hash.addHashy(uint32(tile.kind))
      for value in tile.tops:
        hash.addHashy(value)
      hash.addHashy(layerWalkable[layerIndex][index])
  for index in 0 ..< GridCells:
    hash.addHashy(result.passable[index])
    hash.addHashy(result.kinds[index])
    hash.addHashy(result.heights[index])
  result.hash = uint64(hash)

proc mountTile*(slot: int32): tuple[x, y: int32] =
  ## Hop-on pad in the sand beside one seat.
  result.y = MapCenter
  if slot == 0:
    result.x = MapCenter - MountOffset
  else:
    result.x = MapCenter + MountOffset

proc restTile*(slot: int32): tuple[x, y: int32] =
  ## Bench this rider walks to when they get off.
  (MapCenter + RestDeltaX[slot], MapCenter + RestDeltaY[slot])

proc tileOpen*(map: MapData, x, y: int32): bool =
  ## Walkability at one generated tile.
  x >= 0 and y >= 0 and x < GridSide and y < GridSide and
    map.passable[y * GridSide + x] == 1

proc validateMap*(map: MapData) =
  ## Asserts that a generated playground has a pit, a path, and a forest.
  let seed = map.seed
  doAssert map.passable.len == GridCells
  doAssert map.kinds.len == GridCells
  var
    pit = 0
    path = 0
    forest = 0
    blockedCenter = 0
  for y in 0'i32 ..< GridSide:
    for x in 0'i32 ..< GridSide:
      let
        index = y * GridSide + x
        kind = map.kinds[index]
      if kind == uint8(PitTileKind):
        inc pit
      elif kind == uint8(PathTileKind):
        inc path
      elif kind == uint8(TreeTile):
        inc forest
        doAssert map.passable[index] == 0,
          &"seed {seed}: a forest tile is walkable"
      if abs(x - MapCenter) <= FulcrumReach and
          abs(y - MapCenter) <= FulcrumReach:
        doAssert map.passable[index] == 0,
          &"seed {seed}: the fulcrum pad is walkable at ({x},{y})"
        inc blockedCenter
  doAssert pit >= 12, &"seed {seed}: sand pit is too small ({pit})"
  doAssert path >= 40, &"seed {seed}: path ring is too thin ({path})"
  doAssert forest >= 800, &"seed {seed}: forest is too thin ({forest})"
  doAssert blockedCenter == 9,
    &"seed {seed}: fulcrum pad is {blockedCenter} tiles"
  for slot in 0'i32 ..< int32(RiderCount):
    let
      mount = mountTile(slot)
      rest = restTile(slot)
    doAssert map.tileOpen(mount.x, mount.y),
      &"seed {seed}: mount tile ({mount.x},{mount.y}) is blocked"
    doAssert map.tileOpen(rest.x, rest.y),
      &"seed {seed}: rest tile ({rest.x},{rest.y}) is blocked"
