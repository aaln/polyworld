## Human-facing guidance and match flow, separate from the spectator HUD.
import std/[times, strutils], pixie, silky, vmath, windy,
  polyworld/[chrome, gameuis, metrics, player, fxshapes],
  content, sim, game, controls, keybinds, playaudio

const
  Gold = rgbx(249, 218, 137, 255)
  White = rgbx(239, 243, 250, 255)
  Muted = rgbx(174, 188, 207, 255)
  Red = rgbx(255, 122, 110, 255)

type
  CombatSnapshot* = object
    hp*: seq[int32]
    dead*: seq[bool]
    towers*: seq[int32]
    damage*: seq[int64]
  FloatingNumber = object
    position: WorldPoint
    text: string
    at: float64
    heal: bool
  FeedLine = object
    text: string
    at: float64

var
  resumeAfterMenu* = false
  combatNumbers: seq[FloatingNumber]
  eventFeed: seq[FeedLine]
  tooltipAbility* = -1
  tooltipAnchor*: GameUiPanel
  acknowledgedPing = -1'i32
  hitDamage: int64
  hitAt: float64

proc isHumanGame*(): bool = options.playerSlot > 0 and not run.replayMode
proc closePlayAudio*() = closeCombatAudio()
proc humanHero*(): Hero =
  if isHumanGame(): result = run.world.heroes[options.playerSlot - 1]

proc gotaUiScale*(window: Window): float32 =
  if isHumanGame():
    clamp(min(window.size.x.float32 / 1920, window.size.y.float32 / 1080), 0.5'f32, 1.25'f32)
  else: gameUiScale(window)

proc resetPlayFeedback*() =
  combatNumbers.setLen(0)
  eventFeed.setLen(0)
  tooltipAbility = -1
  acknowledgedPing = -1
  hitAt = 0

proc snapshotCombat*(world: World): CombatSnapshot =
  for hero in world.heroes:
    result.hp.add hero.hp
    result.dead.add(hero.state == Dying or hero.hp <= 0)
  for tower in world.towers: result.towers.add tower.hp
  for row in world.stats.values: result.damage.add row[DamageMetric]

proc addFeed(text: string) =
  eventFeed.add FeedLine(text: text, at: epochTime())
  if eventFeed.len > 4: eventFeed.delete(0)

proc observeCombat*(before: CombatSnapshot, world: World, ownId: int32) =
  let own = world.heroById(ownId)
  if own.id == 0: return
  let ownSlot = world.heroIndex(ownId)
  let dealt = world.stats.values[ownSlot][DamageMetric] - before.damage[ownSlot]
  if dealt > 0:
    hitDamage = dealt
    hitAt = epochTime()
    playCombatCue(HitCue)
  let ping = world.activeTeamPing(own.team)
  let responder = world.heroById(ping.responderId)
  if ping.byId == ownId and acknowledgedPing != ping.tick and
      responder.id != 0 and responder.hasMoveTarget and
      responder.moveTileX == ping.x and responder.moveTileY == ping.y:
    acknowledgedPing = ping.tick
    addFeed(responder.class.heroSpec.name & " is responding to your call")
  for i, hero in world.heroes:
    if i >= before.hp.len: continue
    let dead = hero.state == Dying or hero.hp <= 0
    let visible = hero.team == own.team or world.visible(own.team, hero.position)
    if not before.dead[i] and dead and visible:
      if hero.id == ownId: playCombatCue(DeathCue)
      addFeed(if hero.id == ownId: "You fell. You will respawn at your base."
        else: hero.class.heroSpec.name & " was defeated")
    if before.dead[i] and not dead and hero.id == ownId:
      playCombatCue(RespawnCue)
      followPlayer = true
      focusPlayerRequested = true
      notifyPlayer("Respawned - your camera is following you")
    let delta = max(0'i32, hero.hp) - max(0'i32, before.hp[i])
    if visible and not before.dead[i] and (delta <= -1 or delta >= 5):
      if hero.id == ownId and not dead: playCombatCue(if delta < 0: HurtCue else: HealCue)
      combatNumbers.add FloatingNumber(position: hero.position,
        text: (if delta > 0: "+" else: "") & $delta,
        heal: delta > 0, at: epochTime())
  while combatNumbers.len > 48: combatNumbers.delete(0)
  for i, tower in world.towers:
    if i < before.towers.len and before.towers[i] > 0 and tower.hp <= 0 and
      (tower.team == own.team or world.visible(own.team, tower.position)):
        addFeed((if tower.team == own.team: "Allied " else: "Enemy ") & $tower.tier & " tower destroyed")

