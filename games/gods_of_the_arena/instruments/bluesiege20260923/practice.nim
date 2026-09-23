## Actual-host public target/safety fixtures; other VMs absent, visibility explicit.
import std/[os,json]
import bassy
import polyworld/[cli,tapes,pathing]
import ../[bots,content,maps,sim,replays]
let source=getEnv("WEEK_POLICY")
let candidateSource=getEnv("PRESSURE_CANDIDATE")=="1"
var rows=newJArray()
var maxInstructions,maxWork:int64
proc step(g:Game)=
  g.tickWorld(proc()=
    g.world.thawObservations()
    for cells in g.world.teamVisible.mitems:
      for cell in cells.mitems:cell=255
    discard g.world.freezeObservations()
    g.runBotDecisions())
  for vm in g.heroVms:
    if vm!=nil:
      doAssert not vm.failed,vm.lastError
      maxInstructions=max(maxInstructions,vm.lastInstructions)
      maxWork=max(maxWork,vm.lastWork)
      doAssert vm.lastInstructions<=19000 and vm.lastWork<=50000
proc middle():WorldPoint=
  let p=lanePathPoints[1][lanePathPoints[1].len div 2]
  const Unit=WorldScale div PathUnitsPerTile
  WorldPoint(x:p.x*Unit,y:p.y*Unit,z:p.z*Unit)
for team in Team:
  for class in [VanguardKnight,Ranger,DruidWarden,Crossbowman]:
    let candidate=candidateSource and (getEnv("BLUE_DRUID_ONLY")!="1" or (team==BlueTeam and class==DruidWarden))
    for scene in ["covered_tower","last_hit","no_cover","free_tower","tower_aggro","low_health","outnumbered","retaliate","outside_reach","wounded_hero"]:
      let g=newGame(generateMap(54),100000,10,false,ReplayData(),drafting=false)
      g.loadBots([BotGroup(path:source,count:10)])
      g.recorder=initReplayRecorder(g.currentSetup(10000),defaultConfig())
      let slot=team.ord*5
      for i,h in g.world.heroes:
        h.manualSpells=true;h.gold=0
        if i!=slot:
          h.hp=0;h.state=Dying;h.deathTicks = -1000000;g.heroVms[i]=nil
      let h=g.world.heroes[slot]
      h.class=class;h.refreshHeroStats();h.hp=h.maxHp;h.mana=h.maxMana
      g.step();h.place(middle())
      let origin=h.position
      let sign=if team==RedTeam:1'i32 else: -1'i32
      for b in g.world.buildings.mitems:b.hp=0
      var towerId=0'i32
      for b in g.world.buildings.mitems:
        if b.team!=team and b.kind==TowerBuilding:
          b.hp=10000;b.targetId=9501
          var at=origin;at.x+=sign*3*WorldScale;b.position=at;towerId=b.id
          if scene=="free_tower":b.targetId=0
          if scene=="tower_aggro":b.targetId=h.id
          break
      var at=origin;at.z+=sign*WorldScale
      g.world.footmen= @[Footman(id:9500,team:Team(1-team.ord),hp:1000,state:Marching,swingTicks: -1)]
      g.world.footmen[0].place(at)
      if scene=="last_hit":g.world.footmen[0].hp=1
      if scene!="no_cover":
        at=origin;at.x+=sign*2*WorldScale
        var ally=Footman(id:9501,team:team,hp:1000,state:Marching,swingTicks: -1)
        ally.place(at);g.world.footmen.add(ally)
      var expected=9500'i32
      if candidate and scene=="covered_tower":expected=towerId
      if scene=="low_health":h.hp=h.maxHp*3 div 5
      if scene in ["retaliate","outside_reach","wounded_hero","outnumbered"]:
        let enemy=g.world.heroes[(1-team.ord)*5]
        enemy.class=Warlock;enemy.hp=10000;enemy.maxHp=10000;enemy.state=Marching;enemy.stunnedUntil=100000
        enemy.level=h.level
        enemy.attackObjectId=h.id
        at=origin;at.x+=sign*WorldScale
        if scene=="outside_reach":at.x+=sign*12*WorldScale
        if scene=="outnumbered":enemy.level=20
        if scene=="wounded_hero":enemy.hp=h.heroAttackDamage()*2;expected=enemy.id
        enemy.place(at)
        if candidate and scene=="retaliate":expected=enemy.id
        if candidate and scene=="outside_reach":expected=towerId
      let vm=g.heroVms[slot]
      vm.runtime.setGlobal("nextThink",0);vm.runtime.setGlobal("moveTick",0)
      h.attackObjectId=0
      let before=g.recorder.data.actions.len
      g.step()
      let chosen=vm.runtime.getGlobal("bestId").int32
      var submitted=0'i32
      for i in before..<g.recorder.data.actions.len:
        let a=g.recorder.data.actions[i]
        if a.kind==ActionAttackTarget:submitted=a.first
      let passed=chosen==expected and (submitted==expected or h.attackObjectId==expected)
      rows.add(%*{"scene":scene,"side":team.ord,"class":class.ord,"selected":chosen,"submitted":submitted,"expected":expected,"passed":passed})
      if not passed:stderr.writeLine($rows[^1])
echo $(%*{"checks":rows.len,"rows":rows,"max_instructions":maxInstructions,"max_work":maxWork,"scope":"Fully visible artificial scenes establish current-host choices, guard precedence and runtime; no competitive inference."})
