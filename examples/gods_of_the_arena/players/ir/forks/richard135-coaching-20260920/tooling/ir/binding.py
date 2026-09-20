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
GAME_VERSIONS = ("2026.9.9.4", "2026.9.10.1", GAME_VERSION, "2026.9.15.1", "2026.9.15.2", "2026.9.15.3", "2026.9.16.2", "2026.9.16.3", "2026.9.16.5")


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

from building_contract import building_contract
CONTRACTS['building_enemy'] = building_contract(contract)

from class_release_contract import class_cadence, class_building, class_building_two
CONTRACTS['class_cadence'] = class_cadence(CONTRACTS['cadence_motion'])
CONTRACTS['class_building'] = class_building(contract, CONTRACTS['building_enemy'], CONTRACTS['nearest_enemy'])
CONTRACTS['class_building_two'] = class_building_two(CONTRACTS['class_building'])

from macro_contract import bounded_pursuit, objectives, lanes
CONTRACTS['bounded_pursuit'] = bounded_pursuit(CONTRACTS['class_building_two'])
CONTRACTS['macro_objectives'] = objectives(contract)
CONTRACTS['macro_lanes'] = lanes(contract)
from macro_contract import budgeted_cadence
CONTRACTS['macro_cadence'] = budgeted_cadence(CONTRACTS['class_cadence'])

from rush_contract import objective as rush_objective, route as rush_route
CONTRACTS['rush_objective'] = rush_objective(contract)
CONTRACTS['rush_route'] = rush_route(contract)

