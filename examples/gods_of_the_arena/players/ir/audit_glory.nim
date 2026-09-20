## Verify lifetime XP against every recorded simulation state before scoring.
import std/[json, strutils]
import polyworld/metrics
import ../../[game, sim, replays]

if not run.replayMode:
  raise newException(ValueError, "--replay is required")
while run.world.tick < run.replayData.hashes.len and not run.world.gameOver:
  advanceGame()
if run.hashCheck.mismatches != 0 or
    run.replayPlayer.actionIndex != run.replayData.actions.len or
    run.world.tick != run.replayData.hashes.len:
  raise newException(ValueError, "Incomplete or mismatched replay")
var heroes = newJArray()
for slot, hero in run.world.heroes:
  let values = run.world.stats.values[slot]
  heroes.add(%*{"slot": slot, "class": $hero.class, "total_xp": hero.totalXp,
    "level": hero.level, "earned_gold": values[GoldMetric],
    "kills": values[KillsMetric], "deaths": values[LossesMetric],
    "assists": values[AssistsMetric]})
echo $(%*{"ticks": run.world.tick, "seed": run.replayData.config.seed,
  "recorded_ticks": run.replayData.hashes.len,
  "recorded_actions": run.replayData.actions.len,
  "actions_consumed": run.replayPlayer.actionIndex,
  "hash_mismatches": run.hashCheck.mismatches,
  "state_hash": run.stateHash().toHex(16),
  "scores": run.world.scores(), "total_xp": run.world.totalXp(),
  "heroes": heroes})
