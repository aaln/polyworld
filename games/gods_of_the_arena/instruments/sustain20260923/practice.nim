## Actual healing, path interruption and safety/resource checks on the pinned host.
import std/[os, json, math]
import bassy
import polyworld/[cli, tapes, pathing]
import ../[bots, content, maps, sim, replays]

let source=getEnv("WEEK_POLICY")
let candidate=getEnv("SUSTAIN_CANDIDATE")=="1"
doAssert source.len>0
var rows=newJArray()
var maxInstructions,maxWork:int64

proc step(g:Game)=
  g.tickWorld(proc()=
    # Fixtures deliberately expose threats to test the public guard, independent
    # of occlusion at the chosen map cells. Full games retain normal fog.
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

proc quiet(team:Team,class:HeroClass):Game=
  result=newGame(generateMap(54),100000,10,false,ReplayData(),drafting=false)
  result.loadBots([BotGroup(path:source,count:10)])
  result.recorder=initReplayRecorder(result.currentSetup(10000),defaultConfig())
  for i,h in result.world.heroes:
    h.manualSpells=true
    h.gold=0
    if i!=team.ord*5:
      h.hp=0;h.state=Dying;h.deathTicks = -1000000
      result.heroVms[i]=nil
  let h=result.world.heroes[team.ord*5]
  h.class=class;h.refreshHeroStats();h.hp=h.maxHp;h.mana=h.maxMana
  result.step()

proc distance(a,b:WorldPoint):float=
  sqrt(float((int64(a.x)-b.x)*(int64(a.x)-b.x)+(int64(a.z)-b.z)*(int64(a.z)-b.z)))/WorldScale.float

proc locate(g:Game,h:Hero,keep:bool):WorldPoint=
  let home=h.position
  var best=1e9
  const Unit=WorldScale div PathUnitsPerTile
  for z in 1..<115:
    for x in 1..<115:
      if not navigationOpen(GroundLayer,x,z):continue
      let q=pathPoint(GroundLayer,x,z)
      let at=WorldPoint(x:q.x*Unit,y:q.y*Unit,z:q.z*Unit)
      h.place(at)
      if h.canShop!=keep or h.inOwnSpawn:continue
      var safe=true
      for b in g.world.buildings.mitems:
        if b.team!=h.team and b.kind==TowerBuilding and distance(at,b.position)<16:safe=false
      if not safe:continue
      let score=abs(distance(at,home)-(if keep:26.0 else:42.0))
      if score<best:best=score;result=at
  h.place(home)
  doAssert best<5,"No suitable fixture location"

proc equip(h:Hero,count:int32)=
  h.inventory=[CrimsonDagger,KnightArmor,BattleAxe,RuneCrossbow,NoItem,NoItem]
  h.itemCounts=[1'i32,1,1,1,0,0]
  if count>0:h.inventory[5]=PortalScroll;h.itemCounts[5]=count
  h.refreshHeroStats()
  h.hp=h.maxHp;h.mana=h.maxMana


for team in Team:
  for scene in ["ready", "no_mana", "no_charges", "cooldown", "near_hero", "near_creep", "restock", "rooted", "recovered", "low_mana_recovered", "below_release", "warning", "warning_overflow", "ally_cover"]:
    let g=quiet(team,DruidWarden)
    let slot=team.ord*5
    let h=g.world.heroes[slot]
    h.level=3
    h.abilityLevels=[0'i32,2,1,0]
    h.refreshHeroStats()
    h.spellsReady=true
    h.charges=[0'i32,2,2,0]
    h.cooldowns=[0'i32,0,0,0]
    h.recharges=[10000'i32,10000,10000,10000]
    h.hp=h.maxHp*29 div 100;h.mana=h.maxMana
    let at=g.locate(h,false)
    h.place(at)
    let homeX=g.heroVms[slot].runtime.getGlobal("spawnX").int32
    let homeY=g.heroVms[slot].runtime.getGlobal("spawnY").int32
    g.heroVms[slot].runtime.setGlobal("retreat",1)
    g.heroVms[slot].runtime.setGlobal("nextThink",0)
    g.heroVms[slot].runtime.setGlobal("moveTick",g.world.tick+1000)
    discard g.world.applyWalkTo(h.id,homeX,homeY)
    if scene in ["recovered","low_mana_recovered"]:h.hp=h.maxHp*90 div 100
    if scene=="below_release":
      h.hp=h.maxHp*74 div 100
      h.cooldowns=[10000'i32,10000,10000,10000]
    if scene in ["no_mana","low_mana_recovered"]:h.mana=0
    if scene=="no_charges":h.charges=[0'i32,0,0,0]
    if scene=="cooldown":h.cooldowns=[10000'i32,10000,10000,10000]
    if scene=="restock":h.gold=600
    if scene=="rooted":g.world.applyRoot(h.id,240)
    if scene=="near_hero":
      let enemy=g.world.heroes[(1-team.ord)*5]
      enemy.hp=100000;enemy.maxHp=100000;enemy.state=Marching;enemy.stunnedUntil=100000
    if scene in ["near_creep","ally_cover"]:
      g.world.footmen = @[Footman(id:9500,team:(if scene=="ally_cover":team else:Team(1-team.ord)),hp:100000,state:Marching,swingTicks: -1)]
    var heals,casts,homeWalks,advances,firstAdvance:int
    firstAdvance = -1
    let initialHp=h.hp
    for tick in 0..<60:
      if scene=="near_hero":
        var q=h.position;q.x+=8*WorldScale;g.world.heroes[(1-team.ord)*5].place(q)
      if scene in ["near_creep","ally_cover"]:
        var q=h.position
        q.x+=(if scene=="ally_cover" and team==BlueTeam: -4 else:4)*WorldScale
        g.world.footmen[0].place(q)
      if scene in ["warning","warning_overflow"]:
        g.world.casts.setLen(0)
        for n in 0..<(if scene=="warning":1 else:25):
          g.world.casts.add(SpellCast(ability:DreadTotem,level:1,heroId:g.world.heroes[(1-team.ord)*5].id,position:h.position,origin:h.position,started:g.world.tick,impact:g.world.tick+24,ends:g.world.tick+48))
      let before=g.recorder.data.actions.len
      g.step()
      for e in g.world.events:
        if e.kind==Healing and e.target.id==h.id and e.actor.id==h.id and e.cause==AbilityEffect:heals+=e.amount
        if e.kind==SpellReleased and e.actor.id==h.id:inc casts
      for i in before..<g.recorder.data.actions.len:
        let a=g.recorder.data.actions[i]
        if a.kind==ActionWalkTo and a.first==homeX and a.second==homeY:inc homeWalks
        if a.kind==ActionAttackMove:
          inc advances
          if firstAdvance<0:firstAdvance=tick
    let released=g.heroVms[slot].runtime.getGlobal("retreat")==0
    let expectedRelease=candidate and scene in ["ready","rooted","recovered","ally_cover"]
    var passed=released==expectedRelease
    if candidate and scene in ["ready","rooted","ally_cover"]:passed=passed and heals>0 and h.hp*100>=h.maxHp*75
    if scene in ["no_mana","no_charges","cooldown","below_release"]:passed=passed and casts==0
    if candidate and scene=="recovered":passed=passed and firstAdvance==0 and homeWalks==0
    if candidate and scene in ["ready","ally_cover"]:passed=passed and homeWalks==0 and advances>0
    if not candidate:passed=passed and heals==0
    let row= %*{"scene":scene,"side":team.ord,"class":DruidWarden.ord,"initial_hp":initialHp,"final_hp":h.hp,"max_hp":h.maxHp,"self_healing":heals,"accepted_casts":casts,"retreat_released":released,"expected_release":expectedRelease,"home_walks":homeWalks,"advance_commands":advances,"first_advance_tick":firstAdvance,"passed":passed}
    rows.add(row)
    if not passed:stderr.writeLine($row);quit(1)
for team in Team:
  for class in HeroClass:
    for scene in ["ally_healed_in_transit","mana_still_empty"]:
      let g=quiet(team,class)
      let slot=team.ord*5
      let h=g.world.heroes[slot]
      h.place(g.locate(h,false));h.hp=h.maxHp
      if scene=="mana_still_empty":h.mana=0
      g.heroVms[slot].runtime.setGlobal("retreat",1)
      g.heroVms[slot].runtime.setGlobal("nextThink",g.world.tick+1000)
      g.heroVms[slot].runtime.setGlobal("moveTick",g.world.tick+1000)
      let homeX=g.heroVms[slot].runtime.getGlobal("spawnX").int32
      let homeY=g.heroVms[slot].runtime.getGlobal("spawnY").int32
      discard g.world.applyWalkTo(h.id,homeX,homeY)
      let before=g.recorder.data.actions.len
      g.step()
      let released=g.heroVms[slot].runtime.getGlobal("retreat")==0
      var advance=false
      for i in before..<g.recorder.data.actions.len:
        if g.recorder.data.actions[i].kind==ActionAttackMove:advance=true
      let expected=candidate and scene=="ally_healed_in_transit"
      let passed=released==expected and (not expected or advance)
      let row= %*{"scene":scene,"side":team.ord,"class":class.ord,"retreat_released":released,"advance_same_tick":advance,"expected_release":expected,"passed":passed}
      rows.add(row)
      if not passed:stderr.writeLine($row);quit(1)
echo $(%*{"checks":rows.len,"rows":rows,"max_instructions":maxInstructions,"max_work":maxWork,"scope":"Actual-tick self-heal and route interruption with public threat/resource/restock guards; all-class immediate healed-transit release. Local mechanism evidence, not competitive score."})
