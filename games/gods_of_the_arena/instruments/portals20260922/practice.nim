## Actual ticking portal fixtures. The control is measured, not expected to pass.
import std/[os, json, math]
import bassy
import polyworld/[cli, tapes, pathing]
import ../[bots, content, maps, sim, replays]

let source=getEnv("WEEK_POLICY")
let enforce=getEnv("PORTAL_ENFORCE")=="1"
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
  for class in [Ranger,Crossbowman]:
    for scene in ["field27","field20","keep20","spawn20","no_scroll","cooldown","rooted","near_creep","far_creep","near_hero","anchor_missing","outward_one","outward_two","stack_restock","interrupted","anchor_destroyed","ordinary_command","posthit_critical","warning_near","warning_far24","warning_overflow"]:
      let g=quiet(team,class)
      let slot=team.ord*5
      let h=g.world.heroes[slot]
      let home=h.position
      h.equip(if scene in ["outward_two"]:2 elif scene=="no_scroll":0 else:1)
      if scene=="keep20":h.place(g.locate(h,true))
      elif scene notin ["spawn20","outward_one","outward_two","stack_restock"]:h.place(g.locate(h,false))
      let origin=h.position
      if scene notin ["outward_one","outward_two","stack_restock"]:
        h.hp=h.maxHp*(if scene in ["field27","posthit_critical"]:27 else:20) div 100
      if scene=="stack_restock":h.gold=100
      if scene=="cooldown":h.portalCooldownEnds=g.world.tick+PortalCooldownTicks
      if scene=="rooted":g.world.applyRoot(h.id,240)
      if scene=="anchor_missing":
        for b in g.world.buildings.mitems:
          if b.team==team and b.kind==TowerBuilding and distance(b.position,home)<25:b.hp=0
      if scene in ["near_creep","far_creep","posthit_critical"]:
        var at=origin
        at.x+=(if scene=="near_creep":4 else:9)*WorldScale
        g.world.footmen = @[Footman(id:9500,team:Team(1-team.ord),hp:100000,state:Marching,swingTicks: -1)]
        g.world.footmen[0].place(at)
        if scene=="posthit_critical":
          h.attackObjectId=9500
          inc h.attacksLanded
      if scene=="near_hero":
        let enemy=g.world.heroes[(1-team.ord)*5]
        enemy.hp=100000;enemy.maxHp=100000;enemy.state=Marching;enemy.stunnedUntil=100000
        var at=origin;at.x+=8*WorldScale;enemy.place(at)
      var startTick = -1'i32
      var completeTick = -1'i32
      var channelActions=0
      var manipulated=false
      var ordinaryRejected=false
      var startedInKeep=false
      let before=g.recorder.data.actions.len
      for tick in 0..<180:
        if scene in ["near_creep","far_creep","posthit_critical"]:
          var at=h.position;at.x+=(if scene=="near_creep":4 else:9)*WorldScale
          g.world.footmen[0].place(at)
        if scene=="near_hero":
          var at=h.position;at.x+=8*WorldScale
          g.world.heroes[(1-team.ord)*5].place(at)
        if scene in ["warning_near","warning_far24","warning_overflow"]:
          g.world.casts.setLen(0)
          for n in 0..<(if scene=="warning_near":1 elif scene=="warning_far24":24 else:25):
            var at=h.position
            if scene!="warning_near":at.x+=(if h.position.x>0: -20 else:20)*WorldScale
            g.world.casts.add(SpellCast(ability:DreadTotem,level:1,heroId:g.world.heroes[(1-team.ord)*5].id,position:at,origin:at,started:g.world.tick,impact:g.world.tick+24,ends:g.world.tick+48))
        let oldActions=g.recorder.data.actions.len
        let channelBefore=h.portalEnds
        g.step()
        if channelBefore>0:channelActions+=g.recorder.data.actions.len-oldActions
        if h.portalEnds>0 and startTick<0:
          startTick=g.world.tick;startedInKeep=h.canShop
        if startTick>=0 and h.portalEnds>0 and g.world.tick-startTick==12 and not manipulated:
          manipulated=true
          if scene=="interrupted":g.world.applyRoot(h.id,12)
          if scene=="anchor_destroyed":
            for b in g.world.buildings.mitems:
              if b.id==h.portalTowerId:b.hp=0
          if scene=="ordinary_command":
            let ends=h.portalEnds
            ordinaryRejected=not g.world.applyWalkTo(h.id,58,58) and h.portalEnds==ends
        for e in g.world.events:
          if e.kind==PortalCompleted and e.actor.id==h.id:completeTick=g.world.tick
      var portalCommands,walks,attacks,boughtScrolls,attacksBeforeStart:int
      for i in before..<g.recorder.data.actions.len:
        let a=g.recorder.data.actions[i]
        if a.kind==ActionUseItemAt:inc portalCommands
        if a.kind==ActionWalkTo:inc walks
        if a.kind==ActionAttackTarget:
          inc attacks
          if a.tick.int32 <= max(startTick,36):inc attacksBeforeStart
        if a.kind==ActionBuyItem and a.first==PortalScroll.ord:inc boughtScrolls
      let shouldStart=scene in ["field27","field20","far_creep","outward_two","stack_restock","interrupted","anchor_destroyed","ordinary_command","posthit_critical","warning_far24"]
      var passed=(startTick>=0)==shouldStart and channelActions==0
      if shouldStart:passed=passed and startTick<=40
      if shouldStart and scene notin ["interrupted","anchor_destroyed"]:passed=passed and completeTick==startTick+PortalChannelTicks
      if scene in ["interrupted","anchor_destroyed"]:passed=passed and completeTick<0 and portalCommands==1 and h.portalCooldownEnds>g.world.tick
      if scene=="ordinary_command":passed=passed and ordinaryRejected
      if scene in ["outward_one"]:passed=passed and h.itemCounts[5]==1
      if scene in ["outward_two","stack_restock"]:passed=passed and h.itemCounts[5]==1
      if scene=="posthit_critical":passed=passed and attacksBeforeStart==0
      let row = %*{"scene":scene,"side":team.ord,"class":class.ord,"start_tick":startTick,"complete_tick":completeTick,"started_in_keep":startedInKeep,"portal_commands":portalCommands,"channel_actions":channelActions,"walks":walks,"attacks":attacks,"scrolls_remaining":h.itemCounts[5],"bought_scrolls":boughtScrolls,"ordinary_rejected_without_cancel":ordinaryRejected,"passed":passed}
      rows.add(row)
      if enforce and not passed:
        stderr.writeLine($row)
        quit(1)

echo $(%*{"checks":rows.len,"rows":rows,"max_instructions":maxInstructions,"max_work":maxWork,"scope":"Deterministic actual-tick fixtures; direct world manipulations test mechanics and guards, not competitive strength."})