from coached_contract import observe as coached_observe, navigate as coached_navigate
CONTRACTS['coached_lane'] = coached_observe(contract)
CONTRACTS['coached_route'] = coached_navigate(CONTRACTS['rush_route'])
from coached_contract import blocker_revision
CONTRACTS['coached_blockers'] = blocker_revision(CONTRACTS['coached_lane'])
from coached_contract import ranged_revision
CONTRACTS['coached_ranged'] = ranged_revision(CONTRACTS['coached_blockers'])
from coached_contract import focus_revision
CONTRACTS['coached_focus'] = focus_revision(CONTRACTS['coached_ranged'])
from coached_contract import guards_revision
CONTRACTS['coached_guards'] = guards_revision(CONTRACTS['coached_focus'])
from coached_contract import convoy_revision
CONTRACTS['coached_convoy'] = convoy_revision(CONTRACTS['coached_guards'])
from coached_contract import defense_revision, recovery_revision
CONTRACTS['coached_defense'] = defense_revision(CONTRACTS['coached_convoy'])
CONTRACTS['coached_recovery'] = recovery_revision(CONTRACTS['macro_cadence'])
from coached_contract import strike_revision
CONTRACTS['coached_strike'] = strike_revision(CONTRACTS['coached_defense'])
from coached_lich_contract import branch as lich_branch
CONTRACTS['lich_lane_route'] = lich_branch(contract,CONTRACTS['rush_route'],CONTRACTS['join_wave'])
CONTRACTS['lich_guard_observe'] = lich_branch(contract,CONTRACTS['coached_guards'],CONTRACTS['bounded_pursuit'])
CONTRACTS['lich_convoy_observe'] = lich_branch(contract,CONTRACTS['coached_convoy'],CONTRACTS['bounded_pursuit'])
CONTRACTS['lich_push_route'] = lich_branch(contract,CONTRACTS['coached_route'],CONTRACTS['join_wave'])
from coached_finish_contract import finish as coached_finish
CONTRACTS['coached_finish'] = coached_finish(CONTRACTS['bounded_pursuit'])
from coached_loadout_contract import selective as selective_loadout
CONTRACTS['selective_loadout'] = selective_loadout(contract, CONTRACTS['buy_ordered_loadout'], CONTRACTS['ranged_weapon_start'])
from rush_defense_contract import observer as rush_defense_observer, navigation as rush_defense_navigation
CONTRACTS['rush_defense'] = rush_defense_observer(contract, CONTRACTS['bounded_pursuit'])
CONTRACTS['defend_or_wave'] = rush_defense_navigation(contract, CONTRACTS['join_wave'])
from rush_defense_contract import bounded_observer as bounded_rush_observer
CONTRACTS['rush_defense_v2'] = bounded_rush_observer(contract, CONTRACTS['bounded_pursuit'])
from rush_defense_contract import persistent_observer as persistent_rush_observer
CONTRACTS['rush_defense_v3'] = persistent_rush_observer(contract, CONTRACTS['bounded_pursuit'])
from rush_defense_contract import lineup_observer, defense_cadence
CONTRACTS['rush_defense_v4'] = lineup_observer(contract, CONTRACTS['bounded_pursuit'])
CONTRACTS['defense_cadence'] = defense_cadence(CONTRACTS['macro_cadence'])
from rush_defense_contract import defensive_recovery
CONTRACTS['defensive_recovery'] = defensive_recovery(CONTRACTS['defense_cadence'])
from rush_defense_contract import opening_guard
CONTRACTS['opening_guard'] = opening_guard(CONTRACTS['defend_or_wave'])
from rush_defense_contract import sentry_observer
CONTRACTS['rush_sentries'] = sentry_observer(contract, CONTRACTS['bounded_pursuit'])
from rush_defense_contract import core_wave_observer, spread_navigation, released_defense, reachable_core_defense
from rush_defense_contract import fused_core_defense, solo_base_defense, assigned_solo_defense
from rush_defense_contract import protected_solo_defense, nearby_solo_defense
CONTRACTS['core_wave_defense'] = core_wave_observer(contract, CONTRACTS['bounded_pursuit'])
CONTRACTS['spread_defense'] = spread_navigation(CONTRACTS['defend_or_wave'])
CONTRACTS['released_defense'] = released_defense(CONTRACTS['core_wave_defense'])
CONTRACTS['reachable_core_defense'] = reachable_core_defense(CONTRACTS['core_wave_defense'])
CONTRACTS['released_reachable_defense'] = released_defense(CONTRACTS['reachable_core_defense'])
CONTRACTS['released_sentry_defense'] = released_defense(CONTRACTS['rush_sentries'], has_core=False)
CONTRACTS['fused_core_defense'] = fused_core_defense(CONTRACTS['rush_sentries'])
CONTRACTS['solo_base_defense'] = solo_base_defense(CONTRACTS['fused_core_defense'])
CONTRACTS['assigned_solo_defense'] = assigned_solo_defense(CONTRACTS['solo_base_defense'])
CONTRACTS['protected_solo_defense'] = protected_solo_defense(CONTRACTS['solo_base_defense'])
CONTRACTS['protected_assigned_defense'] = protected_solo_defense(CONTRACTS['assigned_solo_defense'])
CONTRACTS['protected_near_defense'] = nearby_solo_defense(CONTRACTS['protected_solo_defense'])
from rush_defense_contract import isolated_solo_defense
CONTRACTS['isolated_solo_defense'] = isolated_solo_defense(CONTRACTS['protected_solo_defense'])
CONTRACTS['isolated_assigned_defense'] = isolated_solo_defense(CONTRACTS['protected_assigned_defense'])
CONTRACTS['isolated_near_defense'] = isolated_solo_defense(CONTRACTS['protected_near_defense'])
from rush_defense_contract import blue_solo_defense
CONTRACTS['blue_isolated_assigned'] = blue_solo_defense(CONTRACTS['isolated_assigned_defense'])
from rush_defense_contract import blue_warning_defense
CONTRACTS['blue_warning_defense'] = blue_warning_defense(CONTRACTS['blue_isolated_assigned'])

from root_defense_contract import perimeter_observer, forward_navigation
CONTRACTS['objective_perimeter'] = perimeter_observer(CONTRACTS['blue_isolated_assigned'])
CONTRACTS['forward_perimeter'] = forward_navigation(CONTRACTS['spread_defense'])

from lineup_contract import split as split_lineup
CONTRACTS['lineup_perimeter_observe'] = split_lineup(contract, CONTRACTS['rush_sentries'], CONTRACTS['objective_perimeter'])
CONTRACTS['lineup_perimeter_route'] = split_lineup(contract, CONTRACTS['defend_or_wave'], CONTRACTS['forward_perimeter'])
from middle_rush_contract import early_middle
CONTRACTS['lineup_middle_rush'] = split_lineup(contract, CONTRACTS['rush_sentries'], early_middle(CONTRACTS['objective_perimeter']))
from anchor_liveness_contract import live_anchor, reachable_core
from rolling_core_contract import rolling_core
CONTRACTS['lineup_live_anchor'] = split_lineup(contract, live_anchor(CONTRACTS['rush_sentries']), early_middle(CONTRACTS['objective_perimeter']))
CONTRACTS['lineup_live_anchor_core'] = split_lineup(contract, reachable_core(live_anchor(CONTRACTS['rush_sentries']), rolling_core), early_middle(CONTRACTS['objective_perimeter']))

