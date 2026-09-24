## Retrospective XP and resource attribution. Never available to live policies.
import std/[json, tables, sha1]
import ../[game, sim, replays, content]

doAssert run.replayMode
# Event entity kinds from pinned e42c4822 sim.nim (private host constants).
const HeroObjectKind = 2'i32
const FootmanObjectKind = 3'i32
var xpSources: array[10, Table[string, int64]]
var rejected: array[10, Table[string, int]]
var heroKills, creepKills, neutralKills: array[10, int]
var neutralDamageTaken: array[10, int64]
var heroXpVictims: array[10, array[10, int64]]
var purchases = newJArray()
var spells: array[10, int]
var campEngagements: array[10, int]
var creepShareXp: array[10, array[6, int64]]
var creepShareReceipts: array[10, array[6, int]]
var controlHits: array[10, Table[string, int]]

# Disjoint pre-tick states form an exact time/XP partition, not a causal model.
const StateNames = ["draft", "dead", "stunned", "portal_channel", "own_keep", "moving_field", "other_field"]
var stateTicks, stateXp: array[10, array[7, int64]]
var transitions: array[10, array[7, array[7, int]]]
var prior, current: array[10, int]
var lastXp, droughtMax, drought10, drought30: array[10, int32]
var lowHpTicks, silencedTicks, rootedTicks: array[10, int]
var goldSpent, buybackGold, buybacks: array[10, int]
var consumed, bought: array[10, Table[string, int]]

proc stateOf(h: Hero): int =
  if run.world.phase == Drafting: 0
  elif h.hp <= 0 or h.state == Dying: 1
  elif h.controls[StunControl].ends > run.world.tick: 2
  elif h.portalEnds > run.world.tick: 3
  elif h.canShop(): 4
  elif h.hasMoveTarget: 5
  else: 6

while run.world.tick < run.replayData.hashes.len:
  for i,h in run.world.heroes:
    current[i] = stateOf(h)
    inc stateTicks[i][current[i]]
    if run.world.tick > 0 and current[i] != prior[i]:
      inc transitions[i][prior[i]][current[i]]
    prior[i] = current[i]
    if current[i] == 0: lastXp[i] = run.world.tick
    if current[i] > 1:
      if h.hp * 100 < h.maxHp * 30: inc lowHpTicks[i]
      if h.controls[SilenceControl].ends > run.world.tick: inc silencedTicks[i]
      if h.controls[RootControl].ends > run.world.tick: inc rootedTicks[i]
      let age = run.world.tick - lastXp[i]
      droughtMax[i] = max(droughtMax[i], age)
      if age >= 10 * TickRate: inc drought10[i]
      if age >= 30 * TickRate: inc drought30[i]
  advanceGame()
  var recipients = initTable[int32, int]()
  for e in run.world.events:
    if e.kind == XpGained and e.actor.kind == FootmanObjectKind and e.amount > 0:
      recipients[e.actor.id] = recipients.getOrDefault(e.actor.id) + 1
  for e in run.world.events:
    let actor = e.actor.player
    let target = e.target.player
    if e.kind == Damage and e.actor.kind == 6 and target >= 0 and target < 10:
      neutralDamageTaken[target] += e.amount
    if e.kind == XpGained and target >= 0 and target < 10:
      let source = if e.actor.kind == HeroObjectKind: "hero"
                   elif e.actor.kind == FootmanObjectKind: "creep"
                   elif e.actor.kind == 6: "neutral"
                   else: "structure_or_other"
      xpSources[target][source] = xpSources[target].getOrDefault(source) + e.amount
      if e.actor.kind == FootmanObjectKind and e.amount > 0:
        let n = recipients[e.actor.id]
        doAssert n >= 1 and n <= 5
        creepShareXp[target][n] += e.amount
        inc creepShareReceipts[target][n]
      stateXp[target][current[target]] += e.amount
      if e.amount > 0: lastXp[target] = run.world.tick
      if e.actor.kind == HeroObjectKind:
        doAssert actor >= 0 and actor < 10
        heroXpVictims[target][actor] += e.amount
    if actor >= 0 and actor < 10:
      if e.kind == GoldSpent:
        goldSpent[actor] -= e.amount
        if e.cause == Buyback:
          buybackGold[actor] -= e.amount
          inc buybacks[actor]
      if e.kind == ItemConsumed:
        let key = $Item(e.detail)
        consumed[actor][key] = consumed[actor].getOrDefault(key) - int(e.amount)
      if e.kind == ItemPurchased:
        let key = $Item(e.detail)
        bought[actor][key] = bought[actor].getOrDefault(key) + int(e.amount)
        purchases.add(%*{"tick": e.tick, "slot": actor, "item": e.detail,
                         "hp": run.world.heroes[actor].hp,
                         "level": run.world.heroes[actor].level})
      if e.kind == SpellReleased: inc spells[actor]
      if e.kind == CampEngaged: inc campEngagements[actor]
      if e.kind in {Stunned, Silenced, Rooted} and e.target.kind == HeroObjectKind:
        let key = $e.kind
        controlHits[actor][key] = controlHits[actor].getOrDefault(key) + 1
      if e.kind == ActionRejected:
        let key = $e.error
        rejected[actor][key] = rejected[actor].getOrDefault(key) + 1
      if e.kind == Death:
        if e.target.kind == HeroObjectKind: inc heroKills[actor]
        if e.target.kind == FootmanObjectKind: inc creepKills[actor]
        if e.target.kind == 6: inc neutralKills[actor]

