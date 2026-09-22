## Artificial public scenes exercise legal spell selection and actual damage.
import std/[os,json]
import bassy
import polyworld/[cli,tapes,pathing]
import ../[bots,content,maps,sim,replays]
let source=getEnv("WEEK_POLICY")
let enforce=getEnv("ADAPTIVE_ENFORCE")=="1"
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
  for class in [Ranger,Crossbowman,Arcanist,Warlock]:
    for scene in ["split","fallback","ally","retreat","channel","mana"]:
      if scene=="mana" and class notin [Arcanist,Warlock]:continue
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
      g.step()
      h.place(middle())
      let origin=h.position
      let sign=if team==RedTeam:1'i32 else: -1'i32
      for b in g.world.buildings.mitems:b.hp=0
      var at=origin;at.x+=sign*4*WorldScale
      let enemy=g.world.heroes[(1-team.ord)*5]
      enemy.place(at);enemy.hp=10000;enemy.maxHp=10000;enemy.state=Marching;enemy.stunnedUntil=100000
      if scene=="fallback":
        at=origin;at.x+=sign*9*WorldScale;enemy.place(at)
      if scene=="ally":enemy.team=team
      at=origin;at.z+=sign*WorldScale
      g.world.footmen = @[Footman(id:9500,team:Team(1-team.ord),hp:1,state:Marching,swingTicks: -1)]
      g.world.footmen[0].place(at)
      if scene=="retreat":h.hp=h.maxHp div 5
      if scene=="channel":h.portalEnds=g.world.tick+72
      if scene=="mana" and class in [Arcanist,Warlock]:
        h.abilityLevels=[1'i32,0,0,0];h.mana=1;h.charges[PassiveAbility]=1
      for a in HeroAbilitySlot:h.cooldowns[a]=0
      g.heroVms[slot].runtime.setGlobal("nextThink",0)
      h.attackObjectId=0
      let before=g.recorder.data.actions.len
      g.step()
      var target:int32
      var casts:int
      for i in before..<g.recorder.data.actions.len:
        let a=g.recorder.data.actions[i]
        if a.kind==ActionCastTarget:
          target=a.first;inc casts
      let accepted=h.cooldowns[PrimaryAbility]>0
      let restored=h.cooldowns[PassiveAbility]>0
      g.heroVms[slot]=nil
      var heroDamage:int64
      let manaBefore=h.mana
      for i in 0..<96:
        g.step()
        for e in g.world.events:
          if e.kind==Damage and e.actor.player==slot and e.target.id==enemy.id and e.cause==AbilityEffect:heroDamage+=e.amount
      let expected=if scene=="split":enemy.id
        elif scene in ["fallback","ally"]:9500'i32
        elif scene=="mana" and class in [Arcanist,Warlock]:h.id
        else:0'i32
      let passed=if scene=="split":target==expected and accepted and heroDamage>0
        elif scene in ["fallback","ally"]:target==expected and accepted
        elif scene in ["retreat","channel"]:casts==0
        elif scene=="mana" and class in [Arcanist,Warlock]:target==expected and restored and h.mana>manaBefore
        else:true
      let row = %*{"scene":scene,"class":class.ord,"side":team.ord,"last_spell_target":target,"expected_target":expected,"casts":casts,"accepted_primary":accepted,"hero_spell_damage":heroDamage,"mana_restore":restored,"passed":passed}
      rows.add(row)
      if enforce and not passed:stderr.writeLine($row);quit(1)
echo $(%*{"checks":rows.len,"rows":rows,"max_instructions":maxInstructions,"max_work":maxWork,"scope":"Artificial fully visible actual-tick fixtures. No competitive inference."})
