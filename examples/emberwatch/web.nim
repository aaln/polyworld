## Small JSON boundary. Presentation cannot mutate the authoritative world.
import std/json
import session
var game = newSession()

proc exchange(payload: cstring): cstring {.exportc.} =
  try: cstring($game.request(parseJson($payload)))
  except CatchableError as e: cstring($(%*{"ok": false, "error": e.msg}))

{.emit: "globalThis.emberwatchCore = function(payload) { return exchange(payload); };".}
