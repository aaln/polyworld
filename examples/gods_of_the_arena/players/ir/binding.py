"""Versioned semantic skills for the Gods of the Arena BASIC host.

Templates are the executable definitions of these skills, not opaque policy
payloads. The reverse extractor matches their complete parsed control flow.
Only declared integer parameters may vary within a skill contract.
"""

from dataclasses import dataclass
import re
from textwrap import dedent


VERSION = "gota-basic/1"
GAME_VERSION = "2026.9.10.3"
# 27a8fd5 changes replay/config metadata; the BASIC host, combat rules and
# content remain compatible. Hosted tapes must use that published reader.
GAME_VERSIONS = ("2026.9.9.4", "2026.9.10.1", GAME_VERSION, "2026.9.15.1", "2026.9.15.2", "2026.9.15.3")


@dataclass(frozen=True)
class Contract:
    template: str
    parameters: dict[str, tuple[int, int, int]]  # default, minimum, maximum
    reads: tuple[str, ...]
    writes: tuple[str, ...]
    actions: tuple[str, ...]
    meaning: str
    memory: tuple[str, ...] = ()

    def defaults(self):
        return {name: spec[0] for name, spec in self.parameters.items()}

    def source(self, parameters):
        if set(parameters) != set(self.parameters):
            raise ValueError("skill parameters must exactly match its binding contract")
        for name, value in parameters.items():
            _, low, high = self.parameters[name]
            if type(value) is not int or not low <= value <= high:
                raise ValueError(f"{name} must be an integer in {low}..{high}")
        return re.sub(r"\bparam_(\w+)\b", lambda m: str(parameters[m[1]]), self.template)


def contract(source, parameters, reads, writes, actions, meaning, memory=()):
    return Contract(dedent(source).strip(), parameters, tuple(reads), tuple(writes),
                    tuple(actions), meaning, tuple(memory))


def guarded(condition, body):
    return f"if {condition} then\n" + "\n".join("  " + line for line in body.splitlines()) + "\nend if"


def buy(item, price):
    return guarded(f"selfGold >= {price}", f"buyItem({item})")


def consumable_source(poison):
    lines = [
        guarded("selfHp * 2 < selfMaxHp", guarded("hasHeal = 0", buy(2, 50) + "\n" + buy(1, 30))),
        guarded("selfMaxMana > 0", guarded("selfMana * 2 < selfMaxMana",
                guarded("hasMana = 0", buy(3, 45)))),
    ]
    if poison:
        lines.append(guarded("bestId <> 0", guarded("hasPoison = 0", buy(4, 40))))
    return "\n".join(lines)


def equipment_source():
    groups = [
        ("melee", [0, 4, 5, 9], [(7, 70), (5, 80), (11, 110), (13, 150), (18, 180)]),
        ("ranged", [1, 6], [(8, 100), (14, 150), (19, 180)]),
        ("magic", [2, 3, 7, 8], [(12, 140), (10, 120), (17, 170), (20, 190)]),
    ]
    lines = [f"{name} = 0" for name, _, _ in groups]
    for name, classes, _ in groups:
        lines.append(guarded(" or ".join(f"selfClass = {c}" for c in classes), f"{name} = 1"))
    for name, _, purchases in groups:
        body = [guarded("hasGear = 0", buy(*purchases[0]))]
        body.extend(buy(*p) for p in purchases[1:])
        lines.append(guarded(f"{name} = 1", "\n".join(body)))
    lines.extend([buy(6, 90), buy(9, 120)])
    return "\n".join(lines)


def reserved_equipment_source():
    # Count gear anew and account for accepted buys within this decision.
    # The six host slots are queried only once; repeated snapshot counts would
    # miss successful purchases on hosts that snapshot inventory per decision.
    scan = dedent("""
        gearCount = 0
        gearSlot = 0
        while gearSlot < 6
          if itemId(gearSlot) > 4 then
            gearCount = gearCount + 1
          end if
          gearSlot = gearSlot + 1
        wend
    """).strip()

    def cap(match):
        indent, item = match.groups()
        body = guarded("gearCount < param_equipment_cap",
                       f"gearBought = buyItem({item})\n" +
                       guarded("gearBought <> 0", "gearCount = gearCount + 1"))
        return "\n".join(indent + line for line in body.splitlines())

    return scan + "\n" + re.sub(r"(?m)^( *)buyItem\((\d+)\)$", cap, equipment_source())


