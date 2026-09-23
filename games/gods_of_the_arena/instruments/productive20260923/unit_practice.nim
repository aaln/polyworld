## Public target selection on actual host, both teams/all classes.
import std/[os,json]
import bassy
import polyworld/[cli,tapes,pathing]
import ../[bots,content,maps,sim,replays]
let source=getEnv("WEEK_POLICY")
let candidate=getEnv("UNIT_CANDIDATE")=="1"
var checks=0
var maxInstructions,maxWork:int64
var rows=newJArray()
proc middle():WorldPoint=
  let p=lanePathPoints[1][lanePathPoints[1].len div 2]
  const Unit=WorldScale div PathUnitsPerTile
  WorldPoint(x:p.x*Unit,y:p.y*Unit,z:p.z*Unit)
for team in Team:
 for cl in HeroClass:
  for scene in ["barracks_only","tower_only","mixed_creep","mixed_hero"]:
   let g=newGame(generateMap(54),100000,10,false,ReplayData(),drafting=false)
   g.loadBots([BotGroup(path:source,count:10)])
   g.recorder=initReplayRecorder(g.currentSetup(1000),defaultConfig())
   let slot=team.ord*5;let h=g.world.heroes[slot]
   for i,hero in g.world.heroes:
    hero.manualSpells=true;hero.gold=0
    if i!=slot:hero.hp=0;hero.state=Dying;g.heroVms[i]=nil
   h.class=cl;h.refreshHeroStats();h.hp=h.maxHp;h.mana=h.maxMana;h.place(middle())
   var targetBuilding= -1
   for i in 0..<g.world.buildings.len:
    if g.world.buildings[i].team!=team:
     if targetBuilding<0 and g.world.buildings[i].kind==(if scene=="tower_only":TowerBuilding else:BarracksBuilding):targetBuilding=i
     g.world.buildings[i].hp=0
   doAssert targetBuilding>=0
   g.world.buildings[targetBuilding].hp=10000
   g.world.buildings[targetBuilding].position=h.position
   g.world.buildings[targetBuilding].position.x+=2*WorldScale
   let buildingId=g.world.buildings[targetBuilding].id
   for t in 0..1:
    for vi in 0..<g.world.teamVisible[t].len:g.world.teamVisible[t][vi]=255
   var unitId=0'i32
   if scene=="mixed_creep":
    var p=h.position;p.x+=WorldScale
    g.world.footmen = @[Footman(id:9900,team:Team(1-team.ord),hp:1,position:p,state:Marching)]
    unitId=9900
   if scene=="mixed_hero":
    let enemy=g.world.heroes[(1-team.ord)*5]
    enemy.hp=1;enemy.maxHp=300;enemy.state=Marching
    var p=h.position;p.x+=WorldScale;enemy.place(p);unitId=enemy.id
   g.world.tick+=6;g.runBotDecisions()
   let vm=g.heroVms[slot]
   doAssert not vm.failed,vm.lastError
   maxInstructions=max(maxInstructions,vm.lastInstructions);maxWork=max(maxWork,vm.lastWork)
   let chosen=vm.runtime.getGlobal("bestId").int32
   if scene in ["barracks_only","tower_only"]:
    doAssert chosen==(if candidate:0'i32 else:buildingId)
   else:doAssert chosen==unitId
   for a in g.recorder.data.actions:
    if candidate and a.kind in [ActionAttackTarget,ActionCastTarget]:doAssert a.first!=buildingId
   rows.add(%*{"team":team.ord,"class": $cl,"scene":scene,"selected":chosen})
   inc checks
   doAssert maxInstructions<19000 and maxWork<=50000
echo $(%*{"passed":true,"checks":checks,"max_instructions":maxInstructions,"max_work":maxWork,"rows":rows,"scope":"Actual BASIC host/observations and command acceptance; supplied visible mixed or building-only scene, not competitive evidence."})
