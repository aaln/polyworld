' Generated from gota_formation3600_ally_under_attack_v1; gota-semantic-policy/1; gota-basic/1
' @rule comments identify regions only; the extractor reads all executable statements.

' @rule R0
decisions = decisions + 1

' @rule R1
if adMode = 0 and worldTick <= 1800 and (worldTick / 24) * 24 = worldTick then
defCount = 0
defMates = 0
defSentry = 0
defI = 0
while defI < objectCount() and defI < 64
if objectKind(defI) = 2 and objectTeam(defI) <> selfTeam and objectAlive(defI) and objectHp(defI) > 0 then
defDx = 0
defDy = 0
defScore = 0
defFront = 0
defKind = 0
while defKind < 6
defD = objectItemId(defI, defKind)
if defD <> 0 then
defDx = defDx + 1
end if
if defD = 8 then
defDy = defDy + 1
end if
if defD = 2 then
defScore = defScore + 1
end if
if defD = 11 then
defFront = defFront + 1
end if
defKind = defKind + 1
wend
if defDx = 2 and defDy = 1 and defScore = 1 then
defCount = defCount + 1
end if
if defDx = 1 and defDy = 1 then
defMates = defMates + 1
end if
if defDx = 1 and defFront = 1 then
defSentry = defSentry + 1
end if
end if
defI = defI + 1
wend
if defCount >= 2 and defMates = 0 and defSentry = 0 then
adMode = 1
end if
if defMates >= 2 and defCount = 0 and defSentry = 0 then
adMode = 2
end if
if defSentry >= 2 and defCount = 0 and defMates = 0 then
adMode = 3
end if
end if
gaActive = 0
if selfTeam = 0 and worldTick >= 3600 and (adMode = 0 or adMode = 3) then
gaActive = 1
defActive = 0
defUntil = 0
bestId = 0
bestDistance = 2147483647
index = objectCount()
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
while defI < index and defI < 64
defKind = objectKind(defI)
coreTarget = objectTeam(defI)
pairAnchorHp = objectHp(defI)
ap34 = objectX(defI)
ap35 = objectY(defI)
if defKind = 1 and coreTarget = selfTeam then
coreValue = pairAnchorHp
end if
if defKind = 2 and pairAnchorHp > 0 and objectAlive(defI) then
if coreTarget = selfTeam then
defGroupSize = defGroupSize + 1
defPointX = defPointX + ap34
defPointY = defPointY + ap35
else
defCount = defCount + 1
if ap34 < coreDx then
coreDx = ap34
end if
if ap34 > coreDy then
coreDy = ap34
end if
if ap35 < coreX then
coreX = ap35
end if
if ap35 > coreY then
coreY = ap35
end if
defDx = ap34 - 105
defDy = ap35 - 11
defD = defDx * defDx + defDy * defDy
if defD <= 50 * 50 then
coreRespond = coreRespond + 1
end if
if defD < defFrontD then
defFrontD = defD
defFrontX = ap34
defFrontY = ap35
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
defMates = 0
defFront = 0
defScore = 2147483647
coreId = 0
coreD = 2147483647
ap20 = 28
ap21 = 79
ap10 = 0
ap2 = 0
ap4 = 2147483647
ap28 = (defPointX - 8) * (defPointX - 8) + (defPointY - 70) * (defPointY - 70)
ap36 = (defPointX - 28) * (defPointX - 28) + (defPointY - 79) * (defPointY - 79)
ap37 = (defPointX - 48) * (defPointX - 48) + (defPointY - 103) * (defPointY - 103)
defI = 0
while defI < index and defI < 160
defKind = objectKind(defI)
coreTarget = objectTeam(defI)
pairAnchorHp = objectHp(defI)
if pairAnchorHp > 0 and objectAlive(defI) then
ap34 = objectX(defI)
ap35 = objectY(defI)
defDx = ap34 - defPointX
defDy = ap35 - defPointY
defD = defDx * defDx + defDy * defDy
if coreTarget = selfTeam then
if defKind = 2 and pairAnchorHp >= 120 and defD <= 14 * 14 then
defMates = defMates + 1
end if
if defKind = 3 and defD <= 144 then
ap10 = ap10 + 1
end if
else
if defKind = 2 then
coreScore = defD * 4 + pairAnchorHp
if defD <= 484 and coreScore < defScore then
defFront = objectId(defI)
defScore = coreScore
end if
if (ap34 - 8) * (ap34 - 8) + (ap35 - 70) * (ap35 - 70) <= 784 then
ap28 = ap28 + pairAnchorHp * 4
end if
if (ap34 - 28) * (ap34 - 28) + (ap35 - 79) * (ap35 - 79) <= 784 then
ap36 = ap36 + pairAnchorHp * 4
end if
if (ap34 - 48) * (ap34 - 48) + (ap35 - 103) * (ap35 - 103) <= 784 then
ap37 = ap37 + pairAnchorHp * 4
end if
end if
if defKind = 1 or defKind = 4 then
if defD < coreD then
coreId = objectId(defI)
coreD = defD
ap20 = ap34
ap21 = ap35
end if
end if
if defKind = 2 or defKind = 3 then
ap16 = ap34 - selfX
ap17 = ap35 - selfY
ap15 = ap16 * ap16 + ap17 * ap17
if ap15 <= 36 and ap15 < ap4 then
ap2 = objectId(defI)
ap4 = ap15
end if
end if
end if
end if
defI = defI + 1
wend
waveCached = 0
if defMates >= 4 then
waveCached = 1
end if
pairedRush = 0
if defCount >= 3 and ((coreDy - coreDx) * (coreDy - coreDx) + (coreY - coreX) * (coreY - coreX)) >= 1024 then
pairedRush = 1
end if
ap27 = (defPointX - 11) * (defPointX - 11) + (defPointY - 105) * (defPointY - 105)
defSentry = 0
if coreRespond >= 2 or coreValue < 400 then
defSentry = 1
end if
if worldTick <= ap13 or worldTick > ap13 + 1 then
ap7 = 0
ap5 = 0
ap3 = 0
end if
ap13 = worldTick
defGoalX = defPointX
defGoalY = defPointY
defSentryRole = 1
if waveCached then
if defSentry then
defSentryRole = 4
defGoalX = defFrontX
defGoalY = defFrontY
ap5 = 0
else
defSentryRole = 2
defGoalX = ap20
defGoalY = ap21
if ap27 <= 3600 then
if ap5 = 0 then
ap5 = worldTick
end if
if worldTick >= ap7 then
if ap7 > 0 then
if ap19 = 0 then
ap28 = ap28 + 800
end if
if ap19 = 1 then
ap36 = ap36 + 800
end if
if ap19 = 2 then
ap37 = ap37 + 800
end if
end if
ap19 = 0
ap25 = ap28
if ap36 < ap25 then
ap19 = 1
ap25 = ap36
end if
if ap37 < ap25 then
ap19 = 2
end if
ap7 = (worldTick / 240 + 1) * 240
end if
defGoalX = 8
defGoalY = 70
if ap19 = 1 then
defGoalX = 28
defGoalY = 79
end if
if ap19 = 2 then
defGoalX = 48
defGoalY = 103
end if
if ap10 >= 2 or pairedRush or worldTick - ap5 >= 480 then
ap3 = worldTick + 240
end if
if worldTick < ap3 then
defSentryRole = 3
defGoalX = ap20
defGoalY = ap21
end if
else
ap5 = 0
defSentryRole = 3
end if
end if
if defFront <> 0 then
bestId = defFront
bestDistance = defScore
else
if defSentryRole = 3 and coreD <= 784 then
bestId = coreId
bestDistance = coreD
end if
end if
else
ap3 = 0
end if
if bestId = 0 and ap2 <> 0 then
bestId = ap2
bestDistance = ap4
end if
defDx = selfX - defPointX
defDy = selfY - defPointY
gaTethered = 0
if defDx * defDx + defDy * defDy > 20 * 20 then
bestId = 0
defGoalX = defPointX
defGoalY = defPointY
gaTethered = 1
end if
end if
if gaActive = 0 then
ap24 = objectCount()
waveCached = 0
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
while defI < ap24 and defI < 2
if objectTeam(defI) = selfTeam and objectKind(defI) = 1 then
defHomeX = objectX(defI)
defHomeY = objectY(defI)
end if
defI = defI + 1
wend
defFront = 0
defFrontD = 100 * 100 + 1
defI = 0
while defI < ap24 and defI < 64
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
while defI < ap24 and defI < 64
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
if defAnchor <> 0 and (((adMode = 0 or adMode = 3) and defFrontD <= 3600 and defCount >= 2) or defCount >= defGroupSize or (worldTick < defUntil and defFrontD <= defContinueHome * defContinueHome)) then
defUntil = worldTick + defHoldTicks
if (adMode = 0 or adMode = 3) and defFrontD <= 3600 and defCount >= 2 then
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
ap23 = ap23 + 1
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
while defI < ap24
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
while defI < ap24 and defI < 64
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
ap22 = ap22 + 1
else
if selfClass = 9 or selfClass = 7 then
bestId = 0
bestDistance = 2147483647
waveCached = 1
waveChosen = 0
waveDistance = 2147483647
waveRetained = 0
waveHomeX = 64
waveHomeY = 64
defMates = 12 * 12 * 1
index = 0
while index < ap24
id = objectId(index)
if objectTeam(index) <> selfTeam then
if objectAlive(index) then
dx = objectX(index) - selfX
dy = objectY(index) - selfY
distance = dx * dx + dy * dy
if distance < bestDistance then
bestDistance = distance
bestId = id
macroSelectedKind = objectKind(index)
macroSelectedX = objectX(index)
macroSelectedY = objectY(index)
end if
end if
else
if bestId = 0 or bestDistance > defMates then
if objectHp(index) > 0 and objectAlive(index) then
waveKind = objectKind(index)
if waveKind = 1 then
waveHomeX = objectX(index)
waveHomeY = objectY(index)
end if
if waveKind = 3 then
if id = escortId then
waveRetained = 1
waveChosen = id
waveX = objectX(index)
waveY = objectY(index)
dx = waveX - selfX
dy = waveY - selfY
waveDistance = dx * dx + dy * dy
else
if waveRetained = 0 then
dx = objectX(index) - selfX
dy = objectY(index) - selfY
distance = dx * dx + dy * dy
if distance < waveDistance or (distance = waveDistance and id < waveChosen) then
waveChosen = id
waveDistance = distance
waveX = objectX(index)
waveY = objectY(index)
end if
end if
end if
end if
end if
else
waveCached = 0
end if
end if
index = index + 1
wend
else
bestId = 0
bestDistance = 2147483647
waveCached = 1
waveChosen = 0
waveDistance = 2147483647
waveRetained = 0
waveHomeX = 64
waveHomeY = 64
defMates = 12 * 12 * 1
index = 0
while index < ap24
id = objectId(index)
if objectTeam(index) <> selfTeam then
if objectAlive(index) and objectHp(index) > 0 then
dx = objectX(index) - selfX
dy = objectY(index) - selfY
buildingWeight = objectKind(index)
if buildingWeight = 1 or buildingWeight = 4 or buildingWeight = 5 then
if dx < 0 then
dx = -dx
end if
if dy < 0 then
dy = -dy
end if
buildingInset = 2
if buildingWeight = 1 then
buildingInset = 4
end if
dx = dx - buildingInset
dy = dy - buildingInset
if dx < 0 then
dx = 0
end if
if dy < 0 then
dy = 0
end if
distance = (dx * dx + dy * dy) * 1
else
distance = (dx * dx + dy * dy) * 1
end if
if distance < bestDistance then
bestDistance = distance
bestId = id
macroSelectedKind = objectKind(index)
macroSelectedX = objectX(index)
macroSelectedY = objectY(index)
end if
end if
else
if bestId = 0 or bestDistance > defMates then
if objectHp(index) > 0 and objectAlive(index) then
waveKind = objectKind(index)
if waveKind = 1 then
waveHomeX = objectX(index)
waveHomeY = objectY(index)
end if
if waveKind = 3 then
if id = escortId then
waveRetained = 1
waveChosen = id
waveX = objectX(index)
waveY = objectY(index)
dx = waveX - selfX
dy = waveY - selfY
waveDistance = dx * dx + dy * dy
else
if waveRetained = 0 then
dx = objectX(index) - selfX
dy = objectY(index) - selfY
distance = dx * dx + dy * dy
if distance < waveDistance or (distance = waveDistance and id < waveChosen) then
waveChosen = id
waveDistance = distance
waveX = objectX(index)
waveY = objectY(index)
end if
end if
end if
end if
end if
else
waveCached = 0
end if
end if
index = index + 1
wend
end if
if bestId <> 0 then
if macroSelectedKind = 2 or macroSelectedKind = 3 then
macroDx = macroSelectedX - selfX
macroDy = macroSelectedY - selfY
if macroDx * macroDx + macroDy * macroDy > 12 * 12 then
bestId = 0
end if
end if
end if
end if
else
ap31 = 0
ap36 = 24 * 24
ap37 = 32 * 32
if 2 = 2 or selfTeam = 2 then
ap31 = 1
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
ap18 = 0
ap7 = 0
ap19 = 0
ap5 = 0
ap13 = 0
ap3 = 0
end if
defLastTick = worldTick
defHomeX = 105
defHomeY = 11
if selfTeam = 1 then
defHomeX = 11
defHomeY = 105
end if
defI = 0
while defI < ap24 and defI < 2
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
while defI < ap24 and defI < 64
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
while defI < ap24 and defI < 64
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
if defAnchor <> 0 and (((adMode = 0 or adMode = 3) and defFrontD <= 3600 and defCount >= 2) or pairedRush or middleRush or defCount >= defGroupSize or (worldTick < defUntil and defFrontD <= defContinueHome * defContinueHome)) then
ap26 = defAnchor
ap38 = defAnchorX
ap39 = defAnchorY
defUntil = worldTick + defHoldTicks
if (adMode = 0 or adMode = 3) and defFrontD <= 3600 and defCount >= 2 then
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
ap23 = ap23 + 1
end if
end if
ap1 = 0
if worldTick >= ap18 then
ap3 = 0
end if
ap6 = 1
ap8 = 28
ap9 = 29
if selfTeam = 1 then
ap6 = 2
ap8 = 30
ap9 = 31
end if
if defCount >= defGroupSize then
ap18 = 0
ap7 = defUntil
end if
if selfTeam = 1 and defCount <= 1 and defFront <> 0 and defFrontD <= 24 * 24 then
if defAnchor = defFrontTarget and (defFrontTarget = ap6 or defFrontTarget = ap8 or defFrontTarget = ap9) then
ap16 = selfX - defHomeX
ap17 = selfY - defHomeY
ap15 = ap16 * ap16 + ap17 * ap17
if ap19 <> defFront or worldTick > ap13 + 72 then
ap5 = worldTick
end if
ap19 = defFront
ap13 = worldTick
ap14 = 0
ap10 = 0
ap11 = 0
while ap11 < ap24 and ap11 < 64
ap12 = objectKind(ap11)
if ap12 = 3 then
ap11 = 64
else
if ap12 = 2 and objectTeam(ap11) = selfTeam and objectHp(ap11) > 0 and objectAlive(ap11) then
ap2 = objectId(ap11)
if ap2 <> selfId then
ap20 = objectX(ap11) - defHomeX
ap21 = objectY(ap11) - defHomeY
ap4 = ap20 * ap20 + ap21 * ap21
if ap4 < ap15 or (ap4 = ap15 and ap2 < selfId) then
ap14 = ap14 + 1
end if
if objectTarget(ap11) = defFront then
ap10 = ap10 + 1
end if
end if
end if
end if
ap11 = ap11 + 1
wend
ap0 = 0
if ap15 <= 28 * 28 or ap3 = defFront then
ap0 = 1
end if
if ap10 = 0 and worldTick >= ap5 + ap14 * 96 then
ap0 = 1
end if
if ap0 then
ap3 = defFront
ap1 = 1
defThreatX = defFrontX
defThreatY = defFrontY
defPointX = defFrontX
defPointY = defFrontY
if defCount < defGroupSize and worldTick >= ap7 then
ap18 = worldTick + 480
end if
end if
end if
end if
if ap18 > 0 then
defUntil = ap18
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
ap27 = 32
if 10 > ap27 then
ap27 = 10
end if
if coreRespond and 24 + 14 > ap27 then
ap27 = 24 + 14
end if
ap28 = ap27 * ap27
if ap26 = 0 then
ap26 = coreHomeId
ap38 = defHomeX
ap39 = defHomeY
end if
if selfTeam = 1 then
defDx = selfX - defHomeX
defDy = selfY - defHomeY
if defDx * defDx + defDy * defDy > 28 * 28 and adMode <> 1 and worldTick >= criticalUntil then
defActive = 0
defUntil = 0
ap18 = 0
ap1 = 0
end if
end if

