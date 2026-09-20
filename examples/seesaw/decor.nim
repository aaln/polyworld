## Seesaw decorations: benches, lamps, a fence, flowers, and a well.
## Purely visual and derived from the map seed, so a live game and its
## replay dress identically. Nothing here reaches the sim.

import
  std/math,
  vmath,
  polyworld/[pathing, rngs],
  content,
  maps

type
  DecorKit* = enum
    MeadowProps, MeadowVegetation, MeadowBuildings, MeadowRocks, ValleyProps

  Decoration* = object
    kit*: DecorKit
    node*: string
    x*, y*: float32
    lift*: float32
    yaw*: float32
    height*: float32
    tint*: Vec3

  Placer = object
    map: MapData
    rng: Rng
    placed: seq[Decoration]

const
  DecorSalt = 0x5EE5A11'u64
  KitFiles: array[DecorKit, string] = [
    "terrain/toon_enchanted_meadow/props.glb",
    "terrain/toon_enchanted_meadow/vegetation.glb",
    "terrain/toon_enchanted_meadow/buildings.glb",
    "terrain/toon_enchanted_meadow/rocks.glb",
    "terrain/toon_golden_valley/props.glb",
  ]
  DecorNodes: array[DecorKit, seq[string]] = [
    @["lamp_post_01a", "flower_pot_01a", "wood_fence_01a",
      "wood_fence_pole_01a", "wood_crate_01a"],
    @["flowers_patch_01a", "flowers_patch_02a", "flowers_patch_03a",
      "flower_bush_01a", "bush_01a", "grass_patch_01a", "grass_patch_02a",
      "grass_patch_03a"],
    @["wood_bench_01a", "wood_bench_01b", "wood_table_01a",
      "wood_pillar_01a"],
    @["rock_small_01a", "rock_small_02a", "rock_small_03a",
      "rock_medium_01a"],
    @["well_01a", "wood_sign_01a"],
  ]
  FlowerBeds = ["flowers_patch_01a", "flowers_patch_02a", "flowers_patch_03a"]
  SmallRocks = ["rock_small_01a", "rock_small_02a", "rock_small_03a"]
  Tufts = ["grass_patch_01a", "grass_patch_02a", "grass_patch_03a"]

proc kitFile*(kit: DecorKit): string =
  KitFiles[kit]

proc nodesFor*(kit: DecorKit): seq[string] =
  DecorNodes[kit]

proc unit(rng: var Rng): float32 =
  float32(rng.below(10001)) / 10000.0'f32

proc pick[T](rng: var Rng, items: openArray[T]): T =
  items[rng.below(int32(items.len))]

proc kindAt(map: MapData, x, y: int32): uint8 =
  if x < 0 or y < 0 or x >= GridSide or y >= GridSide:
    return 255
  map.kinds[y * GridSide + x]

proc add(
    p: var Placer, kit: DecorKit, node: string, x, y, yaw, height: float32,
    lift = 0.0'f32, tint = vec3(1, 1, 1)
) =
  p.placed.add Decoration(
    kit: kit, node: node, x: x, y: y, yaw: yaw, height: height,
    lift: lift, tint: tint
  )

