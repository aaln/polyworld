## Seesaw rider scripting: the whole surface a BASIC program has on
## the simulation.
##
## One VM per rider. Every command acts as the calling rider, so the
## captured `slot` in the host closures is the entire authorisation
## boundary. Hidden traits, the partner's fun, and exact weather magnitudes
## never cross this surface.

import
  polyworld/[basic, profiles],
  content,
  sim

type
  RiderDataSlot = enum
    DataSelfSlot,
    DataWorldTick,
    DataRemainingTicks,
    DataDecisionPeriod,
    DataAngleMilli,
    DataOmegaMilli,
    DataMyLean,
    DataMyPump,
    DataMyFun,
    DataMyNausea,
    DataMySick,
    DataMyFunDelta,
    DataMySeated,
    DataTempBand,
    DataWindBand,
    DataWetBand,
    DataPartnerLean,
    DataPartnerPump,
    DataPartnerExpr,
    DataPartnerExprAge,
    DataExpressionCount

const
  RiderDataNames: array[RiderDataSlot, string] = [
    "selfSlot",
    "worldTick",
    "remainingTicks",
    "decisionPeriod",
    "angleMilli",
    "omegaMilli",
    "myLean",
    "myPump",
    "myFun",
    "myNausea",
    "mySick",
    "myFunDelta",
    "mySeated",
    "tempBand",
    "windBand",
    "wetBand",
    "partnerLean",
    "partnerPump",
    "partnerExpr",
    "partnerExprAge",
    "expressionCount"
  ]

var
  activeGame: Game
  riderDataIds: array[RiderDataSlot, int32]

proc bindRiderData(program: Program) =
  for slot, name in RiderDataNames:
    riderDataIds[slot] = program.hostDataIndex(name)
    doAssert riderDataIds[slot] >= 0, "missing host data " & name

proc riderLimits*(): Limits =
  result = defaultLimits()
  result.maxSourceBytes = 128 * 1024
  result.maxCodeInstructions = 80_000
  result.maxArrays = 8
  result.maxArrayElements = 1_024
  result.maxGlobals = 256
  result.maxHostData = 32
  result.maxHostFunctions = 32
  result.maxRoutines = 32
  result.maxParameters = 8
  result.maxRegisters = 128
  result.maxSyntaxDepth = 32
  result.maxCallDepth = 16
  result.maxMemoryBytes = 512 * 1024
  result.maxInstructions = 80_000
  result.maxWorkUnits = 100_000
  result.maxPrintBytes = 4 * 1024
  result.maxPrintEvents = 64

proc buildRiderHost*(slot: int32): Host =
  result = initHost()
  for name in RiderDataNames:
    discard result.addData(name)

  let absValProc: HostProc = proc(arguments: openArray[int32]): int32 =
    abs(arguments[0])
  discard result.addFunction("absVal", 1, absValProc, 1)

  let signOfProc: HostProc = proc(arguments: openArray[int32]): int32 =
    if arguments[0] > 0: 1 elif arguments[0] < 0: -1 else: 0
  discard result.addFunction("signOf", 1, signOfProc, 1)

  let leanProc: HostProc = proc(arguments: openArray[int32]): int32 =
    int32(activeGame.applyLean(slot, arguments[0]))
  discard result.addFunction("lean", 1, leanProc, 20)

  let pumpProc: HostProc = proc(arguments: openArray[int32]): int32 =
    int32(activeGame.applyPump(slot, arguments[0]))
  discard result.addFunction("pump", 1, pumpProc, 20)

  let expressProc: HostProc = proc(arguments: openArray[int32]): int32 =
    int32(activeGame.applyExpress(slot, arguments[0]))
  discard result.addFunction("express", 1, expressProc, 20)

  let restProc: HostProc = proc(arguments: openArray[int32]): int32 =
    int32(activeGame.applyRest(slot))
  discard result.addFunction("rest", 0, restProc, 10)

proc loadBots*(game: Game, sources: openArray[string]) =
  let limits = riderLimits()
  let schema = buildRiderHost(0)
  var bound = false
  for slot in 0'i32 ..< int32(RiderCount):
    if sources[slot].len == 0:
      continue
    let program = compile(sources[slot], schema, limits)
    game.brains[slot] = RiderVm(
      runtime: initRuntime(program, buildRiderHost(slot), limits),
      ready: true
    )
    if not bound:
      bindRiderData(program)
      bound = true

proc runDecision(game: Game, slot: int32) =
  if game.brains[slot] == nil or
      not game.brains[slot].ready or
      game.brains[slot].failed:
    return
  let
    me = game.world.riders[slot]
    other = game.world.riders[1 - slot]
  game.brains[slot].runtime.restart()
  try:
    let ids = riderDataIds
    game.brains[slot].runtime.setData(ids[DataSelfSlot], slot)
    game.brains[slot].runtime.setData(ids[DataWorldTick], game.world.tick)
    game.brains[slot].runtime.setData(
      ids[DataRemainingTicks], game.world.remainingTicks)
    game.brains[slot].runtime.setData(ids[DataDecisionPeriod], DecisionTicks)
    game.brains[slot].runtime.setData(ids[DataAngleMilli], game.world.angleMilli)
    game.brains[slot].runtime.setData(ids[DataOmegaMilli], game.world.omegaMilli)
    game.brains[slot].runtime.setData(ids[DataMyLean], me.lean)
    game.brains[slot].runtime.setData(ids[DataMyPump], int32(me.pump))
    game.brains[slot].runtime.setData(ids[DataMyFun], me.feltFun)
    game.brains[slot].runtime.setData(ids[DataMyNausea], me.nausea)
    game.brains[slot].runtime.setData(ids[DataMySick], int32(me.sick))
    game.brains[slot].runtime.setData(ids[DataMyFunDelta], me.funDelta)
    game.brains[slot].runtime.setData(ids[DataMySeated], int32(me.seated))
    game.brains[slot].runtime.setData(
      ids[DataTempBand], int32(game.world.tempBand.ord))
    game.brains[slot].runtime.setData(
      ids[DataWindBand], int32(game.world.windBand.ord))
    game.brains[slot].runtime.setData(
      ids[DataWetBand], int32(game.world.wetBand.ord))
    game.brains[slot].runtime.setData(ids[DataPartnerLean], other.lean)
    game.brains[slot].runtime.setData(ids[DataPartnerPump], int32(other.pump))
    game.brains[slot].runtime.setData(ids[DataPartnerExpr], other.expression)
    game.brains[slot].runtime.setData(
      ids[DataPartnerExprAge], other.expressionAge)
    game.brains[slot].runtime.setData(
      ids[DataExpressionCount], ExpressionCount)
    discard game.brains[slot].runtime.run()
    inc game.brains[slot].decisions
  except BasicError as error:
    game.brains[slot].failed = true
    game.brains[slot].lastError = error.msg
    echo "rider ", slot, " BASIC error: ", error.msg
  game.brains[slot].lastWork = game.brains[slot].runtime.workUsed
  game.brains[slot].lastInstructions =
    game.brains[slot].runtime.instructionsUsed

proc runBotDecisions*(game: Game) {.measure.} =
  activeGame = game
  let first = (game.world.tick div DecisionTicks) mod int32(RiderCount)
  for offset in 0'i32 ..< int32(RiderCount):
    game.runDecision((first + offset) mod int32(RiderCount))
  activeGame = nil