from arrival_defense_contract import arrival_observer
CONTRACTS['lineup_arrival_observe'] = split_lineup(contract, CONTRACTS['rush_sentries'], arrival_observer(CONTRACTS['objective_perimeter']))
from paired_siege_contract import paired_siege
CONTRACTS['lineup_paired_siege'] = split_lineup(contract, CONTRACTS['rush_sentries'], arrival_observer(paired_siege(early_middle(CONTRACTS['objective_perimeter']))))
CONTRACTS['lineup_paired_legacy'] = split_lineup(contract, CONTRACTS['rush_sentries'], paired_siege(early_middle(CONTRACTS['objective_perimeter'])))
from watch_defense_contract import watch_defense, quiet_watch, protected_watch
CONTRACTS['lineup_watch_defense'] = split_lineup(contract, watch_defense(CONTRACTS['rush_sentries']), paired_siege(early_middle(CONTRACTS['objective_perimeter'])))
CONTRACTS['lineup_quiet_watch'] = split_lineup(contract, quiet_watch(CONTRACTS['rush_sentries']), paired_siege(early_middle(CONTRACTS['objective_perimeter'])))
CONTRACTS['lineup_protected_watch'] = split_lineup(contract, protected_watch(CONTRACTS['rush_sentries']), paired_siege(early_middle(CONTRACTS['objective_perimeter'])))
from coach_split_contract import observe as coached_split, navigate as coached_center
CONTRACTS['lineup_coached_split'] = split_lineup(contract, coached_split(CONTRACTS['rush_sentries']), paired_siege(early_middle(CONTRACTS['objective_perimeter'])))
CONTRACTS['lineup_coached_center'] = split_lineup(contract, coached_center(CONTRACTS['defend_or_wave'], CONTRACTS['rush_route']), CONTRACTS['forward_perimeter'])
from coach_split_contract import assembled as coached_assembled
CONTRACTS['lineup_coached_assembled'] = split_lineup(contract, coached_assembled(coached_split(CONTRACTS['rush_sentries'])), paired_siege(early_middle(CONTRACTS['objective_perimeter'])))
from coach_split_contract import mobile as coached_mobile
CONTRACTS['lineup_coached_mobile'] = split_lineup(contract, coached_mobile(coached_assembled(coached_split(CONTRACTS['rush_sentries']))), paired_siege(early_middle(CONTRACTS['objective_perimeter'])))
from scoped_pair_contract import scoped_pair
from autoresearch_wave_v1 import wave_observer as ar_wave_v1, outer_observer as ar_outer_v1, outer_navigation as ar_outer_nav_v1
_ar_mobile_v1 = coached_mobile(coached_assembled(coached_split(CONTRACTS['rush_sentries'])))
_ar_blue_v1 = paired_siege(early_middle(CONTRACTS['objective_perimeter']))
CONTRACTS['lineup_autowave_v1'] = split_lineup(contract, ar_wave_v1(_ar_mobile_v1), _ar_blue_v1)
CONTRACTS['lineup_autoouter_v1'] = split_lineup(contract, ar_outer_v1(_ar_mobile_v1), _ar_blue_v1)
CONTRACTS['lineup_autoouter_route_v1'] = split_lineup(contract, ar_outer_nav_v1(CONTRACTS['defend_or_wave'], CONTRACTS['rush_route']), CONTRACTS['forward_perimeter'])
from autoresearch_damage_v1 import damaged_pair as ar_damage_v1
CONTRACTS['lineup_red_damage_v1'] = split_lineup(contract, ar_damage_v1(CONTRACTS['rush_sentries']), _ar_blue_v1)
CONTRACTS['lineup_raid_wave_v2'] = split_lineup(contract, ar_damage_v1(ar_wave_v1(_ar_mobile_v1)), _ar_blue_v1)
from autoresearch_rankraid_v1 import ranked_raid as ar_rankraid_v1
CONTRACTS['lineup_red_rankraid_v1'] = split_lineup(contract, ar_rankraid_v1(ar_damage_v1(CONTRACTS['rush_sentries'])), _ar_blue_v1)
from autoresearch_nearraids_v1 import nearby_raid as ar_nearraids_v1
CONTRACTS['lineup_red_nearraids_v1'] = split_lineup(contract, ar_nearraids_v1(ar_rankraid_v1(ar_damage_v1(CONTRACTS['rush_sentries']))), _ar_blue_v1)
from autoresearch_role_raid_v1 import sentry_raid as ar_role_raid_v1
CONTRACTS['lineup_red_role_raid_v1'] = split_lineup(contract, ar_role_raid_v1(ar_nearraids_v1(ar_rankraid_v1(ar_damage_v1(CONTRACTS['rush_sentries'])))), _ar_blue_v1)
from autoresearch_melee_raid_v1 import melee_raid as ar_melee_raid_v1
CONTRACTS['lineup_red_melee_raid_v1'] = split_lineup(contract, ar_melee_raid_v1(ar_nearraids_v1(ar_rankraid_v1(ar_damage_v1(CONTRACTS['rush_sentries'])))), _ar_blue_v1)
CONTRACTS['lineup_paired_scoped'] = split_lineup(contract, CONTRACTS['rush_sentries'], scoped_pair(arrival_observer(paired_siege(early_middle(CONTRACTS['objective_perimeter'])))))

