## Transport shared by the web client and the native JSON-lines AI interface.
import std/json
import content, sim, bots

type
  RecordedCommand* = object
    tick*: int
    command*: Command
  Checkpoint* = object
    tick*, hash*: int
  Session* = object
    world*: World
    ai*: array[2, bool]
    expert*: bool
    actions*: seq[RecordedCommand]
    checks*: seq[Checkpoint]
    replaying*: bool
    replayTicks*, replayHash*, cursor*, checkCursor*: int

proc newSession*(seed = 2026, difficulty = 1): Session =
  result.world = newWorld(seed, difficulty)
  result.ai = [false, true]
  result.expert = true

proc act*(s: var Session, c: Command): string =
  if s.replaying: return "Replay playback cannot accept commands."
  if s.actions.len >= 100_000: return "Command limit reached."
  result = s.world.apply(c)
  if result.len == 0:
    s.actions.add RecordedCommand(tick: s.world.tick, command: c)

proc replayCommands(s: var Session) =
  while s.cursor < s.actions.len and s.actions[s.cursor].tick == s.world.tick:
    let error = s.world.apply(s.actions[s.cursor].command)
    if error.len > 0: raise newException(ValueError, "Invalid replay command: " & error)
    inc s.cursor

proc advance*(s: var Session, ticks = 1) =
  for n in 0 ..< clamp(ticks, 0, MaxTicks):
    if s.replaying:
      s.replayCommands()
      if s.world.tick >= s.replayTicks: break
    elif s.world.tick mod 12 == 0:
      for actor in 0 .. 1:
        if s.ai[actor]:
          for c in decide(s.world, actor, s.expert): discard s.act(c)
    if s.world.terminal: break
    s.world.step()
    if s.replaying:
      while s.checkCursor < s.checks.len and s.checks[s.checkCursor].tick == s.world.tick:
        if s.world.stateHash != s.checks[s.checkCursor].hash:
          raise newException(ValueError, "Replay diverged at tick " & $s.world.tick)
        inc s.checkCursor
    elif s.world.tick mod TickRate == 0:
      s.checks.add Checkpoint(tick: s.world.tick, hash: s.world.stateHash)
  if s.replaying:
    s.replayCommands()
    if s.world.tick == s.replayTicks and s.world.stateHash != s.replayHash:
      raise newException(ValueError, "Replay final hash did not match.")

proc recording*(s: Session): JsonNode =
  %*{"game": "emberwatch", "version": GameVersion, "seed": s.world.seed,
    "difficulty": s.world.difficulty, "ticks": s.world.tick,
    "hash": s.world.stateHash, "actions": s.actions, "checks": s.checks}

proc boundedInt(n: JsonNode, key: string, low, high: int): int =
  if not n.hasKey(key) or n[key].kind != JInt or
      n[key].getBiggestInt < low or n[key].getBiggestInt > high:
    raise newException(ValueError, "Invalid integer field: " & key)
  n[key].getInt

proc readReplay*(n: JsonNode): Session =
  if n.kind != JObject or n{"game"}.getStr != "emberwatch" or
      n.boundedInt("version", GameVersion, GameVersion) != GameVersion:
    raise newException(ValueError, "Unsupported Emberwatch replay.")
  result = newSession(n.boundedInt("seed", 0, 1_000_000), n.boundedInt("difficulty", 0, 2))
  result.ai = [false, false]
  result.replaying = true
  result.replayTicks = n.boundedInt("ticks", 0, MaxTicks)
  result.replayHash = n.boundedInt("hash", 0, 2_147_483_646)
  if n{"actions"}.kind != JArray or n["actions"].len > 100_000:
    raise newException(ValueError, "Invalid replay actions.")
  var lastTick = 0
  for a in n["actions"]:
    let tick = a.boundedInt("tick", lastTick, result.replayTicks)
    result.actions.add RecordedCommand(tick: tick, command: parseCommand(a["command"]))
    lastTick = tick
  if n{"checks"}.kind != JArray or n["checks"].len != result.replayTicks div TickRate:
    raise newException(ValueError, "Missing replay checksums.")
  var tick = TickRate
  for check in n["checks"]:
    result.checks.add Checkpoint(tick: check.boundedInt("tick", tick, tick),
      hash: check.boundedInt("hash", 0, 2_147_483_646))
    tick += TickRate

proc verify*(s: Session) =
  var replay = s
  replay.advance(replay.replayTicks + 1)
  if replay.world.tick != replay.replayTicks or replay.cursor != replay.actions.len:
    raise newException(ValueError, "Replay ended before all commands were consumed.")

proc observe*(s: Session): JsonNode =
  result = s.world.observation()
  result["ai"] = %s.ai
  result["replaying"] = %s.replaying
  result["replayTicks"] = %s.replayTicks

proc request*(s: var Session, n: JsonNode): JsonNode =
  ## Malformed or rejected requests return an error and keep the session usable.
  try:
    if n.kind != JObject: raise newException(ValueError, "Expected an object.")
    case n{"op"}.getStr
    of "reset":
      s = newSession(n.boundedInt("seed", 0, 1_000_000), n.boundedInt("difficulty", 0, 2))
    of "act":
      let error = s.act(parseCommand(n["command"]))
      if error.len > 0: return %*{"ok": false, "error": error}
    of "step": s.advance(n.boundedInt("ticks", 0, 2400))
    of "observe": discard
    of "ai":
      if s.replaying: raise newException(ValueError, "A replay cannot change controllers.")
      let actor = n.boundedInt("actor", 0, 1)
      if n{"enabled"}.kind != JBool: raise newException(ValueError, "enabled must be boolean.")
      s.ai[actor] = n["enabled"].getBool
    of "export": return %*{"ok": true, "replay": s.recording()}
    of "load":
      var replay = readReplay(n["replay"])
      replay.verify()
      replay.advance(0)
      s = replay
    of "seek":
      if not s.replaying: raise newException(ValueError, "Seeking requires a replay.")
      let tick = n.boundedInt("tick", 0, s.replayTicks)
      s.world = newWorld(s.world.seed, s.world.difficulty)
      s.cursor = 0
      s.checkCursor = 0
      s.advance(tick)
    else: raise newException(ValueError, "Unknown operation.")
    %*{"ok": true, "state": s.observe()}
  except CatchableError as e:
    %*{"ok": false, "error": e.msg}