doAssert run.hashCheck.mismatches == 0
doAssert run.replayPlayer.actionIndex == run.replayData.actions.len
var heroes = newJArray()
for i, h in run.world.heroes:
  var total: int64
  var sources = newJObject()
  var errors = newJObject()
  var controls = newJObject()
  for k,v in controlHits[i]: controls[k] = %v
  for k, v in xpSources[i]:
    total += v
    sources[k] = %v
  for k, v in rejected[i]: errors[k] = %v
  doAssert total == h.totalXp
  var sharedTotal: int64
  for value in creepShareXp[i]: sharedTotal += value
  doAssert sharedTotal == xpSources[i].getOrDefault("creep")
  var counts, incomes, spentItems, usedItems = newJObject()
  var timeTotal, xpTotal: int64
  for state,name in StateNames:
    counts[name] = %stateTicks[i][state]
    incomes[name] = %stateXp[i][state]
    timeTotal += stateTicks[i][state]
    xpTotal += stateXp[i][state]
  doAssert timeTotal == int64(run.world.tick)
  doAssert xpTotal == int64(h.totalXp)
  for k,v in consumed[i]: usedItems[k] = %v
  for k,v in bought[i]: spentItems[k] = %v
  heroes.add(%*{"slot": i, "class": $h.class, "total_xp": h.totalXp,
    "creep_xp_by_recipient_count": creepShareXp[i],
    "creep_receipts_by_recipient_count": creepShareReceipts[i],
    "xp_sources": sources, "hero_kills": heroKills[i], "creep_last_hits": creepKills[i],
    "hero_xp_by_victim_slot": heroXpVictims[i],
    "camp_engagements": campEngagements[i], "neutral_kills":neutralKills[i], "neutral_damage_taken":neutralDamageTaken[i],
    "deaths": h.deaths, "level": h.level, "spells": spells[i],
    "rejected": errors, "hero_control_hits": controls,
    "time_ticks": counts, "xp_by_pre_tick_state": incomes, "transitions": transitions[i],
    "alive_low_hp_ticks": lowHpTicks[i], "alive_silenced_ticks": silencedTicks[i],
    "alive_rooted_ticks": rootedTicks[i], "alive_xp_drought_max_ticks": droughtMax[i],
    "alive_xp_drought_ge10_ticks": drought10[i], "alive_xp_drought_ge30_ticks": drought30[i],
    "gold_spent": goldSpent[i], "buyback_gold": buybackGold[i], "buybacks": buybacks[i],
    "items_bought": spentItems, "items_consumed": usedItems})
echo $(%*{"ticks": run.world.tick, "hash_mismatches": run.hashCheck.mismatches,
          "canonical_commands_sha1": $secureHash($run.replayData.actions),
          "state_names": StateNames, "heroes": heroes, "purchases": purchases})
