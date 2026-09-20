## Seesaw spectator viewer.
##
## Reads the simulation and never writes it. The plank angle is interpolated
## for the eye; that float never flows back into `World`.

import
  std/[json, math, strutils, times],
  chroma, opengl, pixie, vmath, windy, silky,
  polyworld/[
    actioncam, characters, chrome, common, inputs, pathing, player,
    profiles, quadterrain, rtscameras, shadows, shapes, tapes, viewers
  ],
  content,
  sim,
  game,
  ui,
  controls,
  decor

when defined(takeScreenshot):
  import std/os

const
  WindowTitle = "Seesaw"
  AtlasPath = TmpRoot & "/seesaw.atlas.png"
  SeekCheckpointTicks = TickRate * 10
  RiderHeight = 1.18'f32
  ModularCharacterPath = DataRoot & "/characters/modular_chars/character.glb"
  ModularManifestPath = DataRoot & "/characters/modular_chars/manifest.json"
  RiderPresetNumbers: array[RiderCount, int] = [6, 5]
  PlankHalf = 2.05'f32
  SeatAlong = 1.82'f32
  SeatLift = 0.18'f32
  FulcrumLift = 1.48'f32
  SitDrop = 0.02'f32
  PlankWest = rgbx(232, 86, 92, 255)
  PlankEast = rgbx(72, 156, 224, 255)
  SeatColor = rgbx(250, 208, 72, 255)
  HandleColor = rgbx(250, 220, 96, 255)
  FulcrumColor = rgbx(255, 214, 64, 255)
  PivotColor = rgbx(236, 236, 240, 255)
  RainColor = rgbx(210, 228, 240, 120)

type
  GraphicsError = object of CatchableError
  SeekCheckpoint = object
    world: World
    hashCheck: ReplayHashCheck

var
  window*: Window
  sk*: Silky
  cameraDistance* = 10.0'f32
  cameraTarget* = vec3(0, 0, 0)
  cameraEye = vec3(0, 0, 0)
  panning = false
  followSlot* = -1'i32
  seekCheckpoints: seq[SeekCheckpoint]
  transport* = initPlayer(
    live = not run.replayMode,
    durationTicks = run.maximumTicks,
    playing = not options.pauseOnStart,
    speed = options.speed
  )
  frameAlpha = 0.0'f32
  previousAngle = 0.0'f32
  haveAngle = false

proc riderPresetName(slot: int): string =
  "Preset " & $RiderPresetNumbers[slot]

proc riderParts(slot: int): seq[string] =
  let
    manifest = parseFile(ModularManifestPath)
    wanted = riderPresetName(slot)
  var found = false
  for preset in manifest["presets"]:
    if preset["name"].getStr != wanted:
      continue
    found = true
    for part in preset["parts"]:
      let name = part.getStr
      if name.startsWith("Back_") or name.startsWith("Wield_Gear_"):
        continue
      result.add name
  doAssert found, ModularManifestPath & ": no preset " & wanted

proc riderPortraitPath(slot: int): string =
  DataRoot & "/characters/modular_chars/character.preset_" &
    $RiderPresetNumbers[slot] & ".profile.png"

proc clipIndex(model: CharacterModel, slot: AnimationSlot): int =
  const Names: array[AnimationSlot, seq[string]] = [
    SitAnimation: @["Idle", "IdleBattle"],
    PumpAnimation: @["JumpStart", "Attack01", "Idle"],
    FunAnimation: @["Victory", "LevelUp", "Idle"],
    DizzyAnimation: @["Dizzy", "GetHit", "Idle"],
    SickAnimation: @["GetHit", "Death", "Idle"],
    WalkAnimation: @["Walk", "Run", "Idle"]
  ]
  for name in Names[slot]:
    if name in model.clips:
      return model.clips[name]
  raise newException(GraphicsError, "missing clip for " & $slot)

