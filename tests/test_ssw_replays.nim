## Seesaw replays: roundtrip fidelity and named rejection of everything
## malformed.

import
  ../examples/seesaw/content,
  ../examples/seesaw/replays,
  polyworld/tapes

proc sampleSetup(): Setup =
  Setup(
    mapSeed: DefaultSeed,
    tickRate: uint16(TickRate),
    gridTiles: uint16(GridSide),
    decisionTicks: uint16(DecisionTicks),
    maximumTicks: uint32(MatchTicks),
    mapHash: 0xDEADBEEF'u64,
    contentHash: contentHash()
  )

proc sampleReplay(): ReplayData =
  let recorder = initReplayRecorder(sampleSetup())
  recorder.recordAction(uint32(DecisionTicks), 0, ActionLean, 1)
  recorder.recordAction(uint32(DecisionTicks), 1, ActionPump, 1)
  recorder.recordAction(uint32(DecisionTicks * 2), 0, ActionExpress, 1)
  recorder.recordAction(uint32(DecisionTicks * 2), 1, ActionRest)
  for tick in 0 ..< MatchTicks:
    recorder.recordHash(uint64(tick) * 0x9E3779B97F4A7C15'u64 + 1)
  recorder.data

echo "Testing roundtrip fidelity"
block roundtrip:
  let
    data = sampleReplay()
    encoded = encodeReplay(data)
    decoded = decodeReplay(encoded)
  doAssert decoded.header.setup == data.header.setup
  doAssert decoded.actions.len == data.actions.len
  doAssert decoded.hashes.len == data.hashes.len
  for index in 0 ..< data.actions.len:
    doAssert decoded.actions[index] == data.actions[index]

proc rejects(mutate: proc(data: var ReplayData)): bool =
  var data = sampleReplay()
  data.mutate()
  try:
    discard encodeReplay(data)
    false
  except ReplayError:
    true

echo "Testing named rejection"
block rejections:
  doAssert rejects(proc(data: var ReplayData) =
    data.header.setup.tickRate = 60),
    "a foreign tick rate was accepted"
  doAssert rejects(proc(data: var ReplayData) =
    data.header.setup.mapHash = 0),
    "a missing map fingerprint was accepted"
  doAssert rejects(proc(data: var ReplayData) =
    data.header.setup.contentHash = 0),
    "a missing content fingerprint was accepted"
  doAssert rejects(proc(data: var ReplayData) =
    data.header.setup.maximumTicks = 0),
    "a zero-length game was accepted"
  doAssert rejects(proc(data: var ReplayData) =
    data.actions[0].playerId = uint8(RiderCount)),
    "an unknown rider was accepted"
  doAssert rejects(proc(data: var ReplayData) =
    data.actions[0].kind = ActionKindHigh + 1),
    "an unknown action kind was accepted"
  doAssert rejects(proc(data: var ReplayData) =
    data.actions[0].first = 9),
    "an out-of-range lean was accepted"

echo "test_ssw_replays: all checks passed"
