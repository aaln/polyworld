## Actual release62 observations, camp states and accepted movement commands.
import std/[os, json, math]
import bassy
import polyworld/[cli, pathing]
import ../[bots, content, maps, sim, replays]

let source = getEnv("AUDIT_POLICY")
var rows = newJArray()
var maxInstructions, maxWork: int64

proc gap(a,b: WorldPoint): float =
  sqrt(float((int64(a.x)-b.x)*(int64(a.x)-b.x)+(int64(a.z)-b.z)*(int64(a.z)-b.z)))/WorldScale.float

for scenario in ["start", "on_us", "low_hp", "root", "no_wave", "handoff", "timeout", "returning"]:
  for team in Team:
    for class in [Ranger, DruidWarden, Warlock]:
      let g = newGame(generateMap(54), 480, 10, false, ReplayData(), drafting=false)
      g.loadBots([BotGroup(path:source,count:10)])
      g.recorder = initReplayRecorder(g.currentSetup(10000), defaultConfig())
      let slot = team.ord * 5
      for i,h in g.world.heroes:
        h.gold = 0
        if i != slot:
          h.hp = 0; h.state = Dying; h.deathTicks = -1000000
          g.heroVms[i] = nil
      let h = g.world.heroes[slot]
      h.class=class; h.refreshHeroStats();h.hp=h.maxHp;h.mana=h.maxMana
      g.world.spawnTimerTicks = 0
      g.tickWorld(proc() = g.runBotDecisions())
      var camp = -1
      var nearest = 1e9
      for i,c in g.world.camps:
        let d = gap(h.spawnPosition,c.center)
        if c.tier == 1 and d < nearest: camp=i;nearest=d
      doAssert camp >= 0
      let center=g.world.camps[camp].center
      var wave = center
      var error = 1e9
      const Unit = WorldScale div PathUnitsPerTile
      for z in 1..<115:
        for x in 1..<115:
          if not navigationOpen(GroundLayer,x,z):continue
          let q=pathPoint(GroundLayer,x,z)
          let p=WorldPoint(x:q.x*Unit,y:q.y*Unit,z:q.z*Unit)
          let d=gap(p,center)
          if d >= 5 and d <= 7 and abs(d-6) < error:
            error=abs(d-6);wave=p
      doAssert error < 1
      h.place(wave)
      h.level=4;h.refreshHeroStats();h.hp=h.maxHp;h.mana=h.maxMana
      var selected:seq[Footman]
      var mob=0'i32
      for unit in g.world.footmen:
        if unit.camp == camp+1:
          selected.add(unit)
          if mob==0:mob=unit.id
      doAssert mob>0, "Camp must spawn in the current engine"
      var waves=0
      for unit in g.world.footmen:
        if unit.camp==0 and unit.team==team and waves<2:
          var f=unit
          f.place(wave)
          f.targetId=0;f.targetHeroId=0;f.targetBuildingId=0
          if scenario=="handoff":f.targetId=mob
          selected.add(f);inc waves
      doAssert waves==2
      if scenario=="no_wave":
        selected.setLen(selected.len-2)
      g.world.footmen=selected
      g.world.tick=600
      g.world.rebuildVision()
      let vm=g.heroVms[slot]
      template set(name:string,value:int32)=vm.runtime.setGlobal(name,value)
      if scenario in ["on_us","low_hp","root","handoff","timeout","returning"]:
        set("nPullStage",1);set("nPullCamp",camp.int32);set("nPullMob",mob)
        set("nPullCenterX",mapCoordinate(center.x,team));set("nPullCenterY",mapCoordinate(center.z,team))
        set("nPullX",mapCoordinate(center.x,team));set("nPullY",mapCoordinate(center.z,team))
        set("nLastSeen",600);set("nPullUntil",900)
      if scenario=="on_us":
        g.world.camps[camp].state=FightingCamp
        for f in g.world.footmen.mitems:
          if f.camp==camp+1:f.targetHeroId=h.id
      if scenario=="low_hp":h.hp=h.maxHp div 4
      if scenario=="root":g.world.applyControl(h.id,RootControl,48)
      if scenario=="timeout":set("nPullUntil",600)
      if scenario=="returning":g.world.camps[camp].state=ReturningCamp;set("nLastSeen",500)
      let before=g.recorder.data.actions.len
      g.runBotDecisions()
      doAssert not vm.failed,vm.lastError
      maxInstructions=max(maxInstructions,vm.lastInstructions)
      maxWork=max(maxWork,vm.lastWork)
      let stage=vm.runtime.getGlobal("nPullStage")
      if scenario=="start":doAssert stage==1,scenario & " " & $team & " " & $class
      elif scenario=="on_us":doAssert stage==2,scenario & " " & $team & " " & $class
      else:doAssert stage==0,scenario & " " & $team & " " & $class
      if scenario=="returning":doAssert vm.runtime.getGlobal("bestKind") != 6 or vm.runtime.getGlobal("bestId")==0
      rows.add(%*{"scenario":scenario,"team":team.ord,"class": $class,"stage":stage,
        "commands":g.recorder.data.actions.len-before,"camp":camp,"mob":mob})

doAssert maxInstructions<=19000 and maxWork<=50000
echo $(%*{"passed":true,"fixtures":rows.len,"rows":rows,
  "max_instructions":maxInstructions,"max_work":maxWork,
  "scope":"48constructed release62 host-decision fixtures. Neutral/wave positions and aggro are controlled; complete native and hosted games provide outcome evidence."})
