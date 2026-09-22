## Retrospective actual-engine events. Never exposed as policy observations.
import std/[json, tables]
import ../[game, sim, replays, content]

const HeroObjectKind = 2
const FootmanObjectKind = 3
doAssert run.replayMode
var xpCreeps, xpHeroes, xpOther, creepGold: array[10, int64]
var aliveTicks, homeTicks: array[10, int64]
var portals, completed, interrupted: array[10, int]
var purchases: array[10, Table[string, int]]
var rejected: array[10, Table[string, int]]
var lastHit, hitGaps: array[10, int32]
var hitCounts: array[10, int]

while run.world.tick < run.replayData.hashes.len:
  advanceGame()
  for e in run.world.events:
    let slot = e.target.player
    if e.kind == XpGained and slot >= 0:
      if e.actor.kind == FootmanObjectKind: xpCreeps[slot] += e.amount
      elif e.actor.kind == HeroObjectKind: xpHeroes[slot] += e.amount
      else: xpOther[slot] += e.amount
    if e.kind == GoldGained and slot >= 0 and e.actor.kind == FootmanObjectKind:
      creepGold[slot] += e.amount
    let actor = e.actor.player
    if actor >= 0:
      case e.kind
      of ItemPurchased:
        let key = $e.detail
        purchases[actor][key] = purchases[actor].getOrDefault(key) + 1
      of PortalStarted: inc portals[actor]
      of PortalCompleted: inc completed[actor]
      of PortalInterrupted: inc interrupted[actor]
      of ActionRejected:
        let key = $e.action & ":" & $e.error
        rejected[actor][key] = rejected[actor].getOrDefault(key) + 1
      of Damage:
        if e.cause == BasicAttack and e.amount > 0:
          if lastHit[actor] > 0: hitGaps[actor] += e.tick - lastHit[actor]
          lastHit[actor] = e.tick
          inc hitCounts[actor]
      else: discard
  if run.world.phase == Playing:
    for i,h in run.world.heroes:
      if h.hp > 0:
        inc aliveTicks[i]
        if h.canShop: inc homeTicks[i]

doAssert run.hashCheck.mismatches == 0
doAssert run.replayPlayer.actionIndex == run.replayData.actions.len
var heroes = newJArray()
for i,h in run.world.heroes:
  doAssert xpCreeps[i] + xpHeroes[i] + xpOther[i] == h.totalXp
  heroes.add(%*{"slot":i,"class":h.class.ord,"xp":h.totalXp,
    "creep_xp":xpCreeps[i],"hero_xp":xpHeroes[i],"other_xp":xpOther[i],
    "last_hit_gold":creepGold[i],"alive_ticks":aliveTicks[i],"shop_ticks":homeTicks[i],
    "portals_started":portals[i],"portals_completed":completed[i],
    "portals_interrupted":interrupted[i],"purchases":purchases[i],
    "rejections":rejected[i],"basic_damage_events":hitCounts[i],
    "inter_hit_ticks":hitGaps[i]})
echo $(%*{"heroes":heroes,"ticks":run.world.tick,"hash_mismatches":run.hashCheck.mismatches,
  "scope":"Retrospective typed events from an exact full replay, not live observations or an opponent proxy."})
