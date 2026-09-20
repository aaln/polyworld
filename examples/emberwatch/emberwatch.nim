## Native accelerated runner and JSON-lines environment for external AI players.
import std/[json, os, strutils]
import content, sim, session

proc main() =
  var game = newSession()
  game.ai = [true, true]
  var recordPath, replayPath: string
  var jsonl = false
  var args = commandLineParams()
  var i = 0
  while i < args.len:
    case args[i]
    of "--jsonl": jsonl = true
    of "--naive": game.expert = false
    of "--seed", "--difficulty", "--record", "--replay":
      if i + 1 >= args.len: raise newException(ValueError, "Missing value for " & args[i])
      let flag = args[i]
      inc i
      case flag
      of "--seed": game.world.seed = clamp(parseInt(args[i]), 0, 1_000_000)
      of "--difficulty": game.world.difficulty = clamp(parseInt(args[i]), 0, 2)
      of "--record": recordPath = args[i]
      else: replayPath = args[i]
    of "--help", "-h":
      echo """Emberwatch: a cooperative tower defense game.
Play: python3 examples/emberwatch/serve.py
Run AI: nim r -d:headless examples/emberwatch/emberwatch.nim [options]
  --seed N          Expedition seed (0..1000000, default 2026)
  --difficulty N    0 scout, 1 veteran, 2 ordeal
  --naive           Run a deliberately limited bolt-only baseline
  --record PATH     Save commands and checksums as JSON
  --replay PATH     Verify an exported native or browser replay
  --jsonl           One JSON request / response per line on stdin / stdout"""
      return
    else: raise newException(ValueError, "Unknown flag: " & args[i])
    inc i
  if jsonl:
    game.ai = [false, true]
    for line in stdin.lines:
      try:
        if line.len > 16_000_000: raise newException(ValueError, "Request exceeds 16 MB.")
        echo game.request(parseJson(line))
      except CatchableError as e: echo %*{"ok": false, "error": e.msg}
    return
  if replayPath.len > 0:
    game = readReplay(parseFile(replayPath))
    game.verify()
    game.advance(game.replayTicks)
    echo "Replay verified: ", game.world.tick, " ticks, hash ", game.world.stateHash
  else:
    while not game.world.terminal: game.advance(240)
    if recordPath.len > 0:
      if recordPath.parentDir.len > 0: createDir(recordPath.parentDir)
      writeFile(recordPath, $game.recording())
  echo %*{"seed": game.world.seed, "difficulty": game.world.difficulty,
    "victory": game.world.phase == 2, "wave": game.world.wave,
    "core": game.world.core, "kills": game.world.kills,
    "ticks": game.world.tick, "score": game.world.score, "hash": game.world.stateHash}

when isMainModule:
  try: main()
  except CatchableError as e:
    stderr.writeLine(e.msg)
    quit(1)
