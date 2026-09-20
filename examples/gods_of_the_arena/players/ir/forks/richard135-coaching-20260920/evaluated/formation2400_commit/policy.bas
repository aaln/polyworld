' Generated from gota_richard_coaching_committed_return_v5; gota-semantic-policy/1; gota-basic/1
' @rule comments identify regions only; the extractor reads all executable statements.

' @rule R0
decisions = decisions + 1

' @rule R1
gaActive = 0
if selfTeam = 0 and worldTick >= 2400 then
  gaActive = 1
  defActive = 0
  bestId = 0
  bestDistance = 2147483647
  macroIndex = objectCount()
  defGroupSize = 0
  defPointX = 0
  defPointY = 0
  defCount = 0
  coreDx = 116
  coreDy = 0
  coreX = 116
  coreY = 0
  coreRespond = 0
  defFrontD = 2147483647
  defFrontX = 105
  defFrontY = 11
  coreValue = 400
  defI = 0
  while defI < macroIndex and defI < 64
    defKind = objectKind(defI)
    if defKind = 1 or defKind = 2 then
    coreTarget = objectTeam(defI)
    pairAnchorHp = objectHp(defI)
    perimeterObjX = objectX(defI)
    perimeterObjY = objectY(defI)
    if defKind = 1 and coreTarget = selfTeam then
      coreValue = pairAnchorHp
    end if
    if defKind = 2 and pairAnchorHp > 0 and objectAlive(defI) then
      if coreTarget = selfTeam then
        defGroupSize = defGroupSize + 1
        defPointX = defPointX + perimeterObjX
        defPointY = defPointY + perimeterObjY
      else
        defCount = defCount + 1
        if perimeterObjX < coreDx then
          coreDx = perimeterObjX
        end if
        if perimeterObjX > coreDy then
          coreDy = perimeterObjX
        end if
        if perimeterObjY < coreX then
          coreX = perimeterObjY
        end if
        if perimeterObjY > coreY then
          coreY = perimeterObjY
        end if
        defDx = perimeterObjX - 105
        defDy = perimeterObjY - 11
        defD = defDx * defDx + defDy * defDy
        if defD <= 60 * 60 then
          coreRespond = coreRespond + 1
          if objectTarget(defI) > 0 and objectTarget(defI) < 100 then
            coreRespond = coreRespond + 1
          end if
        end if
        if defD < defFrontD then
          defFrontD = defD
          defFrontX = perimeterObjX
          defFrontY = perimeterObjY
        end if
      end if
    end if
    end if
    defI = defI + 1
  wend
  if defGroupSize > 0 then
    defPointX = defPointX / defGroupSize
    defPointY = defPointY / defGroupSize
  else
    defPointX = selfX
    defPointY = selfY
  end if
  if defGroupSize = 5 then
    perimeterAdmit = 0
    defNavX = defPointX
    defNavY = defPointY
    defI = 0
    while defI < macroIndex and defI < 64
      if objectKind(defI) = 2 and objectTeam(defI) = selfTeam and objectHp(defI) > 0 then
        perimeterObjX = objectX(defI)
        perimeterObjY = objectY(defI)
        defD = (perimeterObjX - defPointX) * (perimeterObjX - defPointX) + (perimeterObjY - defPointY) * (perimeterObjY - defPointY)
        if defD > perimeterAdmit then
          perimeterAdmit = defD
          defNavX = perimeterObjX
          defNavY = perimeterObjY
        end if
      end if
      defI = defI + 1
    wend
    if perimeterAdmit > 14 * 14 then
      defPointX = (defPointX * 5 - defNavX) / 4
      defPointY = (defPointY * 5 - defNavY) / 4
    end if
  end if
  defMates = 0
  defFront = 0
  defScore = 2147483647
  coreId = 0
  coreD = 2147483647
  backdoorX = 28
  backdoorY = 79
  backdoorHelpers = 0
  backdoorAlly = 0
  backdoorD = 2147483647
  perimeterBoundSq = (defPointX - 8) * (defPointX - 8) + (defPointY - 70) * (defPointY - 70)
  perimeterRadiusSq = (defPointX - 28) * (defPointX - 28) + (defPointY - 79) * (defPointY - 79)
  perimeterReachSq = (defPointX - 48) * (defPointX - 48) + (defPointY - 103) * (defPointY - 103)
  defI = 0
  while defI < macroIndex and defI < 160
    defKind = objectKind(defI)
    coreTarget = objectTeam(defI)
    pairAnchorHp = objectHp(defI)
    if pairAnchorHp > 0 and objectAlive(defI) then
      perimeterObjX = objectX(defI)
      perimeterObjY = objectY(defI)
      defDx = perimeterObjX - defPointX
      defDy = perimeterObjY - defPointY
      defD = defDx * defDx + defDy * defDy
      backdoorSelfX = perimeterObjX - selfX
      backdoorSelfY = perimeterObjY - selfY
      backdoorSelfD = backdoorSelfX * backdoorSelfX + backdoorSelfY * backdoorSelfY
      if coreTarget = selfTeam then
        if defKind = 2 and pairAnchorHp >= 120 and defD <= 14 * 14 then
          defMates = defMates + 1
        end if
        if defKind = 3 and defD <= 144 then
          backdoorHelpers = backdoorHelpers + 1
        end if
      else
        if defKind = 2 then
          coreScore = defD * 4 + pairAnchorHp
          if defD <= 484 and coreScore < defScore then
            defFront = objectId(defI)
            defScore = coreScore
          end if
          if (perimeterObjX - 8) * (perimeterObjX - 8) + (perimeterObjY - 70) * (perimeterObjY - 70) <= 784 then
            perimeterBoundSq = perimeterBoundSq + pairAnchorHp * 4
          end if
          if (perimeterObjX - 28) * (perimeterObjX - 28) + (perimeterObjY - 79) * (perimeterObjY - 79) <= 784 then
            perimeterRadiusSq = perimeterRadiusSq + pairAnchorHp * 4
          end if
          if (perimeterObjX - 48) * (perimeterObjX - 48) + (perimeterObjY - 103) * (perimeterObjY - 103) <= 784 then
            perimeterReachSq = perimeterReachSq + pairAnchorHp * 4
          end if
        end if
        if defKind = 1 or defKind = 4 then
          if defD < coreD then
            coreId = objectId(defI)
            coreD = defD
            backdoorX = perimeterObjX
            backdoorY = perimeterObjY
          end if
        end if
        if defKind = 2 or defKind = 3 then
          if backdoorSelfD <= 36 and backdoorSelfD < backdoorD then
            backdoorAlly = objectId(defI)
            backdoorD = backdoorSelfD
          end if
        end if
      end if
    end if
    defI = defI + 1
  wend
  gaReady = 0
  if defMates >= 4 then
    gaReady = 1
  end if
  pairedRush = 0
  if defCount >= 3 and ((coreDy - coreDx) * (coreDy - coreDx) + (coreY - coreX) * (coreY - coreX)) >= 1024 then
    pairedRush = 1
  end if
  perimeterBound = (defPointX - 11) * (defPointX - 11) + (defPointY - 105) * (defPointY - 105)
  if worldTick <= backdoorLastSeen or worldTick > backdoorLastSeen + 1 then
    backdoorGroupUntil = 0
    backdoorFirstSeen = 0
    backdoorCommitted = 0
    defUntil = 0
  end if
  if coreRespond >= 2 or coreValue < 400 then
    defUntil = worldTick + 1200
    defThreatX = defFrontX
    defThreatY = defFrontY
  end if
  defSentry = 0
  if worldTick < defUntil then
    defSentry = 1
    defFrontX = defThreatX
    defFrontY = defThreatY
  end if
  backdoorLastSeen = worldTick
  defGoalX = defPointX
  defGoalY = defPointY
  defSentryRole = 1
  if gaReady then
    if defSentry then
      defSentryRole = 4
      defGoalX = defFrontX
      defGoalY = defFrontY
      backdoorFirstSeen = 0
    else
      defSentryRole = 2
      defGoalX = backdoorX
      defGoalY = backdoorY
      if perimeterBound <= 3600 and (backdoorX - 11) * (backdoorX - 11) + (backdoorY - 105) * (backdoorY - 105) <= 1024 then
        if backdoorFirstSeen = 0 then
          backdoorFirstSeen = worldTick
        end if
        if worldTick >= backdoorGroupUntil then
          if backdoorGroupUntil > 0 then
            if backdoorWatched = 0 then
              perimeterBoundSq = perimeterBoundSq + 800
            end if
            if backdoorWatched = 1 then
              perimeterRadiusSq = perimeterRadiusSq + 800
            end if
            if backdoorWatched = 2 then
              perimeterReachSq = perimeterReachSq + 800
            end if
          end if
          backdoorWatched = 0
          perimeterAdmit = perimeterBoundSq
          if perimeterRadiusSq < perimeterAdmit then
            backdoorWatched = 1
            perimeterAdmit = perimeterRadiusSq
          end if
          if perimeterReachSq < perimeterAdmit then
            backdoorWatched = 2
          end if
          backdoorGroupUntil = (worldTick / 240 + 1) * 240
        end if
        defGoalX = 8
        defGoalY = 70
        if backdoorWatched = 1 then
          defGoalX = 28
          defGoalY = 79
        end if
        if backdoorWatched = 2 then
          defGoalX = 48
          defGoalY = 103
        end if
        if backdoorHelpers >= 2 or pairedRush or worldTick - backdoorFirstSeen >= 480 then
          backdoorCommitted = worldTick + 240
        end if
        if worldTick < backdoorCommitted then
          defSentryRole = 3
          defGoalX = backdoorX
          defGoalY = backdoorY
        end if
      else
        backdoorFirstSeen = 0
        defSentryRole = 3
      end if
    end if
    if defSentry = 0 and coreId = 0 then
      defSentryRole = 2
      defGoalX = 11
      defGoalY = 105
      backdoorCommitted = 0
    end if
    if defSentryRole = 3 and coreD <= 784 and (pairedRush or backdoorHelpers >= 2) then
      bestId = coreId
      bestDistance = coreD
    else
      if defFront <> 0 then
        bestId = defFront
        bestDistance = defScore
      else
        if defSentryRole = 3 and coreD <= 784 then
          bestId = coreId
          bestDistance = coreD
        end if
      end if
    end if
  else
    backdoorCommitted = 0
    if defSentry then
      defGoalX = (defFrontX + 105) / 2
      defGoalY = (defFrontY + 11) / 2
    end if
  end if
  if bestId = 0 and backdoorAlly <> 0 then
    bestId = backdoorAlly
    bestDistance = backdoorD
  end if
  if defSentry and (defPointX - defFrontX) * (defPointX - defFrontX) + (defPointY - defFrontY) * (defPointY - defFrontY) > 784 then
    bestId = 0
  end if
  defDx = selfX - defPointX
  defDy = selfY - defPointY
  gaTethered = 0
  if defDx * defDx + defDy * defDy > 20 * 20 and (defSentry = 0 or gaReady) then
    bestId = 0
    defGoalX = defPointX
    defGoalY = defPointY
    gaTethered = 1
  end if
