## Controlled actual-engine micropractice, not a competitive opponent proxy.
import std/[os, json, math]
import bassy
import polyworld/[cli, tapes, pathing]
import ../[bots, content, maps, sim, replays]

let source = getEnv("WEEK_POLICY")
doAssert source.len > 0
var maxInstructions, maxWork: int64
var rows = newJArray()

proc middle(): WorldPoint =
  let p = lanePathPoints[1][lanePathPoints[1].len div 2]
  const Unit = WorldScale div PathUnitsPerTile
  WorldPoint(x:p.x*Unit,y:p.y*Unit,z:p.z*Unit)

proc step(g: Game) =
  g.tickWorld(proc() = g.runBotDecisions())
  for vm in g.heroVms:
    if vm != nil:
      doAssert not vm.failed, vm.lastError
      maxInstructions = max(maxInstructions,vm.lastInstructions)
      maxWork = max(maxWork,vm.lastWork)
      doAssert vm.lastInstructions <= 19000
      doAssert vm.lastWork <= 50000

proc quiet(team: Team, class: HeroClass): Game =
  result = newGame(generateMap(54),100_000,10,false,ReplayData(),drafting=false)
  result.loadBots([BotGroup(path:source,count:10)])
  result.recorder = initReplayRecorder(result.currentSetup(10000),defaultConfig())
  for i,h in result.world.heroes:
    h.manualSpells = true
    h.gold = 0
    if i != team.ord*5:
      h.hp = 0; h.state = Dying; h.deathTicks = -1_000_000
      result.heroVms[i] = nil
  let h=result.world.heroes[team.ord*5]
  h.class=class; h.refreshHeroStats();h.hp=h.maxHp;h.mana=h.maxMana
  result.step()

proc stationary(g: Game, team: Team, at: WorldPoint): Hero =
  result=g.world.heroes[team.ord*5]
  result.state=Marching;result.hp=100_000;result.maxHp=100_000
  result.stunnedUntil=1_000_000
  result.place(at)

for team in Team:
  for class in HeroClass:
    let g=quiet(team,class)
    let h=g.world.heroes[team.ord*5]
    let at=middle()
    h.place(at)
    var target=at;target.x+=WorldScale div 2
    discard g.stationary(Team(1-team.ord),target)
    var hits: seq[int32]
    var old=h.attacksLanded
    for i in 0..<360:
      h.hp=h.maxHp;h.mana=0
      g.step()
      if h.attacksLanded>old:hits.add(g.world.tick)
      old=h.attacksLanded
    var gaps: seq[int32]
    for i in 1..<hits.len:gaps.add(hits[i]-hits[i-1])
    rows.add(%*{"kind":"basic_cadence","side":team.ord,"class":class.ord,"ticks":360,"hits":hits.len,"hit_ticks":hits,"intervals":gaps})

  block:
    let g=quiet(team,Ranger)
    let h=g.world.heroes[team.ord*5]
    let at=middle();h.place(at)
    var aim=at;aim.x+=WorldScale*3
    let startGold=h.gold
    let startXp=h.totalXp
    for trial in 0..<24:
      g.world.footmen = @[
        Footman(id:int32(9000+trial*2),team:Team(1-team.ord),hp:int32(20+(trial mod 5)*10),state:Marching,swingTicks: -1),
        Footman(id:int32(9001+trial*2),team:team,hp:10_000,state:Marching,swingTicks:int32((trial*7) mod 32))]
      for f in g.world.footmen.mitems:f.place(aim)
      for i in 0..<90:
        h.hp=h.maxHp;h.mana=0
        for f in g.world.footmen.mitems:
          if f.hp>0:f.place(aim)
        g.step()
    rows.add(%*{"kind":"contested_last_hits","side":team.ord,"trials":24,"ticks":2160,"gold_gain":h.gold-startGold,"xp_gain":h.totalXp-startXp,"hits":h.attacksLanded})

  block:
    let g=quiet(team,Crossbowman)
    let h=g.world.heroes[team.ord*5]
    var origin,aim: WorldPoint
    var found=false
    const Unit=WorldScale div PathUnitsPerTile
    let path=lanePathPoints[1]
    for i in path.len div 3 ..< path.len*2 div 3:
      for j in i+1 ..< min(path.len,i+30):
        let a=WorldPoint(x:path[i].x*Unit,y:path[i].y*Unit,z:path[i].z*Unit)
        let b=WorldPoint(x:path[j].x*Unit,y:path[j].y*Unit,z:path[j].z*Unit)
        let dx=int64(a.x)-b.x;let dz=int64(a.z)-b.z
        let d=dx*dx+dz*dz
        if a.y==b.y and d>int64(WorldScale)*WorldScale*37 and d<int64(WorldScale)*WorldScale*42:
          origin=a;aim=b;found=true;break
      if found:break
    doAssert found,"No same-floor XP boundary fixture"
    h.place(origin)
    doAssert not h.inOwnSpawn
    g.world.footmen = @[Footman(id:9500,team:Team(1-team.ord),hp:10,state:Marching,swingTicks: -1)]
    g.world.footmen[0].place(aim)
    doAssert h.navLayer==g.world.footmen[0].navLayer
    for i in 0..<180:
      h.hp=h.maxHp;h.mana=0
      for f in g.world.footmen.mitems:
        if f.hp>0:f.place(aim)
      g.step()
    rows.add(%*{"kind":"crossbow_xp_boundary","side":team.ord,"xp":h.totalXp,"gold":h.gold,"hits":h.attacksLanded})

  block:
    let g=quiet(team,Ranger)
    let h=g.world.heroes[team.ord*5]
    h.gold=1000
    for i in 0..<6:g.step()
    rows.add(%*{"kind":"equipment","side":team.ord,"damage":h.heroAttackDamage,"max_hp":h.maxHp,"gold":h.gold,"inventory":h.inventory,"counts":h.itemCounts})

  for threat in [false,true]:
    let g=quiet(team,Ranger)
    let h=g.world.heroes[team.ord*5]
    h.level=5;h.refreshHeroStats();h.hp=h.maxHp;h.mana=h.maxMana
    h.inventory[5]=PortalScroll;h.itemCounts[5]=1
    h.place(middle())
    var home=g.world.forts[team.ord].center
    if threat:
      home.x+=WorldScale*2
      discard g.stationary(Team(1-team.ord),home)
    var started=false;var completed=false
    for i in 0..<240:
      g.step()
      if h.portalEnds>0:started=true
      if started and h.portalEnds==0 and h.portalCooldownEnds>g.world.tick:completed=true;break
    if threat:
      let enemy=g.world.heroes[(1-team.ord)*5]
      enemy.hp=0;enemy.state=Dying;enemy.deathTicks = -1_000_000
    let before=g.recorder.data.actions.len
    for i in 0..<30:g.step()
    var released=false
    for i in before..<g.recorder.data.actions.len:
      if g.recorder.data.actions[i].kind==ActionAttackMove:released=true
    rows.add(%*{"kind":"defensive_portal","side":team.ord,"threat":threat,"started":started,"completed":completed,"released":released})

echo $(%*{"source":source,"max_instructions":maxInstructions,"max_work":maxWork,"rows":rows,"scope":"Controlled engine practice: stationary targets, clamped creep positions, normalized HP/mana for attack drills. Mechanics and directional evidence only, never competitive qualification."})
