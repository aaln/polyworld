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
  else:
    raise newException(ReplayError, "replay action kind is invalid")

proc actionsJson(actions:seq[ReplayAction]):JsonNode=
  result=newJArray()
  for a in actions:
    result.add(%*{"tick":a.tick,"hero_id":a.heroId,"kind":a.kind,"slot":a.slot,"first":a.first,"second":a.second,"offset_raw":[int32(a.offset.x),int32(a.offset.y)]})

doAssert game.run.replayMode
let tape = game.run.replayData
let controlled = parseInt(getEnv("AUDIT_SLOT", "7"))
loadBots(game.run, [BotGroup(path: getEnv("AUDIT_POLICY"), count: 10)])
game.run.historyPlayback = false
startReplayRecording(uint32(tape.hashes.len))
var index, checked, decisions, previousXp: int
var rows = newJArray()
var previousRetreat, previousRestock, previousBase: int32
proc memory(vm: HeroVm): JsonNode =
  result = newJObject()
  for key in ["active", "retreat", "restock", "inBase", "gearCount", "threatDistance", "bestId", "bestKind", "moveTick", "portalReady", "spawnX", "spawnY", "homeX", "homeY", "stopped", "towerAggro", "tanks", "objects", "scanOffset", "recallCreepDistance"]:
    result[key] = %vm.runtime.getGlobal(key)
while game.run.world.tick < tape.hashes.len and not game.run.world.gameOver:
  tickWorld(game.run, proc() =
    var perSlot: array[10, seq[ReplayAction]]
    while index < tape.actions.len and tape.actions[index].tick == uint32(game.run.world.tick):
      let a = tape.actions[index]
      perSlot[heroIndex(game.run.world, a.heroId)].add(a)
      inc index
    let wasDrafting = game.run.world.phase == Drafting
    let draftSlot = game.run.world.heroIndex(game.run.world.draftHeroId())
    for offset in 0..<10:
      let slot = if wasDrafting: offset else: (game.run.world.heroTurnStart + offset) mod 10
      if wasDrafting and slot != draftSlot:
        doAssert perSlot[slot].len == 0
        continue
      if slot != controlled:
        for a in perSlot[slot]: applyRecorded(game.run.world, a)
      else:
        let first = game.run.recorder.data.actions.len
        let vm = game.run.heroVms[slot]
        let before = vm.decisions
        let hero = game.run.world.heroes[slot]
        var visible = newJArray()
        if game.run.world.tick == 3530:
          for oi in 0..<game.run.world.worldObjectCount(hero.id):
            var obj: WorldObject
            if game.run.world.worldObjectAt(hero.id, oi, obj) and obj.team != hero.team and obj.kind == 3 and obj.alive and obj.hp > 0:
              let dx = float64(int64(obj.position.x) - hero.position.x) / float64(WorldScale)
              let dz = float64(int64(obj.position.z) - hero.position.z) / float64(WorldScale)
              visible.add(%*{"index":oi,"id":obj.id,"distance_squared_tiles":dx*dx+dz*dz,"hp":obj.hp})
        runHeroScript(game.run, slot)
        if vm.failed: raise newException(ValueError, vm.lastError)
        let actual = game.run.recorder.data.actions[first..<game.run.recorder.data.actions.len]
        if actual != perSlot[slot]:
          echo $(%*{"type":"command_mismatch", "tick":game.run.world.tick, "expected":actionsJson(perSlot[slot]), "actual":actionsJson(actual)})
          quit(2)
        checked += actual.len
        if vm.decisions > before:
          inc decisions
          let retreat = vm.runtime.getGlobal("retreat")
          let restock = vm.runtime.getGlobal("restock")
          let base = vm.runtime.getGlobal("inBase")
          var purchase = false
          for a in actual:
            if a.kind in [ActionBuyItem, ActionUseItemAt]: purchase = true
          if hero.totalXp != previousXp or retreat != previousRetreat or restock != previousRestock or base != previousBase or purchase or (game.run.world.tick >= 3200 and game.run.world.tick <= 6500 and game.run.world.tick mod 24 == 0):
            rows.add(%*{"visible_enemy_creeps_at_trigger":visible,"tick":game.run.world.tick, "hp":hero.hp,"max_hp":hero.maxHp,"mana":hero.mana,"max_mana":hero.maxMana,"gold":hero.gold,"xp":hero.totalXp,"x_raw":hero.position.x,"z_raw":hero.position.z,"ranks":hero.abilityLevels,"inventory":hero.inventory,"item_counts":hero.itemCounts,"memory":memory(vm),"commands":actionsJson(actual)})
          previousRetreat = retreat
          previousRestock = restock
          previousBase = base
          previousXp = hero.totalXp
    if not wasDrafting: game.run.world.heroTurnStart = (game.run.world.heroTurnStart + 1) mod 10
  )
  if game.run.stateHash() != tape.hashes[game.run.world.tick - 1]:
    echo $(%*{"type":"hash_mismatch", "tick":game.run.world.tick})
    quit(3)
doAssert game.run.world.tick == tape.hashes.len and index == tape.actions.len
echo $(%*{"schema":"gota-own-source-coaching-audit/1", "slot":controlled, "ticks":game.run.world.tick,"commands_matched":checked,"decisions":decisions,"all_state_hashes_equal":true,"all_actions_consumed":true,"rows":rows})
