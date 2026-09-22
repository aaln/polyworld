## Real-host Crossbowman-first preference and public availability fallback.
import std/[os, json]
import bassy
import polyworld/[cli, tapes]
import ../[bots, content, maps, sim, replays]

let policy = getEnv("WEEK_POLICY")
doAssert policy.len > 0
var rows = newJArray()
for first in [Crossbowman, Ranger, Warlock, Arcanist]:
  let game = newGame(generateMap(54), 100_000, 10, false,
    ReplayData(), drafting = true)
  game.loadBots([BotGroup(path: policy, count: 10)])
  game.recorder = initReplayRecorder(game.currentSetup(1000), defaultConfig())
  for i in 0 ..< 10:
    if i != 5: game.heroVms[i] = nil
  let subject = game.world.heroes[5]
  while not subject.drafted and game.world.tick < 30:
    game.tickWorld(proc() =
      if game.world.draftTurn == 0:
        doAssert game.world.applyDraft(game.world.heroes[0].id, first.ord.int32)
      else:
        game.runBotDecisions())
  let vm = game.heroVms[5]
  doAssert not vm.failed, vm.lastError
  doAssert subject.drafted
  doAssert subject.class == (if first == Crossbowman: Ranger else: Crossbowman)
  doAssert game.world.tick == 13
  doAssert vm.lastInstructions <= 19000 and vm.lastWork <= 50000
  rows.add(%*{"first_red_pick": $first, "blue_pick": $subject.class,
    "world_tick": game.world.tick, "instructions": vm.lastInstructions,
    "work": vm.lastWork})
echo $(%*{"passed": true, "rows": rows,
  "scope": "Public opening draft only, responsive BASIC on actual host; not a counterfactual full match."})
