## Seesaw Silky HUD.
##
## Two rider cards, weather, the pair score, expression buttons, and the
## shared replay transport.

import
  std/strformat,
  chroma, pixie, silky, vmath, windy,
  polyworld/[actioncam, chrome, gameuis, inputs, player],
  content, sim, game, controls

const
  PanelRoster = vec2(300, 292)
  PanelClock = vec2(360, 72)
  PanelFaces = vec2(300, 188)
  HudClearance = 24.0'f32
  RiderColors*: array[RiderCount, ColorRGBX] = [
    rgbx(226, 108, 92, 255),
    rgbx(92, 148, 214, 255)
  ]

var riderPortraitKeys: array[RiderCount, string]
for slot in 0 ..< RiderCount:
  riderPortraitKeys[slot] = "ssw_p" & $slot

proc riderPortraitKey*(slot: int32): string =
  riderPortraitKeys[slot]

type
  HudChrome = object
    layout: GameUiLayout
    roster: GameUiPanel
    clock: GameUiPanel
    faces: GameUiPanel

proc placeChrome(layout: GameUiLayout): HudChrome =
  result.layout = layout
  result.roster = layout.panel(GameUiRegion.TopLeft, PanelRoster)
  result.clock = layout.panel(GameUiRegion.TopCenter, PanelClock)
  result.faces = layout.panel(GameUiRegion.TopRight, PanelFaces)

proc hudLayoutFits(layoutSize: Vec2): bool =
  let
    layout = initGameUiLayout(layoutSize, TransportHeight)
    chrome = placeChrome(layout)
  layoutFits(
    layout,
    [chrome.roster, chrome.clock, chrome.faces],
    HudClearance
  )

proc hudUiScale*(windowSize: Vec2): float32 =
  fitUiScale(windowSize, hudLayoutFits, UiCrispSteps)

proc hudUiScale*(window: Window): float32 =
  hudUiScale(vec2(window.size.x.float32, window.size.y.float32))

proc currentLayout*(window: Window): GameUiLayout =
  initGameUiLayout(
    vec2(window.size.x.float32, window.size.y.float32) /
      hudUiScale(window),
    TransportHeight
  )

proc currentChrome(window: Window): HudChrome =
  placeChrome(currentLayout(window))

proc mouseOverUi*(window: Window, mouse: Vec2): bool =
  if mouseOverDebugMenu(mouse):
    return true
  let chrome = currentChrome(window)
  mouseOverPanels(
    mouse,
    chrome.layout,
    [chrome.roster, chrome.clock, chrome.faces]
  )

proc drawRiderCard(
    sk: Silky, origin: Vec2, slot: int32, r: Rider, pairScore: int32
) =
  let color = RiderColors[slot]
  sk.drawSprite(riderPortraitKey(slot), origin, vec2(56), radius = 8)
  sk.drawLabel(
    RiderNames[slot],
    origin + vec2(64, 0),
    vec2(160, 22),
    color,
    "Bold"
  )
  sk.drawLabel(
    &"fun {r.feltFun}",
    origin + vec2(64, 22),
    vec2(160, 18),
    rgbx(220, 224, 232, 255),
    "Small"
  )
  sk.drawBar(
    origin + vec2(64, 42),
    vec2(170, 10),
    float32(r.feltFun),
    max(float32(pairScore), 1),
    color
  )
  sk.drawBar(
    origin + vec2(64, 56),
    vec2(170, 8),
    float32(r.nausea),
    float32(SickLimit),
    rgbx(120, 196, 96, 255)
  )
  if r.expression > 0:
    sk.drawSprite(
      expressionKey(r.expression),
      origin + vec2(238, 8),
      vec2(40)
    )
  let status =
    if r.seated: "on the board"
    elif r.walking: "walking"
    else: "taking a break"
  sk.drawLabel(
    status,
    origin + vec2(64, 70),
    vec2(170, 16),
    rgbx(180, 188, 198, 255),
    "Small"
  )

proc drawUi*(
    sk: Silky,
    window: Window,
    transport: var player.Player,
    actionCam: var ActionCam,
    followSlot: var int32
) =
  let
    chrome = currentChrome(window)
    roster = sk.beginPanel(chrome.roster)
    clock = sk.beginPanel(chrome.clock)
    faces = sk.beginPanel(chrome.faces)
    world = run.world
    pair = world.scores[0]
    shownPair =
      if world.over: pair
      else: pairScore(world.riders[0].feltFun, world.riders[1].feltFun)

  sk.drawLabel(
    "THE BOARD",
    roster.origin,
    vec2(roster.size.x, 20),
    rgbx(200, 205, 216, 255),
    "Small"
  )
  for slot in 0 ..< RiderCount:
    let y = 26.0'f32 + float32(slot) * 120.0'f32
    sk.drawRiderCard(
      roster.origin + vec2(0, y),
      int32(slot),
      world.riders[slot],
      max(shownPair, 1)
    )

  let
    left = world.maximumTicks - world.tick
    seconds = left div TickRate
  sk.drawLabel(
    &"{TempNames[world.tempBand]}  {WindNames[world.windBand]}  " &
      &"{WetNames[world.wetBand]}",
    clock.origin,
    vec2(clock.size.x, 22),
    rgbx(220, 224, 232, 255),
    "Small",
    CenterAlign
  )
  sk.drawLabel(
    &"{seconds div 60}:{seconds mod 60:02}   pair {shownPair}",
    clock.origin + vec2(0, 24),
    vec2(clock.size.x, 28),
    rgbx(235, 216, 154, 255),
    "Bold",
    CenterAlign
  )

  sk.drawLabel(
    "FACES",
    faces.origin,
    vec2(faces.size.x, 20),
    rgbx(200, 205, 216, 255),
    "Small"
  )
  const FaceCols = 5
  for face in 1 ..< ExpressionCount:
    let
      index = face - 1
      col = index mod FaceCols
      row = index div FaceCols
      pos = faces.origin + vec2(
        float32(col) * 52 + 8,
        float32(row) * 44 + 28
      )
      panel = GameUiPanel(origin: pos, size: vec2(40, 40))
    sk.drawSprite(expressionKey(int32(face)), pos, vec2(40))
    if options.playerSlot > 0 and not run.replayMode:
      if window.mouseReleased(MouseLeft) and panel.contains(sk.mousePos):
        queueExpress(options.playerSlot - 1, int32(face))

  if world.over:
    sk.drawLabel(
      describeResult(),
      chrome.layout.panel(GameUiRegion.Center, vec2(520, 40)).origin,
      vec2(520, 40),
      rgbx(235, 216, 154, 255),
      "H1",
      CenterAlign
    )

  var following = followSlot >= 0
  transport.drawTransport(
    sk,
    window,
    chrome.layout.transportPanel,
    actionCam,
    following
  )
  if not following:
    followSlot = -1

  if run.hashCheck.mismatches > 0:
    sk.drawError(
      chrome.layout.size,
      &"REPLAY DIVERGED - {run.hashCheck.mismatches} mismatches, " &
        &"first at tick {run.hashCheck.firstTick}"
    )
  sk.drawDebugMenu(window)