proc objective*(world: World, hero: Hero): tuple[text: string, id: int32, position: WorldPoint] =
  result.text = "Follow a friendly wave: outer tower > inner > gate > fort"
  var distance = int64.high
  for tower in world.towers:
    if tower.team == hero.team or not world.towerExposed(tower) or
      not world.visible(hero.team, tower.position): continue
    let dx = int64(hero.position.x) - tower.position.x
    let dz = int64(hero.position.z) - tower.position.z
    let d = dx * dx + dz * dz
    if d < distance:
      distance = d
      result = ("Push with your wave: destroy the " & $tower.tier & " tower",
        tower.id, tower.position)
  for fort in world.forts:
    if fort.team != hero.team and world.fortExposed(fort.team) and fort.hp > 0 and
      world.visible(hero.team, fort.center):
        result = ("The enemy fort is exposed - destroy it to win", fort.id, fort.center)

proc barPanel*(size: Vec2): GameUiPanel =
  GameUiPanel(origin: vec2(18, 170), size: vec2(520, 94))
proc cameraPanel*(size: Vec2): GameUiPanel =
  GameUiPanel(origin: vec2(size.x - 360, 170), size: vec2(340, 104))
proc tutorialPanel(size: Vec2): GameUiPanel =
  GameUiPanel(origin: vec2((size.x - 850) / 2, size.y - 425), size: vec2(850, 90))

proc playUiContains*(mouse, size: Vec2): bool =
  if not isHumanGame(): return false
  if controlsOpen or setupOpen or (not historyOpen and
      (run.world.gameOver or run.world.tick >= options.maximumTicks)):
    return true
  barPanel(size).contains(mouse) or cameraPanel(size).contains(mouse) or
    (tutorialEnabled and tutorialStep < 5 and tutorialPanel(size).contains(mouse))

proc playButton(sk: Silky, window: Window, panel: GameUiPanel,
    label: string, active = false): bool =
  sk.drawTab(panel, selected = active, hovered = sk.hovered(panel))
  sk.drawLabel(label, panel.origin + vec2(8, 0), panel.size - vec2(16, 0),
    if active: Gold else: White, "Bold", CenterAlign)
  window.mousePressed(MouseLeft) and panel.contains(sk.mousePos)

proc abilityLines*(hero: Hero, slot: HeroAbilitySlot): seq[string] =
  let spec = heroAbility(hero.class, slot).abilitySpec
  result.add abilityKeyLabel(slot.ord) & " - " & spec.name
  result.add(case spec.casting
    of SelfCast: "Instantly affects you."
    of MeleeCast: "Strike nearby enemies in the direction you aim."
    of ProjectileCast: "Aim at an enemy, or fire at the ground."
    of AreaCast: "Aim the marked area to affect " & (if spec.kind == Strike: "enemies." else: "allies."))
  result.add(if spec.kind == Heal: "Use when wounded; area healing can aid teammates."
    elif spec.kind == Restore: "Recover mana before your next spell rotation."
    elif spec.casting == ProjectileCast: "Ground shots stop at the first enemy they hit."
    elif spec.area.innerRadius > 0: "Keep enemies in the band; the center misses."
    elif spec.area.shape == SectorFootprint: "Face a group to catch them inside the cone."
    elif spec.area.shape == LineFootprint: "Line up enemies along the marked strip."
    else: "Aim where enemies will be when the effect lands.")
  if spec.damage > 0: result.add $spec.damage & " damage"
  if spec.heal > 0: result.add "Restores " & $spec.heal & " health"
  if spec.restore > 0: result.add "Restores " & $spec.restore & " mana"
  result.add $spec.manaCost & " mana | range " & formatFloat(spec.range.float / WorldScale.float, ffDecimal, 1)
  result.add "Cooldown " & spec.cooldownTicks.secondsLabel & " | " & $spec.charges & " charges"
  result.add "One charge returns every " & spec.rechargeTicks.secondsLabel
  let reason = run.world.abilityReadyReason(hero, slot)
  result.add(if reason.len == 0: "Ready" else: reason)

