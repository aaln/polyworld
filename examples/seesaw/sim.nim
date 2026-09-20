## Seesaw simulation.
##
## Two riders on one integer board. Weather and inner lives are sampled from
## the seed; fun and nausea update every tick; the pair score is written
## when the match ends. This module must not import anything that returns a
## float.

import
  polyworld/[basic, fixed, hashes, profiles, rngs, tapes],
  content,
  maps,
  replays

type
  Rider* = object
    slot*: int32                      # HASH: include
    lean*: int32                      # HASH: include, -2 .. 2
    pump*: bool                       # HASH: include
    expression*: int32                # HASH: include, 0 .. 15
    expressionAge*: int32             # HASH: include
    rawFun*: int32                    # HASH: include
    funDelta*: int32                  # HASH: include
    nausea*: int32                    # HASH: include
    maxNausea*: int32                 # HASH: include
    sick*: bool                       # HASH: include
    sickEvents*: int32                # HASH: include
    fatigue*: int32                   # HASH: include
    energy*: EnergyKind               # HASH: include
    stomach*: StomachKind             # HASH: include
    vestibular*: VestibularKind       # HASH: include
    mood*: MoodKind                   # HASH: include
    thirst*: ThirstKind               # HASH: include
    preferred*: int32                 # HASH: include
    seated*: bool                     # HASH: include
    tileX*: int32                     # HASH: include
    tileY*: int32                     # HASH: include
    fromX*: int32                     # HASH: include
    fromY*: int32                     # HASH: include
    destX*: int32                     # HASH: include
    destY*: int32                     # HASH: include
    walkHold*: int32                  # HASH: include
    animation*: AnimationSlot         # HASH: include
    animationTicks*: int32            # HASH: include

  World* = ref object
    ## One game. A ref so `a = b` aliases and a second world is `clone()`.
    tick*: int32                      # HASH: include
    rng*: Rng                         # HASH: include
    over*: bool                       # HASH: include
    maximumTicks*: int32              # HASH: include
    angleMilli*: int32                # HASH: include
    omegaMilli*: int32                # HASH: include
    prevOmegaMilli*: int32            # HASH: include
    torqueCarry*: int32               # HASH: include
    tempBand*: TempBand               # HASH: include
    windBand*: WindBand               # HASH: include
    wetBand*: WetBand                 # HASH: include
    windForce*: int32                 # HASH: include
    dampBonus*: int32                 # HASH: include
    heatBonus*: int32                 # HASH: include
    riders*: array[RiderCount, Rider] # HASH: include
    scores*: array[RiderCount, int32] # HASH: include
    map*: MapData                     # HASH: derived, fixed at generation

  RiderVm* = ref object
    ## One compiled BASIC program for a rider. Not simulation state.
    runtime*: Runtime
    ready*: bool
    failed*: bool
    lastError*: string
    decisions*: int
    lastWork*, lastInstructions*: int64

  Game* = ref object
    world*: World
    recorder*: ReplayRecorder
    replayData*: ReplayData
    replayPlayer*: ReplayPlayer
    hashCheck*: ReplayHashCheck
    historyPlayback*: bool
    replayMode*: bool
    brains*: array[RiderCount, RiderVm]
    mapSeed*: int32
    maximumTicks*: int32

proc validSlot*(slot: int32): bool =
  slot >= 0 and slot < RiderCount

proc walking*(r: Rider): bool =
  ## True while this rider is between the board and a bench.
  not r.seated and (r.tileX != r.destX or r.tileY != r.destY)

proc restingOffBoard*(r: Rider): bool =
  ## Sitting on a bench, not walking, not on the plank.
  not r.seated and not r.walking