def hp_investment_source():
    scan = ["hpHelmet = 0", "hpBuckler = 0", "hpAmulet = 0", "hpSpace = 0", "hpSlot = 0"]
    body = ["hpItem = itemId(hpSlot)", guarded("hpItem = 0", "hpSpace = 1")]
    body.extend(guarded(f"hpItem = {item}", f"{flag} = 1")
                for item,flag in [(5,"hpHelmet"),(6,"hpBuckler"),(9,"hpAmulet")])
    body.append("hpSlot = hpSlot + 1")
    scan.append("while hpSlot < 6\n" + "\n".join("  "+line for part in body for line in part.splitlines()) + "\nwend")
    scan.append("hpGearBought = 0")
    attempts = []
    for item,price,bonus,flag in [(5,80,50,"hpHelmet"),(6,90,60,"hpBuckler"),(9,120,70,"hpAmulet")]:
        attempts.append(guarded(f"hpGearBought = 0 and {flag} = 0 and selfGold >= {price}",
            f"hpGearBought = buyItem({item})\n" + guarded("hpGearBought <> 0",
            f"hpGearInvestments = hpGearInvestments + 1\nhpGearGrantedHp = hpGearGrantedHp + {bonus}")))
    scan.append(guarded("hpSpace <> 0", "\n".join(attempts)))
    investment = guarded("selfHp * param_hp_denominator < selfMaxHp * param_hp_numerator",
                         guarded("hasHeal = 0", "\n".join(scan)))
    return investment + "\n" + consumable_source(poison=False)


def ordered_loadout_source():
    names = ["first", "second", "third", "fourth", "fifth"]
    lines = [f"owns{n} = 0" for n in names]
    lines += ["loadoutSpace = 0", "loadoutSlot = 0", "while loadoutSlot < 6",
              "  loadoutItem = itemId(loadoutSlot)", "  if loadoutItem = 0 then",
              "    loadoutSpace = 1", "  end if"]
    for name in names:
        lines += [f"  if loadoutItem = param_{name}_item then", f"    owns{name} = 1", "  end if"]
    lines += ["  loadoutSlot = loadoutSlot + 1", "wend", "loadoutNext = 0"]
    for name in names:
        lines.append(guarded(f"loadoutNext = 0 and owns{name} = 0", f"loadoutNext = param_{name}_item"))
    prices = {5:80, 6:90, 7:70, 8:100, 9:120, 10:120, 11:110, 12:140,
              13:150, 14:150, 15:140, 16:160, 17:170, 18:180, 19:180, 20:190}
    lines.append("loadoutPrice = 2147483647")
    for item,price in prices.items():
        lines.append(guarded(f"loadoutNext = {item}", f"loadoutPrice = {price}"))
    lines.append(guarded("loadoutSpace <> 0 and selfGold >= loadoutPrice",
        "loadoutBought = buyItem(loadoutNext)\n" + guarded("loadoutBought <> 0",
        "loadoutPurchases = loadoutPurchases + 1")))
    return "\n".join(lines)


