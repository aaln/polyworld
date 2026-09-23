## Full replay validation, with fine-grained truth only for recorded coaching context.
import std/json
import ../[game,sim,content,replays]
doAssert run.replayMode
var frames=newJArray()
var events=newJArray()
while run.world.tick < run.replayData.hashes.len:
  advanceGame()
  let h=run.world.heroes[4]
  if run.world.tick in 3800..6500:
    if run.world.tick mod 6==0:
      frames.add(%*{"tick":run.world.tick,"hp":h.hp,"max_hp":h.maxHp,"mana":h.mana,"max_mana":h.maxMana,"xp":h.totalXp,"level":h.level,"x":h.position.x,"z":h.position.z,"in_keep":h.canShop,"in_spawn":h.inOwnSpawn,"move_target":h.hasMoveTarget,"attack_moving":h.attackMoving,"move_x":h.moveTileX,"move_y":h.moveTileY,"home_x":mapCoordinate(h.spawnPosition.x,h.team),"home_y":mapCoordinate(h.spawnPosition.z,h.team),"target_id":h.attackObjectId})
    for e in run.world.events:
      if e.actor.player==4 or e.target.player==4:
        if e.kind in {Healing,Damage,SpellReleased,PortalStarted,PortalCompleted,ItemConsumed,ActionRejected}:
          events.add(%*{"tick":e.tick,"kind": $e.kind,"actor":e.actor.player,"target":e.target.player,"cause": $e.cause,"detail":e.detail,"amount":e.amount,"error": $e.error})
doAssert run.hashCheck.mismatches==0
var actions=newJArray()
for a in run.replayData.actions:
  if a.heroId==run.world.heroes[4].id and a.tick.int in 3800..6500:
    actions.add(%*{"tick":a.tick,"kind": $a.kind,"first":a.first,"second":a.second})
echo $(%*{"ticks":run.world.tick,"hash_mismatches":run.hashCheck.mismatches,"slot":4,"class": $run.world.heroes[4].class,"frames":frames,"events":events,"actions":actions,"scope":"Recorded episode4a6d182f. Full truth used only to review coaching, never as a live feature or a competitive counterfactual."})
