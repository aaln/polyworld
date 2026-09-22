## Scarce-gold shopping drill: gold grants are fixture interventions, not a bot input.
import std/[os, json]
import bassy
import polyworld/[cli, tapes]
import ../[bots, content, maps, sim, replays]

let source = getEnv("WEEK_POLICY")
doAssert source.len > 0
var rows = newJArray()
for team in Team:
  for class in [Ranger,VanguardKnight,DemonHunter]:
    let g = newGame(generateMap(54), 100_000, 10, false, ReplayData(), drafting=false)
    g.loadBots([BotGroup(path:source,count:10)])
    g.recorder = initReplayRecorder(g.currentSetup(1000), defaultConfig())
    for i,h in g.world.heroes:
      h.manualSpells = true
      h.gold = 0
      if i != team.ord*5:
        h.hp = 0; h.state = Dying; h.deathTicks = -1_000_000
        g.heroVms[i] = nil
    let h = g.world.heroes[team.ord*5]
    h.class = class; h.refreshHeroStats(); h.hp=h.maxHp;h.mana=h.maxMana
    let spawn = h.position
    var visits = newJArray()
    for grant in [150,90,90,100]:
      h.gold += grant
      for i in 0..<6:
        h.place(spawn)
        g.tickWorld(proc() = g.runBotDecisions())
        let vm=g.heroVms[team.ord*5]
        doAssert not vm.failed,vm.lastError
        doAssert vm.lastInstructions <= 19000 and vm.lastWork <= 50000
      visits.add(%*{"grant":grant,"remaining_gold":h.gold,"armor":KnightArmor in h.inventory,
        "max_hp":h.maxHp,"damage":h.heroAttackDamage,"inventory":h.inventory,"counts":h.itemCounts})
    rows.add(%*{"side":team.ord,"class":class.ord,"visits":visits})

echo $(%*{"source":source,"rows":rows,
  "scope":"Controlled shop-income sequence, actual host purchases. Measures allocation only; travel, combat and long-run value require responsive games."})