if defActive then

bestId = 0
bestDistance = 2147483647
defI = 0
while defI < ap24
defKind = objectKind(defI)
if ap31 and (defKind = 1 or defKind = 4) then
if objectId(defI) = ap26 and objectHp(defI) <= 0 then
ap26 = coreHomeId
ap38 = defHomeX
ap39 = defHomeY
end if
end if
if defKind = 2 or defKind = 3 then
if objectTeam(defI) <> selfTeam then
ap34 = objectX(defI)
ap35 = objectY(defI)
defDx = ap34 - selfX
defDy = ap35 - selfY
defD = defDx * defDx + defDy * defDy
if defD <= ap28 then
if objectAlive(defI) and objectHp(defI) > 0 then
if coreRespond then
coreDx = ap34 - defHomeX
coreDy = ap35 - defHomeY
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
coreX = ap34
coreY = ap35
end if
end if
end if
end if
ap25 = 0
if ap31 and defD <= ap37 then
ap29 = ap34 - ap38
ap30 = ap35 - ap39
if ap29 * ap29 + ap30 * ap30 <= ap36 then
ap25 = 1
end if
end if
defGroupD = 0
if ap25 = 0 then
defGx = ap34 - defThreatX
defGy = ap35 - defThreatY
defGroupD = defGx * defGx + defGy * defGy
end if
if ap25 or (defD <= 10 * 10 and (defGroupD <= 400 or defD <= 9)) then
defScore = defD * 10 + objectHp(defI) * 1
if (adMode <> 1 and defKind = 3) or (adMode = 1 and defKind = 2) then
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
while defI < ap24 and defI < 64
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
ap22 = ap22 + 1
else
if selfClass = 9 or selfClass = 7 then
bestId = 0
bestDistance = 2147483647
waveCached = 1
waveChosen = 0
waveDistance = 2147483647
waveRetained = 0
waveHomeX = 64
waveHomeY = 64
defMates = 12 * 12 * 1
index = 0
while index < ap24
id = objectId(index)
if objectTeam(index) <> selfTeam then
if objectAlive(index) then
dx = objectX(index) - selfX
dy = objectY(index) - selfY
distance = dx * dx + dy * dy
if distance < bestDistance then
bestDistance = distance
bestId = id
macroSelectedKind = objectKind(index)
macroSelectedX = objectX(index)
macroSelectedY = objectY(index)
end if
end if
else
if bestId = 0 or bestDistance > defMates then
if objectHp(index) > 0 and objectAlive(index) then
waveKind = objectKind(index)
if waveKind = 1 then
waveHomeX = objectX(index)
waveHomeY = objectY(index)
end if
if waveKind = 3 then
if id = escortId then
waveRetained = 1
waveChosen = id
waveX = objectX(index)
waveY = objectY(index)
dx = waveX - selfX
dy = waveY - selfY
waveDistance = dx * dx + dy * dy
else
if waveRetained = 0 then
dx = objectX(index) - selfX
dy = objectY(index) - selfY
distance = dx * dx + dy * dy
if distance < waveDistance or (distance = waveDistance and id < waveChosen) then
waveChosen = id
waveDistance = distance
waveX = objectX(index)
waveY = objectY(index)
end if
end if
end if
end if
end if
else
waveCached = 0
end if
end if
index = index + 1
wend
else
bestId = 0
bestDistance = 2147483647
waveCached = 1
waveChosen = 0
waveDistance = 2147483647
waveRetained = 0
waveHomeX = 64
waveHomeY = 64
defMates = 12 * 12 * 1
index = 0
while index < ap24
id = objectId(index)
if objectTeam(index) <> selfTeam then
if objectAlive(index) and objectHp(index) > 0 then
dx = objectX(index) - selfX
dy = objectY(index) - selfY
buildingWeight = objectKind(index)
if buildingWeight = 1 or buildingWeight = 4 or buildingWeight = 5 then
if dx < 0 then
dx = -dx
end if
if dy < 0 then
dy = -dy
end if
buildingInset = 2
if buildingWeight = 1 then
buildingInset = 4
end if
dx = dx - buildingInset
dy = dy - buildingInset
if dx < 0 then
dx = 0
end if
if dy < 0 then
dy = 0
end if
distance = (dx * dx + dy * dy) * 1
else
distance = (dx * dx + dy * dy) * 1
end if
if distance < bestDistance then
bestDistance = distance
bestId = id
macroSelectedKind = objectKind(index)
macroSelectedX = objectX(index)
macroSelectedY = objectY(index)
end if
end if
else
if bestId = 0 or bestDistance > defMates then
if objectHp(index) > 0 and objectAlive(index) then
waveKind = objectKind(index)
if waveKind = 1 then
waveHomeX = objectX(index)
waveHomeY = objectY(index)
end if
if waveKind = 3 then
if id = escortId then
waveRetained = 1
waveChosen = id
waveX = objectX(index)
waveY = objectY(index)
dx = waveX - selfX
dy = waveY - selfY
waveDistance = dx * dx + dy * dy
else
if waveRetained = 0 then
dx = objectX(index) - selfX
dy = objectY(index) - selfY
distance = dx * dx + dy * dy
if distance < waveDistance or (distance = waveDistance and id < waveChosen) then
waveChosen = id
waveDistance = distance
waveX = objectX(index)
waveY = objectY(index)
end if
end if
end if
end if
end if
else
waveCached = 0
end if
end if
index = index + 1
wend
end if
if bestId <> 0 then
if macroSelectedKind = 2 or macroSelectedKind = 3 then
macroDx = macroSelectedX - selfX
macroDy = macroSelectedY - selfY
if macroDx * macroDx + macroDy * macroDy > 12 * 12 then
bestId = 0
end if
end if
end if
end if
if coreId <> 0 then
bestId = coreId
bestDistance = coreScore
defPointX = coreX
defPointY = coreY
defThreatX = coreX
defThreatY = coreY
end if

