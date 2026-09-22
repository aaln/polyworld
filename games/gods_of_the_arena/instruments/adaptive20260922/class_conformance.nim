## Compare complete real-tick actions and states against preserved controllers.
import std/[os,json]
import bassy
import polyworld/[cli,tapes,pathing]
import ../[bots,content,maps,sim,replays]
let candidate=getEnv("WEEK_POLICY")
let baseline=getEnv("BASELINE_POLICY")
let broad=getEnv("BROAD_POLICY")
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
      maxInstructions=max(maxInstructions,vm.lastInstructions);maxWork=max(maxWork,vm.lastWork)
      doAssert vm.lastInstructions<=19000 and vm.lastWork<=50000
proc middle():WorldPoint=
  let p=lanePathPoints[1][lanePathPoints[1].len div 2]
  const Unit=WorldScale div PathUnitsPerTile
  WorldPoint(x:p.x*Unit,y:p.y*Unit,z:p.z*Unit)
proc sample(source:string,team:Team,class:HeroClass,scene:string):tuple[actions:seq[ReplayAction],hashes:seq[uint64]]=
  let g=newGame(generateMap(54),100000,10,false,ReplayData(),drafting=false)
  g.loadBots([BotGroup(path:source,count:10)])
  g.recorder=initReplayRecorder(g.currentSetup(1000),defaultConfig())
  let slot=team.ord*5
  for i,h in g.world.heroes:
    h.manualSpells=true;h.gold=0
    if i!=slot:
      h.hp=0;h.state=Dying;h.deathTicks= -1000000;g.heroVms[i]=nil
  let h=g.world.heroes[slot]
  h.class=class;h.refreshHeroStats();h.hp=h.maxHp;h.mana=h.maxMana
  g.step();h.place(middle())
  let origin=h.position
  let sign=if team==RedTeam:1'i32 else: -1'i32
  for b in g.world.buildings.mitems:b.hp=0
  var at=origin;at.x+=sign*4*WorldScale
  let enemy=g.world.heroes[(1-team.ord)*5]
  enemy.place(at);enemy.hp=10000;enemy.maxHp=10000;enemy.state=Marching;enemy.stunnedUntil=100000
  if scene=="range":at=origin;at.x+=sign*9*WorldScale;enemy.place(at)
  if scene=="ally":enemy.team=team
  if scene=="fort":enemy.hp=0;at=origin;at.x+=sign*3*WorldScale;g.world.forts[1-team.ord].center=at
  at=origin;at.z+=sign*WorldScale
  g.world.footmen = @[Footman(id:9500,team:Team(1-team.ord),hp:1,state:Marching,swingTicks: -1)]
  g.world.footmen[0].place(at)
  if scene=="priority":g.world.footmen[0].hp=1000
  if scene=="dense":
    for i in 1..<600:
      g.world.footmen.add(Footman(id:9500+i.int32,team:Team(1-team.ord),hp:1000,position:at,state:Marching,swingTicks: -1))
  if scene=="hurt":h.hp=h.maxHp div 5
  if scene=="channel":h.portalEnds=g.world.tick+72
  g.heroVms[slot].runtime.setGlobal("nextThink",0);h.attackObjectId=0
  for i in 0..<96:g.step();result.hashes.add(g.stateHash())
  result.actions=g.recorder.data.actions
var rows=newJArray()
for team in Team:
  for class in HeroClass:
    for scene in ["split","priority","range","ally","fort","dense","hurt","channel"]:
      let reference=if class==Crossbowman:broad else:baseline
      let old=sample(reference,team,class,scene)
      let current=sample(candidate,team,class,scene)
      let equal=old.actions==current.actions and old.hashes==current.hashes
      let row = %*{"side":team.ord,"class":class.ord,"scene":scene,"reference":(if class==Crossbowman:"broad spell-pressure" else:"deployed portal"),"commands":current.actions.len,"ticks":current.hashes.len,"passed":equal}
      rows.add(row)
      if not equal:stderr.writeLine($row);quit(1)
echo $(%*{"passed":true,"checks":rows.len,"rows":rows,"max_instructions":maxInstructions,"max_work":maxWork,"scope":"Complete command and per-tick state equivalence in artificial actual-engine scenes. Nine non-Crossbow classes match deployed behavior; Crossbow matches screened intervention. Competitive full-policy comparison remains required."})
