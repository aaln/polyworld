## Actual healing, path interruption and safety/resource checks on the pinned host.
import std/[os, json, math]
import bassy
import polyworld/[cli, tapes, pathing]
import ../[bots, content, maps, sim, replays]

let source=getEnv("WEEK_POLICY")
let candidate=getEnv("LANE_CANDIDATE")=="1"
let druidOnly=getEnv("DRUID_ONLY")=="1"
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
  for scene in ["ready", "cooldown_three_seconds", "no_mana", "no_charges", "long_cooldown", "near_hero", "near_creep", "shop_affordable", "shop_unaffordable", "full_inventory", "rooted", "recovered", "low_mana_recovered", "warning", "warning_overflow", "timeout"]:
    let g=quiet(team,DruidWarden)
    let slot=team.ord*5
    let h=g.world.heroes[slot]
    h.level=3
    h.abilityLevels=[0'i32,2,1,0]
    h.equip(0)
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
    g.heroVms[slot].runtime.setGlobal("moveTick",0)
    discard g.world.applyWalkTo(h.id,homeX,homeY)
    if scene in ["recovered","low_mana_recovered"]:h.hp=h.maxHp*90 div 100
    if scene in ["no_mana","low_mana_recovered"]:h.mana=0
    if scene=="no_charges":h.charges=[0'i32,0,0,0]
    if scene=="long_cooldown":h.cooldowns=[10000'i32,10000,10000,10000]
    if scene=="cooldown_three_seconds":h.cooldowns=[72'i32,72,72,72]
    if scene in ["shop_affordable","shop_unaffordable"]:
      h.inventory[0]=NoItem;h.itemCounts[0]=0
      h.gold=if scene=="shop_affordable":110 else:109
    if scene=="full_inventory":
      h.inventory[0]=ManaElixir
      h.inventory[4]=ManaPotion;h.inventory[5]=ManaElixir
      h.itemCounts=[1'i32,1,1,1,1,1];h.gold=200
    if scene=="rooted":g.world.applyRoot(h.id,480)
    if scene=="near_hero":
      let enemy=g.world.heroes[(1-team.ord)*5]
      enemy.hp=100000;enemy.maxHp=100000;enemy.state=Marching;enemy.stunnedUntil=100000
    if scene=="near_creep":
      g.world.footmen = @[Footman(id:9500,team:Team(1-team.ord),hp:100000,state:Marching,swingTicks: -1)]
    var heals,casts,homeWalks,advances,firstAdvance,firstHome,firstCast:int
    firstAdvance = -1;firstHome = -1;firstCast = -1
    let initialHp=h.hp
    let duration=if scene=="timeout":360 else:180
    var firstHeld=false
    for tick in 0..<duration:
      if scene=="timeout":
        h.hp=h.maxHp*29 div 100;h.mana=h.maxMana
        h.charges=[0'i32,2,2,0];h.cooldowns=[0'i32,0,0,0]
      if scene=="near_hero":
        var q=h.position;q.x+=8*WorldScale;g.world.heroes[(1-team.ord)*5].place(q)
      if scene=="near_creep":
        var q=h.position;q.x+=4*WorldScale;g.world.footmen[0].place(q)
      if scene in ["warning","warning_overflow"]:
        g.world.casts.setLen(0)
        for n in 0..<(if scene=="warning":1 else:25):
          g.world.casts.add(SpellCast(ability:DreadTotem,level:1,heroId:g.world.heroes[(1-team.ord)*5].id,position:h.position,origin:h.position,started:g.world.tick,impact:g.world.tick+24,ends:g.world.tick+48))
      let before=g.recorder.data.actions.len
      g.step()
      if tick==0 and candidate:firstHeld=g.heroVms[slot].runtime.getGlobal("laneUntil")>g.world.tick
      for e in g.world.events:
        if e.kind==Healing and e.target.id==h.id and e.actor.id==h.id and e.cause==AbilityEffect:heals+=e.amount
        if e.kind==SpellReleased and e.actor.id==h.id:
          inc casts
          if firstCast<0:firstCast=tick
      for i in before..<g.recorder.data.actions.len:
        let a=g.recorder.data.actions[i]
        if a.kind==ActionWalkTo and a.first==homeX and a.second==homeY:
          inc homeWalks
          if firstHome<0:firstHome=tick
        if a.kind==ActionAttackMove:
          inc advances
          if firstAdvance<0:firstAdvance=tick
    let released=g.heroVms[slot].runtime.getGlobal("retreat")==0
    let expectedRelease=candidate and scene in ["ready","cooldown_three_seconds","rooted","recovered","shop_unaffordable","full_inventory"]
    var passed=released==expectedRelease
    if expectedRelease and scene!="recovered":passed=passed and heals>0 and h.hp*100>=h.maxHp*60
    if expectedRelease:passed=passed and homeWalks==0
    if candidate and scene=="recovered":passed=passed and firstAdvance==0
    if candidate and scene=="cooldown_three_seconds":passed=passed and firstHeld and firstCast>=70
    if candidate and scene=="shop_affordable":passed=passed and homeWalks>0 and casts==0 and (g.heroVms[slot].runtime.getGlobal("restock")==1 or h.inventory[0]==CrimsonDagger)
    if candidate and scene=="timeout":passed=passed and firstHeld and firstHome>=288 and firstHome<=300
    if scene in ["no_mana","no_charges","long_cooldown","low_mana_recovered"]:passed=passed and casts==0
    if not candidate:passed=passed and heals==0
    let row= %*{"scene":scene,"side":team.ord,"class":DruidWarden.ord,"initial_hp":initialHp,"final_hp":h.hp,"max_hp":h.maxHp,"self_healing":heals,"accepted_casts":casts,"retreat_released":released,"expected_release":expectedRelease,"home_walks":homeWalks,"first_home_tick":firstHome,"first_cast_tick":firstCast,"advance_commands":advances,"first_advance_tick":firstAdvance,"passed":passed}
    rows.add(row)
    if not passed:stderr.writeLine($row)

for team in Team:
  for class in HeroClass:
    for scene in ["potion_recovery","no_heal_source","recovered"]:
      let g=quiet(team,class)
      let slot=team.ord*5
      let h=g.world.heroes[slot]
      h.abilityLevels=[0'i32,0,0,0]
      h.equip(0)
      h.place(g.locate(h,false));h.hp=h.maxHp*29 div 100
      h.charges=[0'i32,0,0,0]
      if scene=="recovered":h.hp=h.maxHp*90 div 100
      if scene=="potion_recovery":
        h.inventory[4]=HealthPotion;h.itemCounts[4]=1
      g.heroVms[slot].runtime.setGlobal("retreat",1)
      g.heroVms[slot].runtime.setGlobal("nextThink",0)
      g.heroVms[slot].runtime.setGlobal("moveTick",0)
      g.heroVms[slot].runtime.setGlobal("previousHp",h.hp)
      g.heroVms[slot].runtime.setGlobal("hurtTick",-1000)
      let homeX=g.heroVms[slot].runtime.getGlobal("spawnX").int32
      let homeY=g.heroVms[slot].runtime.getGlobal("spawnY").int32
      discard g.world.applyWalkTo(h.id,homeX,homeY)
      var heals,homeWalks,advances:int
      for tick in 0..<288:
        let before=g.recorder.data.actions.len
        g.step()
        for e in g.world.events:
          if e.kind==Healing and e.target.id==h.id and e.cause==ItemEffect:heals+=e.amount
        for i in before..<g.recorder.data.actions.len:
          let a=g.recorder.data.actions[i]
          if a.kind==ActionWalkTo and a.first==homeX and a.second==homeY:inc homeWalks
          if a.kind==ActionAttackMove:inc advances
      let released=g.heroVms[slot].runtime.getGlobal("retreat")==0
      let enoughPotion=h.maxHp*29 div 100+HealthPotion.itemSpec.heal>= (h.maxHp*60+99) div 100
      let expected=candidate and (not druidOnly or class==DruidWarden) and (scene=="recovered" or (scene=="potion_recovery" and enoughPotion))
      let passed=released==expected and (not expected or (advances>0 and homeWalks==0)) and (scene!="potion_recovery" or heals>0) and (not candidate or scene!="potion_recovery" or enoughPotion or homeWalks>0)
      let row= %*{"scene":scene,"side":team.ord,"class":class.ord,"retreat_released":released,"healing":heals,"max_hp":h.maxHp,"enough_potion_to_recover":enoughPotion,"home_walks":homeWalks,"advances":advances,"expected_release":expected,"passed":passed}
      rows.add(row)
      if not passed:stderr.writeLine($row)
var allPassed=true
for row in rows:
  if not row["passed"].getBool:allPassed=false
echo $(%*{"passed":allPassed,"checks":rows.len,"rows":rows,"max_instructions":maxInstructions,"max_work":maxWork,"scope":"Actual-tick lane healing, useful shopping and bounded escape. Local mechanism only."})
if not allPassed:quit(1)