proc makeFace(face: Expression): Image =
  ## A 64px cartoon glyph for one expression. Packed into the HUD atlas.
  result = newImage(64, 64)
  let ctx = newContext(result)
  var skin = rgb(250, 214, 90)
  case face
  of FaceNauseous: skin = rgb(168, 206, 92)
  of FaceHot: skin = rgb(242, 164, 86)
  of FaceCold: skin = rgb(186, 220, 236)
  of FaceTired: skin = rgb(214, 196, 140)
  else: discard
  if face == FaceClear:
    ctx.fillStyle = rgb(40, 44, 52)
    ctx.fillCircle(circle(vec2(32, 32), 22))
    return
  ctx.fillStyle = skin
  ctx.fillCircle(circle(vec2(32, 32), 28))
  ctx.fillStyle = rgb(40, 32, 28)
  let
    eyeY =
      if face in {FaceTired, FaceNauseous}: 26.0'f32
      else: 24.0'f32
    eyeR =
      if face == FaceTired: 3.2'f32
      elif face == FaceDelighted: 4.4'f32
      else: 3.8'f32
  ctx.fillCircle(circle(vec2(22, eyeY), eyeR))
  ctx.fillCircle(circle(vec2(42, eyeY), eyeR))
  ctx.fillStyle = rgb(40, 32, 28)
  let mouthY =
    case face
    of FaceSmile, FaceDelighted, FaceBliss, FaceCheer: 42.0'f32
    of FaceFrown, FaceAnxious, FaceNauseous, FaceGrimace, FaceDizzy: 46.0'f32
    else: 44.0'f32
  let mouthR =
    case face
    of FaceDelighted, FaceCheer, FaceBliss: 8.0'f32
    of FaceFrown, FaceAnxious: 5.0'f32
    of FaceNauseous: 6.5'f32
    else: 6.0'f32
  if face in {FaceFrown, FaceAnxious, FaceGrimace, FaceTired}:
    ctx.fillCircle(circle(vec2(32, mouthY - 4), mouthR))
    ctx.fillStyle = skin
    ctx.fillCircle(circle(vec2(32, mouthY + 2), mouthR + 1))
  else:
    ctx.fillCircle(circle(vec2(32, mouthY), mouthR))
    ctx.fillStyle = skin
    ctx.fillCircle(circle(vec2(32, mouthY - 6), mouthR + 1))

proc makeLogo(): Image =
  result = newImage(256, 256)
  let ctx = newContext(result)
  ctx.fillStyle = rgb(92, 148, 214)
  ctx.fillCircle(circle(vec2(128, 118), 86))
  ctx.fillStyle = rgb(250, 214, 90)
  ctx.fillCircle(circle(vec2(128, 118), 70))
  ctx.fillStyle = rgb(120, 78, 44)
  ctx.fillRect(rect(38, 110, 180, 18))
  ctx.fillStyle = rgb(176, 122, 72)
  ctx.fillRect(rect(42, 112, 172, 14))
  ctx.fillStyle = rgb(226, 108, 92)
  ctx.fillCircle(circle(vec2(64, 96), 16))
  ctx.fillStyle = rgb(92, 148, 214)
  ctx.fillCircle(circle(vec2(192, 132), 16))

proc addHudIcons(builder: AtlasBuilder) =
  if not builder.addImage(SplashName, makeLogo()):
    raise newException(GraphicsError, "the UI atlas is too small for the logo")
  for slot in 0 ..< RiderCount:
    if not builder.addImage(
        riderPortraitKey(int32(slot)),
        readImage(riderPortraitPath(slot))
      ):
      raise newException(
        GraphicsError,
        "the UI atlas is too small for rider portraits"
      )
  for face in Expression:
    if not builder.addImage(expressionKey(int32(face.ord)), makeFace(face)):
      raise newException(
        GraphicsError,
        "the UI atlas is too small for faces"
      )

proc rotateZ(point: Vec3, angle: float32): Vec3 =
  let
    cosine = cos(angle)
    sine = sin(angle)
  vec3(
    point.x * cosine - point.y * sine,
    point.x * sine + point.y * cosine,
    point.z
  )

