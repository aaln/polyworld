## Portal diagnosis from complete, hash-checked current-engine replays.
import std/[json, math]
import ../[game, sim, replays, content]

doAssert run.replayMode
var records = newJArray()
var starts, completed, interrupted, deadChannel: array[10, int]
var lowFieldTicks, readyLowFieldTicks, baseHomeStarts: array[10, int]
var home: array[10, WorldPoint]
var initialized: array[10, bool]
var previousChannel: array[10, int32]

proc tile(p: WorldPoint, t: Team): JsonNode =
  %*[mapCoordinate(p.x,t),mapCoordinate(p.z,t)]

proc dist(a,b: WorldPoint): float =
  sqrt(float((int64(a.x)-b.x)*(int64(a.x)-b.x) +
    (int64(a.z)-b.z)*(int64(a.z)-b.z))) / WorldScale.float

while run.world.tick < run.replayData.hashes.len:
  for i,h in run.world.heroes:
    previousChannel[i] = h.portalEnds
    if not initialized[i] and run.world.phase == Playing:
      home[i] = h.position
      initialized[i] = true
  advanceGame()
  for e in run.world.events:
    let slot=e.actor.player
    if slot < 0 or slot >= 10: continue
    let h=run.world.heroes[slot]
    if e.kind in {PortalStarted,PortalCompleted,PortalInterrupted}:
      if e.kind==PortalStarted:
        inc starts[slot]
        if h.canShop and dist(h.portalDestination,home[slot]) < 15:
          inc baseHomeStarts[slot]
      if e.kind==PortalCompleted:inc completed[slot]
      if e.kind==PortalInterrupted:inc interrupted[slot]
      records.add(%*{"tick":e.tick,"slot":slot,"kind": $e.kind,
        "class":h.class.ord,"hp":h.hp,"max_hp":h.maxHp,
        "position":tile(h.position,h.team),"destination":tile(h.portalDestination,h.team),
        "home":tile(home[slot],h.team),"source_in_keep":h.canShop,
        "source_in_spawn":h.inOwnSpawn,"distance_home":dist(h.position,home[slot]),
        "destination_distance_home":dist(h.portalDestination,home[slot]),
        "travel_tiles":dist(h.position,h.portalDestination),"tower":e.target.id})
    if e.kind==ActionRejected and e.action==ActionUseItemAt:
      records.add(%*{"tick":e.tick,"slot":slot,"kind":"PortalRejected","error": $e.error})
  if run.world.phase==Playing:
    for i,h in run.world.heroes:
      if previousChannel[i]>0 and h.hp<=0 and h.portalEnds==0:inc deadChannel[i]
      if h.hp>0 and h.hp*100<h.maxHp*30 and not h.canShop:
        inc lowFieldTicks[i]
        if h.portalEnds==0 and h.portalCooldownEnds<=run.world.tick and PortalScroll in h.inventory:
          inc readyLowFieldTicks[i]

doAssert run.hashCheck.mismatches==0
doAssert run.replayPlayer.actionIndex==run.replayData.actions.len
var heroes=newJArray()
for i,h in run.world.heroes:
  heroes.add(%*{"slot":i,"class":h.class.ord,"xp":h.totalXp,"deaths":h.deaths,
    "portals_started":starts[i],"completed":completed[i],"interrupted":interrupted[i],
    "died_during_channel":deadChannel[i],"home_portals_from_keep":baseHomeStarts[i],
    "low_field_ticks":lowFieldTicks[i],"ready_low_field_ticks":readyLowFieldTicks[i]})
echo $(%*{"ticks":run.world.tick,"hash_mismatches":run.hashCheck.mismatches,
  "heroes":heroes,"portals":records,"scope":"Retrospective full replay; no hidden state is exposed to the policy. Home-origin classification uses the actual initial spawn, not a replay camera inference."})
