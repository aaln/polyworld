' Generated from gota_duelist_hp_investment; gota-semantic-policy/1; gota-basic/1
' @rule comments identify regions only; the extractor reads all executable statements.

' @rule R0
decisions = decisions + 1

' @rule R1
bestId = 0
bestDistance = 2147483647
index = 0
while index < objectCount()
  id = objectId(index)
  if objectAlive(index) and objectTeam(index) <> selfTeam then
    dx = objectX(index) - selfX
    dy = objectY(index) - selfY
    distance = dx * dx + dy * dy
    priorityDistance = distance * 4
    if objectKind(index) = 2 then
      priorityDistance = distance * 1
    end if
    if objectKind(index) = 1 or objectKind(index) = 4 then
      priorityDistance = distance * 4
    end if
    if priorityDistance < bestDistance then
      bestDistance = priorityDistance
      bestId = id
    end if
  end if
  index = index + 1
wend

' @rule R2
if bestId <> 0 then
  attackTarget(bestId)
end if

' @rule E0
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
    if selfHp * 5 < selfMaxHp * 3 then
      useItem(slot)
    end if
  end if
  if id = 3 then
    if selfMana * 5 < selfMaxMana * 2 then
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

' @rule E1
if selfHp * 2 < selfMaxHp * 1 then
  if hasHeal = 0 then
    hpHelmet = 0
    hpBuckler = 0
    hpAmulet = 0
    hpSpace = 0
    hpSlot = 0
    while hpSlot < 6
      hpItem = itemId(hpSlot)
      if hpItem = 0 then
        hpSpace = 1
      end if
      if hpItem = 5 then
        hpHelmet = 1
      end if
      if hpItem = 6 then
        hpBuckler = 1
      end if
      if hpItem = 9 then
        hpAmulet = 1
      end if
      hpSlot = hpSlot + 1
    wend
    hpGearBought = 0
    if hpSpace <> 0 then
      if hpGearBought = 0 and hpHelmet = 0 and selfGold >= 80 then
        hpGearBought = buyItem(5)
        if hpGearBought <> 0 then
          hpGearInvestments = hpGearInvestments + 1
          hpGearGrantedHp = hpGearGrantedHp + 50
        end if
      end if
      if hpGearBought = 0 and hpBuckler = 0 and selfGold >= 90 then
        hpGearBought = buyItem(6)
        if hpGearBought <> 0 then
          hpGearInvestments = hpGearInvestments + 1
          hpGearGrantedHp = hpGearGrantedHp + 60
        end if
      end if
      if hpGearBought = 0 and hpAmulet = 0 and selfGold >= 120 then
        hpGearBought = buyItem(9)
        if hpGearBought <> 0 then
          hpGearInvestments = hpGearInvestments + 1
          hpGearGrantedHp = hpGearGrantedHp + 70
        end if
      end if
    end if
  end if
end if
if selfHp * 2 < selfMaxHp then
  if hasHeal = 0 then
    if selfGold >= 50 then
      buyItem(2)
    end if
    if selfGold >= 30 then
      buyItem(1)
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

' @rule E2
if emptySlot <> 0 then
  melee = 0
  ranged = 0
  magic = 0
  if selfClass = 0 or selfClass = 4 or selfClass = 5 or selfClass = 9 then
    melee = 1
  end if
  if selfClass = 1 or selfClass = 6 then
    ranged = 1
  end if
  if selfClass = 2 or selfClass = 3 or selfClass = 7 or selfClass = 8 then
    magic = 1
  end if
  if melee = 1 then
    if hasGear = 0 then
      if selfGold >= 70 then
        buyItem(7)
      end if
    end if
    if selfGold >= 80 then
      buyItem(5)
    end if
    if selfGold >= 110 then
      buyItem(11)
    end if
    if selfGold >= 150 then
      buyItem(13)
    end if
    if selfGold >= 180 then
      buyItem(18)
    end if
  end if
  if ranged = 1 then
    if hasGear = 0 then
      if selfGold >= 100 then
        buyItem(8)
      end if
    end if
    if selfGold >= 150 then
      buyItem(14)
    end if
    if selfGold >= 180 then
      buyItem(19)
    end if
  end if
  if magic = 1 then
    if hasGear = 0 then
      if selfGold >= 140 then
        buyItem(12)
      end if
    end if
    if selfGold >= 120 then
      buyItem(10)
    end if
    if selfGold >= 170 then
      buyItem(17)
    end if
    if selfGold >= 190 then
      buyItem(20)
    end if
  end if
  if selfGold >= 90 then
    buyItem(6)
  end if
  if selfGold >= 120 then
    buyItem(9)
  end if
end if

' @rule R4
if bestId = 0 then
  walkTo(64, 64)
end if