from pressure_defense_contract import pressure_observer
CONTRACTS['lineup_pressure_observe'] = split_lineup(contract, pressure_observer(CONTRACTS['rush_sentries']), CONTRACTS['objective_perimeter'])
CONTRACTS['lineup_coverage_observe'] = split_lineup(contract, pressure_observer(CONTRACTS['rush_sentries']), arrival_observer(CONTRACTS['objective_perimeter']))
from breach_defense_contract import breach_observer
CONTRACTS['lineup_breach_observe'] = split_lineup(contract, breach_observer(pressure_observer(CONTRACTS['rush_sentries'])), CONTRACTS['objective_perimeter'])
CONTRACTS['lineup_core_pressure_observe'] = split_lineup(contract, fused_core_defense(pressure_observer(CONTRACTS['rush_sentries'])), CONTRACTS['objective_perimeter'])
CONTRACTS['lineup_core_breach_observe'] = split_lineup(contract, fused_core_defense(breach_observer(pressure_observer(CONTRACTS['rush_sentries']))), CONTRACTS['objective_perimeter'])
from sentry_farm_contract import farm_observer
CONTRACTS['lineup_farm_core_observe'] = split_lineup(contract, farm_observer(fused_core_defense(pressure_observer(CONTRACTS['rush_sentries']))), CONTRACTS['objective_perimeter'])
from bounded_core_contract import bounded_targets
CONTRACTS['lineup_bounded_core_observe'] = split_lineup(contract, bounded_targets(fused_core_defense(pressure_observer(CONTRACTS['rush_sentries']))), CONTRACTS['objective_perimeter'])
CONTRACTS['lineup_bounded_farm_observe'] = split_lineup(contract, bounded_targets(farm_observer(fused_core_defense(pressure_observer(CONTRACTS['rush_sentries'])))), CONTRACTS['objective_perimeter'])
from mage_reserve_contract import mage_reserve
CONTRACTS['mage_reserve'] = mage_reserve(contract,CONTRACTS['selective_loadout'],CONTRACTS['buy_equipment_reserved'])
from warlock_cadence_contract import warlock_cadence
CONTRACTS['red_warlock_cadence'] = warlock_cadence(CONTRACTS['defense_cadence'])
from rolling_core_contract import rolling_core
CONTRACTS['lineup_rolling_creep_observe'] = split_lineup(contract, rolling_core(CONTRACTS['rush_sentries']), CONTRACTS['objective_perimeter'])
from counterpush_contract import counterpush
CONTRACTS['lineup_counterpush_observe'] = split_lineup(contract, counterpush(CONTRACTS['rush_sentries']), CONTRACTS['objective_perimeter'])
CONTRACTS['lineup_counterpush_route'] = split_lineup(contract, CONTRACTS['spread_defense'], CONTRACTS['forward_perimeter'])
from counterpush_contract import counterpush_visible
CONTRACTS['lineup_counterpush_observe_v2'] = split_lineup(contract, counterpush_visible(counterpush(CONTRACTS['rush_sentries'])), CONTRACTS['objective_perimeter'])
from victory_counterpush_contract import victory_counterpush
CONTRACTS['lineup_victory_observe'] = split_lineup(contract, victory_counterpush(CONTRACTS['rush_sentries']), CONTRACTS['objective_perimeter'])
from counterwatch_contract import counterwatch
CONTRACTS['lineup_counterwatch_observe'] = split_lineup(contract, counterwatch(victory_counterpush(CONTRACTS['rush_sentries'])), CONTRACTS['objective_perimeter'])
from shared_engagement_contract import shared_engagement
CONTRACTS['lineup_shared_engagement'] = split_lineup(contract, shared_engagement(pressure_observer(CONTRACTS['rush_sentries'])), CONTRACTS['objective_perimeter'])
from ally_assist_contract import ally_assist
CONTRACTS['lineup_ally_assist'] = split_lineup(contract, ally_assist(pressure_observer(CONTRACTS['rush_sentries'])), CONTRACTS['objective_perimeter'])
from ally_assist_contract import caster_assist
CONTRACTS['lineup_caster_assist'] = split_lineup(contract, caster_assist(ally_assist(pressure_observer(CONTRACTS['rush_sentries']))), CONTRACTS['objective_perimeter'])
from ally_assist_contract import caster_assist_bound
CONTRACTS['lineup_caster_assist_v2'] = split_lineup(contract, caster_assist_bound(caster_assist(ally_assist(pressure_observer(CONTRACTS['rush_sentries'])))), CONTRACTS['objective_perimeter'])
from supported_defense_contract import supported_defense
CONTRACTS['lineup_supported_defense'] = split_lineup(contract, supported_defense(caster_assist_bound(caster_assist(ally_assist(pressure_observer(CONTRACTS['rush_sentries']))))), CONTRACTS['objective_perimeter'])
from supported_defense_contract import reachable_support
CONTRACTS['lineup_reachable_support'] = split_lineup(contract, reachable_support(supported_defense(caster_assist_bound(caster_assist(ally_assist(pressure_observer(CONTRACTS['rush_sentries'])))))), CONTRACTS['objective_perimeter'])
from anchored_support_contract import anchored_support
CONTRACTS['lineup_anchored_support'] = split_lineup(contract, anchored_support(caster_assist_bound(caster_assist(ally_assist(pressure_observer(CONTRACTS['rush_sentries']))))), CONTRACTS['objective_perimeter'])
CONTRACTS['lineup_anchored_readiness'] = split_lineup(contract, anchored_support(reachable_support(supported_defense(caster_assist_bound(caster_assist(ally_assist(pressure_observer(CONTRACTS['rush_sentries']))))))), CONTRACTS['objective_perimeter'])
from post_defense_contract import post_defense
CONTRACTS['lineup_post_defense'] = split_lineup(contract, post_defense(anchored_support(caster_assist_bound(caster_assist(ally_assist(pressure_observer(CONTRACTS['rush_sentries'])))))), CONTRACTS['objective_perimeter'])