CONTRACTS = {
    "burst_kite": contract("""
        kiteMoved = 0
        kiteThreat = 0
        kiteThreatDistance = 2147483647
        kiteTargetKind = 0
        kiteIndex = 0
        while kiteIndex < objectCount()
          if objectTeam(kiteIndex) <> selfTeam and objectHp(kiteIndex) > 0 then
            kiteKind = objectKind(kiteIndex)
            if objectId(kiteIndex) = bestId then
              kiteTargetKind = kiteKind
            end if
            if kiteKind = 2 or kiteKind = 3 or kiteKind = 4 then
              kiteDx = selfX - objectX(kiteIndex)
              kiteDy = selfY - objectY(kiteIndex)
              kiteDistance = kiteDx * kiteDx + kiteDy * kiteDy
              if kiteDistance < kiteThreatDistance then
                kiteThreatDistance = kiteDistance
                kiteThreat = objectId(kiteIndex)
                kiteThreatX = objectX(kiteIndex)
                kiteThreatY = objectY(kiteIndex)
              end if
            end if
          end if
          kiteIndex = kiteIndex + 1
        wend
        if worldTick <> kiteLastTick + 1 or bestId <> kiteLastTarget or selfX <> kiteLastX or selfY <> kiteLastY then
          kiteStillTicks = 0
        end if
        if worldTick <> kiteLastTick + 1 then
          kiteUntil = 0
          kiteReady = 0
        end if
        if bestId = 0 then
          kiteStillTicks = 0
          kiteUntil = 0
        end if
        kiteRanged = 0
        if selfClass = 1 or selfClass = 2 or selfClass = 3 or selfClass = 6 or selfClass = 7 or selfClass = 8 then
          kiteRanged = 1
        end if
        kiteTrigger = 0
        if bestId <> 0 and kiteThreat <> 0 and worldTick >= kiteReady then
          if selfHp * 100 < selfMaxHp * param_critical_percent and kiteThreatDistance <= 36 and selfHp < kiteLastHp then
            kiteTrigger = 2
          end if
          if kiteTrigger = 0 and kiteRanged and (kiteTargetKind = 2 or kiteTargetKind = 3) and kiteStillTicks >= param_burst_ticks and kiteThreatDistance <= param_threat_tiles * param_threat_tiles then
            kiteTrigger = 1
          end if
        end if
        if kiteTrigger <> 0 then
          kiteUntil = worldTick + param_retreat_ticks
          kiteReady = kiteUntil + param_burst_ticks
          kiteBursts = kiteBursts + 1
          if kiteTrigger = 2 then
            kiteEscapes = kiteEscapes + 1
          end if
        end if
        if bestId <> 0 and kiteThreat <> 0 and worldTick < kiteUntil then
          kiteDx = selfX - kiteThreatX
          kiteDy = selfY - kiteThreatY
          if kiteDx = 0 and kiteDy = 0 then
            kiteDx = 1
            kiteDy = 1
            if selfTeam = 0 then
              kiteDx = 0 - kiteDx
              kiteDy = 0 - kiteDy
            end if
          end if
          kiteAx = kiteDx
          kiteAy = kiteDy
          if kiteAx < 0 then
            kiteAx = 0 - kiteAx
          end if
          if kiteAy < 0 then
            kiteAy = 0 - kiteAy
          end if
          kiteScale = kiteAx
          if kiteAy > kiteScale then
            kiteScale = kiteAy
          end if
          kiteX = selfX + kiteDx * param_step_tiles / kiteScale
          kiteY = selfY + kiteDy * param_step_tiles / kiteScale
          if terrainWalkable(kiteX, kiteY) = 0 then
            if terrainWalkable(kiteX, selfY) then
              kiteY = selfY
            else
              kiteX = selfX
            end if
          end if
          if (kiteX <> selfX or kiteY <> selfY) and terrainWalkable(kiteX, kiteY) then
            kiteMoved = walkTo(kiteX, kiteY)
          end if
          if kiteMoved then
            kiteMoveTicks = kiteMoveTicks + 1
          else
            kiteUntil = 0
          end if
        end if
        if bestId <> 0 and kiteMoved = 0 then
          attackTarget(bestId)
          kiteStillTicks = kiteStillTicks + 1
        else
          kiteStillTicks = 0
        end if
        kiteLastTick = worldTick
        kiteLastTarget = bestId
        kiteLastX = selfX
        kiteLastY = selfY
        kiteLastHp = selfHp
    """, {"burst_ticks": (18, 16, 48), "retreat_ticks": (10, 1, 32),
           "critical_percent": (35, 1, 70), "threat_tiles": (3, 1, 5),
           "step_tiles": (3, 1, 5)}, ["candidate"], [], ["attackTarget", "walkTo"],
        "Replace unconditional pursuit with timed bursts: ranged classes only step away from a "
        "nearby observed mobile threat after burst_ticks consecutive stationary target decisions; "
        "all classes may escape when low HP is falling near a threat, including protected towers. "
        "Use a bounded retreat and mandatory attack interval before another retreat. Walkable "
        "destinations point away from the nearest threat; failed movement restores attack intent. "
        "Timing is an inference from stationary tile observations, not proof of a landed hit. "
        "Missing targets and decision gaps clear timing. Economy and no-target wave following remain separate.",
        ["kiteLastTick", "kiteLastTarget", "kiteLastX", "kiteLastY", "kiteLastHp",
         "kiteStillTicks", "kiteUntil", "kiteReady", "kiteBursts", "kiteEscapes", "kiteMoveTicks"]),
    "supported_objective_enemy": contract("""
        bestId = 0
        bestDistance = 2147483647
        index = 0
        while index < objectCount()
          if objectAlive(index) and objectTeam(index) <> selfTeam then
            dx = objectX(index) - selfX
            dy = objectY(index) - selfY
            distance = dx * dx + dy * dy
            if distance < bestDistance then
              bestDistance = distance
              bestId = objectId(index)
            end if
          end if
          index = index + 1
        wend
        nearestId = bestId
        siegeId = 0
        siegeRank = 2
        siegeDistance = 2147483647
        if selfHp * 100 >= selfMaxHp * param_health_percent then
          index = 0
          while index < objectCount()
            kind = objectKind(index)
            if (kind = 1 or kind = 4) and objectAlive(index) and objectTeam(index) <> selfTeam then
              dx = objectX(index) - selfX
              dy = objectY(index) - selfY
              distance = dx * dx + dy * dy
              if distance <= param_pursuit_tiles * param_pursuit_tiles then
                supported = 0
                supportIndex = 0
                while supportIndex < objectCount()
                  if objectKind(supportIndex) = 3 and objectTeam(supportIndex) = selfTeam and objectAlive(supportIndex) and objectHp(supportIndex) > 0 then
                    sx = objectX(supportIndex) - objectX(index)
                    sy = objectY(supportIndex) - objectY(index)
                    if sx * sx + sy * sy <= param_support_tiles * param_support_tiles then
                      supported = 1
                    end if
                  end if
                  supportIndex = supportIndex + 1
                wend
                if supported then
                  rank = 1
                  if kind = 1 then
                    rank = 0
                  end if
                  id = objectId(index)
                  if rank < siegeRank or (rank = siegeRank and (distance < siegeDistance or (distance = siegeDistance and id < siegeId))) then
                    siegeId = id
                    siegeRank = rank
                    siegeDistance = distance
                  end if
                end if
              end if
            end if
            index = index + 1
          wend
        end if
        if siegeId <> 0 then
          bestId = siegeId
          if bestId <> nearestId then
            siegeOverrides = siegeOverrides + 1
          end if
        end if
    """, {"health_percent": (60, 1, 100), "pursuit_tiles": (8, 1, 16),
           "support_tiles": (5, 1, 10)}, [], ["candidate"], [],
        "Start with the baseline nearest observed attackable enemy. At or above health_percent HP, "
        "prefer an exposed fort, then tower, within pursuit_tiles of self if a currently observed "
        "living allied footman is within support_tiles of that structure. Among equal structure "
        "kinds use squared self-distance, then stable ID. Revalidate every decision. Otherwise keep "
        "the nearest enemy. Support is spatial evidence, not proof of tanking, path reachability "
        "or safety. No hidden tower target is inspected. Count decisions that change the target.",
        ["siegeOverrides"]),
    "buy_ordered_loadout": contract(ordered_loadout_source(),
        {name+"_item": (item,5,20) for name,item in
         zip(["first","second","third","fourth","fifth"],[11,13,16,18,20])},
        [], [], ["buyItem"],
        "Scan live inventory; buy only the first missing item in the five-item ordered equipment plan, "
        "when an empty slot and enough starting gold exist. At most one equipment attempt per decision; "
        "the host enforces the remaining balance after earlier purchases. No class restriction. Five "
        "planned equipment items leave one slot for consumables; earlier consumables may still block gear.",
        ["loadoutPurchases"]),
    "count_decision": contract(
        "decisions = decisions + 1", {}, [], [], [],
        "Increment a diagnostic counter; it does not influence actions.", ["decisions"]),
    "nearest_enemy": contract("""
        bestId = 0
        bestDistance = 2147483647
        index = 0
        while index < objectCount()
          id = objectId(index)
          if objectAlive(index) and objectTeam(index) <> selfTeam then
            dx = objectX(index) - selfX
            dy = objectY(index) - selfY
            distance = dx * dx + dy * dy
            if distance < bestDistance then
              bestDistance = distance
              bestId = id
            end if
          end if
          index = index + 1
        wend
    """, {}, [], ["candidate"], [],
        "Nearest observed attackable enemy by squared tile distance; enumeration order breaks ties. "
        "objectAlive includes exposure for structures. Missing enemies are unobserved, not dead."),
    "attack_candidate": contract("attackTarget(bestId)", {}, ["candidate"], [], ["attackTarget"],
        "Request pursuit/attack of the current candidate; ignore acceptance; abilities are automatic."),
    "wave_enemy": contract("""
        chosenId = 0
        chosenDistance = 2147483647
        retained = 0
        escortX = 0
        escortY = 0
        index = 0
        while index < objectCount()
          if objectTeam(index) = selfTeam and objectHp(index) > 0 and objectAlive(index) then
            if objectKind(index) = 3 then
              id = objectId(index)
              dx = objectX(index) - selfX
              dy = objectY(index) - selfY
              distance = dx * dx + dy * dy
              choose = 0
              if id = escortId then
                choose = 1
                retained = 1
              end if
              if retained = 0 then
                if distance < chosenDistance or (distance = chosenDistance and id < chosenId) then
                  choose = 1
                end if
              end if
              if choose then
                chosenId = id
                chosenDistance = distance
                escortX = objectX(index)
                escortY = objectY(index)
              end if
            end if
          end if
          index = index + 1
        wend
        escortId = chosenId
        bestId = 0
        bestDistance = 2147483647
        bestRank = 3
        radiusSq = param_radius_tiles * param_radius_tiles
        index = 0
        while index < objectCount()
          id = objectId(index)
          if chosenId <> 0 and objectAlive(index) and objectTeam(index) <> selfTeam then
            dx = objectX(index) - escortX
            dy = objectY(index) - escortY
            distance = dx * dx + dy * dy
            if distance <= radiusSq then
              rank = 2
              if objectKind(index) = 2 then
                rank = 1
              end if
              if objectKind(index) = 3 then
                rank = 0
              end if
              better = 0
              if rank < bestRank then
                better = 1
              end if
              if rank = bestRank then
                if distance < bestDistance or (distance = bestDistance and id < bestId) then
                  better = 1
                end if
              end if
              if better then
                bestRank = rank
                bestDistance = distance
                bestId = id
              end if
            end if
          end if
          index = index + 1
        wend
    """, {"radius_tiles": (6, 1, 16)}, [], ["candidate"], [],
        "Retain a currently observed living allied footman, else nearest by squared self-distance then ID. "
        "Among attackable enemies within radius_tiles of that escort, prefer footman over hero over "
        "structure, then nearest to the escort, then stable ID. No escort means no candidate: a distant "
        "visible enemy is ignored. Structure exposure and visibility remain host predicates. This is a "
        "local-wave filter, not a claim that the escort absorbs tower fire or that the enemy is reachable.",
        ["escortId"]),
    "weighted_enemy": contract("""
        bestId = 0
        bestDistance = 2147483647
        index = 0
        while index < objectCount()
          id = objectId(index)
          if objectAlive(index) and objectTeam(index) <> selfTeam then
            dx = objectX(index) - selfX
            dy = objectY(index) - selfY
            distance = dx * dx + dy * dy
            priorityDistance = distance * param_footman_weight
            if objectKind(index) = 2 then
              priorityDistance = distance * param_hero_weight
            end if
            if objectKind(index) = 1 or objectKind(index) = 4 then
              priorityDistance = distance * param_structure_weight
            end if
            if priorityDistance < bestDistance then
              bestDistance = priorityDistance
              bestId = id
            end if
          end if
          index = index + 1
        wend
    """, {"hero_weight": (1, 1, 16), "footman_weight": (4, 1, 16),
            "structure_weight": (4, 1, 16)}, [], ["candidate"], [],
        "Choose the observed attackable enemy with minimum squared tile distance times its kind weight. "
        "Smaller weights increase priority; enumeration order breaks ties. All weights are positive. "
        "Structure exposure and visibility remain host predicates. This expresses target preference, "
        "not predicted damage, reachability, or a guarantee of winning the fight."),
    "consume_inventory": contract("""
        hasHeal = 0
        hasMana = 0
        hasPoison = 0
        hasGear = 0
        emptySlot = 0
        slot = 0
        while slot < 6
          id = itemId(slot)
          if id = 0 then
            emptySlot = 1
          end if
          if id = 1 then
            hasHeal = 1
          end if
          if id = 2 then
            hasHeal = 1
          end if
          if id = 3 then
            hasMana = 1
          end if
          if id = 4 then
            hasPoison = 1
          end if
          if id > 4 then
            hasGear = 1
          end if
          if id = 1 or id = 2 then
            if selfHp * param_heal_denominator < selfMaxHp * param_heal_numerator then
              useItem(slot)
            end if
          end if
          if id = 3 then
            if selfMana * param_mana_denominator < selfMaxMana * param_mana_numerator then
              useItem(slot)
            end if
          end if
          if id = 4 then
            if bestId <> 0 then
              useItem(slot)
            end if
          end if
          slot = slot + 1
        wend
    """, {"heal_denominator": (5, 1, 100), "heal_numerator": (3, 0, 100),
            "mana_denominator": (5, 1, 100), "mana_numerator": (2, 0, 100)},
        ["candidate"], ["inventory"], ["useItem"],
        "Scan slots in order, set presence before use, consume below strict HP/mana ratios or poison "
        "with a candidate. Self snapshots and earlier presence flags are not refreshed; ignore returns."),
    "buy_consumables": contract(consumable_source(poison=True), {}, ["candidate", "inventory"], [], ["buyItem"],
        "Ordered independent sustain/poison purchase attempts against starting gold and scan flags. "
        "No local budget refresh; engine checks each purchase against the live balance."),
    "buy_sustain_only": contract(consumable_source(poison=False), {}, ["inventory"], [], ["buyItem"],
        "Buy healing below half HP and mana below half mana, using baseline order and snapshot flags. "
        "Make no poison purchase attempt, leaving that spending available for later equipment. "
        "Engine checks live balances; equipment acquisition and improved wins are hypotheses, not guarantees."),
    "buy_hp_investment": contract(hp_investment_source(),
        {"hp_numerator": (1,0,100), "hp_denominator": (2,1,100)}, ["inventory"], [], ["buyItem"],
        "Below the declared starting-HP ratio and without healing in the earlier scan, check live "
        "inventory for space and missing HP gear. Try helmet, buckler, then amulet; stop this "
        "investment phase after one accepted purchase. Then run unchanged sustain-only buying "
        "and later ordinary equipment rules. Starting HP/gold and earlier flags are not refreshed. "
        "HP gear grants current HP as well as maximum HP, but spends gold and permanent slots "
        "that could fund consumables or class weapons. Counters measure accepted investments.",
        ["hpGearInvestments", "hpGearGrantedHp"]),
    "buy_single_heal": contract("""
        if selfHp * 2 < selfMaxHp then
          if hasHeal = 0 then
            healBought = 0
            if selfGold >= 50 then
              healBought = buyItem(2)
            end if
            if healBought = 0 and selfGold >= 30 then
              healBought = buyItem(1)
            end if
          end if
        end if
        if selfMaxMana > 0 then
          if selfMana * 2 < selfMaxMana then
            if hasMana = 0 then
              if selfGold >= 45 then
                buyItem(3)
              end if
            end if
          end if
        end if
    """, {}, ["inventory"], [], ["buyItem"],
        "Keep sustain-only thresholds and mana buying. Below half HP without a healing item, "
        "try the elixir, then attempt a ration only if the elixir purchase was not accepted. "
        "At most one healing purchase succeeds per decision; no poison purchase. "
        "This trades immediate healing stock for gold and inventory capacity."),
    "buy_equipment": contract(equipment_source(), {}, ["inventory"], [], ["buyItem"],
        "Class-group ordered baseline equipment attempts, initial item only without gear, then buckler "
        "and amulet. Starting gold governs all attempts; engine rejects duplicates/overspending."),
    "buy_equipment_reserved": contract(reserved_equipment_source(),
        {"equipment_cap": (4, 1, 5)}, ["inventory"], [], ["buyItem"],
        "Preserve baseline equipment order and affordability guards, but limit permanent gear "
        "to the declared cap. Count existing gear and increment only for accepted purchases "
        "within this decision. Remaining slots may hold consumables; fewer gear stats and "
        "blocked mana/healing by other consumables remain possible. No selling or replacement."),
    "walk_point": contract("walkTo(param_x, param_y)", {"x": (64, 0, 127), "y": (64, 0, 127)},
        [], [], ["walkTo"], "Request movement to the fixed tile destination; ignore acceptance."),
    "join_wave": contract("""
        chosenId = 0
        chosenDistance = 2147483647
        retained = 0
        homeX = param_fallback_x
        homeY = param_fallback_y
        index = 0
        while index < objectCount()
          if objectTeam(index) = selfTeam and objectHp(index) > 0 and objectAlive(index) then
            if objectKind(index) = 1 then
              homeX = objectX(index)
              homeY = objectY(index)
            end if
            if objectKind(index) = 3 then
              id = objectId(index)
              dx = objectX(index) - selfX
              dy = objectY(index) - selfY
              distance = dx * dx + dy * dy
              choose = 0
              if id = escortId then
                choose = 1
                retained = 1
              end if
              if retained = 0 then
                if distance < chosenDistance or (distance = chosenDistance and id < chosenId) then
                  choose = 1
                end if
              end if
              if choose then
                chosenId = id
                chosenDistance = distance
                escortX = objectX(index)
                escortY = objectY(index)
              end if
            end if
          end if
          index = index + 1
        wend
        if selfX <> lastJoinX or selfY <> lastJoinY or worldTick <> lastJoinTick + 1 then
          stalled = 0
        end if
        if chosenId <> escortId then
          stalled = 0
        end if
        stalled = stalled + 1
        escortId = chosenId
        moveX = param_fallback_x
        moveY = param_fallback_y
        if escortId <> 0 then
          dx = homeX - escortX
          dy = homeY - escortY
          ax = dx
          ay = dy
          if ax < 0 then
            ax = 0 - ax
          end if
          if ay < 0 then
            ay = 0 - ay
          end if
          scale = ax
          if ay > scale then
            scale = ay
          end if
          moveX = escortX
          moveY = escortY
          if scale > param_offset_tiles then
            moveX = escortX + dx * param_offset_tiles / scale
            moveY = escortY + dy * param_offset_tiles / scale
          else
            moveX = homeX
            moveY = homeY
          end if
        end if
        if stalled >= param_stall_decisions then
          escortId = 0
          stalled = 0
          moveX = param_fallback_x
          moveY = param_fallback_y
        end if
        moveAccepted = walkTo(moveX, moveY)
        if moveAccepted = 0 then
          escortId = 0
          moveAccepted = walkTo(param_fallback_x, param_fallback_y)
        end if
        lastJoinX = selfX
        lastJoinY = selfY
        lastJoinTick = worldTick
    """, {"offset_tiles": (2, 0, 8), "stall_decisions": (48, 2, 240),
            "fallback_x": (64, 0, 127), "fallback_y": (64, 0, 127)},
        [], [], ["walkTo"],
        "Retain a currently observed living allied footman, else nearest by squared distance then ID. "
        "Walk offset tiles toward own living fort using max-axis normalization and truncating integer "
        "division. Without an escort use the fallback point. Clear commitment and use fallback on "
        "rejected movement or consecutive no-progress join decisions. No claim of tower protection.",
        ["escortId", "lastJoinX", "lastJoinY", "lastJoinTick", "stalled"]),
}

