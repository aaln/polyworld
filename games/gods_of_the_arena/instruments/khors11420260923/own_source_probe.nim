## Current58 source-reveal audit. Exact opponent VMs replace their recorded commands;
## all other commands and every complete world-state hash must still match.
## Private memory is retrospective audit evidence, never observer-model input.
import std/[json, os, strutils, tables]
import ../game
include ../bots

proc applyRecorded(world: World, action: ReplayAction): bool {.discardable.} =
  ## Applies one recorded bot command without requiring its private VM.
  case action.kind
  of ActionWalkTo:
    applyWalkTo(world, action.heroId, action.first, action.second, action.offset)
  of ActionAttackMove:
    applyAttackMove(
      world, action.heroId, action.first, action.second, action.offset
    )
  of ActionAttackTarget:
    applyAttackTarget(world, action.heroId, action.first)
  of ActionBuyItem:
    applyBuyItem(world, action.heroId, action.first)
  of ActionBuyback:
    applyBuyback(world, action.heroId)
  of ActionUseItem:
    applyUseItem(world, action.heroId, action.first)
  of ActionUseItemAt:
    applyUseItemAt(world, action.heroId, action.slot,
      action.first, action.second, action.offset)
  of ActionCastTarget:
    applyCastTarget(world, action.heroId,
      action.slot, action.first)
  of ActionCastPoint:
    applyCastPoint(world, action.heroId,
      action.slot, action.first, action.second, action.offset)
  of ActionLevelAbility:
    applyLevelAbility(world, action.heroId, action.slot)
  of ActionDraft:
    applyDraft(world, action.heroId, action.first)
  of ActionManualSpells:
    let index = world.heroIndex(action.heroId)
    if index >= 0:
      world.heroes[index].manualSpells = action.first != 0
    false
  else:
    raise newException(ReplayError, "replay action kind is invalid")

proc actionsJson(actions:seq[ReplayAction]):JsonNode=
  result=newJArray()
  for a in actions:
    result.add(%*{"tick":a.tick,"hero_id":a.heroId,"kind":a.kind,"slot":a.slot,"first":a.first,"second":a.second,"offset_raw":[int32(a.offset.x),int32(a.offset.y)]})

doAssert game.run.replayMode
let tape = game.run.replayData
var controlled: array[10, bool]
var slots: seq[int]
for s in getEnv("AUDIT_SLOTS").split(','):
  let slot = parseInt(s)
  doAssert slot in 0..9 and not controlled[slot]
  slots.add(slot)
  controlled[slot] = true
loadBots(game.run, [BotGroup(path: getEnv("AUDIT_POLICY"), count: 10)])
game.run.historyPlayback = false
startReplayRecording(uint32(tape.hashes.len))
var index, checked, decisions, maxInstructions, maxWork: int
var counts = initCountTable[string]()
var examples = newJObject()
proc event(name: string, tick, slot: int, vm: HeroVm) =
  counts.inc(name)
  if not examples.hasKey(name):
    var memory = newJObject()
    for key in ["decision", "combatDecision", "objectiveBuild", "neuralActionCountdown",
                "bestId", "objectiveId", "objectiveKind", "objectiveDistance", "heroId",
                "heroDistance", "siegeThreatId", "routeFallback", "routeGroupCount", "groupDeparture",
                "reserveHome", "reserveNearest", "reserveGuards", "reserveGuardCritical",
                "reserveDistance", "reserveTarget", "reserveDirect", "reserveFinish"]:
      memory[key] = %vm.runtime.getGlobal(key)
    examples[name] = %*{"tick": tick, "slot": slot, "memory": memory}