from post_defense_contract import arrived_post_defense
CONTRACTS['lineup_post_arrival'] = split_lineup(contract, arrived_post_defense(post_defense(anchored_support(caster_assist_bound(caster_assist(ally_assist(pressure_observer(CONTRACTS['rush_sentries']))))))), CONTRACTS['objective_perimeter'])

# Additive versioned economic contract; captured old contracts are unchanged.
from autoresearch_mana_alignment_v1 import aligned_purchase as ar_mana_purchase_v1
CONTRACTS['buy_mana_aligned_v1'] = ar_mana_purchase_v1(CONTRACTS['buy_sustain_only'])

from autoresearch_core_focus_v1 import core_focus as ar_core_focus_v1
CONTRACTS['lineup_red_core_focus_v1'] = split_lineup(contract, ar_core_focus_v1(CONTRACTS['rush_sentries']), _ar_blue_v1)
CONTRACTS['lineup_red_role_core_focus_v1'] = split_lineup(contract, ar_core_focus_v1(ar_role_raid_v1(ar_nearraids_v1(ar_rankraid_v1(ar_damage_v1(CONTRACTS['rush_sentries']))))), _ar_blue_v1)

from autoresearch_dense_cadence_v1 import dense_cadence as ar_dense_cadence_v1
CONTRACTS['dense_defense_cadence_v1'] = ar_dense_cadence_v1(CONTRACTS['defense_cadence'])