else
  if selfTeam = 0 then
    defGroupSize = 4
    defHoldTicks = 1440
    defContinueHome = 48
    if selfTeam = 1 then
      defGroupSize = 4
      defHoldTicks = 1200
      defContinueHome = 24
    end if
    defSentryRole = 3
    if selfTeam = 1 then
      defSentryRole = 3
    end if
    defSentry = 0
    if defSentryRole >= 2 and (selfClass = 2 or selfClass = 3 or selfClass = 7 or selfClass = 8) then
      defSentry = 1
    end if
    if (defSentryRole = 1 or defSentryRole = 3) and (selfClass = 0 or selfClass = 5) then
      defSentry = 1
    end if
    if defSentry then
      defHoldTicks = 7200
    end if
    defActive = 0
    if worldTick <= defLastTick or (worldTick <> defLastTick + 1 and defSentry = 0) then
      defUntil = 0
    end if
    defLastTick = worldTick
    defHomeX = 105
    defHomeY = 11
    if selfTeam = 1 then
      defHomeX = 11
      defHomeY = 105
    end if
    defI = 0
    while defI < objectCount() and defI < 2
      if objectTeam(defI) = selfTeam and objectKind(defI) = 1 then
        defHomeX = objectX(defI)
        defHomeY = objectY(defI)
      end if
      defI = defI + 1
    wend
    defFront = 0
    defFrontD = 100 * 100 + 1
    defI = 0
    while defI < objectCount() and defI < 64
      if objectKind(defI) = 3 then
        defI = 64
      else
      if objectKind(defI) = 2 then
      if objectTeam(defI) <> selfTeam and objectAlive(defI) and objectHp(defI) > 0 then
        defDx = objectX(defI) - defHomeX
        defDy = objectY(defI) - defHomeY
        defD = defDx * defDx + defDy * defDy
        if defD < defFrontD then
          defFront = objectId(defI)
          defFrontD = defD
          defFrontX = objectX(defI)
          defFrontY = objectY(defI)
          defFrontTarget = objectTarget(defI)
        end if
      end if
      end if
      end if
      defI = defI + 1
    wend
    if defFront <> 0 then
      defCount = 0
      defAnchor = 0
      defAnchorD = 14 * 14 + 1
      defI = 0
      while defI < objectCount() and defI < 64
        defKind = objectKind(defI)
        if defKind = 3 then
          defI = 64
        else
        if objectHp(defI) > 0 then
          defDx = objectX(defI) - defFrontX
          defDy = objectY(defI) - defFrontY
          defD = defDx * defDx + defDy * defDy
          if objectTeam(defI) <> selfTeam and defKind = 2 and objectAlive(defI) and defD <= 12 * 12 then
            defCount = defCount + 1
          end if
          if objectTeam(defI) = selfTeam and (defKind = 4 or defKind = 1) and defD <= 14 * 14 then
            if objectId(defI) = defFrontTarget then
              defD = -1
            end if
            if defD < defAnchorD then
              defAnchor = objectId(defI)
              defAnchorD = defD
              defAnchorX = objectX(defI)
              defAnchorY = objectY(defI)
            end if
          end if
        end if
        end if
        defI = defI + 1
      wend
      if defAnchor <> 0 and ((defFrontD <= 60 * 60 and defCount >= 2) or defCount >= defGroupSize or (worldTick < defUntil and defFrontD <= defContinueHome * defContinueHome)) then
        defUntil = worldTick + defHoldTicks
        if defFrontD <= 60 * 60 and defCount >= 2 then
          criticalUntil = worldTick + 1200
        end if
        defThreatX = defFrontX
        defThreatY = defFrontY
        defDx = defHomeX - defAnchorX
        defDy = defHomeY - defAnchorY
        defAx = defDx
        defAy = defDy
        if defAx < 0 then
          defAx = -defAx
        end if
        if defAy < 0 then
          defAy = -defAy
        end if
        defScale = defAx
        if defAy > defScale then
          defScale = defAy
        end if
        if defScale > 0 then
          defPointX = defAnchorX + defDx * 4 / defScale
          defPointY = defAnchorY + defDy * 4 / defScale
        else
          defPointX = defHomeX + 4
          defPointY = defHomeY + 4
          if selfTeam = 1 then
            defPointX = defHomeX - 4
            defPointY = defHomeY - 4
          end if
        end if
        defenseRefreshes = defenseRefreshes + 1
      end if
    end if
    if worldTick < defUntil then
      defActive = 1
    end if
  
    defDx = selfX - defHomeX
    defDy = selfY - defHomeY
    if defDx * defDx + defDy * defDy > 28 * 28 and worldTick >= criticalUntil then
      defActive = 0
      defUntil = 0
    end if
  
    if defActive then
  
      bestId = 0
      bestDistance = 2147483647
      defI = 0
      while defI < objectCount()
        defKind = objectKind(defI)
        if (defKind = 2 or defKind = 3) and objectTeam(defI) <> selfTeam and objectAlive(defI) and objectHp(defI) > 0 then
          defDx = objectX(defI) - selfX
          defDy = objectY(defI) - selfY
          defD = defDx * defDx + defDy * defDy
          defGx = objectX(defI) - defThreatX
          defGy = objectY(defI) - defThreatY
          defGroupD = defGx * defGx + defGy * defGy
          if defD <= 10 * 10 and (defGroupD <= 400 or defD <= 9) then
            defScore = defD * 10 + objectHp(defI) * 1
            if (1 = 1 and defKind = 3) or (1 = 0 and defKind = 2) then
              defScore = defScore - 10000
            end if
            if defScore < bestDistance then
              bestDistance = defScore
              bestId = objectId(defI)
            end if
          end if
        end if
        defI = defI + 1
      wend
  
      defMates = 0
      defI = 0
      while defI < objectCount() and defI < 64
        defKind = objectKind(defI)
        if defKind = 3 then
          defI = 64
        else
          if defKind = 2 then
            if objectTeam(defI) = selfTeam and objectHp(defI) > 0 and objectAlive(defI) then
              defDx = objectX(defI) - selfX
              defDy = objectY(defI) - selfY
              if defDx * defDx + defDy * defDy <= 196 then
                defMates = defMates + 1
              end if
            end if
          end if
        end if
        defI = defI + 1
      wend
      if defMates < 0 then
        bestId = 0
      end if
      defenseDecisions = defenseDecisions + 1
    else
      if selfClass = 9 or selfClass = 7 then
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
      else
        bestId = 0
        bestDistance = 2147483647
        index = 0
        while index < objectCount()
          id = objectId(index)
          if objectAlive(index) and objectHp(index) > 0 and objectTeam(index) <> selfTeam then
            dx = objectX(index) - selfX
            dy = objectY(index) - selfY
            if dx < 0 then
              dx = -dx
            end if
            if dy < 0 then
              dy = -dy
            end if
            buildingInset = 0
            buildingWeight = 1
            if objectKind(index) = 4 or objectKind(index) = 5 then
              buildingInset = 2
              buildingWeight = 1
            end if
            if objectKind(index) = 1 then
              buildingInset = 4
              buildingWeight = 1
            end if
            dx = dx - buildingInset
            dy = dy - buildingInset
            if dx < 0 then
              dx = 0
            end if
            if dy < 0 then
              dy = 0
            end if
            distance = (dx * dx + dy * dy) * buildingWeight
            if distance < bestDistance then
              bestDistance = distance
              bestId = id
            end if
          end if
          index = index + 1
        wend
      end if
      macroIndex = 0
      while macroIndex < objectCount()
        if objectId(macroIndex) = bestId then
          if objectKind(macroIndex) = 2 or objectKind(macroIndex) = 3 then
            macroDx = objectX(macroIndex) - selfX
            macroDy = objectY(macroIndex) - selfY
            if macroDx * macroDx + macroDy * macroDy > 12 * 12 then
              bestId = 0
            end if
          end if
        end if
        macroIndex = macroIndex + 1
      wend
    end if
  else
    perimeterEnabled = 0
    perimeterRadiusSq = 24 * 24
    perimeterReachSq = 32 * 32
    if 2 = 2 or selfTeam = 2 then
      perimeterEnabled = 1
    end if
    defGroupSize = 4
    defHoldTicks = 1440
    defContinueHome = 48
    if selfTeam = 1 then
      defGroupSize = 4
      defHoldTicks = 1200
      defContinueHome = 24
    end if
    defSentryRole = 3
    if selfTeam = 1 then
      defSentryRole = 3
    end if
    defSentry = 0
    if defSentryRole >= 2 and (selfClass = 2 or selfClass = 3 or selfClass = 7 or selfClass = 8) then
      defSentry = 1
    end if
    if (defSentryRole = 1 or defSentryRole = 3) and (selfClass = 0 or selfClass = 5) then
      defSentry = 1
    end if
    if defSentry then
      defHoldTicks = 7200
    end if
    defActive = 0
    if worldTick <= defLastTick or (worldTick <> defLastTick + 1 and defSentry = 0) then
      defUntil = 0
      backdoorUntil = 0
      backdoorGroupUntil = 0
      backdoorWatched = 0
      backdoorFirstSeen = 0
      backdoorLastSeen = 0
      backdoorCommitted = 0
    end if
    defLastTick = worldTick
    defHomeX = 105
    defHomeY = 11
    if selfTeam = 1 then
      defHomeX = 11
      defHomeY = 105
    end if
    defI = 0
    while defI < objectCount() and defI < 2
      if objectTeam(defI) = selfTeam and objectKind(defI) = 1 then
        defHomeX = objectX(defI)
        defHomeY = objectY(defI)
      end if
      defI = defI + 1
    wend
    defCount = 0
    defFront = 0
    defFrontD = 100 * 100 + 1
    defI = 0
    while defI < objectCount() and defI < 64
      if objectKind(defI) = 3 then
        defI = 64
      else
      if objectKind(defI) = 2 then
      if objectTeam(defI) <> selfTeam and objectAlive(defI) and objectHp(defI) > 0 then
        defDx = objectX(defI) - defHomeX
        defDy = objectY(defI) - defHomeY
        defD = defDx * defDx + defDy * defDy
        if defD < defFrontD then
          defFront = objectId(defI)
          defFrontD = defD
          defFrontX = objectX(defI)
          defFrontY = objectY(defI)
          defFrontTarget = objectTarget(defI)
        end if
      end if
      end if
      end if
      defI = defI + 1
    wend
    if defFront <> 0 then
      defCount = 0
      defAnchor = 0
      defAnchorD = 14 * 14 + 1
      defI = 0
      while defI < objectCount() and defI < 64
        defKind = objectKind(defI)
        if defKind = 3 then
          defI = 64
        else
        if objectHp(defI) > 0 then
          defDx = objectX(defI) - defFrontX
          defDy = objectY(defI) - defFrontY
          defD = defDx * defDx + defDy * defDy
          if objectTeam(defI) <> selfTeam and defKind = 2 and objectAlive(defI) and defD <= 12 * 12 then
            defCount = defCount + 1
          end if
          if objectTeam(defI) = selfTeam and (defKind = 4 or defKind = 1) and defD <= 14 * 14 then
            if objectId(defI) = defFrontTarget then
              defD = -1
            end if
            if defD < defAnchorD then
              defAnchor = objectId(defI)
              defAnchorD = defD
              defAnchorX = objectX(defI)
              defAnchorY = objectY(defI)
              pairAnchorHp = objectHp(defI)
            end if
          end if
        end if
        end if
        defI = defI + 1
      wend
      middleRush = 0
      if selfTeam = 1 and worldTick <= 1800 and defCount >= 3 then
        if defAnchor = 19 or defAnchor = 20 or defAnchor = 21 then
          middleRush = 1
        end if
      end if
      pairedRush = 0
      pairMaxHp = 0
      if defAnchor = 13 or defAnchor = 25 then
        pairMaxHp = 950
      end if
      if defAnchor = 14 or defAnchor = 26 then
        pairMaxHp = 1300
      end if
      if defAnchor = 15 or defAnchor = 27 then
        pairMaxHp = 1950
      end if
      if selfTeam = 1 and worldTick <= 3600 and defCount >= 2 then
        if pairMaxHp > 0 and pairAnchorHp <= pairMaxHp - 150 then
          pairedRush = 1
        end if
      end if
      if defAnchor <> 0 and ((defFrontD <= 60 * 60 and defCount >= 2) or pairedRush or middleRush or defCount >= defGroupSize or (worldTick < defUntil and defFrontD <= defContinueHome * defContinueHome)) then
        perimeterAnchor = defAnchor
        perimeterX = defAnchorX
        perimeterY = defAnchorY
        defUntil = worldTick + defHoldTicks
        if defFrontD <= 60 * 60 and defCount >= 2 then
          criticalUntil = worldTick + 1200
        end if
        defThreatX = defFrontX
        defThreatY = defFrontY
        defDx = defHomeX - defAnchorX
        defDy = defHomeY - defAnchorY
        defAx = defDx
        defAy = defDy
        if defAx < 0 then
          defAx = -defAx
        end if
        if defAy < 0 then
          defAy = -defAy
        end if
        defScale = defAx
        if defAy > defScale then
          defScale = defAy
        end if
        if defScale > 0 then
          defPointX = defAnchorX + defDx * 4 / defScale
          defPointY = defAnchorY + defDy * 4 / defScale
        else
          defPointX = defHomeX + 4
          defPointY = defHomeY + 4
          if selfTeam = 1 then
            defPointX = defHomeX - 4
            defPointY = defHomeY - 4
          end if
        end if
        defenseRefreshes = defenseRefreshes + 1
      end if
    end if
    backdoorActive = 0
    if worldTick >= backdoorUntil then
      backdoorCommitted = 0
    end if
    backdoorGod = 1
    backdoorGuardA = 28
    backdoorGuardB = 29
    if selfTeam = 1 then
      backdoorGod = 2
      backdoorGuardA = 30
      backdoorGuardB = 31
    end if
    if defCount >= defGroupSize then
      backdoorUntil = 0
      backdoorGroupUntil = defUntil
    end if
    if selfTeam = 1 and defCount <= 1 and defFront <> 0 and defFrontD <= 24 * 24 then
      if defAnchor = defFrontTarget and (defFrontTarget = backdoorGod or defFrontTarget = backdoorGuardA or defFrontTarget = backdoorGuardB) then
        backdoorSelfX = selfX - defHomeX
        backdoorSelfY = selfY - defHomeY
        backdoorSelfD = backdoorSelfX * backdoorSelfX + backdoorSelfY * backdoorSelfY
        if backdoorWatched <> defFront or worldTick > backdoorLastSeen + 72 then
          backdoorFirstSeen = worldTick
        end if
        backdoorWatched = defFront
        backdoorLastSeen = worldTick
        backdoorNearer = 0
        backdoorHelpers = 0
        backdoorI = 0
        while backdoorI < objectCount() and backdoorI < 64
          backdoorKind = objectKind(backdoorI)
          if backdoorKind = 3 then
            backdoorI = 64
          else
            if backdoorKind = 2 and objectTeam(backdoorI) = selfTeam and objectHp(backdoorI) > 0 and objectAlive(backdoorI) then
              backdoorAlly = objectId(backdoorI)
              if backdoorAlly <> selfId then
                backdoorX = objectX(backdoorI) - defHomeX
                backdoorY = objectY(backdoorI) - defHomeY
                backdoorD = backdoorX * backdoorX + backdoorY * backdoorY
                if backdoorD < backdoorSelfD or (backdoorD = backdoorSelfD and backdoorAlly < selfId) then
                  backdoorNearer = backdoorNearer + 1
                end if
                if objectTarget(backdoorI) = defFront then
                  backdoorHelpers = backdoorHelpers + 1
                end if
              end if
            end if
          end if
          backdoorI = backdoorI + 1
        wend
        backdoorAccept = 0
        if backdoorSelfD <= 28 * 28 or backdoorCommitted = defFront then
          backdoorAccept = 1
        end if
        if backdoorHelpers = 0 and worldTick >= backdoorFirstSeen + backdoorNearer * 96 then
          backdoorAccept = 1
        end if
        if backdoorAccept then
          backdoorCommitted = defFront
        backdoorActive = 1
        defThreatX = defFrontX
        defThreatY = defFrontY
        defPointX = defFrontX
        defPointY = defFrontY
        if defCount < defGroupSize and worldTick >= backdoorGroupUntil then
          backdoorUntil = worldTick + 480
        end if
      end if
      end if
    end if
    if backdoorUntil > 0 then
      defUntil = backdoorUntil
    end if
    if worldTick < defUntil then
      defActive = 1
    end if
  
    coreId = 0
    coreScore = 2147483647
    coreHomeId = 1
    if selfTeam = 1 then
      coreHomeId = 2
    end if
    coreDx = selfX - defHomeX
    coreDy = selfY - defHomeY
    coreRespond = 0
    if coreDx * coreDx + coreDy * coreDy <= 24 * 24 then
      coreRespond = 1
    end if
    perimeterBound = 32
    if 10 > perimeterBound then
      perimeterBound = 10
    end if
    if coreRespond and 24 + 14 > perimeterBound then
      perimeterBound = 24 + 14
    end if
    perimeterBoundSq = perimeterBound * perimeterBound
    if perimeterAnchor = 0 then
      perimeterAnchor = coreHomeId
      perimeterX = defHomeX
      perimeterY = defHomeY
    end if
    if selfTeam = 1 then
      defDx = selfX - defHomeX
      defDy = selfY - defHomeY
      if defDx * defDx + defDy * defDy > 28 * 28 and worldTick >= criticalUntil then
        defActive = 0
        defUntil = 0
        backdoorUntil = 0
        backdoorActive = 0
      end if
    end if
  
    if defActive then
  
      bestId = 0
      bestDistance = 2147483647
      defI = 0
      while defI < objectCount()
        defKind = objectKind(defI)
        if perimeterEnabled and (defKind = 1 or defKind = 4) then
          if objectId(defI) = perimeterAnchor and objectHp(defI) <= 0 then
            perimeterAnchor = coreHomeId
            perimeterX = defHomeX
            perimeterY = defHomeY
          end if
        end if
        if defKind = 2 or defKind = 3 then
        if objectTeam(defI) <> selfTeam then
          perimeterObjX = objectX(defI)
          perimeterObjY = objectY(defI)
          defDx = perimeterObjX - selfX
          defDy = perimeterObjY - selfY
          defD = defDx * defDx + defDy * defDy
        if defD <= perimeterBoundSq then
        if objectAlive(defI) and objectHp(defI) > 0 then
          if coreRespond then
            coreDx = perimeterObjX - defHomeX
            coreDy = perimeterObjY - defHomeY
            coreD = coreDx * coreDx + coreDy * coreDy
            if coreD <= 14 * 14 then
              coreTarget = objectTarget(defI)
              if coreTarget = coreHomeId or coreD <= 36 then
                coreValue = coreD * 100 + objectHp(defI)
                if coreTarget = coreHomeId then
                  coreValue = coreValue - 100000
                end if
                if coreValue < coreScore then
                  coreScore = coreValue
                  coreId = objectId(defI)
                  coreX = perimeterObjX
                  coreY = perimeterObjY
                end if
              end if
            end if
          end if
          perimeterAdmit = 0
        if perimeterEnabled and defD <= perimeterReachSq then
          perimeterDx = perimeterObjX - perimeterX
          perimeterDy = perimeterObjY - perimeterY
          if perimeterDx * perimeterDx + perimeterDy * perimeterDy <= perimeterRadiusSq then
            perimeterAdmit = 1
          end if
        end if
        defGroupD = 0
        if perimeterAdmit = 0 then
          defGx = perimeterObjX - defThreatX
          defGy = perimeterObjY - defThreatY
          defGroupD = defGx * defGx + defGy * defGy
        end if
        if perimeterAdmit or (defD <= 10 * 10 and (defGroupD <= 400 or defD <= 9)) then
            defScore = defD * 10 + objectHp(defI) * 1
            if (1 = 1 and defKind = 3) or (1 = 0 and defKind = 2) then
              defScore = defScore - 10000
            end if
            if defScore < bestDistance then
              bestDistance = defScore
              bestId = objectId(defI)
            end if
          end if
        end if
        end if
        end if
        end if
        defI = defI + 1
      wend
  
      defMates = 0
      defI = 0
      while defI < objectCount() and defI < 64
        defKind = objectKind(defI)
        if defKind = 3 then
          defI = 64
        else
          if defKind = 2 then
            if objectTeam(defI) = selfTeam and objectHp(defI) > 0 and objectAlive(defI) then
              defDx = objectX(defI) - selfX
              defDy = objectY(defI) - selfY
              if defDx * defDx + defDy * defDy <= 196 then
                defMates = defMates + 1
              end if
            end if
          end if
        end if
        defI = defI + 1
      wend
      if defMates < 0 then
        bestId = 0
      end if
      defenseDecisions = defenseDecisions + 1
    else
      if selfClass = 9 or selfClass = 7 then
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
      else
        bestId = 0
        bestDistance = 2147483647
        index = 0
        while index < objectCount()
          id = objectId(index)
          if objectAlive(index) and objectHp(index) > 0 and objectTeam(index) <> selfTeam then
            dx = objectX(index) - selfX
            dy = objectY(index) - selfY
            if dx < 0 then
              dx = -dx
            end if
            if dy < 0 then
              dy = -dy
            end if
            buildingInset = 0
            buildingWeight = 1
            if objectKind(index) = 4 or objectKind(index) = 5 then
              buildingInset = 2
              buildingWeight = 1
            end if
            if objectKind(index) = 1 then
              buildingInset = 4
              buildingWeight = 1
            end if
            dx = dx - buildingInset
            dy = dy - buildingInset
            if dx < 0 then
              dx = 0
            end if
            if dy < 0 then
              dy = 0
            end if
            distance = (dx * dx + dy * dy) * buildingWeight
            if distance < bestDistance then
              bestDistance = distance
              bestId = id
            end if
          end if
          index = index + 1
        wend
      end if
      macroIndex = 0
      while macroIndex < objectCount()
        if objectId(macroIndex) = bestId then
          if objectKind(macroIndex) = 2 or objectKind(macroIndex) = 3 then
            macroDx = objectX(macroIndex) - selfX
            macroDy = objectY(macroIndex) - selfY
            if macroDx * macroDx + macroDy * macroDy > 12 * 12 then
              bestId = 0
            end if
          end if
        end if
        macroIndex = macroIndex + 1
      wend
    end if
    if coreId <> 0 then
      bestId = coreId
      bestDistance = coreScore
      defPointX = coreX
      defPointY = coreY
      defThreatX = coreX
      defThreatY = coreY
    end if
  
    if backdoorActive and coreId = 0 then
      bestId = defFront
      bestDistance = defFrontD
    end if
  
    if worldTick <= perimeterLastTick then
      perimeterLastCombat = 0
    end if
    perimeterLastTick = worldTick
    if defActive = 0 or bestId <> 0 or perimeterLastCombat = 0 then
      perimeterLastCombat = worldTick
    end if
    if perimeterEnabled and defActive and bestId = 0 and 1 > 0 then
      if 1 = 2 or defSentry = 0 then
        if worldTick - perimeterLastCombat >= 480 then
          defActive = 0
          defUntil = 0
          backdoorUntil = 0
          backdoorGroupUntil = 0
        end if
      end if
    end if
  end if
