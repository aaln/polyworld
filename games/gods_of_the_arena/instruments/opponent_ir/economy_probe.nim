## Logging-only source-reveal audit, compiled against the pinned overlay.
import std/[os, json]
import examples/gods_of_the_arena/[replays, sim, maps, content]

let data = loadReplay(paramStr(1))
let game = newGame(generateMap(data.config.seed, data.config.mapPreset),
  data.header.setup.spawnIntervalTicks.int32, data.header.setup.heroes.len, true, data)
game.historyPlayback = true
game.replayPlayer = initReplayPlayer(data)
var samples = newJArray()
var transitions = newJArray()
var previousLevel = newSeq[int](game.world.heroes.len)
var previousAlive = newSeq[bool](game.world.heroes.len)

proc snapshot(hero: Hero): JsonNode =
  %*{"id": hero.id, "team": hero.team.ord, "class": $hero.class,
    "level": hero.level, "xp": hero.xp, "total_xp": hero.totalXp,
    "gold": hero.gold, "hp": hero.hp, "max_hp": hero.maxHp,
    "damage": hero.heroAttackDamage(), "attacks_landed": hero.attacksLanded,
    "inventory": hero.inventory, "item_counts": hero.itemCounts,
    "x": mapCoordinate(hero.position.x), "y": mapCoordinate(hero.position.z)}

for i, hero in game.world.heroes:
  previousLevel[i] = hero.level
  previousAlive[i] = hero.hp > 0
  samples.add %*{"tick": 0, "hero": snapshot(hero)}
for tick in 1 .. data.hashes.len:
  game.tickWorld(proc() = discard)
  doAssert game.hashCheck.mismatches == 0
  for i, hero in game.world.heroes:
    if hero.level != previousLevel[i] or (hero.hp > 0) != previousAlive[i]:
      transitions.add %*{"tick": tick, "hero": snapshot(hero),
        "level_changed": hero.level != previousLevel[i],
        "alive_changed": (hero.hp > 0) != previousAlive[i]}
    previousLevel[i] = hero.level
    previousAlive[i] = hero.hp > 0
    if tick mod 1000 == 0 or tick == data.hashes.len:
      samples.add %*{"tick": tick, "hero": snapshot(hero)}
doAssert game.world.tick == data.hashes.len
doAssert game.replayPlayer.actionIndex == data.actions.len
echo $(%*{"schema": "gota-source-economy-replay/1", "ticks": game.world.tick,
  "all_state_hashes_equal": true, "all_actions_consumed": true,
  "setup": data.header.setup.heroes, "samples": samples, "transitions": transitions,
  "rewards": economyRewardTrace, "purchases": economyPurchaseTrace,
  "basic_hits": economyBasicTrace,
  "scope": "Retrospective truth from logging-only pinned simulator; not observation-model features."})
