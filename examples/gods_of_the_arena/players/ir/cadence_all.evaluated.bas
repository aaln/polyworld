' Generated from gota_cadence_cadence_all; gota-semantic-policy/1; gota-basic/1
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
motionActive = 0
kiteMoved = 0
kiteTrigger = 0
mNew = 0
if motionLastTick = 0 or worldTick <> motionLastTick + 1 then
  motionUntil = 0
  motionReady = 0
  motionLastHits = selfAttacksLanded
  motionLastHp = selfHp
  motionLoss = 0
end if
motionLoss = motionLoss * 23 / 24
if selfHp < motionLastHp then
  motionLoss = motionLoss + motionLastHp - selfHp
end if
mThreat = 0
mSecond = 0
mDistance = 2147483647
mSecondDistance = 2147483647
mTower = 0
mTowerDistance = 2147483647
mAlly = 0
mAllyDistance = 2147483647
mEnemies = 0
mAllies = 0
mAttackers = 0
mTracked = 0
mFacingX = 0
mFacingY = 0
mIndex = 0
while mIndex < objectCount()
  mId = objectId(mIndex)
  mKind = objectKind(mIndex)
  mX = objectX(mIndex)
  mY = objectY(mIndex)
  mDx = mX - selfX
  mDy = mY - selfY
  mD = mDx * mDx + mDy * mDy
  if mId = selfId then
    mFacingX = objectFacingX(mIndex)
    mFacingY = objectFacingY(mIndex)
  end if
  if objectHp(mIndex) > 0 then
    if mKind = 4 and mD < mTowerDistance then
      mTower = mId
      mTowerX = mX
      mTowerY = mY
      mTowerDistance = mD
    end if
    if objectTeam(mIndex) = selfTeam and mId <> selfId then
      if mKind = 2 or mKind = 3 then
        if mD <= 36 then
          mAllies = mAllies + 1
          if mKind = 2 then
            mAllies = mAllies + 2
          end if
        end if
        if mKind = 2 and mD < mAllyDistance then
          mAlly = mId
          mAllyX = mX
          mAllyY = mY
          mAllyDistance = mD
        end if
      end if
    end if
    if objectTeam(mIndex) <> selfTeam and (mKind = 2 or mKind = 3 or mKind = 4) then
      if mD <= 36 then
        mEnemies = mEnemies + 1
        if mKind = 2 then
          mEnemies = mEnemies + 2
        end if
        if objectTarget(mIndex) = selfId then
          mAttackers = mAttackers + 1
        end if
      end if
      if mId = motionThreat then
        mTracked = 1
        mTrackedX = mX
        mTrackedY = mY
      end if
      if 0 = 0 or objectTarget(mIndex) = selfId then
        if mD < mDistance then
          mSecond = mThreat
          mSecondX = mThreatX
          mSecondY = mThreatY
          mSecondDistance = mDistance
          mThreat = mId
          mThreatX = mX
          mThreatY = mY
          mDistance = mD
        else
          if mD < mSecondDistance then
            mSecond = mId
            mSecondX = mX
            mSecondY = mY
            mSecondDistance = mD
          end if
        end if
      end if
    end if
  end if
  mIndex = mIndex + 1
wend
if worldTick < motionUntil and worldTick >= motionStart + 12 then
  mSepX = selfX - mTrackedX
  mSepY = selfY - mTrackedY
  if mSepX < 0 then
    mSepX = -mSepX
  end if
  if mSepY < 0 then
    mSepY = -mSepY
  end if
  if mTracked = 0 or mSepX + mSepY >= motionStartSeparation + 2 then
    motionUntil = 0
    motionCompletions = motionCompletions + 1
    motionReady = worldTick + 8
  end if
