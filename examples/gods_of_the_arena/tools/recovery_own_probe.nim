## Exact62 full source audit; retrospective commands and neutral-pull states.
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
let subject = parseInt(getEnv("AUDIT_SLOT"))
doAssert subject in 0..9
loadBots(game.run, [BotGroup(path: getEnv("AUDIT_POLICY"), count: 10)])
game.run.historyPlayback = false
startReplayRecording(uint32(tape.hashes.len))
var index, checked, maxInstructions, maxWork: int
var firstChoice = newJNull()
var decisionFrames = newJArray()
var neutralDecisions, pullDecisions, pullStarts, handoffFrames, priorPull: int
var pullFrames = newJArray()
var gateCounts=initCountTable[string]()
var farmExamples=newJArray()
let until = tape.hashes.len
while game.run.world.tick < until and not game.run.world.gameOver:
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
      if slot != subject:
        for a in perSlot[slot]: applyRecorded(game.run.world, a)
      else:
        let first = game.run.recorder.data.actions.len
        let vm = game.run.heroVms[slot]
        let before = vm.decisions
        runHeroScript(game.run, slot)
        doAssert not vm.failed, vm.lastError
        let actual = game.run.recorder.data.actions[first..<game.run.recorder.data.actions.len]
        doAssert actual == perSlot[slot], "Command mismatch at " & $game.run.world.tick
        checked += actual.len
        maxInstructions = max(maxInstructions, int(vm.lastInstructions))
        maxWork = max(maxWork, int(vm.lastWork))
        if not wasDrafting and vm.decisions > before:
          proc v(key: string): int32 =
            if key == "selfHp": int32(game.run.world.heroes[slot].hp)
            elif key == "selfMaxHp": int32(game.run.world.heroes[slot].maxHp)
            else: vm.runtime.getGlobal(key)
          if v("active") == 1:
            gateCounts.inc("active")
            if v("nCampId")>0:
              gateCounts.inc("visible_tier_eligible_camp")
              if v("retreat")==1:gateCounts.inc("camp_seen_while_retreating")
              if v("enemyPower")>0:gateCounts.inc("camp_seen_with_hero_within10")
              if v("selfHp")*10 < v("selfMaxHp")*7:gateCounts.inc("camp_seen_below70hp")
              if v("bestId")>0 and v("bestKind") in [2'i32,3'i32]:
                gateCounts.inc("camp_seen_but_final_hero_or_wave")
              if v("bestKind")==6 and v("bestId")>0:gateCounts.inc("camp_selected")
              if farmExamples.len<30 and v("bestKind")!=6 and v("retreat")==0:
                var q=newJObject();q["tick"] = %game.run.world.tick
                for key in ["nCampId","nCampHp","nCampDistance","selfHp","selfMaxHp","enemyPower","bestId","bestKind","bestDistance","retreat","nPullStage","stopped","nSafe"]:q[key] = %v(key)
                q["commands"] = actionsJson(actual)
                farmExamples.add(q)
            if v("bestKind") == 6 and v("bestId") > 0: inc neutralDecisions
            if v("nPullStage") > 0: inc pullDecisions
            if v("nHandoff") == 1: inc handoffFrames
            if priorPull == 0 and v("nPullStage") > 0: inc pullStarts
            if priorPull != int(v("nPullStage")) and pullFrames.len < 40:
              pullFrames.add(%*{"tick": game.run.world.tick, "from": priorPull,
                "stage": v("nPullStage"), "camp": v("nPullCamp"),
                "waveCount": v("nWaveCount"), "handoff": v("nHandoff"),
                "retreat": v("retreat"), "safe": v("nSafe")})
            priorPull = int(v("nPullStage"))
          if v("active") == 1 and firstChoice.kind == JNull:
            var frame = newJObject()
            frame["tick"] = %game.run.world.tick
            for key in ["lane", "laneAssigned", "laneChanged", "laneStored", "laneKnown",
                        "laneCount0", "laneCount1", "laneCount2", "laneDecisionStart",
                        "laneCurrent", "laneChoice", "bestDistance", "threatDistance",
                        "retreat", "goalX", "goalY"]:
              frame[key] = %v(key)
            if game.run.world.tick mod 24 == 0: decisionFrames.add(frame)
            if v("laneAssigned") == 1: firstChoice = frame
    if not wasDrafting:
      game.run.world.heroTurnStart = (game.run.world.heroTurnStart + 1) mod 10
  )
  doAssert game.run.stateHash() == tape.hashes[game.run.world.tick - 1], "Hash mismatch at " & $game.run.world.tick
var gates=newJObject()
for k,v in gateCounts:gates[k] = %v
echo $(%*{"neutral_gate_counts":gates,"farm_examples":farmExamples,"valid": true, "slot": subject, "prefix_ticks": game.run.world.tick,
  "matched_commands": checked, "max_instructions": maxInstructions, "max_work": maxWork,
  "first_choice": firstChoice, "opening_frames": decisionFrames,
  "neutral_target_decisions": neutralDecisions, "pull_decisions": pullDecisions,
  "pull_starts": pullStarts, "handoff_frames": handoffFrames, "first40_pull_transitions": pullFrames,
  "scope": "All subject commands and full state hashes match through the complete episode; nine recorded policies used only for retrospective source reconstruction, not counterfactual score evidence."})