end if

' @rule R2
if gaActive and gaTethered then
  motionActive = 0
else
  defMotionLimit = 80
  if defActive then
    defMotionLimit = 40
  end if
  if objectCount() > defMotionLimit then
    motionActive = 0
    if bestId <> 0 then
      attackTarget(bestId)
    end if
  else
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
      if kiteTrigger = 0 and 1 = 1 and bestId <> 0 and selfClass <> 9 and mDistance <= 7 * 7 then
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
  end if
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
  if selfTeam = 1 or (0 = 1 and selfClass <> 7 and selfClass <> 8) then
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
      if loadoutItem = 18 then
        ownsthird = 1
      end if
      if loadoutItem = 19 then
        ownsfourth = 1
      end if
      if loadoutItem = 16 then
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
      loadoutNext = 18
    end if
    if loadoutNext = 0 and ownsfourth = 0 then
      loadoutNext = 19
    end if
    if loadoutNext = 0 and ownsfifth = 0 then
      loadoutNext = 16
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
  else
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
end if

' @rule R4
if bestId = 0 and motionActive = 0 then
  if gaActive then
    defNavX = defGoalX
    defNavY = defGoalY
    defNavFound = terrainWalkable(defNavX, defNavY)
    defdirection = 0
    while defdirection < 8 and defNavFound = 0
      defDirX = 0
      defDirY = 0
      if defdirection = 0 or defdirection = 1 or defdirection = 7 then
        defDirX = 3
      end if
      if defdirection = 3 or defdirection = 4 or defdirection = 5 then
        defDirX = -3
      end if
      if defdirection = 1 or defdirection = 2 or defdirection = 3 then
        defDirY = 3
      end if
      if defdirection = 5 or defdirection = 6 or defdirection = 7 then
        defDirY = -3
      end if
      defNavX = defGoalX + defDirX
      defNavY = defGoalY + defDirY
      defNavFound = terrainWalkable(defNavX, defNavY)
      defdirection = defdirection + 1
    wend
    defMoveAccepted = 0
    if defNavFound then
      defMoveAccepted = walkTo(defNavX, defNavY)
    end if
    if defMoveAccepted = 0 then
      defMoveAccepted = walkTo(defPointX, defPointY)
    end if
  else
    if selfTeam = 0 then
      if defActive then
    
        defNavX = defPointX
        defNavY = defPointY
        defNavFound = terrainWalkable(defNavX, defNavY)
        defdirection = 0
        while defdirection < 8 and defNavFound = 0
          defDirX = 0
        defDirY = 0
        if defdirection = 0 or defdirection = 1 or defdirection = 7 then
          defDirX = 1
        end if
        if defdirection = 3 or defdirection = 4 or defdirection = 5 then
          defDirX = -1
        end if
        if defdirection = 1 or defdirection = 2 or defdirection = 3 then
          defDirY = 1
        end if
        if defdirection = 5 or defdirection = 6 or defdirection = 7 then
          defDirY = -1
        end if
          defNavX = defPointX + defDirX * 3
          defNavY = defPointY + defDirY * 3
          defNavFound = terrainWalkable(defNavX, defNavY)
          defdirection = defdirection + 1
        wend
        defMoveAccepted = 0
        if defNavFound then
          defMoveAccepted = walkTo(defNavX, defNavY)
        end if
        if defMoveAccepted = 0 then
          defMoveAccepted = walkTo(defThreatX, defThreatY)
        end if
      else
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
    else
      if defActive then
        defGoalX = defPointX
      defGoalY = defPointY
      if perimeterEnabled and 0 = 1 then
        defGoalX = perimeterX
        defGoalY = perimeterY
        if defThreatX > perimeterX then
          defGoalX = defGoalX + 3
        else
          defGoalX = defGoalX - 3
        end if
        if defThreatY > perimeterY then
          defGoalY = defGoalY + 3
        else
          defGoalY = defGoalY - 3
        end if
      end if
        if selfClass = 0 or selfClass = 5 then
          defGoalX = defGoalX - 2
        end if
        if selfClass = 1 or selfClass = 6 then
          defGoalX = defGoalX + 2
        end if
        if selfClass = 2 or selfClass = 7 then
          defGoalY = defGoalY - 2
        end if
        if selfClass = 3 or selfClass = 8 then
          defGoalY = defGoalY + 2
        end if
    
        defNavX = defGoalX
        defNavY = defGoalY
        defNavFound = terrainWalkable(defNavX, defNavY)
        defdirection = 0
        while defdirection < 8 and defNavFound = 0
          defDirX = 0
        defDirY = 0
        if defdirection = 0 or defdirection = 1 or defdirection = 7 then
          defDirX = 1
        end if
        if defdirection = 3 or defdirection = 4 or defdirection = 5 then
          defDirX = -1
        end if
        if defdirection = 1 or defdirection = 2 or defdirection = 3 then
          defDirY = 1
        end if
        if defdirection = 5 or defdirection = 6 or defdirection = 7 then
          defDirY = -1
        end if
          defNavX = defGoalX + defDirX * 3
          defNavY = defGoalY + defDirY * 3
          defNavFound = terrainWalkable(defNavX, defNavY)
          defdirection = defdirection + 1
        wend
        defMoveAccepted = 0
        if defNavFound then
          defMoveAccepted = walkTo(defNavX, defNavY)
        end if
        if defMoveAccepted = 0 then
          defMoveAccepted = walkTo(defThreatX, defThreatY)
        end if
      else
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
    end if
  end if
end if
