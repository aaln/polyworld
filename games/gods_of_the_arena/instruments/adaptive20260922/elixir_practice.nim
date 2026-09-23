## Actual ticks, items and healing; quiet artificial scenes are not competition.
import std/[os,json]
import bassy
import polyworld/[cli,tapes,pathing]
import ../[bots,content,maps,sim,replays]
let source=getEnv("WEEK_POLICY")
let candidate=getEnv("ELIXIR_CANDIDATE")=="1"
let enforce=getEnv("ELIXIR_ENFORCE")=="1"
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
    for scene in ["combat","recent_damage","small_injury","spawn","cooldown","missing_item","core_stock","core_budget","full_inventory","early_shop","channel","critical"]:
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
      g.step()
      h.inventory=[CrimsonDagger,KnightArmor,BattleAxe,RuneCrossbow,PortalScroll,NoItem]
      h.itemCounts=[1'i32,1,1,1,2,0]
      h.refreshHeroStats();h.hp=h.maxHp;h.mana=0
      if scene notin ["core_stock","core_budget","full_inventory","early_shop","missing_item"]:
        h.inventory[5]=if candidate:VitalityElixir else:HealthPotion
        h.itemCounts[5]=2
      if scene notin ["spawn","core_stock","core_budget","full_inventory","early_shop"]:
        h.place(middle())
      for b in g.world.buildings.mitems:
        if b.team!=team:b.hp=0
      h.hp=h.maxHp-100
      if scene=="small_injury":h.hp=h.maxHp-69
      if scene=="critical":h.hp=h.maxHp div 5
      if scene in ["core_stock","core_budget","full_inventory","early_shop"]:h.hp=h.maxHp
      if scene in ["combat","critical"]:
        let enemy=g.world.heroes[(1-team.ord)*5]
        var at=h.position;at.x+=(if team==RedTeam:1'i32 else: -1'i32)*WorldScale
        enemy.place(at);enemy.hp=100000;enemy.maxHp=100000
        enemy.state=Fighting;enemy.attackObjectId=h.id
      if scene=="cooldown":h.potionCooldownEnds[HealthRecovery]=g.world.tick+240
      if scene=="channel":h.portalEnds=g.world.tick+72
      if scene=="core_stock":h.gold=1000
      if scene=="core_budget":h.gold=275
      if scene=="full_inventory":
        h.inventory[5]=ManaPotion;h.itemCounts[5]=1;h.gold=1000
      if scene=="early_shop":
        h.inventory[0]=NoItem;h.itemCounts[0]=0;h.gold=100
      let before=g.recorder.data.actions.len
      g.heroVms[slot].runtime.setGlobal("nextThink",0)
      g.step()
      var healed=0;var bought=0;var used=0;var attack=false
      for e in g.world.events:
        if e.kind==Healing and e.target.player==slot and e.cause==ItemEffect:healed+=e.amount
        if e.kind==ItemPurchased and e.actor.player==slot and e.detail==(if candidate:VitalityElixir.ord else:HealthPotion.ord):inc bought
      for i in before..<g.recorder.data.actions.len:
        let a=g.recorder.data.actions[i]
        if a.kind==ActionUseItem:inc used
        if a.kind==ActionAttackTarget:attack=true
      var count=0
      for s in 0..<6:
        if h.inventory[s]==(if candidate:VitalityElixir else:HealthPotion):count+=h.itemCounts[s]
      var passed=true
      if scene in ["combat","recent_damage","critical"]:
        passed=healed==(if candidate:90 else:0) and used==(if candidate:1 else:0)
        if scene=="combat":passed=passed and attack
      elif scene in ["small_injury","spawn","cooldown","missing_item","channel"]:
        passed=healed==0 and used==0
      elif scene=="core_stock":passed=count==(if candidate:6 else:1) and h.gold==(if candidate:550 else:970)
      elif scene=="core_budget":passed=count==1 and h.gold==(if candidate:200 else:245)
      elif scene=="full_inventory":passed=count==0 and h.gold==1000
      elif scene=="early_shop":passed=count==1 and h.gold==(if candidate:25 else:70)
      let row= %*{"scene":scene,"side":team.ord,"class":class.ord,"healed":healed,"used":used,"stack":count,"gold":h.gold,"attack":attack,"passed":passed}
      rows.add(row)
      if enforce and not passed:stderr.writeLine($row);quit(1)
echo $(%*{"checks":rows.len,"rows":rows,"max_instructions":maxInstructions,"max_work":maxWork,"scope":"Actual first-tick item HP/economy and combat guards, all classes/colors. Baseline follows its own cheap-regeneration behavior; not a score verdict."})
