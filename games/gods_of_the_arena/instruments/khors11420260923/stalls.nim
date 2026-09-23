## Retrospective XP droughts and resource time. No opponent memory or source.
import std/[json, tables]
import ../[game, sim, replays, content]
doAssert run.replayMode
var counters: array[10, Table[string,int64]]
var windowStats: array[10, Table[int,Table[string,int64]]]
var lastXp, dryTicks, maxDry: array[10,int64]
var observedDraft: array[10,bool]
var available: array[HeroClass,bool]
for x in HeroClass: available[x]=true
var draft=newJArray()
var portals=newJArray()
var battleStart = -1
proc add(t:var Table[string,int64],s:string,n:int64=1)=t[s]=t.getOrDefault(s)+n
proc obj(t:Table[string,int64]):JsonNode=
  result=newJObject()
  for k,v in t:result[k] = %v
while run.world.tick<run.replayData.hashes.len:
  advanceGame()
  for i,h in run.world.heroes:
    if h.drafted and not observedDraft[i]:
      var choices=newJArray()
      for cl in HeroClass:
        if available[cl]: choices.add(%($cl))
      draft.add(%*{"tick":run.world.tick,"slot":i,"class": $h.class,"available_before":choices})
      available[h.class]=false
      observedDraft[i]=true
  if run.world.phase==Drafting:continue
  if battleStart<0:battleStart=run.world.tick.int
  let window=(run.world.tick.int-battleStart) div (TickRate*60)
  for i,h in run.world.heroes:
    let alive=h.hp>0 and h.state!=Dying
    counters[i].add("battle_ticks")
    windowStats[i].mgetOrPut(window,initTable[string,int64]()).add("ticks")
    let dxp=h.totalXp-lastXp[i]
    if dxp>0:dryTicks[i]=0
    else:inc dryTicks[i]
    lastXp[i]=h.totalXp
    maxDry[i]=max(maxDry[i],dryTicks[i])
    windowStats[i][window].add("xp",dxp)
    let state=if not alive:"dead" elif h.canShop():"keep" else:"field"
    counters[i].add(state & "_ticks")
    windowStats[i][window].add(state & "_ticks")
    if alive:
      if dryTicks[i]>=30*TickRate:
        counters[i].add(state & "_after30s_without_xp_ticks")
        windowStats[i][window].add(state & "_after30s_without_xp_ticks")
      if h.hp*100>=h.maxHp*60:
        counters[i].add("healthy_" & state & "_ticks")
        if dryTicks[i]>=30*TickRate:
          counters[i].add("healthy_" & state & "_after30s_without_xp_ticks")
      if h.attackObjectId==0:
        counters[i].add(state & "_without_attack_target_ticks")
      if h.gold>=500: counters[i].add(state & "_gold500_ticks")
  for e in run.world.events:
    let actor=e.actor.player
    if actor in 0..9:
      if e.kind in {PortalStarted,PortalCompleted,PortalInterrupted}:
        let h=run.world.heroes[actor]
        portals.add(%*{"tick":e.tick,"kind": $e.kind,"slot":actor,"hp":h.hp,"max_hp":h.maxHp,"can_shop":h.canShop(),"x":h.position.x,"z":h.position.z})
      if e.kind==Healing:counters[actor].add("healing_caused",e.amount)
doAssert run.hashCheck.mismatches==0
doAssert run.replayPlayer.actionIndex==run.replayData.actions.len
var heroes=newJArray()
for i,h in run.world.heroes:
  var windows=newJArray()
  for w in 0..((run.world.tick.int-battleStart) div (TickRate*60)):
    if windowStats[i].hasKey(w):
      windows.add(%*{"index":w,"values":obj(windowStats[i][w]),"full_minute":windowStats[i][w].getOrDefault("ticks")==TickRate*60})
  doAssert lastXp[i]==h.totalXp
  heroes.add(%*{"slot":i,"class": $h.class,"totals":obj(counters[i]),"max_without_xp_ticks":maxDry[i],"windows":windows})
echo $(%*{"ticks":run.world.tick,"battle_start_tick":battleStart,"hash_mismatches":run.hashCheck.mismatches,"all_actions_consumed":true,"heroes":heroes,"draft":draft,"portals":portals,"scope":"Post-tick full truth. Healthy meansHP>=60%; drought is30world seconds without XP including dead time. No-target is not proof of inactivity; geometry and intent remain unidentified. Full windows aligned to battle start; final partial window separate."})
