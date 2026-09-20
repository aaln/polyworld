## Inspect hosted action tapes with the exact published game source.
## Copy this file into that checkout's players/ir before compiling.
import std/[json, strutils]
import ../../[game, sim, replays]

if not run.replayMode:
  raise newException(ValueError, "--replay is required")

var
  deaths, aliveTicks, stationaryTicks, towerTargetTicks: array[10, int]
  commands: array[10, array[6, int]]
  buyAttempts: array[10, array[21, int]]
  firstGearTick: array[10, int]
  wasDying: array[10, bool]
  previous: array[10, WorldPoint]
  events = newJArray()

for slot, hero in run.world.heroes:
  previous[slot] = hero.position
  firstGearTick[slot] = -1
for action in run.replayData.actions:
  let slot = heroIndex(run.world, action.heroId)
  inc commands[slot][action.kind]
  if action.kind == ActionBuyItem and action.first in 0..20:
    inc buyAttempts[slot][action.first]

while run.world.tick < run.replayData.hashes.len and not run.world.gameOver:
  advanceGame()
  for slot, hero in run.world.heroes:
    if hero.state == Dying and not wasDying[slot]:
      inc deaths[slot]
      events.add(%*{"tick": run.world.tick, "slot": slot, "event": "death",
        "level": hero.level, "gold": hero.gold, "inventory": hero.inventory})
    wasDying[slot] = hero.state == Dying
    if hero.state != Dying:
      inc aliveTicks[slot]
      if hero.position == previous[slot]:
        inc stationaryTicks[slot]
      for tower in run.world.towers:
        if tower.hp > 0 and tower.targetId == hero.id:
          inc towerTargetTicks[slot]
          break
    if firstGearTick[slot] < 0:
      for item in hero.inventory:
        if item.ord > 4:
          firstGearTick[slot] = run.world.tick
          break
    previous[slot] = hero.position

if run.hashCheck.mismatches != 0 or run.replayPlayer.actionIndex != run.replayData.actions.len:
  raise newException(ValueError, "hosted replay does not match this simulation")

var heroes = newJArray()
for slot, hero in run.world.heroes:
  heroes.add(%*{"slot": slot, "class": $hero.class, "team": hero.team.ord,
    "score": (if run.world.gameOver and run.world.winner == hero.team: 1 else: 0),
    "deaths": deaths[slot], "alive_ticks": aliveTicks[slot],
    "stationary_alive_ticks": stationaryTicks[slot],
    "tower_target_ticks": towerTargetTicks[slot], "first_gear_tick": firstGearTick[slot],
    "level": hero.level, "gold": hero.gold, "inventory": hero.inventory,
    "item_counts": hero.itemCounts, "command_attempts_by_kind": commands[slot],
    "buy_attempts_by_item": buyAttempts[slot]})
echo $(%*{"ticks": run.world.tick, "hash_mismatches": run.hashCheck.mismatches,
  "actions_consumed": run.replayPlayer.actionIndex,
  "state_hash": run.stateHash().toHex(16), "heroes": heroes, "events": events})
