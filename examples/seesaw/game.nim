## Seesaw match setup, command line, and the headless runner.
##
## Owns the one live world and decides where each tick's commands come from:
## two BASIC riders in a live game, or the recorded action stream when
## replaying.

import
  std/[os, strformat, times],
  polyworld/[cli, controllers, profiles, tapes],
  content,
  maps as mapgen,
  sim,
  bots,
  controls,
  replays

proc usage() =
  echo """
Seesaw, a two-rider cooperative playground.

  --bot PATH[:N]   Fill N of the two seats with one program.
  --player         Control Lila; supply one bot.
  --player:N       Control rider N (1 or 2); supply one bot.
  --replay PATH    Play a recorded game instead of running bots.
  --record PATH    Record this game to a replay file.
  --seed N         Playground seed (default 2026).
  --seconds N      Duration in seconds (default 300).
  --minutes N      Duration in minutes (default 5).
  --ticks N        Duration in ticks (default 7200).
  --play=false     Start the graphical transport paused.
  --speed N        Graphical start speed: 1, 2, 4, or 16.
  --windowSize WxH Graphical window, such as 800x400.
  --vsync:off      Unlock the frame rate (default on).
  --help           Show this message.

Compile with -d:headless for a command-line game.
Compile with -d:emscripten for the web backend.
Compile with -d:takeScreenshot for a deterministic capture."""

proc parseGameOptions(): GameOptions =
  result = GameOptions(
    seed: DefaultSeed,
    seconds: MatchMinutes * 60,
    maximumTicks: MatchTicks,
    speed: 1,
    windowWidth: 1280,
    windowHeight: 800
  )
  let arguments = commandLineParams()
  var index = 0
  while index < arguments.len:
    let argument = arguments[index]
    if result.takeCommonFlag(arguments, index, argument):
      discard
    else:
      case argument
      of "--help", "-h":
        usage()
        quit(0)
      else:
        fail("unknown argument: " & argument)
    inc index
  if result.maximumTicks > MaxMatchTicks:
    fail("match duration is too long")
  result.validateGameOptions(
    RiderCount,
    "a live game requires exactly two bots"
  )

let options* = parseGameOptions()

var run*: Game

block:
  startGameProfile()
  var
    mapSeed = options.seed
    maximumTicks = options.maximumTicks
  if options.replayPath.len > 0:
    var replayData: ReplayData
    profileBlock "replay":
      replayData = loadReplay(options.replayPath)
    mapSeed = replayData.header.setup.mapSeed
    maximumTicks = int32(replayData.header.setup.maximumTicks)
    var gameMap: MapData
    profileBlock "map":
      gameMap = generateMap(mapSeed)
    gameMap.validateMap()
    if replayData.header.setup.mapHash != gameMap.hash:
      raise newException(ReplayError,
        "this replay was recorded on a different map generator")
    if replayData.header.setup.contentHash != contentHash():
      raise newException(ReplayError,
        "this replay was recorded against different game tuning")
    run = newGame(gameMap, maximumTicks)
    run.maximumTicks = int32(replayData.hashes.len)
    run.replayMode = true
    run.replayData = replayData
    run.replayPlayer = initReplayPlayer(replayData)
    run.historyPlayback = true
  else:
    var gameMap: MapData
    profileBlock "map":
      gameMap = generateMap(mapSeed)
    gameMap.validateMap()
    run = newGame(gameMap, maximumTicks)
    let
      kinds = controllerKinds(RiderCount, options.playerSlot)
      expanded = options.botGroups.expandBotSources(kinds)
    loadBots(run, expanded)
    run.recorder = initReplayRecorder(Setup(
      mapSeed: mapSeed,
      tickRate: uint16(TickRate),
      gridTiles: uint16(GridSide),
      decisionTicks: uint16(DecisionTicks),
      maximumTicks: uint32(maximumTicks),
      mapHash: gameMap.hash,
      contentHash: contentHash()
    ))
    run.replayPlayer = ReplayPlayer(data: run.recorder.data)

proc decide(w: World) =
  if run.historyPlayback:
    if run.recorder != nil:
      run.replayPlayer.data = run.recorder.data
    var action: ReplayAction
    while run.replayPlayer.takeActionAt(uint32(w.tick), action):
      w.applyReplayAction(action)
  else:
    flushPlayerCommands(run)
    runBotDecisions(run)

proc verifyTick(game: Game) =
  let hashes =
    if game.recorder != nil: game.recorder.data.hashes
    else: game.replayPlayer.data.hashes
  hashes.checkReplayHash(
    uint32(game.world.tick),
    game.stateHash(),
    game.hashCheck
  )

proc advanceGame*() =
  run.world.tickWorld(decide)
  if run.historyPlayback:
    run.verifyTick()
  elif run.recorder != nil:
    run.recorder.recordHash(run.stateHash())

proc saveRecording*(path = options.recordPath) =
  if run.recorder == nil or path.len == 0:
    return
  let directory = path.parentDir
  if directory.len > 0:
    createDir(directory)
  saveReplay(path, run.recorder.data)

proc describeResult*(): string =
  if not run.world.over:
    return "game unfinished"
  let
    a = run.world.riders[0].feltFun
    b = run.world.riders[1].feltFun
    pair = run.world.scores[0]
  &"{RiderNames[0]} {a}  {RiderNames[1]} {b}  pair {pair}"

proc runHeadless*() =
  startGameProfile()
  defer:
    finishGameProfile()
  let started = epochTime()
  while run.world.tick < run.maximumTicks and not run.world.over:
    advanceGame()
    if profileShouldDump(run.world.tick):
      finishGameProfile()
  let
    elapsed = max(epochTime() - started, 0.000001)
    simulated = run.world.tick.float64 / TickRate.float64

  echo &"seed {run.mapSeed}  ticks {run.world.tick}/{run.maximumTicks}  " &
    &"{simulated:.1f}s simulated in {elapsed:.2f}s " &
    &"({simulated / elapsed:.0f}x real time)"
  echo &"  weather  {TempNames[run.world.tempBand]}  " &
    &"{WindNames[run.world.windBand]}  {WetNames[run.world.wetBand]}"
  for slot in 0 ..< RiderCount:
    let r = run.world.riders[slot]
    echo &"  {RiderNames[slot]:>6}  fun {r.feltFun:>6}  nausea {r.nausea:>4}  " &
      &"sick {r.sickEvents}  prefer {r.preferred}"
  if not run.replayMode:
    for slot in 0 ..< RiderCount:
      let brain = run.brains[slot]
      if brain == nil:
        continue
      if brain.failed:
        echo &"  {RiderNames[slot]:>6}  script FAILED: {brain.lastError}"
  echo "  ", describeResult()

  if run.replayMode:
    if not run.replayPlayer.finished:
      echo "error: the replay still had commands left to run"
      quit(1)
    run.hashCheck.requireReplayComplete(
      uint32(run.world.tick),
      run.replayData.hashes.len
    )
    echo "  replay verified: every tick matched its recorded hash"
  else:
    saveRecording()
    if options.recordPath.len > 0:
      echo &"  recorded {run.recorder.data.actions.len} commands to " &
        options.recordPath
