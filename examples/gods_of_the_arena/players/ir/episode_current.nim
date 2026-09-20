## Full-game evaluation using the real game/host, with replay and sparse reasons.
## Accepts the normal GOTA CLI; --record also writes a .trace.jsonl sibling.
import std/[json, strutils]
import polyworld/basic
import ../../[game, sim, replays]

var
  previousDecisions: array[10, int]
  decisionCounts: array[10, int]
  fallbackCounts: array[10, int]
  deaths: array[10, int]
  wasDying: array[10, bool]
  previousRule: array[10, string]
  maxWork: array[10, int64]
  maxInstructions: array[10, int64]
  targetKinds: array[10, array[5, int]]
  targetSwitches, doubleHealTicks, stationaryTargetTicks: array[10, int]
  lastCandidate: array[10, int32]
  lastX, lastY: array[10, int32]
  hasRecovery: array[10, bool]
  lastRecoveries: array[10, int32]
  hasHpInvestment: array[10, bool]
  lastHpInvestments: array[10, int32]
  hasLoadout: array[10, bool]
  lastLoadout: array[10, int32]
  trace: File
  tracing = options.recordPath.len > 0

proc optionalGlobal(runtime: Runtime, name: string): JsonNode =
  try:
    %runtime.getGlobal(name)
  except BasicError:
    newJNull()

if tracing:
  trace = open(options.recordPath & ".trace.jsonl", fmWrite)
startReplayRecording(uint32(options.maximumTicks))
# The research manifest records wall time. Normalize this non-game field so
# bytewise parity compares setup, every action, and every per-tick state hash.
game.run.recorder.data.header.createdUnixMs = 0
while game.run.world.tick < options.maximumTicks and not game.run.world.gameOver:
  let firstAction = game.run.recorder.data.actions.len
  advanceGame()
  for slot, vm in game.run.heroVms:
    let hero = game.run.world.heroes[slot]
    if hero.state == Dying and not wasDying[slot]:
      inc deaths[slot]
    wasDying[slot] = hero.state == Dying
    if vm.failed:
      raise newException(ValueError, "VM failed in slot " & $slot & ": " & vm.lastError)
    if vm.decisions == previousDecisions[slot]:
      continue
    previousDecisions[slot] = vm.decisions
    inc decisionCounts[slot]
    if decisionCounts[slot] == 1:
      hasLoadout[slot] = optionalGlobal(vm.runtime, "loadoutPurchases").kind != JNull
      hasRecovery[slot] = optionalGlobal(vm.runtime, "recoveryActivations").kind != JNull
      hasHpInvestment[slot] = optionalGlobal(vm.runtime, "hpGearInvestments").kind != JNull
    let loadout = if hasLoadout[slot]: vm.runtime.getGlobal("loadoutPurchases") else: 0
    let loadoutChanged = loadout != lastLoadout[slot]
    lastLoadout[slot] = loadout
    let recoveries = if hasRecovery[slot]: vm.runtime.getGlobal("recoveryActivations") else: 0'i32
    let recoveryChanged = recoveries != lastRecoveries[slot]
    lastRecoveries[slot] = recoveries
    let hpInvestments = if hasHpInvestment[slot]: vm.runtime.getGlobal("hpGearInvestments") else: 0'i32
    let hpInvestmentChanged = hpInvestments != lastHpInvestments[slot]
    lastHpInvestments[slot] = hpInvestments
    maxWork[slot] = max(maxWork[slot], vm.lastWork)
    maxInstructions[slot] = max(maxInstructions[slot], vm.lastInstructions)
    let candidate = vm.runtime.getGlobal("bestId")
    if candidate != lastCandidate[slot] and candidate != 0 and lastCandidate[slot] != 0:
      inc targetSwitches[slot]
    let x = vm.runtime.getData("selfX")
    let y = vm.runtime.getData("selfY")
    if candidate != 0 and candidate == lastCandidate[slot] and x == lastX[slot] and y == lastY[slot]:
      inc stationaryTargetTicks[slot]
    lastCandidate[slot] = candidate
    lastX[slot] = x
    lastY[slot] = y
    var targetKind = 0
    if candidate != 0:
      if heroIndex(game.run.world, candidate) >= 0:
        targetKind = 2
      elif towerIndex(game.run.world, candidate) >= 0:
        targetKind = 4
      elif footmanById(game.run.world, candidate).id != 0:
        targetKind = 3
      else:
        for fort in game.run.world.forts:
          if fort.id == candidate:
            targetKind = 1
    inc targetKinds[slot][targetKind]
    var healAttempts = 0
    for i in firstAction ..< game.run.recorder.data.actions.len:
      let action = game.run.recorder.data.actions[i]
      if action.heroId == hero.id and action.kind == ActionBuyItem and action.first in [1'i32, 2'i32]:
        inc healAttempts
    if healAttempts > 1:
      inc doubleHealTicks[slot]
    let rule = if candidate != 0: "R2" else: "R4"
    if candidate == 0:
      inc fallbackCounts[slot]
    if tracing and (rule != previousRule[slot] or loadoutChanged or recoveryChanged or hpInvestmentChanged or game.run.world.tick mod 240 == 0):
      var commands = newJArray()
      for i in firstAction ..< game.run.recorder.data.actions.len:
        let action = game.run.recorder.data.actions[i]
        if action.heroId == hero.id:
          commands.add(%*{"kind": action.kind, "first": action.first, "second": action.second})
      trace.writeLine($(%*{
        "tick": vm.runtime.getData("worldTick"), "slot": slot,
        "class": hero.class.ord, "tactical_rule": rule, "candidate_id": candidate,
        "self_x": vm.runtime.getData("selfX"), "self_y": vm.runtime.getData("selfY"),
        "self_hp": vm.runtime.getData("selfHp"),
        "target_kind_after_tick": targetKind,
        "recovery_activations": recoveries,
        "hp_gear_investments": hpInvestments,
        "loadout_purchases":loadout,
        "blocked_id": optionalGlobal(vm.runtime, "blockedId"),
        "escort_id": (if candidate == 0: optionalGlobal(vm.runtime, "escortId") else: newJNull()),
        "move_accepted": (if candidate == 0: optionalGlobal(vm.runtime, "moveAccepted") else: newJNull()),
        "commands": commands
      }))
    previousRule[slot] = rule
