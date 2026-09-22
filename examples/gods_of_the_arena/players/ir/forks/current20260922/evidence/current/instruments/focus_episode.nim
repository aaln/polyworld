## Exact replay diagnosis for own slot 5 and relh slot 4 in the supplied episode.
import std/[json]
import ../[game, sim]

doAssert run.replayMode
var records = newJArray()
var frames = newJArray()
while run.world.tick < run.replayData.hashes.len:
  advanceGame()
  for e in run.world.events:
    if e.kind == HeroDrafted or
        (e.target.player in [4,5] and e.kind in {Damage,Death,XpGained,LevelChanged,AbilityLeveled}) or
        (e.actor.player in [4,5] and e.kind in {ItemPurchased,PortalStarted,PortalCompleted,PortalInterrupted}):
      records.add(%e)
  if run.world.phase == Playing and run.world.battleTick mod 24 == 0:
    var heroes = newJArray()
    for slot in [4,5]:
      let h=run.world.heroes[slot]
      var visible = newJArray()
      for i in 0..<run.world.worldObjectCount(h.id):
        var o: WorldObject
        if run.world.worldObjectAt(h.id,i,o):
          if o.kind == 2 and o.team != h.team:visible.add(%o)
      heroes.add(%*{"slot":slot,"class":h.class.ord,"hp":h.hp,"level":h.level,
        "xp":h.totalXp,"gold":h.gold,"position":h.position,"layer":h.navLayer,
        "target":h.attackObjectId,"in_spawn":h.inOwnSpawn,"can_shop":h.canShop,
        "visible_enemy_heroes":visible})
    frames.add(%*{"tick":run.world.tick,"battle_tick":run.world.battleTick,"heroes":heroes})
doAssert run.hashCheck.mismatches == 0
doAssert run.replayPlayer.actionIndex == run.replayData.actions.len
echo $(%*{"ticks":run.world.tick,"hash_mismatches":run.hashCheck.mismatches,
  "events":records,"frames":frames,
  "scope":"Actual replay events and post-tick public object samples; not internal policy beliefs or predecision rule attribution."})