proc addBox(
    renderer: var ShapeRenderer,
    center, size: Vec3,
    pitch: float32,
    color: ColorRGBX
) =
  let half = size * 0.5'f32
  proc corner(sx, sy, sz: float32): Vec3 =
    center + rotateZ(vec3(sx * half.x, sy * half.y, sz * half.z), pitch)
  let
    p0 = corner(-1, -1, -1)
    p1 = corner(1, -1, -1)
    p2 = corner(1, 1, -1)
    p3 = corner(-1, 1, -1)
    p4 = corner(-1, -1, 1)
    p5 = corner(1, -1, 1)
    p6 = corner(1, 1, 1)
    p7 = corner(-1, 1, 1)
  renderer.addQuad(p3, p2, p6, p7, color)
  renderer.addQuad(p0, p4, p5, p1, color)
  renderer.addQuad(p0, p3, p7, p4, color)
  renderer.addQuad(p1, p5, p6, p2, color)
  renderer.addQuad(p4, p7, p6, p5, color)
  renderer.addQuad(p0, p1, p2, p3, color)

proc renderAngle(): float32 =
  let current = run.world.angleMilli.float32 / 1000.0'f32
  if not interpolateVisuals or not haveAngle:
    return current
  previousAngle + (current - previousAngle) * frameAlpha

proc seesawOrigin(): Vec3 =
  vec3(0, surfaceHeight(0, 0) + FulcrumLift, 0)

proc seatPoint(slot: int, angle: float32): Vec3 =
  let
    along = if slot == 0: -SeatAlong else: SeatAlong
    origin = seesawOrigin()
    local = rotateZ(vec3(along, SeatLift, 0), angle)
  origin + local - vec3(0, SitDrop, 0)

proc tileWorld(x, y: int32): Vec3 =
  let
    wx = float32(x) - HalfGrid + 0.5'f32
    wz = float32(y) - HalfGrid + 0.5'f32
  vec3(wx, surfaceHeight(wx, wz), wz)