proc placeDecor*(map: MapData, seed: int32): seq[Decoration] =
  ## Lays out the park furniture from the seed alone.
  var p = Placer(map: map, rng: initRng(seed, DecorSalt))
  let
    cx = float32(MapCenter) + 0.5'f32
    cy = float32(MapCenter) + 0.5'f32

  p.add(MeadowBuildings, "wood_pillar_01a", cx, cy, 0.2'f32, 0.35'f32, lift = 0.02'f32)
  for slot in 0 ..< RiderCount:
    let
      rest = restTile(int32(slot))
      yaw = if slot == 0: PI.float32 * 0.5'f32 else: -PI.float32 * 0.5'f32
      bx = float32(rest.x) + 0.5'f32
      by = float32(rest.y) + 0.5'f32
    p.add(MeadowBuildings, "wood_bench_01a", bx, by, yaw, 0.7'f32)
    p.add(MeadowProps, "flower_pot_01a",
      bx + cos(yaw) * 1.1'f32, by + sin(yaw) * 1.1'f32, yaw,
      0.45'f32, tint = vec3(1.15, 1.12, 0.9))
  p.add(ValleyProps, "well_01a", cx + 14.0'f32, cy - 3.0'f32, 0.4'f32, 2.4'f32)
  p.add(ValleyProps, "wood_sign_01a", cx + 12.2'f32, cy - 4.2'f32, -0.6'f32, 0.35'f32,
    lift = 1.1'f32)

  const BenchAngles = [0.4'f32, 2.0'f32, 3.6'f32, 5.1'f32]
  for i, angle in BenchAngles:
    let
      radius = 13.2'f32 + p.rng.unit() * 0.6'f32
      x = cx + cos(angle) * radius
      y = cy + sin(angle) * radius
      yaw = angle + PI.float32 * 0.5'f32
    p.add(MeadowBuildings, p.rng.pick(["wood_bench_01a", "wood_bench_01b"]),
      x, y, yaw, 0.65'f32)
    p.add(MeadowProps, "flower_pot_01a",
      x + cos(angle) * 0.9'f32, y + sin(angle) * 0.9'f32, yaw,
      0.42'f32 + p.rng.unit() * 0.08'f32,
      tint = vec3(1.2, 1.1, 0.95))
    if i mod 2 == 0:
      p.add(MeadowBuildings, "wood_table_01a",
        x + cos(angle) * 1.4'f32, y + sin(angle) * 1.4'f32, yaw, 0.7'f32)

  for i in 0 ..< 16:
    let
      angle = float32(i) * (PI.float32 * 2.0'f32 / 16.0'f32)
      radius = 16.5'f32
      x = cx + cos(angle) * radius
      y = cy + sin(angle) * radius
    p.add(MeadowProps, "wood_fence_01a", x, y, angle + PI.float32 * 0.5'f32, 1.1'f32)

  for i in 0 ..< 8:
    let
      angle = float32(i) * (PI.float32 * 2.0'f32 / 8.0'f32) + 0.2'f32
      radius = 18.0'f32
    p.add(MeadowProps, "lamp_post_01a",
      cx + cos(angle) * radius, cy + sin(angle) * radius, angle, 2.8'f32)

  for i in 0 ..< 42:
    let
      angle = p.rng.unit() * PI.float32 * 2.0'f32
      radius = 8.5'f32 + p.rng.unit() * 10.0'f32
      x = cx + cos(angle) * radius
      y = cy + sin(angle) * radius
      tx = int32(x)
      ty = int32(y)
      kind = p.map.kindAt(tx, ty)
    if kind == uint8(TreeTile) or kind == uint8(PadTileKind) or
        kind == uint8(PitTileKind):
      continue
    if p.rng.below(5) == 0:
      p.add(MeadowVegetation, "bush_01a", x, y, angle,
        1.1'f32 + p.rng.unit() * 0.25'f32, tint = vec3(0.95, 1.15, 0.85))
    elif p.rng.below(3) != 0:
      p.add(MeadowVegetation, p.rng.pick(FlowerBeds), x, y, angle,
        0.42'f32 + p.rng.unit() * 0.18'f32, tint = vec3(1.2, 1.15, 1.05))
    else:
      p.add(MeadowVegetation, p.rng.pick(Tufts), x, y, angle, 0.45'f32)

  for i in 0 ..< 8:
    let
      angle = p.rng.unit() * PI.float32 * 2.0'f32
      radius = 22.0'f32 + p.rng.unit() * 10.0'f32
    p.add(MeadowRocks, p.rng.pick(SmallRocks),
      cx + cos(angle) * radius, cy + sin(angle) * radius, angle,
      0.45'f32 + p.rng.unit() * 0.25'f32)

  p.placed