proc remainingTicks*(w: World): int32 =
  max(0'i32, w.maximumTicks - w.tick)

proc feltFun*(r: Rider): int32 =
  ## Running personal score a rider can feel, penalties included.
  max(0'i32, r.rawFun - r.sickEvents * SickEventPenalty -
    r.nausea * NauseaPenalty)

proc feltFun*(w: World, slot: int32): int32 =
  if validSlot(slot): w.riders[slot].feltFun else: 0

proc intensityOf*(omegaMilli: int32): int32 =
  ## Felt ride intensity, 0 .. 1000.
  let value = abs(omegaMilli) * IntensityScale
  if value > 1000: 1000 else: value

proc sinMilli(milli: int32): int32 =
  toInt(sin(fixed(milli) / 1000) * 1000)

proc cosMilli(milli: int32): int32 =
  toInt(cos(fixed(milli) / 1000) * 1000)

proc pickEnum[T: enum](rng: var Rng): T =
  T(rng.below(int32(ord(high(T)) + 1)))

proc sampleTraits(rng: var Rng): Rider =
  ## Draws one hidden inner life. Two riders from the same seed still differ
  ## because the stream has already advanced.
  result.energy = pickEnum[EnergyKind](rng)
  result.stomach = pickEnum[StomachKind](rng)
  result.vestibular = pickEnum[VestibularKind](rng)
  result.mood = pickEnum[MoodKind](rng)
  result.thirst = pickEnum[ThirstKind](rng)
  result.preferred = preferredIntensity(
    result.energy, result.stomach, result.vestibular, result.mood, result.thirst)

proc sampleWeather(rng: var Rng): tuple[
    temp: TempBand, wind: WindBand, wet: WetBand,
    windForce, dampBonus, heatBonus: int32] =
  result.temp = pickEnum[TempBand](rng)
  result.wind = pickEnum[WindBand](rng)
  result.wet = pickEnum[WetBand](rng)
  result.windForce = int32(result.wind.ord) * WindForceScale +
    rng.below(WindForceJitter)
  result.dampBonus = int32(result.wet.ord) * 10
  result.heatBonus =
    if result.temp >= TempWarm: HeatFatigue + int32(result.temp.ord) - 2
    else: 0

proc commandsOpen(w: World): bool =
  not w.over

proc clampLean(value: int32): int32 =
  max(-MaxLean, min(MaxLean, value))

proc seatHere(r: var Rider, slot: int32) =
  let pad = mountTile(slot)
  r.seated = true
  r.tileX = pad.x
  r.tileY = pad.y
  r.fromX = pad.x
  r.fromY = pad.y
  r.destX = pad.x
  r.destY = pad.y
  r.walkHold = 0

proc headFor(r: var Rider, x, y: int32) =
  r.destX = x
  r.destY = y

proc applyLean*(w: World, player, dir: int32): bool =
  ## Sets one rider's lean, -2 .. 2. Sticky until changed. Off the board
  ## this also walks them back to their seat.
  if not w.commandsOpen or not validSlot(player):
    return false
  w.riders[player].lean = clampLean(dir)
  if not w.riders[player].seated:
    let pad = mountTile(player)
    w.riders[player].headFor(pad.x, pad.y)
  true

proc applyPump*(w: World, player, on: int32): bool =
  ## Sets whether one rider is pumping. Sticky until changed. Off the board
  ## this also walks them back to their seat.
  if not w.commandsOpen or not validSlot(player):
    return false
  w.riders[player].pump = on != 0
  if not w.riders[player].seated:
    let pad = mountTile(player)
    w.riders[player].headFor(pad.x, pad.y)
  true

proc applyExpress*(w: World, player, face: int32): bool =
  ## Sends one face, or 0 to clear. The partner sees the id and its age.
  if not w.commandsOpen or not validSlot(player):
    return false
  if face < 0 or face >= ExpressionCount:
    return false
  w.riders[player].expression = face
  w.riders[player].expressionAge = 0
  true

proc applyRest*(w: World, player: int32): bool =
  ## Gets off the plank and walks to a bench. Lean and pump clear.
  if not w.commandsOpen or not validSlot(player):
    return false
  let
    pad = mountTile(player)
    bench = restTile(player)
  var r = w.riders[player]
  if r.seated:
    r.seated = false
    r.tileX = pad.x
    r.tileY = pad.y
    r.fromX = pad.x
    r.fromY = pad.y
    r.walkHold = 0
  r.lean = 0
  r.pump = false
  r.headFor(bench.x, bench.y)
  w.riders[player] = r
  true

proc pumpWeight(r: Rider, omegaMilli: int32, wetSlip: int32): int32 =
  ## Extra signed weight from pumping: push on the way down, lighten up.
  if not r.seated or not r.pump:
    return 0
  let
    descending =
      (r.slot == 0 and omegaMilli > 0) or
      (r.slot == 1 and omegaMilli < 0)
    tired = r.fatigue div FatiguePumpDiv
    push = max(0'i32, PumpPush - tired - wetSlip)
    lighten = max(0'i32, PumpLighten - tired div 2)
  if descending: push else: -lighten

proc riderWeight*(r: Rider, omegaMilli, wetSlip: int32): int32 =
  if not r.seated:
    return 0
  BaseWeight + r.lean * LeanWeight + r.pumpWeight(omegaMilli, wetSlip)

proc rawComfort(r: Rider, intensity: int32): int32 =
  ## Fun from the ride itself, before the partner's comfort is applied.
  let
    window = comfortWindow(r.mood)
    diff = abs(intensity - r.preferred)
  if diff <= window:
    result = 12 - (diff * 8) div max(window, 1)
  else:
    result = max(0'i32, 4 - (diff - window) div 40)
  if r.energy <= EnergyTired and intensity < 80:
    inc result, 2
  if result < 0:
    result = 0

proc withPartner(comfort, partnerComfort: int32): int32 =
  if partnerComfort >= 4 and comfort >= 4:
    comfort * TogetherBonusNum div TogetherBonusDen
  elif partnerComfort <= 1 and comfort >= 6:
    comfort * MismatchNum div MismatchDen
  else:
    comfort

proc nauseaTick(r: var Rider, intensity, wetExtra, jerk: int32) =
  if not r.seated:
    r.nausea = max(0'i32, r.nausea - RestNauseaRecover)
    if r.nausea < SickLimit div 2:
      r.sick = false
    return
  let threshold = VestibularThreshold[r.vestibular]
  var excess = intensity - threshold
  if excess > 0:
    r.nausea += excess div NauseaGainDiv + wetExtra + jerk div 8
  else:
    r.nausea = max(0'i32, r.nausea - NauseaRecover)
  if r.nausea > r.maxNausea:
    r.maxNausea = r.nausea
  if r.nausea >= SickLimit:
    if not r.sick:
      inc r.sickEvents
    r.sick = true
  elif r.nausea < SickLimit div 2:
    r.sick = false

proc poseRider(r: var Rider, intensity: int32) =
  let next =
    if not r.seated:
      if r.walking: WalkAnimation else: SitAnimation
    elif r.sick: SickAnimation
    elif r.nausea > 420: DizzyAnimation
    elif r.pump: PumpAnimation
    elif intensity >= r.preferred - 40 and intensity > 80: FunAnimation
    else: SitAnimation
  if next != r.animation:
    r.animation = next
    r.animationTicks = 0
  else:
    inc r.animationTicks

proc finishMatch(w: World) =
  if w.over:
    return
  w.over = true
  let
    a = w.riders[0].feltFun
    b = w.riders[1].feltFun
    pair = pairScore(a, b)
  w.scores[0] = pair
  w.scores[1] = pair

proc openTile(map: MapData, x, y: int32): bool =
  map.tileOpen(x, y)

proc stepToward(map: MapData, x, y, destX, destY: int32): tuple[x, y: int32] =
  ## One orthogonal step toward dest, skipping blocked tiles.
  result.x = x
  result.y = y
  let
    dx = destX - x
    dy = destY - y
  if dx == 0 and dy == 0:
    return
  let
    stepX = (if dx > 0: 1'i32 elif dx < 0: -1'i32 else: 0'i32)
    stepY = (if dy > 0: 1'i32 elif dy < 0: -1'i32 else: 0'i32)
  if abs(dx) >= abs(dy):
    if stepX != 0 and map.openTile(x + stepX, y):
      return (x + stepX, y)
    if stepY != 0 and map.openTile(x, y + stepY):
      return (x, y + stepY)
  else:
    if stepY != 0 and map.openTile(x, y + stepY):
      return (x, y + stepY)
    if stepX != 0 and map.openTile(x + stepX, y):
      return (x + stepX, y)

proc stepRiders(w: World) =
  ## Walks anyone who is off the plank toward their dest, then sits them
  ## if they reached the hop-on pad.
  for slot in 0 ..< RiderCount:
    var r = w.riders[slot]
    if r.seated:
      continue
    if r.tileX == r.destX and r.tileY == r.destY:
      let pad = mountTile(int32(slot))
      if r.tileX == pad.x and r.tileY == pad.y:
        r.seatHere(int32(slot))
        w.riders[slot] = r
      continue
    inc r.walkHold
    if r.walkHold < WalkStepTicks:
      w.riders[slot] = r
      continue
    r.walkHold = 0
    r.fromX = r.tileX
    r.fromY = r.tileY
    let next = w.map.stepToward(r.tileX, r.tileY, r.destX, r.destY)
    r.tileX = next.x
    r.tileY = next.y
    if r.tileX == r.destX and r.tileY == r.destY:
      let pad = mountTile(int32(slot))
      if r.tileX == pad.x and r.tileY == pad.y:
        r.seatHere(int32(slot))
    w.riders[slot] = r

proc stepBoard(w: World) {.measure.} =
  ## Advances the plank, then scores how the ride felt.
  let
    intensity = intensityOf(w.omegaMilli)
    wetSlip = w.dampBonus + (if w.wetBand == WetWet: WetSlip else: 0)
    wetNausea = int32(w.wetBand.ord) * WetNauseaExtra
    left = w.riders[0].riderWeight(w.omegaMilli, wetSlip)
    right = w.riders[1].riderWeight(w.omegaMilli, wetSlip)
    cosine = cosMilli(w.angleMilli)
    sine = sinMilli(w.angleMilli)
    massTorque = (left - right) * cosine * ArmScale div 1000
    geometry = sine * BottomBias div 1000
    spring = -(w.angleMilli * SpringMilli) div 1000
    damp = -(w.omegaMilli * (DampBase + w.dampBonus)) div 100
  var wind = 0'i32
  if w.windForce > 0:
    wind = w.rng.between(-w.windForce, w.windForce)
  let
    tau = massTorque + geometry + spring + damp + wind
  w.torqueCarry += tau
  let deltaOmega = w.torqueCarry div max(Inertia, 1)
  w.torqueCarry -= deltaOmega * max(Inertia, 1)
  let nextOmega = w.omegaMilli + deltaOmega
  var
    nextAngle = w.angleMilli + nextOmega
    omega = nextOmega
  if nextAngle > MaxAngleMilli:
    nextAngle = MaxAngleMilli
    omega = -(omega * BounceMilli) div 1000
  elif nextAngle < -MaxAngleMilli:
    nextAngle = -MaxAngleMilli
    omega = -(omega * BounceMilli) div 1000
  let jerk = abs(omega - w.omegaMilli)
  w.prevOmegaMilli = w.omegaMilli
  w.omegaMilli = omega
  w.angleMilli = nextAngle

  var comfort: array[RiderCount, int32]
  for slot in 0 ..< RiderCount:
    if w.riders[slot].seated:
      comfort[slot] = w.riders[slot].rawComfort(intensity)
    else:
      comfort[slot] = 0
  for slot in 0 ..< RiderCount:
    let
      other = 1 - slot
      recovering = w.riders[slot].nausea > 0 or w.riders[slot].sick or
        w.riders[slot].fatigue > 40
      gained =
        if w.riders[slot].seated:
          withPartner(comfort[slot], comfort[other])
        elif recovering:
          RestComfort
        else:
          0'i32
    w.riders[slot].funDelta = gained
    w.riders[slot].rawFun += gained
    w.riders[slot].nauseaTick(intensity, wetNausea, jerk)
    if not w.riders[slot].seated:
      w.riders[slot].fatigue =
        max(0'i32, w.riders[slot].fatigue - RestFatigueRecover)
    elif w.riders[slot].pump:
      w.riders[slot].fatigue += 1 + w.heatBonus
      if w.riders[slot].energy <= EnergyTired:
        inc w.riders[slot].fatigue
    else:
      w.riders[slot].fatigue = max(0'i32, w.riders[slot].fatigue - 2)
    inc w.riders[slot].expressionAge
    w.riders[slot].poseRider(intensity)

proc tickWorld*(w: World, decide: proc(w: World) {.closure.}) {.measure.} =
  ## Advances the simulation by exactly one tick.
  if w.over:
    return
  inc w.tick
  if w.tick mod DecisionTicks == 0 and decide != nil:
    profileBlock "decisions":
      decide(w)
  profileBlock "walk":
    w.stepRiders()
  profileBlock "board":
    w.stepBoard()
  if w.tick >= w.maximumTicks:
    w.finishMatch()

proc applyReplayAction*(w: World, action: ReplayAction) =
  ## Re-executes one recorded command through the same validators.
  let player = int32(action.playerId)
  case action.kind
  of ActionLean:
    discard w.applyLean(player, action.first)
  of ActionPump:
    discard w.applyPump(player, action.first)
  of ActionExpress:
    discard w.applyExpress(player, action.first)
  of ActionRest:
    discard w.applyRest(player)
  else:
    raise newException(ReplayError, "replay action kind is invalid")

proc record(game: Game, kind: uint8, player: int32,
    first = 0'i32, second = 0'i32) =
  if game.recorder == nil or
      game.recorder.data.hashes.len >= game.world.tick:
    return
  game.recorder.recordAction(
    uint32(game.world.tick), player, kind, first, second)

proc applyLean*(game: Game, player, dir: int32): bool =
  result = game.world.applyLean(player, dir)
  if result:
    game.record(ActionLean, player, dir)

proc applyPump*(game: Game, player, on: int32): bool =
  result = game.world.applyPump(player, on)
  if result:
    game.record(ActionPump, player, on)

proc applyExpress*(game: Game, player, face: int32): bool =
  result = game.world.applyExpress(player, face)
  if result:
    game.record(ActionExpress, player, face)

proc applyRest*(game: Game, player: int32): bool =
  result = game.world.applyRest(player)
  if result:
    game.record(ActionRest, player)

proc hashWorld(w: World): uint64 =
  var hash = HashySeed
  hash.addHashy(w.tick)
  hash.addHashy(w.rng)
  hash.addHashy(w.over)
  hash.addHashy(w.maximumTicks)
  hash.addHashy(w.angleMilli)
  hash.addHashy(w.omegaMilli)
  hash.addHashy(w.prevOmegaMilli)
  hash.addHashy(w.torqueCarry)
  hash.addHashy(int32(w.tempBand.ord))
  hash.addHashy(int32(w.windBand.ord))
  hash.addHashy(int32(w.wetBand.ord))
  hash.addHashy(w.windForce)
  hash.addHashy(w.dampBonus)
  hash.addHashy(w.heatBonus)
  for r in w.riders:
    hash.addHashy(r.slot)
    hash.addHashy(r.lean)
    hash.addHashy(r.pump)
    hash.addHashy(r.expression)
    hash.addHashy(r.expressionAge)
    hash.addHashy(r.rawFun)
    hash.addHashy(r.funDelta)
    hash.addHashy(r.nausea)
    hash.addHashy(r.maxNausea)
    hash.addHashy(r.sick)
    hash.addHashy(r.sickEvents)
    hash.addHashy(r.fatigue)
    hash.addHashy(int32(r.energy.ord))
    hash.addHashy(int32(r.stomach.ord))
    hash.addHashy(int32(r.vestibular.ord))
    hash.addHashy(int32(r.mood.ord))
    hash.addHashy(int32(r.thirst.ord))
    hash.addHashy(r.preferred)
    hash.addHashy(r.seated)
    hash.addHashy(r.tileX)
    hash.addHashy(r.tileY)
    hash.addHashy(r.fromX)
    hash.addHashy(r.fromY)
    hash.addHashy(r.destX)
    hash.addHashy(r.destY)
    hash.addHashy(r.walkHold)
    hash.addHashy(int32(r.animation.ord))
    hash.addHashy(r.animationTicks)
  hash.addHashy(w.scores[0])
  hash.addHashy(w.scores[1])
  uint64(hash)

proc stateHash*(game: Game): uint64 =
  hashWorld(game.world)

proc stateHash*(w: World): uint64 =
  hashWorld(w)

proc clone*(world: World): World =
  result = World()
  result[] = world[]

proc restore*(world: World, snapshot: World) =
  world[] = snapshot[]

proc newWorld*(map: MapData, maximumTicks = MatchTicks): World =
  var rng = initRng(map.seed)
  let weather = rng.sampleWeather()
  result = World(
    tick: 0,
    rng: rng,
    maximumTicks: maximumTicks,
    tempBand: weather.temp,
    windBand: weather.wind,
    wetBand: weather.wet,
    windForce: weather.windForce,
    dampBonus: weather.dampBonus,
    heatBonus: weather.heatBonus,
    map: map
  )
  for slot in 0 ..< RiderCount:
    var rider = rng.sampleTraits()
    rider.slot = int32(slot)
    rider.seatHere(int32(slot))
    result.riders[slot] = rider

proc newGame*(map: MapData, maximumTicks = MatchTicks): Game =
  result = Game(
    world: newWorld(map, maximumTicks),
    mapSeed: map.seed,
    maximumTicks: maximumTicks
  )
