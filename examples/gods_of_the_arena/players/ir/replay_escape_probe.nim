## Bounded local counterfactuals from a hash-verified replay checkpoint.
## Other heroes keep their recorded commands. These are NOT competitive games.
## Last arm changes a path waypoint for diagnosis ONLY; not a legal policy.
import std/[json, os, strutils, math]
import ../../[game, sim, replays]

let slot = getEnv("GOTA_SLOT", "7").parseInt
let checkpointTick = getEnv("GOTA_CHECKPOINT", "1200").parseInt
let duration = 96
while run.world.tick < checkpointTick: advanceGame()
if run.hashCheck.mismatches != 0:
  raise newException(ValueError,"checkpoint prefix failed replay verification")
let checkpoint = run.world.clone()
let tape = run.replayData
let cursor = run.replayPlayer.actionIndex
let subject = checkpoint.heroes[slot]
let origin = subject.position
proc distance(p: WorldPoint): float64 =
  let x = (p.x.float64-origin.x.float64)/WorldScale.float64
  let z = (p.z.float64-origin.z.float64)/WorldScale.float64
  sqrt(x*x+z*z)
var trials = newJArray()
let dirs = [(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]
for trial in -1 .. 24:
  run.world = checkpoint.clone()
  run.replayPlayer = initReplayPlayer(tape)
  run.replayPlayer.actionIndex = cursor
  run.hashCheck = default(typeof(run.hashCheck))
  var commands: seq[ReplayAction]
  var name = "recorded_control"
  var dx,dy: int
  if trial in 0 .. 23:
    let step = [1,2,4][trial div 8]
    dx = dirs[trial mod 8][0]*step
    dy = dirs[trial mod 8][1]*step
    name = "walk_" & $dx & "_" & $dy
    # Preserve all other commands and their original order. Replace the subject
    # at the position of its first command in each tick (not after every peer).
    var replacedTick = -1
    for a in tape.actions:
      if a.tick.int <= checkpointTick or a.tick.int > checkpointTick+duration:
        commands.add(a)
      elif a.heroId != subject.id:
        commands.add(a)
      elif a.tick.int != replacedTick:
        replacedTick = a.tick.int
        commands.add(ReplayAction(tick:a.tick,heroId:a.heroId,kind:ActionWalkTo,
          first:mapCoordinate(origin.x)+dx.int32,second:mapCoordinate(origin.z)+dy.int32))
    run.replayPlayer.data.actions = commands
  elif trial == 24:
    name = "ENGINE_ONLY_skip_blocked_first_waypoint"
    # Keep the action tape unchanged. Alter only the first path waypoint once
    # to establish whether that waypoint is the obstruction. Not deployable.
    run.world.heroes[slot].movePath[0] = origin
  var maxDisplacement = 0.0
  for i in 0 ..< duration:
    advanceGame()
    maxDisplacement = max(maxDisplacement,distance(run.world.heroes[slot].position))
  let h = run.world.heroes[slot]
  trials.add(%*{"arm":name,"ticks":duration,"end_displacement_tiles":distance(h.position),
    "max_displacement_tiles":maxDisplacement,"end_hp":h.hp,
    "post_intervention_hash_mismatches":run.hashCheck.mismatches})
echo $(%*{"replay":options.replayPath,"checkpoint_tick":checkpointTick,
  "checkpoint_prefix_verified":true,"slot":slot,"trials":trials,
  "limits":"96-tick open-loop counterfactuals; peers keep recorded actions; no win-rate inference. Engine-only arm is not a policy candidate."})
