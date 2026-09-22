## Copy into the pinned engine's examples/gods_of_the_arena/tools before building.
import std/[json, strutils]
import ../[game, sim, replays, content, scores]

var maxWork, maxInstructions: array[10, int64]
var samples = newJArray()
if not run.replayMode:
  startReplayRecording(uint32(options.maximumTicks))
  run.recorder.data.header.createdUnixMs = 0

proc heroRows(): JsonNode =
  result = newJArray()
  for slot, hero in run.world.heroes:
    result.add(%*{"slot": slot, "team": hero.team.ord, "class": hero.class.ord,
      "drafted": hero.drafted, "hp": hero.hp, "x": hero.position.x,
      "z": hero.position.z, "score": score(hero.totalXp.int, run.world.tick.int), "deaths": hero.deaths,
      "xp": hero.totalXp, "hits": hero.attacksLanded, "level": hero.level,
      "gold": hero.gold, "ranks": hero.abilityLevels, "inventory": hero.inventory,
      "item_counts": hero.itemCounts, "max_work": maxWork[slot],
      "max_instructions": maxInstructions[slot]})

while (if run.replayMode: run.world.tick < run.replayData.hashes.len
       else: not run.finished()):
  advanceGame()
  if not run.replayMode:
    for slot, vm in run.heroVms:
      if vm.failed:
        raise newException(ValueError, "VM failed slot " & $slot & ": " & vm.lastError)
      maxWork[slot] = max(maxWork[slot], vm.lastWork)
      maxInstructions[slot] = max(maxInstructions[slot], vm.lastInstructions)
  if run.world.phase == Playing and run.world.battleTick mod 2400 == 0:
    samples.add(%*{"battle_tick": run.world.battleTick, "heroes": heroRows()})

let tape = if run.replayMode: run.replayData else: run.recorder.data
var commands: array[10, array[19, int]]
for action in tape.actions:
  inc commands[run.world.heroIndex(action.heroId)][action.kind]
if run.replayMode:
  doAssert run.hashCheck.mismatches == 0
  doAssert run.replayPlayer.actionIndex == tape.actions.len
else:
  if options.recordPath.len > 0: saveRecording()
echo $(%*{"ticks": run.world.tick, "battle_ticks": run.world.battleTick,
  "draft_ticks": run.world.draftTicks, "seed": tape.config.seed,
  "winner": (if run.world.gameOver and not run.world.draw: run.world.winner.ord else: -1),
  "simultaneous_draw": run.world.draw, "fort_hp": [run.world.forts[0].hp, run.world.forts[1].hp],
  "actions": tape.actions.len, "hash_mismatches": run.hashCheck.mismatches,
  "state_hash": run.stateHash().toHex(16), "heroes": heroRows(),
  "commands": commands, "samples": samples})