if ap1 and coreId = 0 then
bestId = defFront
bestDistance = defFrontD
end if

if worldTick <= ap33 then
ap32 = 0
end if
ap33 = worldTick
if defActive = 0 or bestId <> 0 or ap32 = 0 then
ap32 = worldTick
end if
if ap31 and defActive and bestId = 0 and 1 > 0 then
if 1 = 2 or defSentry = 0 then
if worldTick - ap32 >= 480 then
defActive = 0
defUntil = 0
ap18 = 0
ap7 = 0
end if
end if
end if
end if
defActive = defActive
end if

' @rule R_profile_transit
transitActive = 0
if selfTeam = 0 and gaActive = 0 and adMode <> 3 then
transitActive = 0
transitX = 58
transitY = 56
if selfTeam = 0 and (selfClass = 7 or selfClass = 8) then
if worldTick <= 1800 and transitDone = 0 then
mDx = selfX - transitX
mDy = selfY - transitY
if mDx * mDx + mDy * mDy <= 6 * 6 then
transitDone = 1
else
if defActive = 0 then
transitActive = 1
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
    mMin = 0
    mSum = 2147483647
    mIndex = 0
    while mIndex < objectCount() and mIndex < 64
      mKind = objectKind(mIndex)
      if mKind = 3 then
        mIndex = 64
      else
        if mKind = 2 and objectTeam(mIndex) <> selfTeam and objectHp(mIndex) > 0 and objectHp(mIndex) < mSum then
          mId = objectTarget(mIndex)
          if mId <> 0 and mId <> selfId then
            mDx = objectX(mIndex) - selfX
            mDy = objectY(mIndex) - selfY
            if mDx * mDx + mDy * mDy <= 8 * 8 then
              mStep = 0
              while mStep < objectCount() and mStep < 64
                if objectKind(mStep) = 3 then
                  mStep = 64
                else
                  if objectId(mStep) = mId and objectKind(mStep) = 2 and objectTeam(mStep) = selfTeam and objectHp(mStep) > 0 then
                    mMin = objectId(mIndex)
                    mSum = objectHp(mIndex)
                  end if
                end if
                mStep = mStep + 1
              wend
            end if
          end if
        end if
      end if
      mIndex = mIndex + 1
    wend
    if mMin <> 0 and selfHp * 100 >= selfMaxHp * 25 then
      bestId = mMin
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
  if transitActive then
  moveAccepted = walkTo(transitX, transitY)
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
  if waveCached then
  chosenId = waveChosen
  chosenDistance = waveDistance
  retained = waveRetained
  homeX = waveHomeX
  homeY = waveHomeY
  if chosenId <> 0 then
  escortX = waveX
  escortY = waveY
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
  end if
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
  if ap31 and 0 = 1 then
  defGoalX = ap38
  defGoalY = ap39
  if defThreatX > ap38 then
  defGoalX = defGoalX + 3
  else
  defGoalX = defGoalX - 3
  end if
  if defThreatY > ap39 then
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
  if waveCached then
  chosenId = waveChosen
  chosenDistance = waveDistance
  retained = waveRetained
  homeX = waveHomeX
  homeY = waveHomeY
  if chosenId <> 0 then
  escortX = waveX
  escortY = waveY
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
  end if
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
end if

