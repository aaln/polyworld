## Reconstruct owned VM state by replaying rivals and rerunning our exact source.
## Every generated owned command and every resulting state hash must match tape.
import std/[json, os, strutils]
import ../../game
include ../../bots

proc applyReplayAction(world: World, action: ReplayAction): bool {.discardable.} =
  ## Applies one recorded bot command without requiring its private VM.
  case action.kind
  of ActionWalkTo:
    applyWalkTo(world, action.heroId, action.first, action.second)
  of ActionAttackMove:
    applyAttackMove(
      world, action.heroId, action.first, action.second
    )
  of ActionAttackTarget:
    applyAttackTarget(world, action.heroId, action.first)
  of ActionBuyItem:
    applyBuyItem(world, action.heroId, action.first)
  of ActionUseItem:
    applyUseItem(world, action.heroId, action.first)
  of ActionCastTarget .. ActionCastPoint - 1:
    applyCastTarget(world, action.heroId,
      int32(action.kind - ActionCastTarget), action.first)
  of ActionCastPoint .. ActionManualSpells - 1:
    applyCastPoint(world, action.heroId,
      int32(action.kind - ActionCastPoint), action.first, action.second)
  of ActionManualSpells:
    let index = world.heroIndex(action.heroId)
    if index >= 0:
      world.heroes[index].manualSpells = action.first != 0
    false
  else:
    raise newException(ReplayError, "replay action kind is invalid")

if not game.run.replayMode:raise newException(ValueError,"--replay required")
let tape=game.run.replayData
## Use 1 to inspect brief visibility/recall transitions; default keeps old traces.
let sampleEvery=parseInt(getEnv("PROBE_SAMPLE_EVERY", "120"))
if sampleEvery<1:raise newException(ValueError,"PROBE_SAMPLE_EVERY must be positive")
let subject=parseInt(getEnv("PROBE_SUBJECT", "0"))
let globalNames=readFile(getEnv("PROBE_GLOBAL_NAMES")).strip().split(',')
let slotText=getEnv("PROBE_SLOTS")
if slotText.len==0:raise newException(ValueError,"PROBE_SLOTS required")
var controlled:array[10,bool]
var probeSlots:seq[int]
for item in slotText.split(','):
  let slot=parseInt(item)
  if slot<0 or slot>=10 or controlled[slot]:raise newException(ValueError,"Invalid/duplicate owned slot")
  controlled[slot]=true
  probeSlots.add(slot)
loadBots(game.run, [BotGroup(path:getEnv("PROBE_POLICY"),count:10)])
game.run.historyPlayback=false
startReplayRecording(uint32(tape.hashes.len))
var index=0
var checked=0
var decisions=0
while game.run.world.tick<tape.hashes.len and not game.run.world.gameOver:
  tickWorld(game.run, proc() =
    var perSlot:array[10,seq[ReplayAction]]
    while index<tape.actions.len and tape.actions[index].tick==uint32(game.run.world.tick):
      let a=tape.actions[index]
      if a.kind==ActionManualSpells:discard applyReplayAction(game.run.world,a)
      else:perSlot[heroIndex(game.run.world,a.heroId)].add(a)
      inc index
    for offset in 0..<10:
      let slot=(game.run.world.heroTurnStart+offset) mod 10
      if not controlled[slot]:
        for a in perSlot[slot]:discard applyReplayAction(game.run.world,a)
      else:
        let first=game.run.recorder.data.actions.len
        let vm=game.run.heroVms[slot]
        let before=vm.decisions
        var observed=newJArray()
        var beforeMemory=newJObject()
        let hero=game.run.world.heroes[slot]
        let alive=hero.state != Dying
        if slot==subject and alive:
          for name in globalNames:
            try:beforeMemory[name]= %vm.runtime.getGlobal(name)
            except BasicError:discard
          var values:seq[WorldObject]
          for i in 0..<game.run.world.worldObjectCount(hero.id):
            var value:WorldObject
            if game.run.world.worldObjectAt(hero.id,i,value):values.add(value)
          for value in values:
            var target=0'i32
            for candidate in values:
              if candidate.id==value.targetId:target=value.targetId
            observed.add(%*{"id":value.id,"kind":value.kind,"team":value.team.ord,
              "class":value.class,"x":mapCoordinate(value.position.x),"y":mapCoordinate(value.position.z),
              "hp":value.hp,"alive":value.alive,"target":target})
        var ruleEvents=newJArray()
        vm.output=proc(event:PrintEvent) =
          if slot==subject and event.kind==TextPrint and event.text.startsWith("IR:"):
            let parts=event.text.split(':')
            var eventMemory=newJObject()
            for name in ["emptySlot","bestId","motionActive","defActive"]:
              eventMemory[name]= %vm.runtime.getGlobal(name)
            ruleEvents.add(%*{"phase":parts[1],"rule":parts[2],
              "command_offset":game.run.recorder.data.actions.len-first,"values":eventMemory})
        runHeroScript(game.run,slot)
        if vm.failed:raise newException(ValueError,vm.lastError)
        let actual=game.run.recorder.data.actions[first..<game.run.recorder.data.actions.len]
        if actual != perSlot[slot]:
          echo $(%*{"type":"command_mismatch","tick":game.run.world.tick,"slot":slot,"expected":perSlot[slot],"actual":actual})
          quit(2)
        checked+=actual.len
        if vm.decisions>before:
          inc decisions
          if slot==subject:
            var memory=newJObject()
            var selfData=newJObject()
            for name in globalNames:
              try:memory[name]= %vm.runtime.getGlobal(name)
              except BasicError:discard
            for name in HeroDataNames:
              selfData[name]= %vm.runtime.getData(name)
            echo $(%*{"type":"decision","tick":game.run.world.tick,"slot":slot,
              "observation":{"self":selfData,"objects":observed},
              "memory_before":beforeMemory,"memory":memory,"actions":actual,"rule_events":ruleEvents})
    game.run.world.heroTurnStart=(game.run.world.heroTurnStart+1) mod 10
  )
  var truthHeroes=newJArray()
  var truthStructures=newJArray()
  for slot,hero in game.run.world.heroes:
    truthHeroes.add(%*{"slot":slot,"id":hero.id,"class": $hero.class,"team":hero.team.ord,
      "x":mapCoordinate(hero.position.x),"y":mapCoordinate(hero.position.z),
      "hp":hero.hp,"max_hp":hero.maxHp,"state": $hero.state,"xp":hero.totalXp,
      "hits":hero.attacksLanded,"gold":hero.gold,"inventory":hero.inventory})
  for fort in game.run.world.forts:
    truthStructures.add(%*{"id":fort.id,"kind":1,"team":fort.team.ord,"hp":fort.hp})
  for tower in game.run.world.buildings:
    truthStructures.add(%*{"id":tower.id,"kind":(if tower.kind==TowerBuilding: 4 else: 5),
      "guards_god":tower.guardsGod,"team":tower.team.ord,"hp":tower.hp,"max_hp":tower.maxHp})
  echo $(%*{"type":"ground_truth","tick":game.run.world.tick,"heroes":truthHeroes,"structures":truthStructures})
  if game.run.stateHash()!=tape.hashes[game.run.world.tick-1]:
    echo $(%*{"type":"hash_mismatch","tick":game.run.world.tick})
    quit(3)
echo $(%*{"type":"summary","controlled_slots":probeSlots,"ticks":game.run.world.tick,"owned_commands_matched":checked,"owned_decisions":decisions,"all_state_hashes_equal":true,"all_actions_consumed":index==tape.actions.len})
