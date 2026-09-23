## Actual dead-state decisions and respawns; no competitive inference.
import std/[os,json]
import bassy
import polyworld/[cli,tapes,pathing]
import ../[bots,content,maps,sim,replays]
let source=getEnv("WEEK_POLICY")
let candidate=getEnv("BUYBACK_CANDIDATE")=="1"
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
for team in Team:
  for class in HeroClass:
    for scene in ["core_first","core_fourth","core_fifth","no_core_first","no_core_fifth","reserve_exact","reserve_short","nearly_ready","alive"]:
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
      h.inventory=[CrimsonDagger,KnightArmor,BattleAxe,RuneCrossbow,PortalScroll,HealthPotion]
      h.itemCounts=[1'i32,1,1,1,2,2]
      if scene in ["no_core_first","no_core_fifth"]:h.inventory[3]=NoItem;h.itemCounts[3]=0
      h.refreshHeroStats();h.hp=0;h.mana=0;h.state=Dying;h.deaths=1;h.deathTicks=0;h.gold=2000
      if scene in ["core_fourth","nearly_ready"]:h.deaths=4
      if scene in ["core_fifth","no_core_fifth"]:h.deaths=5
      if scene in ["reserve_exact","reserve_short"]:
        h.deaths=2;h.gold=if scene=="reserve_exact":300 else:299
      if scene=="nearly_ready":h.deathTicks=h.respawnTicks()-5*TickRate
      if scene=="alive":h.hp=h.maxHp;h.mana=h.maxMana;h.state=Marching
      h.portalCooldownEnds=g.world.tick+600
      h.potionCooldownEnds[HealthRecovery]=g.world.tick+300
      let portalEnd=h.portalCooldownEnds
      let potionEnd=h.potionCooldownEnds[HealthRecovery]
      let oldGold=h.gold
      let price=g.world.buybackPrice(h.id)
      let before=g.recorder.data.actions.len
      g.step()
      var bought=false
      for i in before..<g.recorder.data.actions.len:
        if g.recorder.data.actions[i].kind==ActionBuyback:bought=true
      let expected=scene in ["core_fifth","no_core_fifth"] or (candidate and scene in ["core_first","core_fourth","reserve_exact"])
      var restored=true
      if expected:
        restored=h.hp==h.maxHp and h.mana==h.maxMana and h.state!=Dying and h.inOwnSpawn and h.gold==oldGold-price
        for s in HeroAbilitySlot:
          if h.abilityLevels[s]>0:
            restored=restored and h.charges[s]==heroAbility(h.class,s).abilitySpec(h.abilityLevels[s]).charges
        restored=restored and h.portalCooldownEnds==portalEnd and h.potionCooldownEnds[HealthRecovery]==potionEnd
      elif scene!="alive":restored=h.hp<=0 and h.state==Dying and h.gold==oldGold
      let passed=bought==expected and restored
      let row= %*{"scene":scene,"side":team.ord,"class":class.ord,"bought":bought,"expected":expected,"remaining":h.respawnTicks(),"hp":h.hp,"mana":h.mana,"gold":h.gold,"price":price,"at_spawn":h.inOwnSpawn,"portal_end":h.portalCooldownEnds,"expected_portal":portalEnd,"potion_end":h.potionCooldownEnds[HealthRecovery],"expected_potion":potionEnd,"restored":restored,"passed":passed}
      rows.add(row)
      if not passed:stderr.writeLine($row);quit(1)
echo $(%*{"checks":rows.len,"rows":rows,"max_instructions":maxInstructions,"max_work":maxWork,"scope":"Actual buyback cost/spawn resources/charges/cooldown preservation and non-spending guards, both colors/all classes. Baseline checked against its own unchanged expected behavior; not competitive evidence."})
