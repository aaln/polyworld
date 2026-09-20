## Short legal-command counterfactuals from a verified replay checkpoint.
## Peers retain recorded actions: this is a mechanics probe, NOT a policy eval.
import std/[json, os, strutils, math]
import ../../[game, sim, replays]

let slot = getEnv("GOTA_SLOT", "1").parseInt
let checkpointTick = getEnv("GOTA_CHECKPOINT", "4500").parseInt
let duration = 240
while run.world.tick < checkpointTick: advanceGame()
if run.hashCheck.mismatches != 0:
  raise newException(ValueError, "checkpoint prefix failed verification")
let checkpoint = run.world.clone()
let tape = run.replayData
let cursor = run.replayPlayer.actionIndex
var trials = newJArray()
for retreatTicks in [-1, 0, 1, 4, 8, 12]:
  run.world = checkpoint.clone()
  run.replayPlayer = initReplayPlayer(tape)
  var commands: seq[ReplayAction]
  for a in tape.actions: commands.add(a)
  run.replayPlayer.data.actions = commands
  run.replayPlayer.actionIndex = cursor
  run.hashCheck = default(typeof(run.hashCheck))
  let hero = run.world.heroes[slot]
  let startPosition = hero.position
  let startHits = hero.attacksLanded
  var previousHits = startHits
  var untilTick = 0
  var targetId = hero.attackObjectId
  var destinationX, destinationY: int32
  var hitTicks = newJArray()
  var walkCommands = 0
  var movedTicks = 0
  for step in 0 ..< duration:
    let nextTick = run.world.tick.int + 1
    if retreatTicks >= 0 and hero.hp > 0:
      # Share the same recorded target schedule across all intervention arms.
      # Retaining the last live engine target would stick to a killed enemy and
      # confound recovery timing with target selection after the first hit.
      var referenceIndex = run.replayPlayer.actionIndex
      while referenceIndex < tape.actions.len:
        let reference = tape.actions[referenceIndex]
        if reference.tick.int > nextTick: break
        if reference.tick.int == nextTick and reference.heroId == hero.id and reference.kind == ActionAttackTarget:
          targetId = reference.first
        inc referenceIndex
      if hero.attacksLanded > previousHits and targetId != 0:
        var target: WorldObject
        if run.world.spellTarget(targetId, target):
          let dx = hero.position.x - target.position.x
          let dz = hero.position.z - target.position.z
          let sx = if dx > 0: 2'i32 elif dx < 0: -2'i32 else: 0'i32
          let sy = if dz > 0: 2'i32 elif dz < 0: -2'i32 else: 0'i32
          destinationX = mapCoordinate(hero.position.x) + sx
          destinationY = mapCoordinate(hero.position.z) + sy
          untilTick = nextTick + retreatTicks
      var index = run.replayPlayer.actionIndex
      while index < run.replayPlayer.data.actions.len:
        var action = run.replayPlayer.data.actions[index]
        if action.tick.int > nextTick: break
        if action.tick.int == nextTick and action.heroId == hero.id and
            action.kind in [ActionWalkTo, ActionAttackTarget] and targetId != 0:
          if nextTick < untilTick:
            action.kind = ActionWalkTo
            action.first = destinationX
            action.second = destinationY
            inc walkCommands
          else:
            action.kind = ActionAttackTarget
            action.first = targetId
            action.second = 0
          run.replayPlayer.data.actions[index] = action
        inc index
    previousHits = hero.attacksLanded
    let oldPosition = hero.position
    advanceGame()
    if hero.position != oldPosition: inc movedTicks
    if hero.attacksLanded > previousHits: hitTicks.add(%run.world.tick)
  let dx = (hero.position.x.float64 - startPosition.x.float64) / WorldScale.float64
  let dz = (hero.position.z.float64 - startPosition.z.float64) / WorldScale.float64
  trials.add(%*{"retreat_ticks":retreatTicks,"hits":hero.attacksLanded-startHits,
    "hit_ticks":hitTicks,"walk_commands":walkCommands,"actual_moved_ticks":movedTicks,
    "displacement_tiles":sqrt(dx*dx+dz*dz),"end_hp":hero.hp,
    "post_intervention_hash_mismatches":run.hashCheck.mismatches})
echo $(%*{"checkpoint_prefix_verified":true,"slot":slot,"checkpoint_tick":checkpointTick,
  "duration":duration,"trials":trials,
  "limits":"Ten-second open-loop legal-command probes; peers and subject target schedule retain recorded actions. Minus1 is unmodified replay,0 is attack-only; positive values change recovery movement. Changed trajectories should diverge from recorded hashes. Not full policy games or competitive win evidence."})