proc riderWorldPoint(r: Rider, slot: int, angle: float32): Vec3 =
  if r.seated:
    return seatPoint(slot, angle)
  let
    a = tileWorld(r.fromX, r.fromY)
    b = tileWorld(r.tileX, r.tileY)
    span = max(float32(WalkStepTicks), 1.0'f32)
    t = clamp((float32(r.walkHold) + frameAlpha) / span, 0.0'f32, 1.0'f32)
  mix(a, b, t)

proc riderFacing(r: Rider, slot: int): float32 =
  if r.seated:
    if slot == 0: PI.float32 * 0.5'f32
    else: -PI.float32 * 0.5'f32
  elif r.walking:
    let
      dx = float32(r.destX - r.tileX)
      dz = float32(r.destY - r.tileY)
    arctan2(dx, dz)
  else:
    let
      pos = tileWorld(r.tileX, r.tileY)
      origin = seesawOrigin()
    arctan2(origin.x - pos.x, origin.z - pos.z)

proc renderTime(ticks: int32): float32 =
  (float32(ticks) + frameAlpha) / float32(TickRate)

proc weatherHour(world: World): float32 =
  ## Park lighting stays in daylight. Weather still tints the sky, but a
  ## damp seed must not turn the playground into dusk.
  if world.wetBand == WetWet:
    return 12.2'f32
  if world.wetBand == WetDamp:
    return 12.8'f32
  case world.tempBand
  of TempCold: 11.6'f32
  of TempCool: 12.4'f32
  of TempMild: 13.2'f32
  of TempWarm: 14.0'f32
  of TempHot: 14.6'f32

proc runGraphics*() =
  startGameProfile()
  profileBlock "atlas":
    let builder = newHudAtlas(4096)
    addHudIcons(builder)
    builder.addDefaultFonts()
    builder.write(AtlasPath)
  profileBlock "window":
    (window, sk) = initGameWindow(
      WindowTitle,
      AtlasPath,
      gameWindowSize(options.windowWidth, options.windowHeight),
      options.vsync
    )
  let splash = startSplash(sk, window)

  profileBlock "terrain":
    quadterrain.seed = run.mapSeed
    setTileMaterial(
      int(GrassTile),
      GrassMaterial, DirtMaterial,
      vec3(1.08, 1.22, 0.88), vec3(0.92, 1.02, 0.72),
      1
    )
    setTileMaterial(
      int(MarshTile),
      SandMaterial, SandMaterial,
      vec3(1.14, 1.04, 0.78), vec3(1.06, 0.94, 0.7),
      6
    )
    setTileMaterial(
      int(StoneTile),
      SandMaterial, SandMaterial,
      vec3(1.1, 1.0, 0.76), vec3(1.02, 0.92, 0.68),
      5
    )
    setTileMaterial(
      int(RoadTile),
      DirtMaterial, DirtMaterial,
      vec3(1.12, 0.98, 0.78), vec3(1.02, 0.88, 0.68),
      4
    )
    terrainBlendDepth = 0.06'f32
    initTerrain()
    scatterGrass(1100, run.mapSeed)

  var kits: array[DecorKit, PropPack]
  proc placeParkProps() =
    clearProps()
    for d in placeDecor(run.world.map, run.mapSeed):
      kits[d.kit].placeProp(
        d.node,
        vec3(d.x - HalfGrid, surfaceHeight(d.x - HalfGrid, d.y - HalfGrid) + d.lift,
          d.y - HalfGrid),
        d.yaw, d.height, d.tint)
    bakeTerrain(rebuildWalkability = false)

  profileBlock "props":
    for kit in DecorKit:
      if nodesFor(kit).len == 0:
        continue
      kits[kit] = loadPropPack(
        DataRoot & "/" & kitFile(kit), only = nodesFor(kit), textured = true)
    placeParkProps()

  block:
    var values = newSeq[uint8](GridTiles * GridTiles)
    for value in values.mitems:
      value = 255
    uploadTerrainVisibility(values)

  var
    riderModels: array[RiderCount, CharacterModel]
    riderClips: array[RiderCount, array[AnimationSlot, int]]
  profileBlock "models":
    for slot in 0 ..< RiderCount:
      riderModels[slot] = loadModularCharacterModel(
        ModularCharacterPath,
        riderParts(slot),
        RiderHeight
      )
      for animation in AnimationSlot:
        riderClips[slot][animation] =
          riderModels[slot].clipIndex(animation)
  drawSplash(sk, window, splash.name)

  let scene = newCharacterScene(window)
  scene.useToonShading()
  setEnvironmentPalette(scene.toon)
  var worldShapes = initShapeRenderer()

  cameraTarget = seesawOrigin()
  var actionCam = initActionCam(
    minDistance = 6,
    maxDistance = 28,
    tight = 0.55,
    followRate = 1.35,
    zoomRate = 0.9,
    holdSeconds = 1.6,
    mapSpan = 14,
    closeScale = 0.62
  )

  seekCheckpoints.add SeekCheckpoint(
    world: run.world.clone(),
    hashCheck: run.hashCheck
  )

  proc captureCheckpoint() =
    if run.world.tick div SeekCheckpointTicks < seekCheckpoints.len:
      return
    seekCheckpoints.add SeekCheckpoint(
      world: run.world.clone(),
      hashCheck: run.hashCheck
    )

  proc restoreTo(target: int32) =
    let wanted = clamp(target, 0'i32, transport.timelineEnd)
    var slot = min(
      int(wanted) div SeekCheckpointTicks,
      seekCheckpoints.len - 1
    )
    while slot > 0 and seekCheckpoints[slot].world.tick > wanted:
      dec slot
    run.world.restore(seekCheckpoints[slot].world)
    if run.recorder != nil:
      run.replayPlayer.data = run.recorder.data
    run.replayPlayer.syncCursor(uint32(run.world.tick))
    run.hashCheck = seekCheckpoints[slot].hashCheck
    run.historyPlayback = true
    haveAngle = false
    while run.world.tick < wanted:
      advanceGame()
      captureCheckpoint()

  proc playerMode(): bool =
    options.playerSlot > 0 and not run.replayMode

  proc screenPosition(position: Vec3, viewProjection: Mat4): Vec2 =
    let clip = viewProjection * vec4(
      position.x, position.y, position.z, 1)
    if clip.w <= 0:
      return vec2(-10000)
    let normalized = vec2(clip.x / clip.w, clip.y / clip.w)
    vec2(
      (normalized.x * 0.5'f32 + 0.5'f32) * window.size.x.float32,
      (0.5'f32 - normalized.y * 0.5'f32) * window.size.y.float32
    )

  proc feedActionCam() =
    let
      tick = run.world.tick
      angle = renderAngle()
    actionCam.beginFrame(tick)
    actionCam.noteInterest(1, seesawOrigin(), 90, 4.2, tick, 60)
    for slot in 0 ..< RiderCount:
      let r = run.world.riders[slot]
      let pos = riderWorldPoint(r, slot, angle)
      if r.sick or r.nausea > 500:
        actionCam.noteInterest(int32(slot) + 10, pos, 55, 2.0, tick, 28)
      elif r.pump and r.seated:
        actionCam.noteInterest(int32(slot) + 10, pos, 35, 1.8, tick, 20)

  proc updateCamera(dt: float32) =
    let overUi = mouseOverUi(window, sk.mousePos)
    if window.mousePressed(MouseRight) and not overUi:
      panning = true
    if not window.mouseDown(MouseRight):
      panning = false
    let delta = window.mouseDelta.vec2
    if panning and delta.length > 0:
      followSlot = -1
      actionCam.takeManual()
      let speed = cameraDistance * 0.0015
      cameraTarget.x -= delta.x * speed
      cameraTarget.z -= delta.y * speed
    if applyRtsPan(
        cameraTarget,
        rtsPanDir(window),
        dt,
        cameraDistance,
        40.0'f32
      ):
      followSlot = -1
      actionCam.takeManual()
    if not overUi and window.scrollDelta.y != 0:
      actionCam.takeManual()
      cameraDistance = clamp(
        cameraDistance * pow(0.92'f32, window.scrollDelta.y / 3.0'f32),
        6.0'f32,
        120.0'f32
      )
    if actionCam.enabled:
      feedActionCam()
      actionCam.chooseShot(dt, transport.speed)
      actionCam.follow(
        cameraTarget,
        cameraDistance,
        dt,
        transport.speed
      )
      return
    if followSlot >= 0:
      let
        r = run.world.riders[followSlot]
        focus = riderWorldPoint(r, int(followSlot), renderAngle())
      cameraTarget = mix(cameraTarget, focus, damping(5.0'f32, dt))

  proc cameraView(): Mat4 =
    const Pitch = 0.58'f32
    cameraEye = cameraTarget + vec3(0, sin(Pitch), cos(Pitch)) * cameraDistance
    lookAt(cameraEye, cameraTarget, vec3(0, 1, 0))

  proc drawSeesaw(angle: float32) =
    worldShapes.clear()
    let origin = seesawOrigin()
    let postH = FulcrumLift + 0.06'f32
    worldShapes.addBox(
      origin + vec3(0, -postH * 0.5'f32, 0.18'f32),
      vec3(0.16'f32, postH, 0.16'f32), 0, FulcrumColor)
    worldShapes.addBox(
      origin + vec3(0, -postH * 0.5'f32, -0.18'f32),
      vec3(0.16'f32, postH, 0.16'f32), 0, FulcrumColor)
    worldShapes.addBox(
      origin, vec3(0.36'f32, 0.2'f32, 0.52'f32), 0, PivotColor)
    worldShapes.addBox(
      origin + rotateZ(vec3(-PlankHalf * 0.5'f32, 0, 0), angle),
      vec3(PlankHalf, 0.14'f32, 0.58'f32), angle, PlankWest)
    worldShapes.addBox(
      origin + rotateZ(vec3(PlankHalf * 0.5'f32, 0, 0), angle),
      vec3(PlankHalf, 0.14'f32, 0.58'f32), angle, PlankEast)
    worldShapes.addBox(
      origin + rotateZ(vec3(-SeatAlong, 0.12'f32, 0), angle),
      vec3(0.58'f32, 0.08'f32, 0.62'f32), angle, SeatColor)
    worldShapes.addBox(
      origin + rotateZ(vec3(SeatAlong, 0.12'f32, 0), angle),
      vec3(0.58'f32, 0.08'f32, 0.62'f32), angle, SeatColor)
    worldShapes.addBox(
      origin + rotateZ(vec3(-SeatAlong, 0.4'f32, 0.2'f32), angle),
      vec3(0.09'f32, 0.5'f32, 0.09'f32), angle, HandleColor)
    worldShapes.addBox(
      origin + rotateZ(vec3(SeatAlong, 0.4'f32, 0.2'f32), angle),
      vec3(0.09'f32, 0.5'f32, 0.09'f32), angle, HandleColor)

  proc drawRain() =
    if run.world.wetBand != WetWet:
      return
    worldShapes.clear()
    let origin = seesawOrigin()
    let drops = if run.world.wetBand == WetWet: 90 else: 40
    for i in 0 ..< drops:
      let
        n = uint32(run.world.tick * 13 + i * 97)
        x = origin.x + (float32(n mod 170) / 170.0'f32 - 0.5'f32) * 18.0'f32
        z = origin.z + (float32((n div 170) mod 170) / 170.0'f32 - 0.5'f32) * 18.0'f32
        phase = float32((n + uint32(run.world.tick) * 40) mod 220) / 220.0'f32
        y0 = origin.y + 8.0'f32 - phase * 9.0'f32
      worldShapes.addQuad(
        vec3(x, y0, z),
        vec3(x + 0.03'f32, y0, z),
        vec3(x + 0.03'f32, y0 - 0.55'f32, z),
        vec3(x, y0 - 0.55'f32, z),
        RainColor
      )

  proc drawWorldRiders(angle: float32) =
    for slot in 0 ..< RiderCount:
      let
        r = run.world.riders[slot]
        model = riderModels[slot]
        clip = riderClips[slot][r.animation]
      var animTime = renderTime(r.animationTicks)
      if r.animation in {PumpAnimation, FunAnimation, SickAnimation}:
        animTime = min(animTime, clipDuration(model, clip))
      drawCharacter(
        scene, model, riderWorldPoint(r, slot, angle), riderFacing(r, slot),
        clip, animTime, sizeFactor = 0.88'f32,
        tilt = (if r.seated: angle else: 0'f32))

  var lastFrameTime = epochTime()
  const Step = 1.0'f32 / float32(TickRate)

  proc advanceRenderedGame() =
    previousAngle = run.world.angleMilli.float32 / 1000.0'f32
    haveAngle = true
    advanceGame()
    captureCheckpoint()

  when defined(takeScreenshot):
    applyScreenshotCamera(cameraDistance)
    actionCam.takeManual()
    cameraTarget = seesawOrigin()
    if existsEnv("SIM_SECONDS"):
      let wanted = int32(getEnv("SIM_SECONDS").parseFloat * TickRate.float64)
      while run.world.tick < wanted and
          run.world.tick < run.maximumTicks and not run.world.over:
        advanceGame()
    var screenshotFrame = 0

  holdSplash(sk, window, splash)
  window.onFrame = proc() =
    profileBlock "frame":
      let dt = frameDelta(lastFrameTime, Step)
      sk.uiScale = hudUiScale(window)
      sk.mousePos = window.mousePos.vec2 / sk.uiScale
      profileBlock "camera":
        updateCamera(dt)
      let recorded =
        if run.recorder != nil: int32(run.recorder.data.hashes.len)
        else: int32(run.replayPlayer.data.hashes.len)
      transport.sync(run.world.tick, recorded, run.world.over)
      let restoreTick = transport.takeRestore()
      if restoreTick >= 0:
        restoreTo(restoreTick)
        transport.sync(run.world.tick, recorded, run.world.over)
      transport.startFrame(dt, TickRate)
      let frameStart = epochTime()
      run.historyPlayback = transport.inHistory
      profileBlock "simulate":
        while transport.shouldTick(frameStart):
          if atLiveTickCap(run.world.tick, run.maximumTicks, transport.live):
            break
          run.historyPlayback = transport.inHistory
          advanceRenderedGame()
          let recordedNow =
            if run.recorder != nil: int32(run.recorder.data.hashes.len)
            else: int32(run.replayPlayer.data.hashes.len)
          transport.sync(run.world.tick, recordedNow, run.world.over)
      let active = simulationActive(transport)
      frameAlpha =
        if active:
          clamp(transport.accumulator / Step, 0.0'f32, 1.0'f32)
        else:
          0.0'f32
      let
        aspect = window.size.x.float32 / max(window.size.y.float32, 1)
        view = cameraView()
        projection = perspective(45.0'f32, aspect, 0.1'f32, 1000.0'f32)
        viewProjection = projection * view
        angle = renderAngle()
      profileBlock "drawWorld":
        scene.setToonHour(weatherHour(run.world))
        setEnvironmentPalette(scene.toon)

        proc drawRiders() =
          drawWorldRiders(angle)

        sunDepthPasses(window.size):
          drawTerrainSunDepth()
          scene.sunDepthPass = true
          drawRiders()
          scene.sunDepthPass = false
        glClearColor(0.55, 0.78, 0.94, 1.0)
        if run.world.wetBand != WetDry:
          glClearColor(0.62, 0.74, 0.84, 1.0)
        elif run.world.tempBand == TempHot:
          glClearColor(0.62, 0.84, 0.96, 1.0)
        elif run.world.tempBand == TempCold:
          glClearColor(0.72, 0.84, 0.94, 1.0)
        glClear(GL_COLOR_BUFFER_BIT or GL_DEPTH_BUFFER_BIT)
        drawTerrain(viewProjection, showTiles)
        drawSeesaw(angle)
        worldShapes.draw(viewProjection)
        beginCharacters(scene, window, view, projection, cameraEye)
        drawRiders()
        finishCharacters(scene)
        if run.world.wetBand != WetDry:
          drawRain()
          worldShapes.draw(viewProjection)
      profileBlock "ui":
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glDisable(GL_BLEND)
        when not defined(emscripten):
          glDisable(GL_MULTISAMPLE)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, sk.atlasTextureId())
        sk.beginUi(window, window.size)
        for slot in 0 ..< RiderCount:
          let r = run.world.riders[slot]
          if r.expression <= 0 or r.expressionAge > ExpressionHoldTicks * 2:
            continue
          let anchor = screenPosition(
            riderWorldPoint(r, slot, angle) + vec3(0, RiderHeight + 0.28'f32, 0),
            viewProjection
          ) / sk.uiScale
          sk.drawSprite(
            expressionKey(r.expression),
            anchor - vec2(18, 18),
            vec2(36)
          )
        drawUi(sk, window, transport, actionCam, followSlot)
        sk.endUi()
      when defined(takeScreenshot):
        captureScreenshot(
          window,
          screenshotFrame,
          3,
          "seesaw.png"
        )
      profileBlock "present":
        window.presentFrame(framePaceHz)
    if noteProfileFrame():
      when not defined(emscripten):
        window.closeRequested = true

  window.onButtonPress = proc(button: Button) =
    case button
    of KeySpace: transport.handleKey(button)
    of KeyC:
      var following = followSlot >= 0
      actionCam.toggle(following)
      if not following:
        followSlot = -1
    of KeyT: scene.toggleShading()
    of KeyF1, KeyF2:
      discard handleChromeKey(button)
    of KeyQ:
      if playerMode():
        queueLean(options.playerSlot - 1, -1)
    of KeyE:
      if playerMode():
        queueLean(options.playerSlot - 1, 1)
    of KeyF:
      if playerMode():
        let on = not run.world.riders[options.playerSlot - 1].pump
        queuePump(options.playerSlot - 1, int32(on))
    of KeyR:
      if playerMode():
        queueRest(options.playerSlot - 1)
    of KeyEscape:
      when not defined(emscripten):
        window.closeRequested = true
    else:
      if playerMode() and button in {Key1, Key2, Key3, Key4, Key5,
          Key6, Key7, Key8, Key9}:
        let face = int32(button.ord - Key1.ord) + 1
        queueExpress(options.playerSlot - 1, face)

  while not window.closeRequested:
    pollEvents()
  saveRecording()
  finishGameProfile()