from autoresearch_guard_dense_v1 import guarded_dense as ar_guarded_dense_v1
CONTRACTS['guarded_dense_defense_cadence_v1'] = ar_guarded_dense_v1(CONTRACTS['dense_defense_cadence_v1'])

from autoresearch_weapon_dense_v1 import weapon_dense as ar_weapon_dense_v1
CONTRACTS['weapon_dense_defense_cadence_v1'] = ar_weapon_dense_v1(CONTRACTS['dense_defense_cadence_v1'])

from autoresearch_defense_phase_v1 import defense_phase as ar_defense_phase_v1
CONTRACTS['defense_phase_weapon_cadence_v1'] = ar_defense_phase_v1(CONTRACTS['weapon_dense_defense_cadence_v1'])

from autoresearch_readiness_v1 import readiness as ar_readiness_v1
CONTRACTS['first_level_weapon_cadence_v1'] = ar_readiness_v1(CONTRACTS['weapon_dense_defense_cadence_v1'])

from autoresearch_last_slot_axe_v1 import last_slot_axe as ar_last_slot_axe_v1
CONTRACTS['last_slot_melee_axe_v1'] = ar_last_slot_axe_v1(CONTRACTS['selective_loadout'])

from autoresearch_target_geometry_v1 import target_geometry as ar_target_geometry_v1
CONTRACTS['target_geometry_cadence_v1'] = ar_target_geometry_v1(CONTRACTS['first_level_weapon_cadence_v1'])

# New contract; captured target-geometry semantics remain unchanged.
from autoresearch_target_handoff_v1 import target_handoff as ar_target_handoff_v1
CONTRACTS['target_handoff_cadence_v1'] = ar_target_handoff_v1(CONTRACTS['target_geometry_cadence_v1'])

# Isolated hit readiness; existing captured contracts remain unchanged.
from autoresearch_hit_readiness_v1 import hit_readiness as ar_hit_readiness_v1
CONTRACTS["target_hit_readiness_v1"] = ar_hit_readiness_v1(CONTRACTS["target_geometry_cadence_v1"])

from autoresearch_inward_rally_v1 import inward_rally as ar_inward_rally_v1
CONTRACTS['lineup_inward_rally_v1'] = ar_inward_rally_v1(CONTRACTS['lineup_paired_legacy'])

from autoresearch_wave_work_v1 import compact_wave as ar_compact_wave_v1
CONTRACTS['lineup_compact_wave_v1'] = ar_compact_wave_v1(CONTRACTS['lineup_perimeter_route'])

from autoresearch_target_work_v1 import target_work as ar_target_work_v1
CONTRACTS['lineup_paired_target_work_v1'] = ar_target_work_v1(CONTRACTS['lineup_paired_legacy'])

from autoresearch_fused_wave_work_v1 import observe as ar_fused_wave_observe_v1, fallback as ar_fused_wave_fallback_v1
CONTRACTS['lineup_paired_fused_work_v1'] = ar_fused_wave_observe_v1(CONTRACTS['lineup_paired_target_work_v1'])
CONTRACTS['lineup_inward_fused_work_v1'] = ar_fused_wave_observe_v1(ar_target_work_v1(CONTRACTS['lineup_inward_rally_v1']))
CONTRACTS['lineup_fused_wave_route_v1'] = ar_fused_wave_fallback_v1(CONTRACTS['lineup_perimeter_route'])

from autoresearch_fused_wave_work_v2 import observe_v2 as ar_fused_wave_observe_v2
CONTRACTS['lineup_inward_fused_work_v2'] = ar_fused_wave_observe_v2(ar_target_work_v1(CONTRACTS['lineup_inward_rally_v1']))
