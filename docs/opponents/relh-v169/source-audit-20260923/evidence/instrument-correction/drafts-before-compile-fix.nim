## Exact replay draft prefixes, preserving per-action public availability.
import std/json
import ../[game, sim, replays, content]
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


doAssert run.replayMode
let tape = run.replayData
var rows = newJArray()
var index = 0
run.historyPlayback = false
while run.world.phase == Drafting and run.world.tick < tape.hashes.len:
  tickWorld(run, proc() =
    while index < tape.actions.len and tape.actions[index].tick == uint32(run.world.tick):
      let a = tape.actions[index]
      if a.kind == ActionDraft:
        let slot = run.world.heroIndex(a.heroId)
        let hero = run.world.heroes[slot]
        var legal, picks = newJArray()
        for c in 0..9: legal.add(%run.world.heroAvailable(c.int32))
        for h in run.world.heroes:
          picks.add(%*{"id": h.id, "team": h.team.ord,
            "class": run.world.draftedClass(h.id)})
        rows.add(%*{"tick": run.world.tick, "slot": slot, "team": hero.team.ord,
          "choice": a.first, "legal": legal, "picks": picks})
      discard applyRecorded(run.world, a)
      inc index
  )
  doAssert run.stateHash() == tape.hashes[run.world.tick - 1]
echo $(%*{"draft_ticks": run.world.tick, "rows": rows,
  "prefix_hashes_equal": true,
  "scope": "Only the authentic draft prefix. No changed choices are simulated with future recorded commands."})
