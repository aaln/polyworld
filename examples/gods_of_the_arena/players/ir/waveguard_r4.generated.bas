' Generated from gota_waveguard_r4_v1; gota-semantic-policy/1; gota-basic/1
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
    if distance < bestDistance then
      bestDistance = distance
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
if bestId <> 0 then
  if hasPoison = 0 then
    if selfGold >= 40 then
      buyItem(4)
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
  chosenId = 0
  chosenDistance = 2147483647
  retained = 0
  homeX = 64
  homeY = 64
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
  moveX = 64
  moveY = 64
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
    if scale > 2 then
      moveX = escortX + dx * 2 / scale
      moveY = escortY + dy * 2 / scale
    else
      moveX = homeX
      moveY = homeY
    end if
  end if
  if stalled >= 48 then
    escortId = 0
    stalled = 0
    moveX = 64
    moveY = 64
  end if
  moveAccepted = walkTo(moveX, moveY)
  if moveAccepted = 0 then
    escortId = 0
    moveAccepted = walkTo(64, 64)
  end if
  lastJoinX = selfX
  lastJoinY = selfY
  lastJoinTick = worldTick
end if
