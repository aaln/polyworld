## Current reward-ordered last-hit fixtures; counterpart VM deliberately absent.
## Explicit visibility/health manipulations isolate mechanisms, not competition.
import std/[os, json]
import bassy
import polyworld/[cli, tapes, pathing]
import ../[bots, content, maps, sim, replays]

let source=getEnv("WEEK_POLICY")
let enforce=getEnv("FINISH_ENFORCE")=="1"
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
  for class in HeroClass:
    for scene in ["finishing_hero","healthy_hero","distant_hero","two_hit_hero","finish_building","finish_god","retreat"]:
      let g=newGame(generateMap(54),100000,10,false,ReplayData(),drafting=false)
      g.loadBots([BotGroup(path:source,count:10)])
      g.recorder=initReplayRecorder(g.currentSetup(10000),defaultConfig())
      let slot=team.ord*5
      for i,h in g.world.heroes:
        h.manualSpells=true;h.gold=0
        if i!=slot:
          h.hp=0;h.state=Dying;h.deathTicks = -1000000
          g.heroVms[i]=nil
      let h=g.world.heroes[slot]
      h.class=class;h.refreshHeroStats();h.hp=h.maxHp;h.mana=h.maxMana
      g.step()
      h.place(middle())
      let origin=h.position
      let sign=if team==RedTeam:1'i32 else: -1'i32
      for b in g.world.buildings.mitems:b.hp=0
      var at=origin;at.x+=sign*WorldScale
      let rivalSlot=(1-team.ord)*5
      let enemy=g.world.heroes[rivalSlot]
      enemy.place(at);enemy.hp=1;enemy.maxHp=100000
      enemy.state=Marching;enemy.stunnedUntil=100000
      if scene in ["healthy_hero","bounded_chase","disadvantage"]:
        enemy.hp=if scene=="healthy_hero":100000 else:class.heroDamage(h.level)*4
      if scene=="two_hit_hero":enemy.hp=class.heroDamage(h.level)+1
      if scene=="distant_hero":
        at=origin;at.x+=sign*12*WorldScale;enemy.place(at)
      if scene=="only_fort":enemy.hp=0
      at=origin;at.z+=sign*WorldScale
      g.world.footmen = @[Footman(id:9500,team:Team(1-team.ord),hp:1,state:Marching,swingTicks: -1)]
      g.world.footmen[0].place(at)
      if scene in ["hero_over_fort","only_fort"]:g.world.footmen.setLen(0)
      if scene in ["hero_over_fort","only_fort","finish_god"]:
        g.world.forts[1-team.ord].center=at
      if scene=="finish_god":g.world.forts[1-team.ord].hp=1
      if scene=="disadvantage":
        for offset in 1..2:
          let other=g.world.heroes[rivalSlot+offset]
          other.level=20;other.hp=100000;other.maxHp=100000
          other.state=Marching;other.stunnedUntil=100000
          at=origin;at.x+=sign*(3+offset).int32*WorldScale;other.place(at)
      if scene=="tower_guard":
        for b in g.world.buildings.mitems:
          if b.team!=team and b.kind==TowerBuilding:
            b.hp=10000;b.targetId=0
            at=origin;at.x+=sign*3*WorldScale;b.position=at
            break
      var finishBuildingId=0'i32
      if scene=="finish_building":
        enemy.hp=100000
        for b in g.world.buildings.mitems:
          if b.team!=team and b.kind==BarracksBuilding:
            b.hp=1;finishBuildingId=b.id
            # Keep the native building footprint/navigation at its real map cell.
            at=b.position;at.x+=sign*WorldScale;h.place(at)
            at=h.position;at.z+=sign*WorldScale;g.world.footmen[0].place(at)
            at=h.position;at.x+=sign*4*WorldScale;enemy.place(at)
            break
      if scene=="retreat":h.hp=h.maxHp div 5
      # Force a due decision before automatic creep acquisition can preempt
      # the fixture. This does not change the policy's executable bytes.
      g.heroVms[slot].runtime.setGlobal("nextThink",0)
      h.attackObjectId=0
      let before=g.recorder.data.actions.len
      g.step()
      let vm=g.heroVms[slot]
      let chosen=vm.runtime.getGlobal("bestId")
      var firstTarget=0'i32
      for i in before..<g.recorder.data.actions.len:
        let a=g.recorder.data.actions[i]
        if a.kind==ActionAttackTarget and firstTarget==0:firstTarget=a.first
      let expected=if scene=="finishing_hero":enemy.id
                   elif scene=="finish_god":g.world.forts[1-team.ord].id
                   elif scene=="finish_building":finishBuildingId
                   elif scene=="retreat":0'i32
                   else:9500'i32
      let selected=(scene=="retreat" and firstTarget==0) or (scene!="retreat" and chosen==expected and (firstTarget==expected or h.attackObjectId==expected))
      if scene in ["finishing_hero","finish_building","finish_god"]:
        for tick in 0..<96:g.step()
      let realized=(scene!="finishing_hero" or h.totalXp>=150) and (scene!="finish_god" or h.totalXp>=500) and (scene!="finish_building" or h.totalXp>=100)
      let passed=selected and realized
      let row = %*{"scene":scene,"side":team.ord,"class":class.ord,"first_target":firstTarget,"selected_target":chosen,"expected_target":expected,"xp":h.totalXp,"passed":passed}
      rows.add(row)
      if enforce and not passed:
        stderr.writeLine($row)
        quit(1)

echo $(%*{"checks":rows.len,"rows":rows,"max_instructions":maxInstructions,"max_work":maxWork,"scope":"Artificial fully visible actual-tick fixtures isolate immediate hero150/building100/god500XP finishes versus creep15; two-hit, distant and retreat controls. Not competitive evidence."})
