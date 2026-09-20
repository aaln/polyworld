## Compile after copying into pinned game's players/ir/. No enemy VM is loaded.
import std/[json, os, strutils]
import ../../game
include ../../bots

proc applyReplayAction(world: World, action: ReplayAction): bool {.discardable.} =
  case action.kind
  of ActionWalkTo: applyWalkTo(world, action.heroId, action.first, action.second)
  of ActionAttackMove: applyAttackMove(world, action.heroId, action.first, action.second)
  of ActionAttackTarget: applyAttackTarget(world, action.heroId, action.first)
  of ActionBuyItem: applyBuyItem(world, action.heroId, action.first)
  of ActionUseItem: applyUseItem(world, action.heroId, action.first)
  of ActionCastTarget .. ActionCastPoint - 1:
    applyCastTarget(world, action.heroId, int32(action.kind-ActionCastTarget), action.first)
  of ActionCastPoint .. ActionManualSpells - 1:
    applyCastPoint(world, action.heroId, int32(action.kind-ActionCastPoint), action.first, action.second)
  of ActionManualSpells:
    let index=world.heroIndex(action.heroId)
    if index>=0:world.heroes[index].manualSpells=action.first!=0
    false
  else:raise newException(ReplayError,"Invalid recorded action")

if not game.run.replayMode:raise newException(ValueError,"--replay required")
let tape=game.run.replayData
let subject=parseInt(getEnv("OBSERVER_SLOT","0"))
if subject<0 or subject>=10:raise newException(ValueError,"Invalid observer")
var terrain=newJArray()
for y in 0..<mapTiles():
  var row=""
  for x in 0..<mapTiles():
    row.add(if terrainValue(x.int32,y.int32,0,TerrainWalkableField)!=0:'.' else:'#')
  terrain.add(%row)
echo $(%*{"type":"header","schema":"gota-observer-trajectory/1","version":"2026.9.16.5",
  "source":"f2ab9598d8f8001b6beae3e66404e341770c803f","observer_slot":subject,
  "columns":["id","kind","team","class","x","y","hp","alive","target","vx","vy","level","mana","items","item_counts"],
  "terrain":terrain,"tick_rate":TickRate,
  "note":"Predecision snapshot; exactly host-visible integer fields. Target 0 means none OR hidden. No decisions while observer Dying. Truth only in aggregate visibility audit."})
game.run.historyPlayback=false
var index=0
var liveOpponentTicks=0
var seenOpponentTicks=0
var deadObserverTicks=0
while game.run.world.tick<tape.hashes.len and not game.run.world.gameOver:
  tickWorld(game.run,proc() =
    var perSlot:array[10,seq[ReplayAction]]
    while index<tape.actions.len and tape.actions[index].tick==uint32(game.run.world.tick):
      let a=tape.actions[index]
      if a.kind==ActionManualSpells:discard applyReplayAction(game.run.world,a)
      else:perSlot[heroIndex(game.run.world,a.heroId)].add(a)
      inc index
    for offset in 0..<10:
      let slot=(game.run.world.heroTurnStart+offset) mod 10
      if slot==subject:
        let hero=game.run.world.heroes[slot]
        let available=hero.state!=Dying
        var values:seq[WorldObject]
        var observed=newJArray()
        if available:
          for i in 0..<game.run.world.worldObjectCount(hero.id):
            var value:WorldObject
            if game.run.world.worldObjectAt(hero.id,i,value):values.add(value)
          for v in values:
            var target=0'i32
            for candidate in values:
              if candidate.id==v.targetId:target=v.targetId
            observed.add(%*[v.id,v.kind,v.team.ord,v.class,mapCoordinate(v.position.x),mapCoordinate(v.position.z),
              max(v.hp,0'i32),int(v.alive),target,v.velocity.x,v.velocity.z,v.level,v.mana,v.inventory,v.itemCounts])
            if v.kind==2 and v.team!=hero.team and v.alive:inc seenOpponentTicks
        else:inc deadObserverTicks
        for other in game.run.world.heroes:
          if other.team!=hero.team and other.state!=Dying and other.hp>0:inc liveOpponentTicks
        echo $(%*{"type":"view","tick":game.run.world.tick,"available":available,"objects":observed})
      for a in perSlot[slot]:discard applyReplayAction(game.run.world,a)
    game.run.world.heroTurnStart=(game.run.world.heroTurnStart+1) mod 10
  )
  if game.run.stateHash()!=tape.hashes[game.run.world.tick-1]:
    raise newException(ReplayError,"State hash mismatch at tick " & $game.run.world.tick)
if index!=tape.actions.len or game.run.world.tick!=tape.hashes.len:raise newException(ReplayError,"Incomplete replay")
echo $(%*{"type":"validation","all_state_hashes_equal":true,"ticks":game.run.world.tick,"actions_consumed":index,
  "truth_live_opponent_ticks":liveOpponentTicks,"visible_live_opponent_ticks":seenOpponentTicks,"observer_dead_ticks":deadObserverTicks})
