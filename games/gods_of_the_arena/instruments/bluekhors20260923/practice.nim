## Exercise actual opening decisions across every class, team and ordinal.
import std/[os,json]
import bassy
import polyworld/[cli,tapes,pathing]
import ../[bots,content,maps,sim,replays]
let source=getEnv("WEEK_POLICY")
let candidate=getEnv("BLUE_CANDIDATE")=="1"
var rows=newJArray()
var maxInstructions,maxWork:int64
proc step(g:Game)=
  g.tickWorld(proc()=
    g.world.thawObservations()
    discard g.world.freezeObservations()
    g.runBotDecisions())
  for vm in g.heroVms:
    if vm!=nil:
      doAssert not vm.failed,vm.lastError
      maxInstructions=max(maxInstructions,vm.lastInstructions)
      maxWork=max(maxWork,vm.lastWork)
      doAssert vm.lastInstructions<=19000 and vm.lastWork<=50000
for team in Team:
  for class in HeroClass:
    for ordinal in 0..4:
      let g=newGame(generateMap(54),100000,10,false,ReplayData(),drafting=false)
      g.loadBots([BotGroup(path:source,count:10)])
      g.recorder=initReplayRecorder(g.currentSetup(10000),defaultConfig())
      let slot=team.ord*5+ordinal
      for i,h in g.world.heroes:
        h.manualSpells=true;h.gold=0
        if i!=slot:
          h.hp=0;h.state=Dying;h.deathTicks = -1000000;g.heroVms[i]=nil
      let h=g.world.heroes[slot]
      h.class=class;h.refreshHeroStats();h.hp=h.maxHp;h.mana=h.maxMana
      var advance=false
      var targetX,targetY:int32
      for tick in 0..12:
        let before=g.recorder.data.actions.len
        g.step()
        for i in before..<g.recorder.data.actions.len:
          let a=g.recorder.data.actions[i]
          if a.kind==ActionAttackMove:
            targetX=a.first;targetY=a.second;advance=true
        if advance:break
      let width=mapTiles().int32
      let height=mapTiles().int32
      let center=candidate and team==BlueTeam and ordinal==0 and class in {Ranger,Crossbowman}
      let lane=ordinal mod 3
      let expectedX=if center or lane==1:width div 2 elif lane==0:width div 10 else:width*9 div 10
      let expectedY=if center or lane==1:height div 2 elif lane==0:height div 10 else:height*9 div 10
      let passed=advance and targetX==expectedX and targetY==expectedY
      let row= %*{"side":team.ord,"class":class.ord,"ordinal":ordinal,"center":center,"target":[targetX,targetY],"expected":[expectedX,expectedY],"passed":passed}
      rows.add(row)
      if not passed:stderr.writeLine($row);quit(1)
echo $(%*{"checks":rows.len,"rows":rows,"max_instructions":maxInstructions,"max_work":maxWork,"scope":"Actual first opening command, all ten classes/two teams/five ordinals. Both sources tested against prospective expectations; not competitive evidence."})