if tracing:
  trace.close()
  saveRecording()
var heroes = newJArray()
for slot, hero in game.run.world.heroes:
  var equipmentCount = 0
  for item in hero.inventory:
    if item.ord > 4:
      inc equipmentCount
  heroes.add(%*{"slot": slot, "team": hero.team.ord, "class": hero.class.ord,
    "score": (if game.run.world.gameOver and game.run.world.winner == hero.team: 1 else: 0),
    "decisions": decisionCounts[slot], "fallback_decisions": fallbackCounts[slot],
    "deaths": deaths[slot], "level": hero.level, "gold": hero.gold,
    "equipment_count": equipmentCount,
    "target_kinds_after_tick": targetKinds[slot], "target_switches": targetSwitches[slot],
    "stationary_target_ticks": stationaryTargetTicks[slot], "double_heal_attempt_ticks": doubleHealTicks[slot],
    "recovery_activations": optionalGlobal(game.run.heroVms[slot].runtime, "recoveryActivations"),
    "loadout_purchases":optionalGlobal(game.run.heroVms[slot].runtime,"loadoutPurchases"),
    "hp_gear_investments": optionalGlobal(game.run.heroVms[slot].runtime, "hpGearInvestments"),
    "hp_gear_granted_hp": optionalGlobal(game.run.heroVms[slot].runtime, "hpGearGrantedHp"),
    "max_work": maxWork[slot], "max_instructions": maxInstructions[slot]})
echo $(%*{"seed": options.seed, "ticks": game.run.world.tick,
  "timeout": not game.run.world.gameOver,
  "winner": (if game.run.world.gameOver: game.run.world.winner.ord else: -1),
  "fort_hp": [game.run.world.forts[0].hp, game.run.world.forts[1].hp],
  "actions": game.run.recorder.data.actions.len,
  "state_hash": game.run.stateHash().toHex(16), "map_hash": game.run.map.hash.toHex(16),
  "heroes": heroes})
