' Generated from gota_ordered_loadout_20260915; gota-semantic-policy/1; gota-basic/1
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

' @rule E2
if emptySlot <> 0 then
  ownsfirst = 0
  ownssecond = 0
  ownsthird = 0
  ownsfourth = 0
  ownsfifth = 0
  loadoutSpace = 0
  loadoutSlot = 0
  while loadoutSlot < 6
    loadoutItem = itemId(loadoutSlot)
    if loadoutItem = 0 then
      loadoutSpace = 1
    end if
    if loadoutItem = 11 then
      ownsfirst = 1
    end if
    if loadoutItem = 13 then
      ownssecond = 1
    end if
    if loadoutItem = 16 then
      ownsthird = 1
    end if
    if loadoutItem = 18 then
      ownsfourth = 1
    end if
    if loadoutItem = 20 then
      ownsfifth = 1
    end if
    loadoutSlot = loadoutSlot + 1
  wend
  loadoutNext = 0
  if loadoutNext = 0 and ownsfirst = 0 then
    loadoutNext = 11
  end if
  if loadoutNext = 0 and ownssecond = 0 then
    loadoutNext = 13
  end if
  if loadoutNext = 0 and ownsthird = 0 then
    loadoutNext = 16
  end if
  if loadoutNext = 0 and ownsfourth = 0 then
    loadoutNext = 18
  end if
  if loadoutNext = 0 and ownsfifth = 0 then
    loadoutNext = 20
  end if
  loadoutPrice = 2147483647
  if loadoutNext = 5 then
    loadoutPrice = 80
  end if
  if loadoutNext = 6 then
    loadoutPrice = 90
  end if
  if loadoutNext = 7 then
    loadoutPrice = 70
  end if
  if loadoutNext = 8 then
    loadoutPrice = 100
  end if
  if loadoutNext = 9 then
    loadoutPrice = 120
  end if
  if loadoutNext = 10 then
    loadoutPrice = 120
  end if
  if loadoutNext = 11 then
    loadoutPrice = 110
  end if
  if loadoutNext = 12 then
    loadoutPrice = 140
  end if
  if loadoutNext = 13 then
    loadoutPrice = 150
  end if
  if loadoutNext = 14 then
    loadoutPrice = 150
  end if
  if loadoutNext = 15 then
    loadoutPrice = 140
  end if
  if loadoutNext = 16 then
    loadoutPrice = 160
  end if
  if loadoutNext = 17 then
    loadoutPrice = 170
  end if
  if loadoutNext = 18 then
    loadoutPrice = 180
  end if
  if loadoutNext = 19 then
    loadoutPrice = 180
  end if
  if loadoutNext = 20 then
    loadoutPrice = 190
  end if
  if loadoutSpace <> 0 and selfGold >= loadoutPrice then
    loadoutBought = buyItem(loadoutNext)
    if loadoutBought <> 0 then
      loadoutPurchases = loadoutPurchases + 1
    end if
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
    if scale > 0 then
      moveX = escortX + dx * 0 / scale
      moveY = escortY + dy * 0 / scale
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
