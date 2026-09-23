## Full replay outcome trace; never provides hidden truth to a live policy.
import std/[json,tables]
import ../[game,sim,replays,content]
doAssert run.replayMode
var counts:array[10,Table[string,int64]]
var minutes:array[10,Table[int,Table[string,int64]]]
var buildings=newJArray()
var initialBuildings=newJArray()
for b in run.world.buildings:
  initialBuildings.add(%*{"id":b.id,"team":b.team.ord,"kind": $b.kind,"lane":b.lane,"x":b.position.x,"z":b.position.z})
proc add(t:var Table[string,int64],k:string,n:int64=1)=t[k]=t.getOrDefault(k)+n
proc obj(t:Table[string,int64]):JsonNode=
  result=newJObject()
  for k,v in t:result[k] = %v
proc kind(id:int32):string=
  for h in run.world.heroes:
    if h.id==id:return "hero"
  for f in run.world.footmen:
    if f.id==id:return "creep"
  for b in run.world.buildings:
    if b.id==id:return $b.kind
  for f in run.world.forts:
    if f.id==id:return "god"
  "none"
var ai=0
while run.world.tick<run.replayData.hashes.len:
  while ai<run.replayData.actions.len and run.replayData.actions[ai].tick==uint32(run.world.tick):
    let a=run.replayData.actions[ai]
    let i=run.world.heroIndex(a.heroId)
    if i in 0..9:
      counts[i].add("command_" & $a.kind)
      if a.kind==ActionAttackTarget:counts[i].add("attack_target_" & kind(a.first))
      if a.kind==ActionCastTarget:counts[i].add("cast_target_" & kind(a.first))
    inc ai
  advanceGame()
  for e in run.world.events:
    let i=e.actor.player
    let t=e.target.player
    if e.kind==XpGained and t in 0..9:
      let k=if e.cause==GodDestroyed:"god" elif e.actor.kind==2:"hero" elif e.actor.kind==3:"creep" else:"structure"
      minutes[t].mgetOrPut(e.tick.int div 1440,initTable[string,int64]()).add(k,e.amount)
    if i in 0..9:
      if e.kind==Damage and e.cause==BasicAttack:counts[i].add("landed_basic_" & kind(e.target.id))
      if e.kind==ActionRejected:counts[i].add("rejected_" & $e.action & "_slot" & $e.slot & "_" & $e.error)
      if e.kind==EntityRespawned and e.cause==Buyback:counts[i].add("buybacks")
    if e.kind==Death and e.target.kind in [4'i32,5'i32]:
      buildings.add(%*{"tick":e.tick,"actor":i,"target":e.target.id,"kind":kind(e.target.id),"target_team":e.target.team,"cause": $e.cause})
doAssert run.hashCheck.mismatches==0
doAssert run.replayPlayer.actionIndex==run.replayData.actions.len
var heroes=newJArray()
for i,h in run.world.heroes:
  var ms=newJObject()
  for m,t in minutes[i]:ms[$m]=obj(t)
  heroes.add(%*{"slot":i,"class": $h.class,"counts":obj(counts[i]),"minute_xp_sources":ms})
echo $(%*{"ticks":run.world.tick,"hash_mismatches":run.hashCheck.mismatches,"heroes":heroes,"building_deaths":buildings,"initial_buildings":initialBuildings})