recovery_scan = CONTRACTS["weighted_enemy"].template.replace(
    "if objectAlive(index) and objectTeam(index) <> selfTeam then",
    "if objectAlive(index) and objectTeam(index) <> selfTeam and (id <> blockedId or worldTick >= blockedUntil) then",
).replace("bestId = id", "bestId = id\n      bestHp = objectHp(index)")

CONTRACTS["weighted_enemy_recovery"] = contract(dedent("""
    oldPursuitId = pursuitId
    pursuitSeen = 0
    currentPursuitHp = 0
    index = 0
    while index < objectCount()
      if objectId(index) = pursuitId and objectAlive(index) and objectTeam(index) <> selfTeam then
        pursuitSeen = 1
        currentPursuitHp = objectHp(index)
      end if
      index = index + 1
    wend
    if pursuitSeen and worldTick = pursuitTick + 1 and selfX = pursuitX and selfY = pursuitY and currentPursuitHp = pursuitHp then
      pursuitStalled = pursuitStalled + 1
    else
      pursuitStalled = 0
    end if
    if pursuitStalled >= param_stall_ticks then
      blockedId = pursuitId
      blockedUntil = worldTick + param_ignore_ticks
      recoveryActivations = recoveryActivations + 1
      pursuitStalled = 0
    end if
    bestHp = 0
""").strip() + "\n" + recovery_scan + "\n" + dedent("""
    if bestId <> oldPursuitId then
      pursuitStalled = 0
    end if
    pursuitId = bestId
    pursuitHp = bestHp
    pursuitX = selfX
    pursuitY = selfY
    pursuitTick = worldTick
""").strip(),
    {**CONTRACTS["weighted_enemy"].parameters,
     "stall_ticks": (72, 2, 240), "ignore_ticks": (240, 24, 1200)},
    [], ["candidate"], [],
    "Weighted enemy selection with a bounded pursuit exclusion. After consecutive observed ticks "
    "with the same target HP and self tile, temporarily exclude that target and select again. "
    "Movement, changed target HP, missing/ineligible target, target switch, or a tick gap resets "
    "the progress counter. Only one excluded ID is retained, until its deadline. "
    "Unchanged tile/HP is a progress proxy, not proof of obstruction or attack failure. "
    "If all eligible targets are excluded the existing no-candidate fallback applies.",
    ["pursuitId", "pursuitHp", "pursuitX", "pursuitY", "pursuitTick", "pursuitStalled",
     "blockedId", "blockedUntil", "recoveryActivations"])

