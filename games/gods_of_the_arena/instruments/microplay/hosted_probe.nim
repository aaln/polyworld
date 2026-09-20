## Full hosted-tape reconstruction. Only the subject VM is rerun; every other
## player's command is taken from the tape. Commands and state hashes must match.
## This is an observational mechanism audit, not a responsive counterfactual.
import std/[json, os, strutils]
import ../../examples/gods_of_the_arena/game
include ../../examples/gods_of_the_arena/bots

proc applyRecorded(world: World, action: ReplayAction) {.discardable.} =
  case action.kind
  of ActionWalkTo: discard applyWalkTo(world, action.heroId, action.first, action.second)
  of ActionAttackMove: discard applyAttackMove(world, action.heroId, action.first, action.second)
  of ActionAttackTarget: discard applyAttackTarget(world, action.heroId, action.first)
  of ActionBuyItem: discard applyBuyItem(world, action.heroId, action.first)
  of ActionUseItem: discard applyUseItem(world, action.heroId, action.first)
  of ActionCastTarget .. ActionCastPoint - 1:
    discard applyCastTarget(world, action.heroId, int32(action.kind - ActionCastTarget), action.first)
  of ActionCastPoint .. ActionManualSpells - 1:
    discard applyCastPoint(world, action.heroId, int32(action.kind - ActionCastPoint), action.first, action.second)
  of ActionManualSpells:
    let i = world.heroIndex(action.heroId)
    if i >= 0: world.heroes[i].manualSpells = action.first != 0
  else: raise newException(ReplayError, "invalid action")

if not game.run.replayMode: raise newException(ValueError, "--replay required")
let tape = game.run.replayData
let slot = parseInt(getEnv("PROBE_SLOT"))
doAssert slot in 0..9
loadBots(game.run, [BotGroup(path: getEnv("PROBE_POLICY"), count: 10)])
game.run.historyPlayback = false
startReplayRecording(uint32(tape.hashes.len))
var index, checked, decisions, crowded, eligible, picks, refinements: int
var finishPicks, assistPicks, finishChanges, assistChanges, changedAttackCommands: int
var maxInstructions, maxWork, minObjects, maxObjects: int
minObjects = int.high
while game.run.world.tick < tape.hashes.len and not game.run.world.gameOver:
  tickWorld(game.run, proc() =
    var perSlot: array[10, seq[ReplayAction]]
    while index < tape.actions.len and tape.actions[index].tick == uint32(game.run.world.tick):
      let a = tape.actions[index]
      if a.kind == ActionManualSpells: applyRecorded(game.run.world, a)
      else: perSlot[heroIndex(game.run.world, a.heroId)].add(a)
      inc index
    for offset in 0..<10:
      let current = (game.run.world.heroTurnStart + offset) mod 10
      if current != slot:
        for a in perSlot[current]: applyRecorded(game.run.world, a)
      else:
        let first = game.run.recorder.data.actions.len
        let vm = game.run.heroVms[slot]
        let before = vm.decisions
        let hero = game.run.world.heroes[slot]
        let count = game.run.world.worldObjectCount(hero.id)
        runHeroScript(game.run, slot)
        if vm.failed: raise newException(ValueError, vm.lastError)
        let actual = game.run.recorder.data.actions[first..<game.run.recorder.data.actions.len]
        if actual != perSlot[slot]:
          echo $(%*{"type": "command_mismatch", "tick": game.run.world.tick,
                    "expected": perSlot[slot], "actual": actual})
          quit(2)
        checked += actual.len
        if vm.decisions > before:
          inc decisions
          minObjects = min(minObjects, count)
          maxObjects = max(maxObjects, count)
          maxInstructions = max(maxInstructions, int(vm.lastInstructions))
          maxWork = max(maxWork, int(vm.lastWork))
          if count > 48: inc crowded
          try:
            let picked = vm.runtime.getGlobal("mpPick")
            let original = vm.runtime.getGlobal("mpOriginal")
            let kind = vm.runtime.getGlobal("mpKind")
            if count <= 48 and kind in [2'i32, 3'i32]: inc eligible
            if picked > 0:
              inc picks
              let finish = vm.runtime.getGlobal("mpScore") < 1000000
              if finish: inc finishPicks
              else: inc assistPicks
              if picked != original:
                inc refinements
                if finish: inc finishChanges
                else: inc assistChanges
                var memory = newJObject()
                for key in ["mpOriginal", "mpPick", "mpAssist", "mpLeader", "mpLeaderHp",
                            "mpSelfThreat", "mpScore", "mpRange", "mpChosenDistance", "bestId"]:
                  memory[key] = %vm.runtime.getGlobal(key)
                var publicObjects = newJArray()
                for oi in 0..<count:
                  var value: WorldObject
                  if game.run.world.worldObjectAt(hero.id, oi, value) and
                      (value.id == picked or value.id == original or value.id == vm.runtime.getGlobal("mpLeader")):
                    publicObjects.add(%*{"id": value.id, "kind": value.kind, "hp": value.hp,
                      "alive": value.alive, "x": mapCoordinate(value.position.x),
                      "y": mapCoordinate(value.position.z)})
                var commands = 0
                for a in actual:
                  if a.kind == ActionAttackTarget and a.first == picked: inc commands
                changedAttackCommands += commands
                echo $(%*{"schema": "gota-microplay-hosted-decision/1", "type": "refinement",
                  "tick": game.run.world.tick, "slot": slot,
                  "branch": (if finish: "finish" else: "guarded_assist"),
                  "public_object_count": count, "self_hp": hero.hp,
                  "self_class": $hero.class, "self_x": mapCoordinate(hero.position.x),
                  "self_y": mapCoordinate(hero.position.z), "memory": memory,
                  "public_objects": publicObjects, "actions": actual,
                  "refined_attack_commands": commands,
                  "interpretation": "Selected target and submitted commands; not proof of landed damage"})
          except BasicError: discard # Parent has no microplay memory.
    game.run.world.heroTurnStart = (game.run.world.heroTurnStart + 1) mod 10
  )
  if game.run.stateHash() != tape.hashes[game.run.world.tick - 1]:
    echo $(%*{"type": "hash_mismatch", "tick": game.run.world.tick})
    quit(3)
doAssert game.run.world.tick == tape.hashes.len
doAssert index == tape.actions.len
echo $(%*{"schema": "gota-microplay-hosted-audit/1", "type": "summary", "slot": slot,
  "ticks": game.run.world.tick, "commands_matched": checked, "decisions": decisions,
  "crowded_decisions": crowded, "eligible_original_unit_decisions": eligible,
  "min_objects": minObjects, "max_objects": maxObjects,
  "picks": picks, "finish_picks": finishPicks, "assist_picks": assistPicks,
  "refinements": refinements, "finish_refinements": finishChanges,
  "assist_refinements": assistChanges, "refined_attack_commands": changedAttackCommands,
  "max_instructions": maxInstructions, "max_work": maxWork,
  "all_state_hashes_equal": true, "all_actions_consumed": true})
