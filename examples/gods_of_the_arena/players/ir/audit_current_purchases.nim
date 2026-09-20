## Re-apply recorded commands with their real return values, checking every hash.
## Compile in the exact published checkout. No BASIC or synthetic combat runs.
import std/[json, strutils]
import polyworld/tapes
import ../../[game, sim, replays, content]

if not run.replayMode:
  raise newException(ValueError, "--replay is required")

var
  attempts, purchases: array[10, array[21, int]]
  goldSpent: array[10, array[21, int]]
  doubleHealSuccessTicks, healingNoSpace: array[10, int]
  hpEquipmentEvents: array[10, seq[JsonNode]]
  purchaseEvents: array[10, seq[JsonNode]]

proc replayActions() =
  var
    action: ReplayAction
    healingThisTick: array[10, int]
  while run.replayPlayer.takeActionAt(uint32(run.world.tick), action):
    let slot = heroIndex(run.world, action.heroId)
    if slot < 0:
      raise newException(ValueError, "unknown replay hero")
    case action.kind
    of ActionWalkTo:
      discard applyWalkTo(run.world, action.heroId, action.first, action.second)
    of ActionAttackMove:
      discard applyAttackMove(run.world, action.heroId, action.first, action.second)
    of ActionAttackTarget:
      discard applyAttackTarget(run.world, action.heroId, action.first)
    of ActionBuyItem:
      let item = int(action.first)
      if item notin 1..20:
        raise newException(ValueError, "invalid purchase")
      inc attempts[slot][item]
      let before = run.world.heroes[slot].gold
      let hpBefore = run.world.heroes[slot].hp
      let maxHpBefore = run.world.heroes[slot].maxHp
      let accepted = applyBuyItem(run.world, action.heroId, action.first)
      if accepted:
        inc purchases[slot][item]
        purchaseEvents[slot].add(%*{"tick":run.world.tick,"item":item,"gold_before":before,"gold_after":run.world.heroes[slot].gold})
        goldSpent[slot][item] += before - run.world.heroes[slot].gold
        if itemFromId(action.first).itemSpec.maxHp > 0:
          hpEquipmentEvents[slot].add(%*{"tick":run.world.tick,"item":item,
            "hp_before":hpBefore,"hp_after":run.world.heroes[slot].hp,
            "max_hp_before":maxHpBefore,"max_hp_after":run.world.heroes[slot].maxHp,
            "gold_before":before,"gold_after":run.world.heroes[slot].gold})
        if item in [1, 2]:
          inc healingThisTick[slot]
      elif item in [1, 2] and before >= itemFromId(action.first).itemSpec.cost:
        var noSpace = true
        for owned in run.world.heroes[slot].inventory:
          if owned == NoItem or owned.ord == item:
            noSpace = false
        if noSpace:
          inc healingNoSpace[slot]
    of ActionUseItem:
      discard applyUseItem(run.world, action.heroId, action.first)
    of ActionCastTarget .. ActionCastPoint - 1:
      discard applyCastTarget(run.world,action.heroId,int32(action.kind-ActionCastTarget),action.first)
    of ActionCastPoint .. ActionManualSpells - 1:
      discard applyCastPoint(run.world,action.heroId,int32(action.kind-ActionCastPoint),action.first,action.second)
    of ActionManualSpells:
      run.world.heroes[slot].manualSpells = action.first != 0
    else:
      raise newException(ValueError, "unsupported replay action")
  for slot, count in healingThisTick:
    if count > 1:
      inc doubleHealSuccessTicks[slot]
  # In ordinary replay this rotation follows the actions, once per tick.
  run.world.heroTurnStart = (run.world.heroTurnStart + 1) mod run.world.heroes.len

# Supply the recorded actions at the normal decision point, observing returns.
# Independent per-tick comparisons replace automatic historyPlayback checking.
run.historyPlayback = false
while run.world.tick < run.replayData.hashes.len and not run.world.gameOver:
  tickWorld(run, replayActions)
  if run.stateHash() != run.replayData.hashes[int(run.world.tick) - 1]:
    raise newException(ValueError, "replay hash mismatch at tick " & $run.world.tick)
if run.replayPlayer.actionIndex != run.replayData.actions.len:
  raise newException(ValueError, "not all actions consumed")

var heroes = newJArray()
for slot, hero in run.world.heroes:
  heroes.add(%*{"slot": slot, "class": $hero.class,
    "purchase_events":purchaseEvents[slot],
    "attempts": attempts[slot], "successful_purchases": purchases[slot],
    "gold_spent": goldSpent[slot], "double_heal_success_ticks": doubleHealSuccessTicks[slot],
    "healing_rejected_no_space": healingNoSpace[slot], "inventory": hero.inventory})
  heroes[^1]["hp_equipment_events"] = %hpEquipmentEvents[slot]
echo $(%*{"ticks": run.world.tick, "hash_mismatches": 0,
  "actions_consumed": run.replayPlayer.actionIndex, "state_hash": run.stateHash().toHex(16), "heroes": heroes})
