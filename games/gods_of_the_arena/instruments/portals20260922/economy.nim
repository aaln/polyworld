## Retrospective XP and resource attribution. Never available to live policies.
import std/[json, tables]
import ../[game, sim, replays, content]

doAssert run.replayMode
# Event entity kinds from pinned ffcedcd sim.nim (private host constants).
const HeroObjectKind = 2'i32
const FootmanObjectKind = 3'i32
var xpSources: array[10, Table[string, int64]]
var rejected: array[10, Table[string, int]]
var heroKills, creepKills: array[10, int]
var purchases = newJArray()
var spells: array[10, int]

while run.world.tick < run.replayData.hashes.len:
  advanceGame()
  for e in run.world.events:
    let actor = e.actor.player
    let target = e.target.player
    if e.kind == XpGained and target >= 0 and target < 10:
      let source = if e.actor.kind == HeroObjectKind: "hero"
                   elif e.actor.kind == FootmanObjectKind: "creep"
                   else: "structure_or_other"
      xpSources[target][source] = xpSources[target].getOrDefault(source) + e.amount
    if actor >= 0 and actor < 10:
      if e.kind == ItemPurchased:
        purchases.add(%*{"tick": e.tick, "slot": actor, "item": e.detail,
                         "hp": run.world.heroes[actor].hp,
                         "level": run.world.heroes[actor].level})
      if e.kind == SpellReleased: inc spells[actor]
      if e.kind == ActionRejected:
        let key = $e.error
        rejected[actor][key] = rejected[actor].getOrDefault(key) + 1
      if e.kind == Death:
        if e.target.kind == HeroObjectKind: inc heroKills[actor]
        if e.target.kind == FootmanObjectKind: inc creepKills[actor]

doAssert run.hashCheck.mismatches == 0
doAssert run.replayPlayer.actionIndex == run.replayData.actions.len
var heroes = newJArray()
for i, h in run.world.heroes:
  var total: int64
  var sources = newJObject()
  var errors = newJObject()
  for k, v in xpSources[i]:
    total += v
    sources[k] = %v
  for k, v in rejected[i]: errors[k] = %v
  doAssert total == h.totalXp
  heroes.add(%*{"slot": i, "class": $h.class, "total_xp": h.totalXp,
    "xp_sources": sources, "hero_kills": heroKills[i], "creep_last_hits": creepKills[i],
    "deaths": h.deaths, "level": h.level, "spells": spells[i],
    "rejected": errors})
echo $(%*{"ticks": run.world.tick, "hash_mismatches": run.hashCheck.mismatches,
          "heroes": heroes, "purchases": purchases})
