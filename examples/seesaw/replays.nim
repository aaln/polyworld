## Seesaw action-only replay format and playback cursor.
##
## A replay stores accepted rider commands and one canonical simulation
## hash per tick. It never stores bot source, so replaying a game reveals
## what was done and never how the deciding program was written.

import
  polyworld/tapes,
  content

const
  ReplayGame* = "seesaw"
  ReplayFormatVersion* = 1'u16
  ReplayGameVersion* = 2'u16

  ActionLean* = 1'u8
  ActionPump* = 2'u8
  ActionExpress* = 3'u8
  ActionRest* = 4'u8
  ActionKindHigh* = ActionRest

  MaxReplayBytes* = 16 * 1024 * 1024
  MaxReplayActions* = 2_000_000
  MaxReplayHashes* = 10_000_000

type
  Setup* = object
    mapSeed*: int32
    tickRate*: uint16
    gridTiles*: uint16
    decisionTicks*: uint16
    maximumTicks*: uint32
    mapHash*: uint64
    contentHash*: uint64

  ReplayAction* = object
    tick*: uint32
    playerId*: uint8
      ## The acting rider slot, 0 or 1.
    kind*: uint8
    first*, second*: int32
      ## Payload interpreted per kind:
      ##   Lean     dir -2 .. 2, unused
      ##   Pump     0 or 1, unused
      ##   Express  face 0 .. 15, unused
      ##   Rest     unused, unused. Gets off the board and walks to a bench.
      ##             Lean or pump while off walks back and sits down.

  ReplayHeader* = TapeHeader[Setup]
  ReplayData* = ActionTape[Setup, ReplayAction]
  ReplayRecorder* = TapeRecorder[Setup, ReplayAction]
  ReplayPlayer* = TapePlayer[Setup, ReplayAction]

proc fail(message: string) {.noreturn.} =
  raise newException(ReplayError, message)

proc initReplayData*(setup: Setup): ReplayData =
  initActionTape[Setup, ReplayAction](
    setup,
    ReplayFormatVersion,
    ReplayGameVersion
  )

proc initReplayRecorder*(setup: Setup): ReplayRecorder =
  initTapeRecorder[Setup, ReplayAction](
    setup,
    ReplayFormatVersion,
    ReplayGameVersion
  )

proc record*(recorder: ReplayRecorder, action: ReplayAction) =
  if recorder == nil:
    return
  if action.kind == 0 or action.kind > ActionKindHigh:
    fail("replay action kind is invalid")
  if int(action.playerId) >= RiderCount:
    fail("replay action names an unknown rider")
  recorder.data.actions.appendAction(action, MaxReplayActions)

proc recordAction*(
    recorder: ReplayRecorder,
    tick: uint32,
    playerId: int32,
    kind: uint8,
    first = 0'i32,
    second = 0'i32
) =
  recorder.record ReplayAction(
    tick: tick,
    playerId: uint8(playerId),
    kind: kind,
    first: first,
    second: second
  )

proc recordHash*(recorder: ReplayRecorder, hash: uint64) =
  recordHash(recorder, hash, MaxReplayHashes)

proc validateSetup(setup: Setup) =
  if setup.tickRate != uint16(TickRate):
    fail("replay setup has an unsupported tick rate")
  if setup.gridTiles != uint16(GridSide):
    fail("replay setup has an unsupported map size")
  if setup.decisionTicks != uint16(DecisionTicks):
    fail("replay setup has an unsupported decision interval")
  if setup.maximumTicks == 0 or setup.maximumTicks > uint32(MaxMatchTicks):
    fail("replay setup has an invalid duration")
  if setup.mapHash == 0:
    fail("replay setup has no deterministic map fingerprint")
  if setup.contentHash == 0:
    fail("replay setup has no deterministic content fingerprint")

proc validateAction(action: ReplayAction, setup: Setup) =
  if action.kind == 0 or action.kind > ActionKindHigh:
    fail("replay action kind is invalid")
  if int(action.playerId) >= RiderCount:
    fail("replay action names an unknown rider")
  if action.tick > setup.maximumTicks:
    fail("replay action exceeds the configured duration")
  if action.tick == 0 or action.tick mod uint32(setup.decisionTicks) != 0:
    fail("replay action did not land on a decision tick")
  case action.kind
  of ActionLean:
    if action.first < -MaxLean or action.first > MaxLean:
      fail("replay lean is out of range")
  of ActionPump:
    if action.first != 0 and action.first != 1:
      fail("replay pump is not a flag")
  of ActionExpress:
    if action.first < 0 or action.first >= ExpressionCount:
      fail("replay expression is unknown")
  of ActionRest:
    discard
  else:
    fail("replay action kind is invalid")

proc validate*(data: ReplayData) =
  data.header.requireTapeVersion(
    ReplayFormatVersion,
    ReplayGameVersion
  )
  let setup = data.header.setup
  setup.validateSetup()
  if data.actions.len > MaxReplayActions:
    fail("replay action limit exceeded")
  if data.hashes.len > MaxReplayHashes:
    fail("replay hash limit exceeded")
  if data.hashes.len > int(setup.maximumTicks):
    fail("replay hashes exceed the configured duration")
  var lastTick = 0'u32
  for index, action in data.actions:
    if action.tick > uint32(data.hashes.len):
      fail("replay action exceeds the recorded duration")
    if index > 0 and action.tick < lastTick:
      fail("replay actions move backward in time")
    action.validateAction(setup)
    lastTick = action.tick

proc encodeReplay*(data: ReplayData): string =
  data.validate()
  encodeReplayFile(
    ReplayGame,
    ReplayGameVersion,
    data,
    MaxReplayBytes
  )

proc decodeReplay*(bytes: string): ReplayData =
  result = decodeReplayFile(
    ReplayGame,
    ReplayGameVersion,
    bytes,
    ReplayData,
    MaxReplayBytes
  )
  result.validate()

proc saveReplay*(path: string, data: ReplayData) =
  data.validate()
  saveReplayFile(
    path,
    ReplayGame,
    ReplayGameVersion,
    data,
    MaxReplayBytes
  )

proc loadReplay*(path: string): ReplayData =
  result = loadReplayFile(
    path,
    ReplayGame,
    ReplayGameVersion,
    ReplayData,
    MaxReplayBytes
  )
  result.validate()

proc initReplayPlayer*(data: ReplayData): ReplayPlayer =
  data.validate()
  initTapePlayer(data)