proc drawAbilityTooltip*(sk: Silky, window: Window, hero: Hero,
    slot: HeroAbilitySlot, anchor: GameUiPanel, size: Vec2) =
  let lines = abilityLines(hero, slot)
  let panel = GameUiPanel(origin: vec2(
    clamp(anchor.origin.x, 8'f32, size.x - 478),
    max(8'f32, anchor.origin.y - lines.len.float32 * 27 - 22)),
    size: vec2(470, lines.len.float32 * 27 + 16))
  sk.drawRect(panel.origin, panel.size, rgbx(8, 13, 23, 248))
  for i, line in lines:
    sk.drawLabel(line, panel.origin + vec2(14, 8 + i.float32 * 27), vec2(442, 26),
      if i == 0: Gold else: White, if i == 0: "Bold" else: "Default")

proc drawStartMenu(sk: Silky, window: Window, size: Vec2) =
  sk.drawRect(vec2(0), size, rgbx(5, 9, 16, 225))
  let panel = GameUiPanel(origin: (size - vec2(1110, 720)) / 2, size: vec2(1110, 720))
  let inner = sk.beginPanel(panel)
  sk.drawLabel("GODS OF THE ARENA", inner.origin, vec2(inner.size.x, 46), Gold, "H1", CenterAlign)
  sk.drawLabel("Choose your hero. Four teammates and five opponents are ready.",
    inner.origin + vec2(0, 50), vec2(inner.size.x, 34), White, "Default", CenterAlign)
  for i, hero in run.world.heroes:
    let card = GameUiPanel(origin: inner.origin + vec2((i mod 5).float32 * 210, 100 + (i div 5).float32 * 70),
      size: vec2(200, 58))
    if sk.playButton(window, card, hero.class.heroSpec.name, menuSlot == i.int32 + 1):
      menuSlot = i.int32 + 1
  let hero = run.world.heroes[menuSlot - 1]
  sk.drawLabel((if hero.team == RedTeam: "RED TEAM - " else: "BLUE TEAM - ") & hero.class.heroSpec.role,
    inner.origin + vec2(0, 252), vec2(inner.size.x, 34), Gold, "Bold")
  for slot in HeroAbilitySlot:
    let spec = heroAbility(hero.class, slot).abilitySpec
    sk.drawLabel(abilityKeyLabel(slot.ord) & "  " & spec.name & "  |  " &
      (if spec.damage > 0: $spec.damage & " damage" elif spec.heal > 0: $spec.heal & " healing" else: $spec.restore & " mana") &
      "  |  " & spec.cooldownTicks.secondsLabel & " cooldown",
      inner.origin + vec2(0, 298 + slot.ord.float32 * 34), vec2(inner.size.x, 32), White, "Default")
  if sk.playButton(window, GameUiPanel(origin: inner.origin + vec2(0, 458), size: vec2(510, 48)),
      "Practice - slower enemies, primary abilities", practiceMode): practiceMode = true
  if sk.playButton(window, GameUiPanel(origin: inner.origin + vec2(530, 458), size: vec2(510, 48)),
      "Standard - full bot abilities", not practiceMode): practiceMode = false
  if sk.playButton(window, GameUiPanel(origin: inner.origin + vec2(0, 528), size: vec2(510, 48)),
      "Guide: " & (if tutorialEnabled: "ON" else: "OFF"), tutorialEnabled): tutorialEnabled = not tutorialEnabled
  if sk.playButton(window, GameUiPanel(origin: inner.origin + vec2(530, 528), size: vec2(510, 48)),
      "PLAY VS BOTS  [Enter]", true) or KeyEnter in pressedPlayButtons: startRequested = true
  sk.drawLabel("Destroy the enemy fort. Stay with your wave and clear towers in order.",
    inner.origin + vec2(0, 600), vec2(inner.size.x, 40), Muted, "Default", CenterAlign)

proc drawControls(sk: Silky, window: Window, size: Vec2, transport: var Player) =
  sk.drawRect(vec2(0), size, rgbx(5, 9, 16, 225))
  let inner = sk.beginPanel(GameUiPanel(origin: (size - vec2(960, 720)) / 2, size: vec2(960, 720)))
  sk.drawLabel("PAUSED - CONTROLS", inner.origin, vec2(inner.size.x, 42), Gold, "H1")
  let rows = [
    "Right-click: move / attack. Left-click: inspect or confirm a targeted cast.",
    abilityKeyLabel(0) & " / " & abilityKeyLabel(1) & " / " & abilityKeyLabel(2) &
      " / " & abilityKeyLabel(3) & ": abilities. Cooldowns and charges show below.",
    keyLabel(AttackMove) & ": attack-move. " & keyLabel(Stop) & ": stop. F / G: use items.",
    keyLabel(CenterHero) & ": return to your hero. " & keyLabel(FollowHero) & ": toggle auto camera.",
    "Hold " & keyLabel(PanCamera) & " and move the pointer to pan. Arrows / minimap also pan.",
    keyLabel(TeamCall) & ": assist ping. Shift: defend. Ctrl: retreat. Alt: attack.",
    "Esc cancels aiming. Space pauses. B opens the shop. F6 opens replay inspection."]
  for i, row in rows:
    sk.drawLabel(row, inner.origin + vec2(0, 60 + i.float32 * 36), vec2(inner.size.x, 34), White, "Default")
  for mode in CastMode:
    let i = mode.ord
    let label = ["Quickcast at cursor", "Aim then left-click", "Assist: combat target"][i]
    if sk.playButton(window, GameUiPanel(origin: inner.origin + vec2(i.float32 * 300, 344), size: vec2(286, 48)), label, castMode == mode):
      castMode = mode
      cancelPlayerAim()
  for preset in ControlPreset:
    let i = preset.ord
    if sk.playButton(window, GameUiPanel(origin: inner.origin + vec2(i.float32 * 300, 410), size: vec2(286, 48)),
        ["Mouse + abilities", "WASD + 1-4", "A/D/S mouse keys"][i], controlPreset == preset):
      setControlPreset(preset)
      cancelPlayerAim()
  sk.drawLabel("Quickcast: cast at cursor. Aim mode: preview, then click.",
    inner.origin + vec2(0, 480), vec2(630, 48), Muted, "Default")
  if sk.playButton(window, GameUiPanel(origin: inner.origin + vec2(660, 480), size: vec2(226, 48)),
      "Combat sound: " & (if combatAudio: "ON" else: "OFF"), combatAudio):
    if not toggleCombatAudio(): notifyPlayer("Audio output unavailable", true)
  if sk.playButton(window, GameUiPanel(origin: inner.origin + vec2(0, 548), size: vec2(286, 52)), "Resume", true):
    controlsOpen = false
    transport.playing = true
  if sk.playButton(window, GameUiPanel(origin: inner.origin + vec2(300, 548), size: vec2(286, 52)), "Choose hero / new match"):
    controlsOpen = false
    setupOpen = true
  if sk.playButton(window, GameUiPanel(origin: inner.origin + vec2(600, 548), size: vec2(286, 52)), "Guide: " & (if tutorialEnabled: "ON" else: "OFF")):
    tutorialEnabled = not tutorialEnabled

proc drawPlayUi*(sk: Silky, window: Window, transport: var Player,
    inspectedId: int32, viewProjection: Mat4) =
  if not isHumanGame(): return
  let hero = humanHero()
  let size = window.size.vec2 / sk.uiScale
  let now = epochTime()
  let over = run.world.gameOver or run.world.tick >= options.maximumTicks
  if setupOpen:
    sk.drawStartMenu(window, size)
    return
  if controlsOpen:
    sk.drawControls(window, size, transport)
    return
  if over and not historyOpen:
    sk.drawRect(vec2(0), size, rgbx(5, 9, 16, 210))
    let inner = sk.beginPanel(GameUiPanel(origin: (size - vec2(850, 420)) / 2, size: vec2(850, 420)))
    let outcome = if not run.world.gameOver: "TIME LIMIT - DRAW"
      elif hero.team == run.world.winner: "VICTORY" else: "DEFEAT"
    sk.drawLabel(outcome, inner.origin, vec2(inner.size.x, 60), Gold, "H1", CenterAlign)
    let values = run.world.stats.values[options.playerSlot - 1]
    sk.drawLabel("Kills " & $values[KillsMetric] & "   Deaths " & $values[LossesMetric] &
      "   Assists " & $values[AssistsMetric], inner.origin + vec2(0, 100), vec2(inner.size.x, 38), White, "Bold", CenterAlign)
    sk.drawLabel("Damage " & $values[DamageMetric] & "   Healing " & $values[HealingMetric] &
      "   Level " & $hero.level, inner.origin + vec2(0, 150), vec2(inner.size.x, 38), Muted, "Default", CenterAlign)
    if sk.playButton(window, GameUiPanel(origin: inner.origin + vec2(0, 250), size: vec2(380, 56)), "PLAY AGAIN  [Enter]", true) or KeyEnter in pressedPlayButtons:
      restartRequested = true
    if sk.playButton(window, GameUiPanel(origin: inner.origin + vec2(400, 250), size: vec2(380, 56)), "Choose another hero"):
      setupOpen = true
    return
  if historyOpen:
    let footer = GameUiPanel(origin: vec2((size.x - 980) / 2, size.y - 76), size: vec2(980, 70))
    sk.drawRect(footer.origin, footer.size, rgbx(8, 13, 23, 255))
    if sk.playButton(window, GameUiPanel(origin: footer.origin, size: vec2(220, 58)), "Back 10 seconds"):
      transport.seekTo(max(0'i32, transport.tick - 10 * TickRate), play = false)
    if sk.playButton(window, GameUiPanel(origin: footer.origin + vec2(230, 0), size: vec2(190, 58)),
        if transport.playing: "Pause replay" else: "Play replay"):
      transport.togglePlay()
    if sk.playButton(window, GameUiPanel(origin: footer.origin + vec2(430, 0), size: vec2(240, 58)), "RETURN TO LIVE [F6]", true):
      historyOpen = false
      resetPlayerCommands()
      transport.seekTo(transport.recordedTicks)
    sk.drawLabel("REPLAY  " & transport.tick.secondsLabel, footer.origin + vec2(690, 0), vec2(280, 58), Gold, "Bold")
  let goal = barPanel(size)
  sk.drawRect(goal.origin, goal.size, rgbx(8, 13, 23, 220))
  sk.drawLabel("DESTROY THE ENEMY FORT", goal.origin + vec2(12, 8), vec2(496, 28), Gold, "Bold")
  sk.drawLabel(objective(run.world, hero).text, goal.origin + vec2(12, 40), vec2(496, 48), White, "Default")
  let camera = cameraPanel(size)
  if sk.playButton(window, GameUiPanel(origin: camera.origin, size: vec2(340, 46)),
      "AUTO CAMERA " & (if followPlayer: "ON" else: "OFF") & "  [" & keyLabel(FollowHero) & "]", followPlayer):
    followPlayer = not followPlayer
    focusPlayerRequested = followPlayer
  if sk.playButton(window, GameUiPanel(origin: camera.origin + vec2(0, 56), size: vec2(340, 42)), "Controls / pause  [Esc]"):
    controlsOpen = true
    resumeAfterMenu = transport.playing
    transport.pause()
    resetPlayerCommands()
  if hero.hp > 0 and hero.hp * 4 <= hero.maxHp:
    for panel in [GameUiPanel(origin: vec2(0), size: vec2(size.x, 8)),
      GameUiPanel(origin: vec2(0), size: vec2(8, size.y)),
      GameUiPanel(origin: vec2(size.x - 8, 0), size: vec2(8, size.y))]:
      sk.drawRect(panel.origin, panel.size, rgbx(220, 45, 40, 170))
    sk.drawLabel("LOW HEALTH - FALL BACK", vec2((size.x - 600) / 2, 165), vec2(600, 36), Red, "Bold", CenterAlign)
  if hero.hp <= 0 or hero.state == Dying:
    sk.drawLabel("RESPAWN IN " & hero.respawnTicks.secondsLabel,
      vec2(0, size.y * 0.36), vec2(size.x, 48), Gold, "H1", CenterAlign)
    sk.drawLabel("You will return at your base. Your camera will follow you.",
      vec2(0, size.y * 0.36 + 52), vec2(size.x, 34), White, "Default", CenterAlign)
  for i, event in eventFeed:
    if now - event.at < 7:
      sk.drawLabel(event.text, vec2(24, 290 + i.float32 * 30), vec2(520, 28), Gold, "Default")
  if now - hitAt < 0.65:
    sk.drawLabel("HIT  " & $hitDamage, vec2((size.x - 200) / 2, size.y - 480),
      vec2(200, 34), Gold, "Bold", CenterAlign)
  for number in combatNumbers:
    let age = now - number.at
    if age > 1.1: continue
    let p = number.position
    let clip = viewProjection * vec4(p.x.float32 / WorldScale.float32,
      p.y.float32 / WorldScale.float32 + 2.8, p.z.float32 / WorldScale.float32, 1)
    if clip.w <= 0: continue
    let at = vec2((clip.x / clip.w + 1) * size.x / 2,
      (1 - clip.y / clip.w) * size.y / 2 - age.float32 * 32)
    sk.drawLabel(number.text, at - vec2(50, 0), vec2(100, 36),
      if number.heal: rgbx(132, 246, 150, 255) else: Red, "Bold", CenterAlign)
  if feedbackText.len > 0 and now - feedbackTime < 3:
    let area = GameUiPanel(origin: vec2((size.x - 900) / 2, size.y - 325), size: vec2(900, 38))
    sk.drawRect(area.origin, area.size, rgbx(8, 13, 23, 225))
    sk.drawLabel(feedbackText, area.origin, area.size, if feedbackError: Red else: Gold, "Default", CenterAlign)
  if not transport.playing or historyOpen:
    sk.drawLabel(if historyOpen: "REPLAY INSPECTION - F6 TO RETURN TO LIVE" else: "PAUSED - SPACE TO RESUME",
      vec2(0, 150), vec2(size.x, 38), Gold, "Bold", CenterAlign)
  if tutorialEnabled and tutorialStep < 5 and hero.hp > 0 and not historyOpen:
    if tutorialStep == 0 and successfulMoves > 0: tutorialStep = 1
    if tutorialStep == 1:
      for footman in run.world.footmen:
        if footman.team == hero.team and footman.hp > 0 and within(hero.position, footman.position, 600_000):
          tutorialStep = 2
          break
    if tutorialStep == 2 and successfulAttacks > 0: tutorialStep = 3
    if tutorialStep == 3 and successfulCasts > 0: tutorialStep = 4
    if tutorialStep == 4 and run.world.activeTeamPing(hero.team).byId == hero.id: tutorialStep = 5
    if tutorialStep < 5:
      let panel = tutorialPanel(size)
      sk.drawRect(panel.origin, panel.size, rgbx(8, 13, 23, 235))
      let text = ["Right-click the ground to move out of your base.",
        "Join a friendly wave. Let your minions take the first hits.",
        "Right-click a visible enemy to attack. Left-click only inspects.",
        "Aim at an enemy and press an ability key. Hover its icon to learn more.",
        "Point at the map and press " & keyLabel(TeamCall) & " to ask a teammate for help."][tutorialStep]
      sk.drawLabel("FIRST MATCH  " & $(tutorialStep + 1) & "/5", panel.origin + vec2(14, 5), vec2(650, 28), Gold, "Bold")
      sk.drawLabel(text, panel.origin + vec2(14, 37), vec2(705, 45), White, "Default")
      if sk.playButton(window, GameUiPanel(origin: panel.origin + vec2(730, 15), size: vec2(104, 54)), "Skip"):
        tutorialEnabled = false
  if inspectedId != 0 and inspectedId != hero.id:
    var target: WorldObject
    if run.world.spellTarget(inspectedId, target) and run.world.visible(hero.team, target.position):
      let label = if target.kind == 2: HeroClass(target.class).heroSpec.name else: "Target"
      sk.drawLabel("INSPECTING: " & label & "  |  " & $max(0'i32, target.hp) & " HP" &
        (if target.alive: "" else: "  |  PROTECTED / DEFEATED"),
        vec2((size.x - 800) / 2, 170), vec2(800, 35), Muted, "Default", CenterAlign)
  if tooltipAbility >= 0 and not shopOpen:
    sk.drawAbilityTooltip(window, hero, HeroAbilitySlot(tooltipAbility), tooltipAnchor, size)