end if
if worldTick >= motionUntil and worldTick >= motionReady and mThreat <> 0 then
  if 0 > 0 and mAttackers > 0 and mDistance <= 36 then
    if (selfHp * 100 < selfMaxHp * 0 and selfHp < motionLastHp) or selfHp < motionLoss * 3 then
      kiteTrigger = 2
    end if
  end if
  if kiteTrigger = 0 and 1 = 1 and bestId <> 0 and mDistance <= 7 * 7 then
    if 1 = 1 or selfClass = 1 or selfClass = 2 or selfClass = 3 or selfClass = 6 or selfClass = 7 or selfClass = 8 then
      if selfAttacksLanded > motionLastHits and selfAttackCooldown > 0 then
        kiteTrigger = 1
      end if
    end if
  end if
  if kiteTrigger > 0 then
    motionStart = worldTick
    motionUntil = worldTick + 64
    if kiteTrigger = 1 then
      motionUntil = worldTick + 1
      recoverySteps = recoverySteps + 1
    end if
    motionThreat = mThreat
    mSepX = selfX - mThreatX
    mSepY = selfY - mThreatY
    if mSepX < 0 then
      mSepX = -mSepX
    end if
    if mSepY < 0 then
      mSepY = -mSepY
    end if
    motionStartSeparation = mSepX + mSepY
    mNew = 1
    mBestScore = -2147483647
    mFound = 0
    mdirection = 0
    while mdirection < 8
        mDirX = 0
mDirY = 0
if mdirection = 0 or mdirection = 1 or mdirection = 7 then
  mDirX = 1
end if
if mdirection = 3 or mdirection = 4 or mdirection = 5 then
  mDirX = -1
end if
if mdirection = 1 or mdirection = 2 or mdirection = 3 then
  mDirY = 1
end if
if mdirection = 5 or mdirection = 6 or mdirection = 7 then
  mDirY = -1
end if
      mLegal = 1
      mStep = 1
      while mStep <= 3
        mTryX = selfX + mDirX * mStep
        mTryY = selfY + mDirY * mStep
        if terrainWalkable(mTryX, mTryY) = 0 then
          mLegal = 0
        end if
        if mTower <> 0 then
          mDx = mTryX - mTowerX
          mDy = mTryY - mTowerY
          mTD = mDx * mDx + mDy * mDy
          if mTD < 4 and mTD <= mTowerDistance then
            mLegal = 0
          end if
        end if
        mStep = mStep + 1
      wend
      if mLegal then
        mDx = mTryX - mThreatX
        mDy = mTryY - mThreatY
        mMin = mDx * mDx + mDy * mDy
        mSum = mMin
        if mSecond <> 0 and mSecondDistance <= 64 then
          mDx = mTryX - mSecondX
          mDy = mTryY - mSecondY
          mD = mDx * mDx + mDy * mDy
          mSum = mSum + mD
          if mD < mMin then
            mMin = mD
          end if
        end if
        mScore = mMin * 8 + mSum
        mScore = mScore + (mDirX * mFacingX + mDirY * mFacingY) / 15000
        if 1 = 1 and mAlly <> 0 and mAllyDistance <= 144 then
          mDx = mTryX - mAllyX
          mDy = mTryY - mAllyY
          mScore = mScore - mDx * mDx - mDy * mDy
        end if
        if mScore > mBestScore then
          mBestScore = mScore
          motionX = mTryX
          motionY = mTryY
          mFound = 1
        end if
      end if
      mdirection = mdirection + 1
    wend
    if mFound = 0 then
      motionUntil = 0
      motionFailures = motionFailures + 1
    end if
  end if
end if
if worldTick < motionUntil then
  kiteMoved = walkTo(motionX, motionY)
  if kiteMoved then
    motionActive = 1
    kiteMoveTicks = kiteMoveTicks + 1
    if mNew then
      kiteBursts = kiteBursts + 1
      if kiteTrigger = 2 then
        kiteEscapes = kiteEscapes + 1
      end if
    end if
    if 1 = 1 and bestId <> 0 then
      mSpell = 3
      mCast = 0
      while mSpell >= 1 and mCast = 0
        if selfClass <> 3 or mSpell = 3 then
          if abilityCharges(mSpell) > 0 and abilityCooldown(mSpell) = 0 then
            mCast = castTarget(mSpell, bestId)
          end if
        end if
        mSpell = mSpell - 1
      wend
      if mCast then
        kiteSpellCasts = kiteSpellCasts + 1
      end if
    end if
  else
    motionUntil = 0
    motionFailures = motionFailures + 1
  end if
end if
if motionActive = 0 and bestId <> 0 then
  attackTarget(bestId)
end if
motionLastTick = worldTick
motionLastHits = selfAttacksLanded
motionLastHp = selfHp

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
  if (selfClass = 1 or selfClass = 6) and hasGear = 0 and selfGold >= 110 then
            weaponBought = buyItem(11)
            if weaponBought then
              hasGear = 1
              weaponStarts = weaponStarts + 1
            end if
          end if
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
if bestId = 0 and motionActive = 0 then
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