PREDICATES = {
    "always": (None, (), "Every host decision."),
    "candidate_exists": ("bestId <> 0", ("candidate",), "The current scan selected an observed attackable enemy."),
    "no_candidate": ("bestId = 0", ("candidate",), "No candidate was observed; no assertion about unseen enemies."),
    "inventory_has_empty": ("emptySlot <> 0", ("inventory",), "An empty slot was seen during the earlier inventory scan."),
}


# Combat-event observations were first published in 2026.9.15.3.
from kiting_contract import confirmed_hit_contract
CONTRACTS["confirmed_hit_kite"] = confirmed_hit_contract(CONTRACTS["burst_kite"])

from kiting_contract import targeted_hit_contract
CONTRACTS["targeted_hit_kite"] = targeted_hit_contract(CONTRACTS["confirmed_hit_kite"])
from kiting_contract import spell_hit_contract
CONTRACTS['spell_hit_kite'] = spell_hit_contract(CONTRACTS['confirmed_hit_kite'])

from motion_contract import motion_contract, tower_contract, ranged_weapon_contract
CONTRACTS['motion_feedback'] = motion_contract(contract)
CONTRACTS['tower_detour'] = tower_contract(contract)
CONTRACTS['ranged_weapon_start'] = ranged_weapon_contract(contract, equipment_source)
PREDICATES['no_candidate_no_motion'] = ('bestId = 0 and motionActive = 0', ('candidate','motion'),
    'No observed attackable candidate and no accepted retreat movement in this decision.')
PREDICATES['no_motion'] = ('motionActive = 0', ('motion',), 'The retreat controller did not move this decision.')

from opportunity_contract import opportunity_contract
CONTRACTS['opportunity_enemy'] = opportunity_contract(contract)

from cadence_contract import cadence_contract
CONTRACTS['cadence_motion'] = cadence_contract(CONTRACTS['motion_feedback'])
