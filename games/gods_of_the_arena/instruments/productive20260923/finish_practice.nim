## Bounded structure finishes: public selection and actual death/XP on replay59.
import std/[os,json]
import bassy
import polyworld/[cli,tapes,pathing]
import ../[bots,content,maps,sim,replays]
let source=getEnv("WEEK_POLICY")
var checks=0
var maxInstructions,maxWork:int64
var rows=newJArray()
proc middle():WorldPoint=
  let p=lanePathPoints[1][lanePathPoints[1].len div 2]
  const Unit=WorldScale div PathUnitsPerTile
  WorldPoint(x:p.x*Unit,y:p.y*Unit,z:p.z*Unit)
proc reveal(g:Game)=
  g.world.thawObservations()
  for t in 0..1:
    for vi in 0..<g.world.teamVisible[t].len:g.world.teamVisible[t][vi]=255
  discard g.world.freezeObservations()
proc verifyVm(g:Game,slot:int)=
  let vm=g.heroVms[slot]
  doAssert not vm.failed,vm.lastError
  maxInstructions=max(maxInstructions,vm.lastInstructions);maxWork=max(maxWork,vm.lastWork)
  doAssert maxInstructions<19000 and maxWork<=50000
for team in Team:
 for cl in HeroClass:
  for scene in ["high_tower","twohit_tower","above_twohit_tower","onehit_barracks","twohit_barracks","far_lethal_tower","creep_over_twohit_tower","hero_over_onehit_tower","locked_barracks","twohit_god","high_god"]:
   let g=newGame(generateMap(54),100000,10,false,ReplayData(),drafting=false)
   g.loadBots([BotGroup(path:source,count:10)])
   g.recorder=initReplayRecorder(g.currentSetup(1000),defaultConfig())
   let slot=team.ord*5;let h=g.world.heroes[slot];let enemy=Team(1-team.ord)
   for i,hero in g.world.heroes:
    hero.manualSpells=true;hero.gold=0
    if i!=slot:hero.hp=0;hero.state=Dying;hero.deathTicks = -1000000;g.heroVms[i]=nil
   h.class=cl;h.refreshHeroStats();h.hp=h.maxHp;h.mana=h.maxMana;h.place(middle())
   h.cooldowns=[100000'i32,100000,100000,100000]
   h.charges=[0'i32,0,0,0]
   g.world.footmen = @[]
   var bi = -1
   let barracks=scene in ["onehit_barracks","twohit_barracks","locked_barracks"]
   for i in 0..<g.world.buildings.len:
    if g.world.buildings[i].team==enemy:
     if bi<0 and g.world.buildings[i].kind==(if barracks:BarracksBuilding else:TowerBuilding):bi=i
     g.world.buildings[i].hp=0
   doAssert bi>=0
   let damage=h.heroAttackDamage()
   var targetHp=damage*2
   if scene in ["onehit_barracks","far_lethal_tower","hero_over_onehit_tower","locked_barracks"]:targetHp=damage
   if scene in ["high_tower","high_god"]:targetHp=10000
   if scene=="above_twohit_tower":targetHp=damage*2+1
   var at=h.position;at.x+=(if scene=="far_lethal_tower":15 else:1)*WorldScale
   g.world.buildings[bi].position=at
   # A synthetic unoccupied target avoids teleporting real map footprints.
   # The real host still decides reach, attack timing, damage, death and XP.
   g.world.buildings[bi].footprint = @[]
   g.world.buildings[bi].hp=targetHp
   var targetId=g.world.buildings[bi].id
   let isGod=scene in ["twohit_god","high_god"]
   if isGod:
    g.world.buildings[bi].hp=0
    g.world.forts[enemy.ord].center=at
    g.world.forts[enemy.ord].hp=targetHp
    targetId=g.world.forts[enemy.ord].id
   if scene=="locked_barracks":
    for i in 0..<g.world.buildings.len:
     if g.world.buildings[i].team==enemy and g.world.buildings[i].kind==TowerBuilding and g.world.buildings[i].lane==g.world.buildings[bi].lane:
      g.world.buildings[i].hp=10000
   var unitId=0'i32
   if scene=="creep_over_twohit_tower":
    var q=h.position;q.z+=WorldScale
    g.world.footmen = @[Footman(id:9900,team:enemy,hp:1,position:q,state:Marching)]
    unitId=9900
   if scene=="hero_over_onehit_tower":
    let other=g.world.heroes[enemy.ord*5]
    other.hp=1;other.maxHp=300;other.state=Marching
    var q=h.position;q.z+=WorldScale;other.place(q);unitId=other.id
   g.world.tick+=6;g.reveal();g.runBotDecisions();g.verifyVm(slot)
   let chosen=g.heroVms[slot].runtime.getGlobal("bestId").int32
   let finish=scene in ["twohit_tower","onehit_barracks","twohit_god"]
   let expected=if unitId>0:unitId elif finish:targetId else:0'i32
   doAssert chosen==expected,$team & " " & $cl & " " & scene & " selected " & $chosen & " expected " & $expected
   let beforeXp=h.totalXp;let beforeHits=h.attacksLanded
   var elapsed=0
   if finish:
    while elapsed<144 and (if isGod:g.world.forts[enemy.ord].hp>0 else:g.world.buildings[bi].hp>0):
     g.tickWorld(proc()=g.reveal();g.runBotDecisions())
     g.verifyVm(slot);inc elapsed
    doAssert (if isGod:g.world.forts[enemy.ord].hp<=0 else:g.world.buildings[bi].hp<=0),scene & " not finished"
    doAssert h.totalXp-beforeXp==(if isGod:500 else:100),scene & " missing kill XP"
    doAssert h.attacksLanded-beforeHits<=2,scene & " exceeded short finish"
   rows.add(%*{"team":team.ord,"class": $cl,"scene":scene,"selected":chosen,"xp":h.totalXp-beforeXp,"hits":h.attacksLanded-beforeHits,"ticks":elapsed})
   inc checks
 echo "completed team " & $team
 echo "checks " & $checks
echo $(%*{"passed":true,"checks":checks,"max_instructions":maxInstructions,"max_work":maxWork,"rows":rows,"scope":"Synthetic exposed targets; real host selection, attack timing, damage, death and XP. Both teams/all classes; not competitive evidence."})