' @rule R_profile_tower
if selfTeam = 0 and gaActive = 0 then
if selfTeam = 0 then
ap43 = 0
if worldTick <> ap47 + 1 then
ap48 = 0
ap46 = 0
end if
ap47 = worldTick
if ap48 > 0 and worldTick >= ap48 then
ap48 = 0
ap46 = worldTick + 48
end if
if worldTick < ap48 or (worldTick >= ap46 and bestId <> 0 and selfHp * 100 <= selfMaxHp * 50) then
mThreat = bestId
if worldTick < ap48 then
mThreat = ap45
end if
mFound = 0
mIndex = 0
while mIndex < objectCount() and mIndex < 64 and mFound = 0
if objectId(mIndex) = mThreat then
if objectKind(mIndex) = 4 and objectTeam(mIndex) <> selfTeam and objectHp(mIndex) > 0 and objectTarget(mIndex) = selfId then
if worldTick < ap48 or (objectHp(mIndex) > 150 and objectHp(mIndex) > selfAttackDamage * 2) then
mFound = 1
mThreatX = objectX(mIndex)
mThreatY = objectY(mIndex)
end if
end if
mIndex = 64
end if
mIndex = mIndex + 1
wend
if mFound = 0 then
if worldTick < ap48 then
ap46 = worldTick + 48
end if
ap48 = 0
else
if worldTick >= ap48 then
if 1 then
mFound = 0
mIndex = 0
while mIndex < objectCount() and mIndex < 64 and mFound = 0
if objectKind(mIndex) = 3 and objectTeam(mIndex) = selfTeam and objectAlive(mIndex) and objectHp(mIndex) > 0 then
mDx = objectX(mIndex) - mThreatX
mDy = objectY(mIndex) - mThreatY
if mDx * mDx + mDy * mDy <= 4 * 4 then
mFound = 1
end if
end if
mIndex = mIndex + 1
wend
end if
if mFound then
mFound = 0
mBestScore = 2147483647
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
mTryX = mThreatX + mDirX * 8
mTryY = mThreatY + mDirY * 8
if terrainWalkable(mTryX, mTryY) then
mDx = mTryX - selfX
mDy = mTryY - selfY
mD = mDx * mDx + mDy * mDy
if mD < mBestScore then
mBestScore = mD
ap41 = mTryX
ap42 = mTryY
mFound = 1
end if
end if
mdirection = mdirection + 1
wend
if mFound then
ap45 = mThreat
ap48 = worldTick + 144
ap40 = ap40 + 1
else
ap46 = worldTick + 48
end if
end if
end if
if worldTick < ap48 then
if walkTo(ap41, ap42) then
ap43 = 1
ap44 = ap44 + 1
else
ap48 = 0
ap46 = worldTick + 48
end if
end if
end if
end if
end if
end if
