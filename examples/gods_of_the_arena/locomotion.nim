## Responsive, deterministic walking around solid unit circles.

import polyworld/[bodies, fixed]

proc clearStep(
    body: Body, next: FixedVec2, obstacles: openArray[Body], walkable: Walkable
): bool =
  if not walkable(next):
    return false
  let delta = next - body.pos
  for other in obstacles:
    let
      offset = other.pos - body.pos
      radius = body.radius + other.radius
      startDistance = length(offset)
    if startDistance < radius:
      # Spawn/knockback overlaps may escape, but walking cannot deepen them.
      if length(other.pos - next) <= startDistance:
        return false
    else:
      let span = dot(delta, delta)
      let along = if span > FixedZero:
        clamp(dot(offset, delta) / span, FixedZero, FixedOne)
        else: FixedOne
      if length(offset - delta * along) < radius:
        return false
  true

proc walkStep(
    body: var Body, delta: FixedVec2,
    obstacles: openArray[Body], walkable: Walkable
) =
  let next = body.pos + delta
  if body.clearStep(next, obstacles, walkable):
    body.pos = next
  elif delta.x != FixedZero and body.clearStep(
      fixedVec2(next.x, body.pos.y), obstacles, walkable):
    body.pos.x = next.x
  elif delta.y != FixedZero and body.clearStep(
      fixedVec2(body.pos.x, next.y), obstacles, walkable):
    body.pos.y = next.y

proc walkAround*(
    body: var Body, toward: FixedVec2, speed, turnRate: Fixed,
    obstacles: openArray[Body], walkable: Walkable
): bool =
  ## Translation responds immediately; facing follows the actual travel.
  ## Aim along a nearby body's tangent before contact, like Pudge Wars,
  ## then resume the path once the direct route clears its circle.
  let distance = length(toward)
  if distance <= FixedZero or speed <= FixedZero:
    return false
  let
    desired = normalize(toward)
    step = min(speed, distance)
    lookahead = min(distance, 1.5'fx + speed)
  var
    course = desired
    fallback = desired
    nearest = FixedMaximum
    bestScore = if body.clearStep(body.pos + desired * lookahead, obstacles, walkable):
      FixedOne else: -2'fx
  for other in obstacles:
    let
      offset = other.pos - body.pos
      along = dot(offset, desired)
      clearance = body.radius + other.radius + 0.08'fx
    if along < FixedZero or along > lookahead + clearance:
      continue
    if length(offset - desired * along) >= clearance:
      continue
    let
      gap = length(offset)
      normal = if gap > FixedZero: normalize(offset) else: desired
    if distance <= clearance + 0.05'fx and
        length(offset - toward) < other.radius:
      # An occupied destination is a place to wait, not a circle to orbit.
      return false
    var tangent = fixedVec2(-normal.y, normal.x)
    # A head-on tie always takes the same relative side, so oncoming units
    # pass on opposite world sides without flipping between left and right.
    if dot(tangent, desired) < FixedZero:
      tangent = -tangent
    var preferred, alternate: FixedVec2
    if gap > clearance:
      let
        side = clearance / gap
        forward = sqrt(max(FixedZero, FixedOne - side * side))
      preferred = normal * forward + tangent * side
      alternate = normal * forward - tangent * side
    else:
      preferred = normalize(tangent - normal * 0.25'fx)
      alternate = normalize(-tangent - normal * 0.25'fx)
    if along < nearest:
      nearest = along
      fallback = preferred
    # Check each tangent against the whole nearby group and the terrain.
    # A route around one enemy must not lead straight into its neighbor.
    for candidate in [preferred, alternate]:
      let score = dot(candidate, desired)
      if score > bestScore + FixedEpsilon and body.clearStep(
          body.pos + candidate * lookahead, obstacles, walkable):
        course = candidate
        bestScore = score
  if bestScore == -2'fx:
    course = fallback
  let before = body.pos
  body.walkStep(course * step, obstacles, walkable)
  if length(body.pos - before) < step / 2'i32:
    # Try either side when a body is against terrain or another unit.
    # Restore first so retries never grant an extra movement step.
    let partial = body.pos
    for turn in [0.5'fx, -0.5'fx, 1.0'fx, -1.0'fx, FixedHalfPi, -FixedHalfPi]:
      body.pos = before
      body.walkStep(direction(angle(course) + turn) * step,
        obstacles, walkable)
      if length(body.pos - before) >= step / 2'i32:
        break
    if length(body.pos - before) < length(partial - before):
      body.pos = partial
  let moved = body.pos - before
  if moved != FixedVec2Zero:
    turnToward(body.facing, angle(moved), turnRate)
    return true
