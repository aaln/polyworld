## Responsive ten-VM runner without assumptions about policy-private variables.
## Copy under the pinned engine's examples/gods_of_the_arena/players/ir/.
import std/[json, strutils]
import ../../[game, sim, replays]

if run.replayMode:
  raise newException(ValueError, "Use audit-hosted for replay; this runner executes policies")
var
  maxWork, maxInstructions: array[10, int64]
  deaths: array[10, int]
  wasDying: array[10, bool]
startReplayRecording(uint32(options.maximumTicks))
run.recorder.data.header.createdUnixMs = 0
while run.world.tick < options.maximumTicks and not run.world.gameOver:
  advanceGame()
  for slot, vm in run.heroVms:
    if vm.failed:
      raise newException(ValueError, "VM failed in slot " & $slot & ": " & vm.lastError)
    maxWork[slot] = max(maxWork[slot], vm.lastWork)
    maxInstructions[slot] = max(maxInstructions[slot], vm.lastInstructions)
    let dying = run.world.heroes[slot].state == Dying
    if dying and not wasDying[slot]: inc deaths[slot]
    wasDying[slot] = dying
if options.recordPath.len > 0: saveRecording()
var heroes = newJArray()
for slot, hero in run.world.heroes:
  heroes.add(%*{"slot": slot, "team": hero.team.ord, "class": hero.class.ord,
    "score": (if run.world.gameOver and run.world.winner == hero.team: 1 else: 0),
    "deaths": deaths[slot], "total_xp": hero.totalXp, "basic_hits": hero.attacksLanded,
    "level": hero.level, "gold": hero.gold, "max_work": maxWork[slot],
    "max_instructions": maxInstructions[slot], "vm_failed": run.heroVms[slot].failed})
echo $(%*{"seed": options.seed, "ticks": run.world.tick,
  "timeout": not run.world.gameOver,
  "winner": (if run.world.gameOver: run.world.winner.ord else: -1),
  "fort_hp": [run.world.forts[0].hp, run.world.forts[1].hp],
  "actions": run.recorder.data.actions.len, "state_hash": run.stateHash().toHex(16),
  "heroes": heroes})
