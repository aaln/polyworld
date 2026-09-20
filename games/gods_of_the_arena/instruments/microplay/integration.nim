## Normal complete-game runtime and action-replay qualification, not a win gate.
import std/json
import polyworld/basic
import ../../examples/gods_of_the_arena/[game, sim, replays]

var maxInstructions, maxWork, refinements, decisions: array[10, int]
var lastDecisions: array[10, int]
var deaths: array[10, int]
var wasDead: array[10, bool]

while game.run.world.tick < options.maximumTicks and not game.run.world.gameOver:
  advanceGame()
  if not game.run.replayMode:
    for slot, vm in game.run.heroVms:
      if vm.failed:
        raise newException(ValueError, "VM " & $slot & ": " & vm.lastError)
      maxInstructions[slot] = max(maxInstructions[slot], int(vm.lastInstructions))
      maxWork[slot] = max(maxWork[slot], int(vm.lastWork))
      if vm.decisions > lastDecisions[slot]:
        inc decisions[slot]
        try:
          if vm.runtime.getGlobal("mpPick") > 0 and
              vm.runtime.getGlobal("bestId") != vm.runtime.getGlobal("mpOriginal"):
            inc refinements[slot]
        except BasicError:
          discard
      lastDecisions[slot] = vm.decisions
  for slot, hero in game.run.world.heroes:
    if hero.state == Dying and not wasDead[slot]: inc deaths[slot]
    wasDead[slot] = hero.state == Dying

if game.run.replayMode:
  doAssert game.run.hashCheck.mismatches == 0
  doAssert game.run.world.tick == game.run.replayData.hashes.len
  doAssert game.run.replayPlayer.actionIndex == game.run.replayData.actions.len
else:
  saveRecording()

var heroes = newJArray()
for slot, hero in game.run.world.heroes:
  heroes.add(%*{"slot": slot, "class": $hero.class, "deaths": deaths[slot],
    "hits": hero.attacksLanded, "refinements": refinements[slot],
    "decisions": decisions[slot], "max_instructions": maxInstructions[slot],
    "max_work": maxWork[slot]})
echo $(%*{"ticks": game.run.world.tick, "complete": game.run.world.gameOver or game.run.world.tick == options.maximumTicks,
  "game_over": game.run.world.gameOver, "winner": (if game.run.world.gameOver: game.run.world.winner.ord else: -1),
  "replay": game.run.replayMode, "state_hash": $game.run.stateHash(),
  "hash_mismatches": game.run.hashCheck.mismatches, "heroes": heroes})
