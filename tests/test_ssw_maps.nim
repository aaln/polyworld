## Seesaw map generation: determinism and a playable park.

import
  std/[sets, strformat],
  polyworld/pathing,
  ../examples/seesaw/content,
  ../examples/seesaw/maps

const SeedsUnderTest = 12

echo "Testing map determinism"
block sameSeedSameMap:
  let
    first = generateMap(DefaultSeed)
    second = generateMap(DefaultSeed)
  doAssert first.hash == second.hash, "the same seed produced two maps"
  doAssert first.passable == second.passable
  doAssert first.kinds == second.kinds
  doAssert first.hash != 0, "the map fingerprint is empty"

block differentSeedsDifferentMaps:
  var seen: HashSet[uint64]
  for seed in 1'i32 .. 12'i32:
    let map = generateMap(seed)
    doAssert map.hash notin seen, &"seed {seed} collided with another map"
    seen.incl map.hash

echo "Testing playability"
block everySeedValidates:
  for seed in 1'i32 .. SeedsUnderTest:
    let map = generateMap(seed)
    map.validateMap()

echo "Testing playground layout"
block pitAndForest:
  let map = generateMap(DefaultSeed)
  var
    pit = 0
    forest = 0
  for kind in map.kinds:
    if kind == uint8(PitTileKind):
      inc pit
    elif kind == uint8(TreeTile):
      inc forest
  doAssert pit >= 12
  doAssert forest >= 800
  let center = MapCenter * GridSide + MapCenter
  doAssert map.passable[center] == 0, "the fulcrum pad should be blocked"

echo "test_ssw_maps: all checks passed"
