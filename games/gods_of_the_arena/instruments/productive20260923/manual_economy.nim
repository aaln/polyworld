## Full replay resource audit for manual coaching; retrospective, never a live feature.
import std/[json,tables]
import ../[game,sim,replays,content]
doAssert run.replayMode
var counts:array[10,Table[string,int64]]
var buys:array[10,JsonNode]
for i in 0..9:buys[i]=newJArray()
proc add(t:var Table[string,int64],k:string,n:int64=1)=t[k]=t.getOrDefault(k)+n
proc obj(t:Table[string,int64]):JsonNode=
  result=newJObject()
  for k,v in t:result[k] = %v
proc itemName(detail:int32):string=
  if detail>=Item.low.ord and detail<=Item.high.ord: $Item(detail) else: "UnknownItem"
for a in run.replayData.actions:
  let i=run.world.heroIndex(a.heroId)
  if i in 0..9:counts[i].add("orders")
while run.world.tick<run.replayData.hashes.len:
  advanceGame()
  if run.world.phase!=Drafting:
    for i,h in run.world.heroes:
      let state=if h.hp<=0 or h.state==Dying:"dead" elif h.canShop():"keep" else:"field"
      counts[i].add(state & "_ticks")
      if state=="field":
        if h.hp*100<h.maxHp*50:counts[i].add("field_low_health_ticks")
        if h.mana*100<h.maxMana*25:counts[i].add("field_low_mana_ticks")
        if h.gold>=500:counts[i].add("field_gold500_ticks")
  for e in run.world.events:
    let i=e.actor.player;let t=e.target.player
    if e.kind==ActionRejected and i in 0..9:
      counts[i].add("rejected");counts[i].add("rejected_" & $e.error)
      counts[i].add("rejected_" & $e.action & "_" & $e.slot & "_" & $e.error)
    if t in 0..9:
      case e.kind
      of GoldGained:counts[t].add("gold_earned",e.amount)
      of GoldSpent:
        counts[t].add("gold_spent",-e.amount)
        if e.cause==Buyback:counts[t].add("buybacks");counts[t].add("buyback_gold",-e.amount)
      of ItemPurchased:
        counts[t].add("purchased_" & itemName(e.detail))
        buys[t].add(%*{"tick":e.tick,"item":itemName(e.detail)})
      of ItemConsumed:counts[t].add("used_" & itemName(e.detail));counts[t].add("consumables_used")
      of Healing:
        if e.cause==ItemEffect:counts[t].add("healing_item_" & itemName(e.detail),e.amount)
        else:counts[t].add("healing_other",e.amount)
      of ManaChanged:
        if e.cause==ItemEffect and e.amount>0:counts[t].add("mana_item_" & itemName(e.detail),e.amount)
      of RecoveryInterrupted:counts[t].add("interrupted_" & itemName(e.detail))
      of XpGained:
        if e.cause==NearbyKill:counts[t].add("xp_creep_shared",e.amount)
        elif e.actor.kind==3:counts[t].add("xp_creep_at_last_hit",e.amount)
      else:discard
    if e.kind==Death and i in 0..9:
      if e.target.kind==2:counts[i].add("hero_kills")
      if e.target.kind==3:counts[i].add("creep_last_hits")
doAssert run.hashCheck.mismatches==0
doAssert run.replayPlayer.actionIndex==run.replayData.actions.len
var heroes=newJArray()
for i,h in run.world.heroes:
  heroes.add(%*{"slot":i,"class": $h.class,"xp":h.totalXp,"gold_end":h.gold,"deaths":h.deaths,"counts":obj(counts[i]),"purchases":buys[i]})
echo $(%*{"ticks":run.world.tick,"hash_mismatches":run.hashCheck.mismatches,"all_actions_consumed":true,"heroes":heroes,"scope":"Typed accepted resource events and exact replay. Field/keep/dead time excludes draft. Ratios are diagnostic; no causal effect of spending inferred."})
