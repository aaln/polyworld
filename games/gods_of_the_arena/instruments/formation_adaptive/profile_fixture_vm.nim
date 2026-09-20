## Source-reveal synthetic tests; scripted command acceptance, not combat outcomes.
## Execute JSON observation fixtures in the real BASIC VM. Command acceptance
## is scripted by each fixture; this is not a replacement combat simulator.
import std/[json, os]
import polyworld/basic

let request = parseJson(stdin.readAll())
var
  observation: JsonNode
  actions: JsonNode
  host = initHost()
const dataNames = ["selfId", "selfTeam", "selfClass", "selfX", "selfY",
  "selfHp", "selfMaxHp", "selfMana", "selfMaxMana", "selfGold", "selfLevel", "worldTick", "selfAttackCooldown", "selfAttacksLanded", "selfAttackRange", "selfMoveSpeed", "selfAttackDamage", "selfTarget", "mapWidth", "mapHeight"]
for name in dataNames:
  discard host.addData(name)

proc query(name: string): HostProc =
  result = proc(args: openArray[int32]): int32 =
    if name == "objectCount":
      return int32(observation["objects"].len)
    if name == "abilityCharges" or name == "abilityCooldown":
      if observation.hasKey("abilities"):
        return int32(observation["abilities"][int(args[0])][name].getInt)
      return 0
    if name == "itemId" or name == "itemCount":
      let index = int(args[0])
      if index < 0 or index >= observation["inventory"].len:
        return 0
      if name == "itemCount":
        return int32(observation["inventory"][index].getInt != 0)
      return int32(observation["inventory"][index].getInt)
    let index = int(args[0])
    if name == "objectItemId":
      if index < 0 or index >= observation["objects"].len or not observation["objects"][index].hasKey("items"):
        return 0
      return int32(observation["objects"][index]["items"][int(args[1])].getInt)
    if index < 0 or index >= observation["objects"].len:
      return 0
    (if observation["objects"][index].hasKey(name): int32(observation["objects"][index][name].getInt) else: 0'i32)

for name in ["objectCount", "objectId", "objectKind", "objectTeam", "objectClass",
    "objectX", "objectY", "objectHp", "objectAlive", "objectTarget", "objectFacingX", "objectFacingY", "itemId", "itemCount", "abilityCharges", "abilityCooldown"]:
  discard host.addFunction(name, (if name == "objectCount": 0 else: 1), query(name),
    (if name == "objectCount": 2 elif name in ["objectTarget", "objectFacingX", "objectFacingY"]: 16 else: 4))

discard host.addFunction("objectItemId", 2, query("objectItemId"), 16)

proc terrainWalkable(args: openArray[int32]): int32 =
  if args[0] < 0 or args[1] < 0 or args[0] >= 116 or args[1] >= 116:
    return 0
  if observation.hasKey("blocked"):
    for tile in observation["blocked"]:
      if tile[0].getInt == int(args[0]) and tile[1].getInt == int(args[1]):
        return 0
  1
discard host.addFunction("terrainWalkable", 2, terrainWalkable, 4)

proc command(name: string): HostProc =
  result = proc(args: openArray[int32]): int32 =
    var accepted = 1
    if observation.hasKey("returns") and observation["returns"].hasKey(name):
      accepted = observation["returns"][name].getInt
    actions.add(%*{"command": name, "arguments": @args, "accepted": accepted})
    int32(accepted)

for name in ["walkTo", "attackTarget", "buyItem", "useItem", "castTarget", "castPoint"]:
  discard host.addFunction(name, (if name == "castPoint": 3 elif name == "walkTo" or name == "castTarget": 2 else: 1), command(name),
    (if name == "walkTo": 800 elif name in ["castTarget", "castPoint"]: 80 else: 20))

var limits = defaultLimits()
limits.maxSourceBytes = 64 * 1024
limits.maxInstructions = 20_000
limits.maxWorkUnits = 50_000
limits.maxGlobals = 256
limits.maxCodeInstructions = 20_000
limits.maxArrays = 32
limits.maxArrayElements = 4096
limits.maxRegisters = 256
let program = compile(readFile(paramStr(1)), host, limits)
var runtime = initRuntime(program, host, limits)
var output = newJArray()
for fixture in request["decisions"]:
  observation = fixture
  actions = newJArray()
  runtime.restart()
  for name in dataNames:
    runtime.setData(name, (if observation["self"].hasKey(name): int32(observation["self"][name].getInt) else: 0'i32))
  let stats = runtime.run()
  var memory = newJObject()
  for name in request["memory"]:
    memory[name.getStr] = %runtime.getGlobal(name.getStr)
  output.add(%*{"actions": actions, "memory": memory,
    "instructions": stats.instructions, "work": stats.workUnits, "globals": program.globals})
echo $output
