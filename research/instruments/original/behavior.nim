## Exact62 full source audit; retrospective commands and neutral-pull states.
import std/[json, os, strutils, tables, math]
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


proc gap(a,b: WorldPoint): float =
  sqrt(float((int64(a.x)-b.x)*(int64(a.x)-b.x)+(int64(a.z)-b.z)*(int64(a.z)-b.z)))/WorldScale.float

doAssert game.run.replayMode
let tape=game.run.replayData
var index, decisions: int
var frames=newJArray()
var events=newJArray()
game.run.historyPlayback=false
while game.run.world.tick < tape.hashes.len:
  tickWorld(game.run, proc() =
    var perSlot:array[10,seq[ReplayAction]]
    while index<tape.actions.len and tape.actions[index].tick==uint32(game.run.world.tick):
      let a=tape.actions[index]
      perSlot[game.run.world.heroIndex(a.heroId)].add(a)
      inc index
    let drafting=game.run.world.phase==Drafting
    # All public frames captured before any recorded command changes live state.
    if not drafting:
      for slot,h in game.run.world.heroes:
        if h.hp<=0 or h.state==Dying:continue
        var objects=newJArray()
        for j in 0..<game.run.world.worldObjectCount(h.id):
          var v:WorldObject
          if not game.run.world.worldObjectAt(h.id,j,v):continue
          let d=gap(h.position,v.position)
          if d>18 or v.id==h.id:continue
          objects.add(%*{"id":v.id,"kind":v.kind,"team":v.team.ord,
            "hp":v.hp,"max_hp":v.maxHp,"alive":v.alive,"distance":d,
            "x":mapCoordinate(v.position.x,h.team),"y":mapCoordinate(v.position.z,h.team),
            "target":v.targetId,"returning":v.returning,"camp":v.camp,"leader":v.leader})
        var commands=newJArray()
        for a in perSlot[slot]:
          commands.add(%*{"kind":a.kind,"slot":a.slot,"first":a.first,"second":a.second})
        frames.add(%*{"tick":game.run.world.tick,"slot":slot,"class": $h.class,
          "hp":h.hp,"max_hp":h.maxHp,"mana":h.mana,"max_mana":h.maxMana,
          "level":h.level,"gold":h.gold,"own_keep":h.canShop(),
          "x":mapCoordinate(h.position.x,h.team),"y":mapCoordinate(h.position.z,h.team),
          "attack_range":heroAttackRange(h.class).float/WorldScale.float,
          "attack_damage":h.heroAttackDamage(),"objects":objects,"commands":commands})
      inc decisions
    for offset in 0..<10:
      let slot=if drafting:offset else:(game.run.world.heroTurnStart+offset) mod 10
      for a in perSlot[slot]:discard applyRecorded(game.run.world,a)
    if not drafting:game.run.world.heroTurnStart=(game.run.world.heroTurnStart+1) mod 10
  )
  doAssert game.run.stateHash()==tape.hashes[game.run.world.tick-1], "Hash mismatch at " & $game.run.world.tick
  for e in game.run.world.events:
    if e.kind in {Death,HeroDrafted,ItemPurchased,ItemConsumed,PortalStarted,PortalCompleted,PortalInterrupted,CampEngaged,CampReturning,RecoveryStarted,AbilityLeveled}:
      events.add(%*{"tick":e.tick,"kind": $e.kind,"actor":e.actor.player,"target":e.target.player,
        "target_kind":e.target.kind,"target_id":e.target.id,"detail":e.detail,"amount":e.amount,"cause": $e.cause})
doAssert index==tape.actions.len
echo $(%*{"valid":true,"ticks":game.run.world.tick,"commands":index,"decisions":decisions,
  "scope":"Public per-actor predecision observations paired with retrospective submitted commands; events are separately replay truth. No private policy source, no causal proxy.","frames":frames,"events":events})