while game.run.world.tick < tape.hashes.len and not game.run.world.gameOver:
  tickWorld(game.run, proc() =
    var perSlot: array[10, seq[ReplayAction]]
    while index < tape.actions.len and tape.actions[index].tick == uint32(game.run.world.tick):
      let a = tape.actions[index]
      if a.kind == ActionManualSpells: applyRecorded(game.run.world, a)
      else: perSlot[heroIndex(game.run.world, a.heroId)].add(a)
      inc index
    let wasDrafting = game.run.world.phase == Drafting
    let draftSlot = game.run.world.heroIndex(game.run.world.draftHeroId())
    for offset in 0..<10:
      let slot = if wasDrafting: offset else: (game.run.world.heroTurnStart + offset) mod 10
      if wasDrafting and slot != draftSlot:
        doAssert perSlot[slot].len == 0
        continue
      if not controlled[slot]:
        for a in perSlot[slot]: applyRecorded(game.run.world, a)
      else:
        let first = game.run.recorder.data.actions.len
        let vm = game.run.heroVms[slot]
        let before = vm.decisions
        let hero = game.run.world.heroes[slot]
        let recovery = getEnv("AUDIT_KIND") != "ours" and vm.runtime.getGlobal("recoveryInitialized") != 0 and
          hero.attacksLanded > vm.runtime.getGlobal("recoveryLastHit")
        let wasAlive = hero.hp > 0
        runHeroScript(game.run, slot)
        if vm.failed: raise newException(ValueError, vm.lastError)
        let actual = game.run.recorder.data.actions[first..<game.run.recorder.data.actions.len]
        if actual != perSlot[slot]:
          echo $(%*{"type": "command_mismatch", "tick": game.run.world.tick, "slot": slot,
                    "expected": actionsJson(perSlot[slot]), "actual": actionsJson(actual)})
          quit(2)
        checked += actual.len
        if vm.decisions > before:
          inc decisions
          maxInstructions = max(maxInstructions, int(vm.lastInstructions))
          maxWork = max(maxWork, int(vm.lastWork))
          if wasDrafting or not wasAlive: continue
          template value(key: string): int32 = vm.runtime.getGlobal(key).int32
          template mark(key: string) = event(key, game.run.world.tick, slot, vm)
          if getEnv("AUDIT_KIND") == "ours":
            template ov(key:string):int32=vm.runtime.getGlobal(key).int32
            if ov("active")==1:
              counts.inc("our_active")
              if getEnv("AUDIT_TRANSFER")=="1" and ov("pressureChoice") in [1'i32,2'i32]:
                let label=if ov("pressureChoice")==1:"covered_tower" else:"siege_attacker"
                counts.inc("selected_" & label)
                for a in actual:
                  if a.kind==ActionAttackTarget and a.first==ov("bestId"):
                    counts.inc("submitted_attack_" & label)
                let key="first_selected_" & label
                if not examples.hasKey(key):
                  examples[key] = %*{"tick":game.run.world.tick,"hero":hero.id,"hp":hero.hp,"max_hp":hero.maxHp,"target":ov("bestId"),"target_kind":ov("bestKind"),"target_hp":ov("bestHp"),"commands":actionsJson(actual)}
              counts.inc("our_selected_kind_" & $ov("bestKind"))
              if ov("bestId")==0:counts.inc("our_no_selected_target")
              if ov("inBase")==1:counts.inc("our_in_base")
              if ov("stopped")==1:counts.inc("our_stopped")
              for a in actual:
                if a.kind==ActionAttackMove:
                  counts.inc("our_attack_move")
                  if a.first==ov("homeX") and a.second==ov("homeY"):counts.inc("our_attack_move_home")
                  if a.first==ov("enemyX") and a.second==ov("enemyY"):counts.inc("our_attack_move_enemy_base")
                if a.kind==ActionWalkTo:
                  counts.inc("our_walk")
                  if a.first==ov("homeX") and a.second==ov("homeY"):counts.inc("our_walk_home")
              if game.run.world.tick mod (TickRate*60)==0:
                examples["own_minute_" & $game.run.world.tick] = %*{"tick":game.run.world.tick,"hero":hero.id,"hp":hero.hp,"max_hp":hero.maxHp,"xp":hero.totalXp,"x":hero.position.x,"z":hero.position.z,"target":ov("bestId"),"target_kind":ov("bestKind"),"retreat":ov("retreat"),"home_threat":ov("homeThreat"),"in_base":ov("inBase"),"stopped":ov("stopped"),"goal_x":ov("goalX"),"goal_y":ov("goalY"),"commands":actionsJson(actual)}
              if ov("retreat")==1:counts.inc("our_retreat")
              if ov("homeThreat")>0:counts.inc("our_home_threat")
              if ov("bestKind")==3 and ov("bestHp")>hero.heroAttackDamage():
                var exposed=0
                for oi in 0..<game.run.world.worldObjectCount(hero.id):
                  var obj:WorldObject
                  if game.run.world.worldObjectAt(hero.id,oi,obj) and obj.team!=hero.team and obj.kind==4 and obj.alive and obj.hp>0:
                    let dx=mapCoordinate(obj.position.x,hero.team)-mapCoordinate(hero.position.x,hero.team)
                    let dy=mapCoordinate(obj.position.z,hero.team)-mapCoordinate(hero.position.z,hero.team)
                    if dx*dx+dy*dy<=100:inc exposed
                if exposed>0 and ov("tanks")>0 and ov("towerAggro")==0 and ov("enemyPower")<=ov("friendPower") and hero.hp*100>=hero.maxHp*65 and ov("retreat")==0:
                  counts.inc("safe_tower_opportunity_while_nonlethal_creep_selected")
                  let key="first_safe_tower_opportunity"
                  if not examples.hasKey(key):examples[key] = %*{"tick":game.run.world.tick,"hero":hero.id,"hp":hero.hp,"max_hp":hero.maxHp,"creep":ov("bestId"),"creep_hp":ov("bestHp"),"near_towers":exposed,"tanks":ov("tanks"),"enemy_power":ov("enemyPower"),"friend_power":ov("friendPower"),"commands":actionsJson(actual)}
          else:
            counts.inc("combat_" & $value("combatDecision"))
            counts.inc("build_" & $value("objectiveBuild"))
            if value("neuralActionCountdown") == 4: mark("neural_recompute")
            if actual.len > 1: mark("multiple_commands")
            if recovery: mark("hit_recovery_walk")
            if value("combatDecision") in [2'i32, 8'i32] and value("objectiveKind") == 4 and
                value("objectiveDistance") <= 300 and value("siegeThreatId") != 0:
              mark("siege_counter_guard_true")
              for a in actual:
                if a.kind==ActionAttackTarget and a.first==value("siegeThreatId"):
                  counts.inc("siege_attack_submitted")
              if hero.attackObjectId==value("siegeThreatId"):
                counts.inc("siege_final_target_retained")
              elif recovery:
                counts.inc("siege_then_hit_recovery")
            if value("reserveHome") != 0 and
                (value("reserveGuards") <= 1 or (value("reserveGuardCritical") != 0 and value("reserveDistance") <= 900)) and
                value("reserveNearest") != 0 and value("reserveFinish") == 0:
              mark("home_reservation_guard_true")
            if value("routeFallback") != 0 and value("groupDeparture") != 0:
              mark("route_after_group_departure")
          for a in actual:
            counts.inc("command_kind_" & $a.kind)
    if not wasDrafting:
      game.run.world.heroTurnStart = (game.run.world.heroTurnStart + 1) mod 10
  )
  if game.run.stateHash() != tape.hashes[game.run.world.tick - 1]:
    echo $(%*{"type": "hash_mismatch", "tick": game.run.world.tick})
    quit(3)
doAssert game.run.world.tick == tape.hashes.len and index == tape.actions.len
var totals = newJObject()
for key, count in counts: totals[key] = %count
echo $(%*{"schema": "gota-source-reveal-runtime-audit/1", "slots": slots,
  "ticks": game.run.world.tick, "commands_matched": checked, "decisions": decisions,
  "max_instructions": maxInstructions, "max_work": maxWork, "counts": totals,
  "first_examples": examples, "all_state_hashes_equal": true, "all_actions_consumed": true,
  "label_scope": "Retrospective source/private-state audit; guards can overlap and later commands override earlier ones."})
