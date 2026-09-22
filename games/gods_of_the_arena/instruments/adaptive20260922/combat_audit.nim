## Retrospective actual-effect audit; no hidden replay feature reaches a policy.
import std/[json, tables]
import ../[game, sim, replays, content]

doAssert run.replayMode
var totals: array[10, Table[string, int64]]
var spellCounts, spellDamage: array[10, Table[string, int64]]
var minuteXp: array[10, Table[string, int64]]
var frames = newJArray()
var moments = newJArray()

proc add(t: var Table[string, int64], key: string, amount: int64) =
  t[key] = t.getOrDefault(key) + amount

proc obj(t: Table[string, int64]): JsonNode =
  result = newJObject()
  for k,v in t: result[k] = %v

proc targetKind(kind: int32): string =
  if kind == 2: "hero"
  elif kind == 3: "creep"
  else: "structure"

while run.world.tick < run.replayData.hashes.len:
  advanceGame()
  if run.world.phase != Drafting:
    for i,h in run.world.heroes:
      if h.hp > 0 and h.state != Dying:
        totals[i].add("alive_ticks",1)
        if h.canShop(): totals[i].add("keep_ticks",1)
        else: totals[i].add("field_ticks",1)
        if h.mana * 4 < h.maxMana: totals[i].add("low_mana_ticks",1)
        if h.portalEnds > run.world.tick: totals[i].add("channel_ticks",1)
  for e in run.world.events:
    let actor = e.actor.player
    let target = e.target.player
    if e.kind == XpGained and target in 0..9:
      let source = if e.cause == GodDestroyed: "god" else: targetKind(e.actor.kind)
      totals[target].add("xp_" & source,e.amount)
      minuteXp[target].add($(e.tick div (TickRate * 60)),e.amount)
    if e.kind == Damage:
      if actor in 0..9:
        let cause = if e.cause == AbilityEffect: "spell" elif e.cause == BasicAttack: "basic" else: "other"
        totals[actor].add("damage_" & cause & "_" & targetKind(e.target.kind),e.amount)
        if e.cause == AbilityEffect: spellDamage[actor].add($Ability(e.detail),e.amount)
      if target in 0..9: totals[target].add("damage_taken",e.amount)
    if actor in 0..9:
      if e.kind == SpellReleased: spellCounts[actor].add($Ability(e.detail),1)
      if e.kind == GoldSpent: totals[actor].add("gold_spent",-e.amount)
      if e.kind == ActionRejected: totals[actor].add("rejected_" & $e.error,1)
      if e.kind == Death and e.target.kind == 2:
        moments.add(%*{"tick":e.tick,"kind":"hero_kill","actor":actor,"target":target,"cause": $e.cause,"ability_or_item":e.detail})
      if e.kind in {PortalStarted,PortalCompleted,PortalInterrupted,ItemPurchased}:
        moments.add(%*{"tick":e.tick,"kind": $e.kind,"actor":actor,"detail":e.detail})
  if run.world.tick mod (TickRate * 60) == 0:
    var heroes = newJArray()
    var creeps = newJArray()
    var buildings = newJArray()
    for i,h in run.world.heroes:
      heroes.add(%*{"slot":i,"class": $h.class,"x":h.position.x,"z":h.position.z,"hp":h.hp,"max_hp":h.maxHp,"mana":h.mana,"level":h.level,"xp":h.totalXp,"target":h.attackObjectId})
    for f in run.world.footmen:
      if f.hp > 0: creeps.add(%*{"team":f.team.ord,"x":f.position.x,"z":f.position.z})
    for b in run.world.buildings:
      if b.hp > 0: buildings.add(%*{"team":b.team.ord,"x":b.position.x,"z":b.position.z})
    frames.add(%*{"tick":run.world.tick,"heroes":heroes,"creeps":creeps,"buildings":buildings})

doAssert run.hashCheck.mismatches == 0
doAssert run.replayPlayer.actionIndex == run.replayData.actions.len
var heroes = newJArray()
for i,h in run.world.heroes:
  var xp:int64
  for k in ["hero","creep","structure","god"]: xp += totals[i].getOrDefault("xp_" & k)
  doAssert xp == h.totalXp
  heroes.add(%*{"slot":i,"class": $h.class,"xp":h.totalXp,"gold":h.gold,"deaths":h.deaths,"level":h.level,"totals":obj(totals[i]),"spells":obj(spellCounts[i]),"spell_damage":obj(spellDamage[i]),"xp_by_minute":obj(minuteXp[i])})
echo $(%*{"ticks":run.world.tick,"world_scale":WorldScale,"hash_mismatches":run.hashCheck.mismatches,"heroes":heroes,"frames":frames,"moments":moments,"scope":"Full truth and typed outcomes. Minute frames are post-tick truth, not live-policy observations or exact predecision affordances."})
