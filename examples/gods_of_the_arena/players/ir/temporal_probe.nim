## Controlled actual-host probes, not competitive episodes. Other VMs are
## disabled so only the named probe can change the controlled state.
import std/[json, os]
import polyworld/basic
import ../../[game, sim, bots, content]

let mode = getEnv("GOTA_IR_PROBE")
let hero = game.run.world.heroes[0]
for index in 1 ..< game.run.heroVms.len:
  game.run.heroVms[index].failed = true
for slot in 0 ..< 6:
  hero.inventory[slot] = NoItem
  hero.itemCounts[slot] = 0
hero.hp = 1
hero.mana = hero.maxMana
hero.gold = 150
case mode
of "snapshot":
  hero.inventory[0] = IronrootRation
  hero.itemCounts[0] = 1
of "equipment_health":
  discard
of "inventory":
  hero.inventory = [IronrootRation, SteelHelmet, LeatherGauntlets,
                    SteelBuckler, RangerBoots, PoisonPotion]
  hero.itemCounts = [1'i32,1,1,1,1,1]
  hero.gold = 10000
of "walk_failure":
  hero.hp = hero.maxHp
  hero.position.x = 1_000_000_000
  hero.position.z = 1_000_000_000
  hero.attackObjectId = game.run.world.heroes[5].id
of "poison_target":
  hero.inventory[0] = PoisonPotion
  hero.itemCounts[0] = 1
  hero.attackObjectId = game.run.world.heroes[5].id
else:
  raise newException(ValueError,"unknown GOTA_IR_PROBE mode")

let beforeAttack = hero.attackObjectId
let enemyBefore = game.run.world.heroes[5].hp
runBotDecisions(game.run)
let vm = game.run.heroVms[0]
if vm.failed:
  raise newException(ValueError,vm.lastError)
var memory = newJObject()
for name in ["beforeHp","afterHp","beforeMaxHp","afterMaxHp","beforeItem","afterItem","bought",
             "rejectedBuy","afterBuyGold","afterBuyItem","walkAccepted",
             "hasHeal","emptySlot","used","bestId"]:
  try:
    memory[name] = %vm.runtime.getGlobal(name)
  except BasicError:
    discard
echo $(%*{"mode":mode,"memory":memory,"live_hp":hero.hp,"live_max_hp":hero.maxHp,
  "live_gold":hero.gold,"live_inventory":hero.inventory,
  "attack_before":beforeAttack,"attack_after":hero.attackObjectId,
  "enemy_hp_before":enemyBefore,"enemy_hp_after":game.run.world.heroes[5].hp})
