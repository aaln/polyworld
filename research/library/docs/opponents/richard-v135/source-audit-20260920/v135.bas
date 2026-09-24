' Shared observation/action contract for native training and BASIC deployment.
dim f(25)
bestId = 0
bestDistance = 2147483647
objectiveId = 0
objectiveKind = 0
siegeThreatId = 0
siegeThreatHp = 2147483647
objectiveDistance = 2147483647
heroId = 0
heroDistance = 2147483647
enemyX = selfX
enemyY = selfY
enemyHp = 0
enemyKind = 0
enemyAttackTarget = 0
routeOpeningX = 71
routeOpeningY = 12
if selfTeam = 1 then
  routeOpeningX = 45
  routeOpeningY = 104
end if
routeGroupCount = 0
allyCount = 0
allyX = 0
allyY = 0
maxAllyDistance = 0
index = 0
while index < objectCount()
  if objectAlive(index) then
    if objectTeam(index) = selfTeam and objectKind(index) = 2 then
      allyCount = allyCount + 1
      routeDx = objectX(index) - routeOpeningX
      routeDy = objectY(index) - routeOpeningY
      if routeDx * routeDx + routeDy * routeDy <= 16 then
        routeGroupCount = routeGroupCount + 1
      end if
      allyX = allyX + objectX(index)
      allyY = allyY + objectY(index)
      dx = objectX(index) - selfX
      dy = objectY(index) - selfY
      distance = dx * dx + dy * dy
      if distance > maxAllyDistance then
        maxAllyDistance = distance
      end if
    end if
    if objectTeam(index) <> selfTeam then
      dx = objectX(index) - selfX
      dy = objectY(index) - selfY
      distance = dx * dx + dy * dy
      if distance < bestDistance then
        bestDistance = distance
        bestId = objectId(index)
        enemyX = objectX(index)
        enemyY = objectY(index)
        enemyHp = objectHp(index)
        enemyKind = objectKind(index)
        enemyAttackTarget = objectTarget(index)
      end if
      if objectKind(index) = 2 and objectTarget(index) = selfId then
        siegeRange = selfAttackRange / 1000
        if distance * 3600 <= siegeRange * siegeRange and objectHp(index) < siegeThreatHp then
          siegeThreatId = objectId(index)
          siegeThreatHp = objectHp(index)
        end if
      end if
      if objectKind(index) = 1 or objectKind(index) = 4 then
        if distance < objectiveDistance then
          objectiveDistance = distance
          objectiveId = objectId(index)
          objectiveKind = objectKind(index)
        end if
      end if
      if objectKind(index) = 2 and distance < heroDistance then
        heroDistance = distance
        heroId = objectId(index)
        ringHeroX = objectX(index)
        ringHeroY = objectY(index)
        ringHeroTarget = objectTarget(index)
      end if
    end if
  end if
  index = index + 1
wend
if allyCount > 0 then
  allyX = allyX / allyCount
  allyY = allyY / allyCount
else
  allyX = selfX
  allyY = selfY
end if
f(0) = selfHp * 100 / selfMaxHp
f(1) = 0
if selfMaxMana > 0 then
  f(1) = selfMana * 100 / selfMaxMana
end if
f(2) = maxAllyDistance / 100
f(3) = selfLevel * 5
f(4) = allyX - selfX
f(5) = allyY - selfY
f(6) = enemyX - selfX
f(7) = enemyY - selfY
f(8) = enemyHp / 10
f(9) = enemyKind * 25
if selfTeam = 1 then
  f(4) = 0 - f(4)
  f(5) = 0 - f(5)
  f(6) = 0 - f(6)
  f(7) = 0 - f(7)
end if
f(10) = worldTick / 288
f(11) = abilityCharges(0) * 25
f(12) = abilityCharges(1) * 25
f(13) = abilityCharges(2) * 25
f(14) = abilityCharges(3) * 25
f(15 + selfClass) = 100
index = 0
while index < 25
  if f(index) > 100 then
    f(index) = 100
  end if
  if f(index) < -100 then
    f(index) = -100
  end if
  index = index + 1
wend
dim h(16)
neuralActionCountdown = neuralActionCountdown - 1
if neuralActionCountdown <= 0 then
  neuralActionCountdown = 4
h(0) = 16496 + f(0) * (250) + f(1) * (210) + f(2) * (-70) + f(3) * (-20) + f(4) * (130) + f(5) * (180) + f(6) * (-720) + f(7) * (510) + f(8) * (170) + f(9) * (630) + f(10) * (310) + f(11) * (50) + f(12) * (80) + f(13) * (-160) + f(14) * (210) + f(15) * (20) + f(16) * (-500) + f(17) * (180) + f(18) * (-41) + f(19) * (300) + f(20) * (630) + f(21) * (80) + f(22) * (550) + f(23) * (10) + f(24) * (260)
if h(0) < 0 then
  h(0) = 0
end if
h(1) = 17275 + f(0) * (120) + f(1) * (-30) + f(2) * (110) + f(3) * (-30) + f(4) * (560) + f(5) * (-300) + f(6) * (-380) + f(7) * (160) + f(8) * (230) + f(9) * (20) + f(10) * (30) + f(11) * (-220) + f(12) * (660) + f(13) * (90) + f(14) * (610) + f(15) * (430) + f(16) * (430) + f(17) * (240) + f(18) * (229) + f(19) * (-350) + f(20) * (170) + f(21) * (-80) + f(22) * (80) + f(23) * (-530) + f(24) * (320)
if h(1) < 0 then
  h(1) = 0
end if
h(2) = -226 + f(0) * (-380) + f(1) * (-30) + f(2) * (-190) + f(3) * (160) + f(4) * (70) + f(5) * (720) + f(6) * (-10) + f(7) * (60) + f(8) * (80) + f(9) * (-560) + f(10) * (-260) + f(11) * (-80) + f(12) * (-40) + f(13) * (-50) + f(14) * (-320) + f(15) * (-350) + f(16) * (-320) + f(17) * (-10) + f(18) * (450) + f(19) * (-40) + f(20) * (-130) + f(21) * (180) + f(22) * (-70) + f(23) * (-520) + f(24) * (-20)
if h(2) < 0 then
  h(2) = 0
end if
h(3) = 18141 + f(0) * (180) + f(1) * (150) + f(2) * (-300) + f(3) * (50) + f(4) * (-180) + f(5) * (-120) + f(6) * (220) + f(7) * (10) + f(8) * (-30) + f(9) * (380) + f(10) * (440) + f(11) * (50) + f(12) * (390) + f(13) * (230) + f(14) * (-10) + f(15) * (-700) + f(16) * (110) + f(17) * (360) + f(18) * (-211) + f(19) * (-140) + f(20) * (-150) + f(21) * (-500) + f(22) * (130) + f(23) * (-40) + f(24) * (-10)
if h(3) < 0 then
  h(3) = 0
end if
h(4) = 16850 + f(0) * (420) + f(1) * (-90) + f(2) * (100) + f(3) * (-120) + f(4) * (150) + f(5) * (-310) + f(6) * (-400) + f(7) * (330) + f(8) * (220) + f(9) * (-120) + f(10) * (-290) + f(11) * (-130) + f(12) * (720) + f(13) * (380) + f(14) * (-190) + f(15) * (-190) + f(16) * (100) + f(17) * (380) + f(18) * (199) + f(19) * (550) + f(20) * (180) + f(21) * (320) + f(22) * (30) + f(23) * (640) + f(24) * (-150)
if h(4) < 0 then
  h(4) = 0
end if
h(5) = 16829 + f(0) * (350) + f(1) * (150) + f(2) * (390) + f(3) * (330) + f(4) * (-80) + f(5) * (-350) + f(6) * (-230) + f(7) * (150) + f(8) * (-30) + f(9) * (630) + f(10) * (130) + f(11) * (-440) + f(12) * (-360) + f(13) * (170) + f(14) * (240) + f(15) * (-350) + f(16) * (400) + f(17) * (460) + f(18) * (689) + f(19) * (50) + f(20) * (120) + f(21) * (540) + f(22) * (50) + f(23) * (-80) + f(24) * (60)
if h(5) < 0 then
  h(5) = 0
end if
h(6) = 21361 + f(0) * (110) + f(1) * (-170) + f(2) * (-140) + f(3) * (190) + f(4) * (-90) + f(5) * (-500) + f(6) * (590) + f(7) * (590) + f(8) * (290) + f(9) * (220) + f(10) * (-40) + f(11) * (-390) + f(12) * (-40) + f(13) * (-170) + f(14) * (-300) + f(15) * (370) + f(16) * (120) + f(17) * (-140) + f(18) * (-61) + f(19) * (230) + f(20) * (140) + f(21) * (170) + f(22) * (0) + f(23) * (60) + f(24) * (720)
if h(6) < 0 then
  h(6) = 0
end if
h(7) = 17677 + f(0) * (-100) + f(1) * (480) + f(2) * (340) + f(3) * (350) + f(4) * (90) + f(5) * (-310) + f(6) * (-150) + f(7) * (-60) + f(8) * (230) + f(9) * (-180) + f(10) * (240) + f(11) * (-120) + f(12) * (130) + f(13) * (450) + f(14) * (380) + f(15) * (20) + f(16) * (20) + f(17) * (200) + f(18) * (-121) + f(19) * (470) + f(20) * (-360) + f(21) * (300) + f(22) * (940) + f(23) * (120) + f(24) * (510)
if h(7) < 0 then
  h(7) = 0
end if
h(8) = 16495 + f(0) * (90) + f(1) * (40) + f(2) * (170) + f(3) * (-190) + f(4) * (-340) + f(5) * (510) + f(6) * (-110) + f(7) * (400) + f(8) * (170) + f(9) * (620) + f(10) * (-60) + f(11) * (250) + f(12) * (320) + f(13) * (240) + f(14) * (0) + f(15) * (500) + f(16) * (720) + f(17) * (310) + f(18) * (139) + f(19) * (280) + f(20) * (-270) + f(21) * (240) + f(22) * (550) + f(23) * (-20) + f(24) * (-60)
if h(8) < 0 then
  h(8) = 0
end if
h(9) = 17398 + f(0) * (400) + f(1) * (460) + f(2) * (160) + f(3) * (50) + f(4) * (20) + f(5) * (-10) + f(6) * (-250) + f(7) * (-170) + f(8) * (50) + f(9) * (50) + f(10) * (-30) + f(11) * (-100) + f(12) * (-120) + f(13) * (-410) + f(14) * (60) + f(15) * (560) + f(16) * (-100) + f(17) * (550) + f(18) * (429) + f(19) * (330) + f(20) * (-340) + f(21) * (-469) + f(22) * (-20) + f(23) * (350) + f(24) * (120)
if h(9) < 0 then
  h(9) = 0
end if
h(10) = 16466 + f(0) * (850) + f(1) * (370) + f(2) * (120) + f(3) * (400) + f(4) * (-280) + f(5) * (160) + f(6) * (100) + f(7) * (460) + f(8) * (-150) + f(9) * (-170) + f(10) * (670) + f(11) * (-60) + f(12) * (520) + f(13) * (330) + f(14) * (110) + f(15) * (470) + f(16) * (-80) + f(17) * (380) + f(18) * (239) + f(19) * (-170) + f(20) * (180) + f(21) * (440) + f(22) * (140) + f(23) * (160) + f(24) * (270)
if h(10) < 0 then
  h(10) = 0
end if
h(11) = 20510 + f(0) * (100) + f(1) * (-680) + f(2) * (280) + f(3) * (100) + f(4) * (-210) + f(5) * (50) + f(6) * (-550) + f(7) * (-250) + f(8) * (-300) + f(9) * (-50) + f(10) * (739) + f(11) * (-10) + f(12) * (110) + f(13) * (30) + f(14) * (110) + f(15) * (30) + f(16) * (300) + f(17) * (-360) + f(18) * (409) + f(19) * (280) + f(20) * (10) + f(21) * (-150) + f(22) * (150) + f(23) * (310) + f(24) * (270)
if h(11) < 0 then
  h(11) = 0
end if
h(12) = 18131 + f(0) * (-200) + f(1) * (330) + f(2) * (-140) + f(3) * (-280) + f(4) * (-140) + f(5) * (-320) + f(6) * (90) + f(7) * (70) + f(8) * (-690) + f(9) * (220) + f(10) * (-91) + f(11) * (400) + f(12) * (280) + f(13) * (50) + f(14) * (490) + f(15) * (230) + f(16) * (-260) + f(17) * (-40) + f(18) * (399) + f(19) * (120) + f(20) * (120) + f(21) * (560) + f(22) * (60) + f(23) * (190) + f(24) * (130)
if h(12) < 0 then
  h(12) = 0
end if
h(13) = 19594 + f(0) * (-60) + f(1) * (110) + f(2) * (60) + f(3) * (180) + f(4) * (830) + f(5) * (50) + f(6) * (-90) + f(7) * (-90) + f(8) * (-130) + f(9) * (440) + f(10) * (410) + f(11) * (-470) + f(12) * (10) + f(13) * (390) + f(14) * (-260) + f(15) * (470) + f(16) * (30) + f(17) * (-50) + f(18) * (-111) + f(19) * (-240) + f(20) * (-40) + f(21) * (340) + f(22) * (200) + f(23) * (480) + f(24) * (-280)
if h(13) < 0 then
  h(13) = 0
end if
h(14) = 16487 + f(0) * (420) + f(1) * (470) + f(2) * (390) + f(3) * (-710) + f(4) * (80) + f(5) * (110) + f(6) * (-90) + f(7) * (-250) + f(8) * (540) + f(9) * (190) + f(10) * (340) + f(11) * (80) + f(12) * (160) + f(13) * (70) + f(14) * (-90) + f(15) * (-120) + f(16) * (170) + f(17) * (-210) + f(18) * (259) + f(19) * (-150) + f(20) * (70) + f(21) * (410) + f(22) * (40) + f(23) * (250) + f(24) * (600)
if h(14) < 0 then
  h(14) = 0
end if
h(15) = 16936 + f(0) * (640) + f(1) * (150) + f(2) * (-280) + f(3) * (330) + f(4) * (200) + f(5) * (-540) + f(6) * (-440) + f(7) * (210) + f(8) * (250) + f(9) * (60) + f(10) * (190) + f(11) * (590) + f(12) * (-60) + f(13) * (50) + f(14) * (-190) + f(15) * (190) + f(16) * (200) + f(17) * (-360) + f(18) * (339) + f(19) * (-60) + f(20) * (-280) + f(21) * (290) + f(22) * (420) + f(23) * (-80) + f(24) * (-190)
if h(15) < 0 then
  h(15) = 0
end if
decision = 0
bestScore = -2147483647
score = 389152145 + h(0) * (-130) + h(1) * (-130) + h(2) * (-9) + h(3) * (-150) + h(4) * (-120) + h(5) * (-140) + h(6) * (-190) + h(7) * (-130) + h(8) * (-120) + h(9) * (-130) + h(10) * (-110) + h(11) * (-200) + h(12) * (-140) + h(13) * (-180) + h(14) * (-120) + h(15) * (-130)
if score > bestScore then
  bestScore = score
  decision = 0
end if
score = 8727132 + h(0) * (110) + h(1) * (100) + h(2) * (10) + h(3) * (100) + h(4) * (90) + h(5) * (110) + h(6) * (80) + h(7) * (90) + h(8) * (100) + h(9) * (100) + h(10) * (90) + h(11) * (80) + h(12) * (120) + h(13) * (110) + h(14) * (100) + h(15) * (100)
if score > bestScore then
  bestScore = score
  decision = 1
end if
score = 10047098 + h(0) * (120) + h(1) * (130) + h(2) * (0) + h(3) * (130) + h(4) * (110) + h(5) * (130) + h(6) * (110) + h(7) * (120) + h(8) * (120) + h(9) * (120) + h(10) * (110) + h(11) * (100) + h(12) * (110) + h(13) * (150) + h(14) * (110) + h(15) * (120)
if score > bestScore then
  bestScore = score
  decision = 2
end if
score = 10065948 + h(0) * (120) + h(1) * (130) + h(2) * (20) + h(3) * (130) + h(4) * (110) + h(5) * (130) + h(6) * (100) + h(7) * (120) + h(8) * (110) + h(9) * (110) + h(10) * (100) + h(11) * (80) + h(12) * (110) + h(13) * (120) + h(14) * (120) + h(15) * (120)
if score > bestScore then
  bestScore = score
  decision = 3
end if
score = 10539941 + h(0) * (110) + h(1) * (120) + h(2) * (20) + h(3) * (130) + h(4) * (110) + h(5) * (130) + h(6) * (100) + h(7) * (110) + h(8) * (110) + h(9) * (120) + h(10) * (100) + h(11) * (90) + h(12) * (110) + h(13) * (139) + h(14) * (110) + h(15) * (120)
if score > bestScore then
  bestScore = score
  decision = 4
end if
score = 9827147 + h(0) * (120) + h(1) * (120) + h(2) * (-10) + h(3) * (120) + h(4) * (100) + h(5) * (110) + h(6) * (110) + h(7) * (120) + h(8) * (110) + h(9) * (110) + h(10) * (100) + h(11) * (70) + h(12) * (110) + h(13) * (130) + h(14) * (110) + h(15) * (110)
if score > bestScore then
  bestScore = score
  decision = 5
end if
score = 10406481 + h(0) * (120) + h(1) * (120) + h(2) * (-1) + h(3) * (130) + h(4) * (120) + h(5) * (120) + h(6) * (110) + h(7) * (120) + h(8) * (120) + h(9) * (120) + h(10) * (110) + h(11) * (110) + h(12) * (120) + h(13) * (140) + h(14) * (110) + h(15) * (120)
if score > bestScore then
  bestScore = score
  decision = 6
end if
score = 8779395 + h(0) * (110) + h(1) * (100) + h(2) * (-10) + h(3) * (109) + h(4) * (100) + h(5) * (99) + h(6) * (80) + h(7) * (99) + h(8) * (109) + h(9) * (100) + h(10) * (100) + h(11) * (70) + h(12) * (110) + h(13) * (110) + h(14) * (99) + h(15) * (109)
if score > bestScore then
  bestScore = score
  decision = 7
end if
score = 10008186 + h(0) * (120) + h(1) * (130) + h(2) * (0) + h(3) * (130) + h(4) * (110) + h(5) * (130) + h(6) * (110) + h(7) * (120) + h(8) * (120) + h(9) * (120) + h(10) * (110) + h(11) * (100) + h(12) * (110) + h(13) * (150) + h(14) * (110) + h(15) * (120)
if score > bestScore then
  bestScore = score
  decision = 8
end if
score = 389152241 + h(0) * (-130) + h(1) * (-130) + h(2) * (-9) + h(3) * (-150) + h(4) * (-120) + h(5) * (-140) + h(6) * (-190) + h(7) * (-130) + h(8) * (-120) + h(9) * (-130) + h(10) * (-110) + h(11) * (-200) + h(12) * (-140) + h(13) * (-180) + h(14) * (-120) + h(15) * (-130)
if score > bestScore then
  bestScore = score
  decision = 9
end if
score = 8727232 + h(0) * (110) + h(1) * (100) + h(2) * (10) + h(3) * (100) + h(4) * (90) + h(5) * (110) + h(6) * (80) + h(7) * (90) + h(8) * (100) + h(9) * (100) + h(10) * (90) + h(11) * (80) + h(12) * (120) + h(13) * (110) + h(14) * (100) + h(15) * (100)
if score > bestScore then
  bestScore = score
  decision = 10
end if
score = 10047197 + h(0) * (120) + h(1) * (130) + h(2) * (0) + h(3) * (130) + h(4) * (110) + h(5) * (130) + h(6) * (110) + h(7) * (120) + h(8) * (120) + h(9) * (120) + h(10) * (110) + h(11) * (100) + h(12) * (110) + h(13) * (150) + h(14) * (110) + h(15) * (120)
if score > bestScore then
  bestScore = score
  decision = 11
end if
score = 10066048 + h(0) * (120) + h(1) * (130) + h(2) * (20) + h(3) * (130) + h(4) * (110) + h(5) * (130) + h(6) * (100) + h(7) * (120) + h(8) * (110) + h(9) * (110) + h(10) * (100) + h(11) * (80) + h(12) * (110) + h(13) * (120) + h(14) * (120) + h(15) * (120)
if score > bestScore then
  bestScore = score
  decision = 12
end if
score = 10540041 + h(0) * (110) + h(1) * (120) + h(2) * (20) + h(3) * (130) + h(4) * (110) + h(5) * (130) + h(6) * (100) + h(7) * (110) + h(8) * (110) + h(9) * (120) + h(10) * (100) + h(11) * (90) + h(12) * (110) + h(13) * (139) + h(14) * (110) + h(15) * (120)
if score > bestScore then
  bestScore = score
  decision = 13
end if
score = 9827247 + h(0) * (120) + h(1) * (120) + h(2) * (-10) + h(3) * (120) + h(4) * (100) + h(5) * (110) + h(6) * (110) + h(7) * (120) + h(8) * (110) + h(9) * (110) + h(10) * (100) + h(11) * (70) + h(12) * (110) + h(13) * (130) + h(14) * (110) + h(15) * (110)
if score > bestScore then
  bestScore = score
  decision = 14
end if
score = 10406581 + h(0) * (120) + h(1) * (120) + h(2) * (-1) + h(3) * (130) + h(4) * (120) + h(5) * (120) + h(6) * (110) + h(7) * (120) + h(8) * (120) + h(9) * (120) + h(10) * (110) + h(11) * (110) + h(12) * (120) + h(13) * (140) + h(14) * (110) + h(15) * (120)
if score > bestScore then
  bestScore = score
  decision = 15
end if
score = 8779494 + h(0) * (110) + h(1) * (100) + h(2) * (-10) + h(3) * (109) + h(4) * (100) + h(5) * (99) + h(6) * (80) + h(7) * (99) + h(8) * (109) + h(9) * (100) + h(10) * (100) + h(11) * (70) + h(12) * (110) + h(13) * (110) + h(14) * (99) + h(15) * (109)
if score > bestScore then
  bestScore = score
  decision = 16
end if
score = 10008286 + h(0) * (120) + h(1) * (130) + h(2) * (0) + h(3) * (130) + h(4) * (110) + h(5) * (130) + h(6) * (110) + h(7) * (120) + h(8) * (120) + h(9) * (120) + h(10) * (110) + h(11) * (100) + h(12) * (110) + h(13) * (150) + h(14) * (110) + h(15) * (120)
if score > bestScore then
  bestScore = score
  decision = 17
end if
end if
combatDecision = decision
objectiveBuild = 0
if decision >= 9 then
  combatDecision = decision - 9
  objectiveBuild = 1
end if

' Release only an assembled group while the chosen action uses this route.
' Do not latch arrival during unrelated combat or transit; keep later deadlines.
routeFallback = 0
if combatDecision = 2 or (combatDecision = 8 and bestId = 0) then
  if (objectiveId = 0 or objectiveDistance > 300) and (heroId = 0 or heroDistance > 700) then
    routeFallback = 1
  end if
end if
routeDx = selfX - routeOpeningX
routeDy = selfY - routeOpeningY
if worldTick < 3500 and routeFallback and routeGroupCount >= 3 then
  if routeDx * routeDx + routeDy * routeDy <= 16 then
    groupDeparture = 1
  end if
end if

' Preserve the bundled controller's combat and economy as the policy prior.
' Learned actions below add movement or spell overrides to this complete turn.
if combatDecision = 8 then
  if objectiveId <> 0 and objectiveDistance <= 300 then
    attackTarget(objectiveId)
  else
    if heroId <> 0 and heroDistance <= 700 then
      attackTarget(heroId)
    else
      if bestId <> 0 then
        attackTarget(bestId)
      else
        if selfTeam = 0 then
          if worldTick < 3500 and groupDeparture = 0 then
            walkTo(71, 12)
          else
            if worldTick < 4500 then
              walkTo(9, 33)
            else
              walkTo(11, 106)
            end if
          end if
        else
          if worldTick < 3500 and groupDeparture = 0 then
            walkTo(45, 104)
          else
            if worldTick < 4500 then
              walkTo(107, 83)
            else
              walkTo(105, 10)
            end if
          end if
        end if
      end if
    end if
  end if
else
  if bestId <> 0 then
    attackTarget(bestId)
  else
    walkTo(64, 64)
  end if
end if
' Preempt automatic ring aim for a distant hero approaching this Lich.
' A midpoint center catches the approach after the twenty-four tick delay.
if selfClass = 7 and heroId <> 0 and ringHeroTarget = selfId then
  if heroDistance > 25 and heroDistance <= 49 then
    castPoint(3, (selfX + ringHeroX) / 2, (selfY + ringHeroY) / 2)
  end if
end if
hasHeal = 0
hasMana = 0
hasPoison = 0
hasGear = 0
hasDagger = 0
hasSword = 0
hasArmor = 0
hasAxe = 0
hasBook = 0
emptySlot = 0
slot = 0
while slot < 6
  id = itemId(slot)
  if id = 0 then
    emptySlot = 1
  end if
  if id = 1 or id = 2 then
    hasHeal = 1
    if selfHp * 5 < selfMaxHp * 3 then
      useItem(slot)
    end if
  end if
  if id = 3 then
    hasMana = 1
    if objectiveBuild = 0 and selfMana * 5 < selfMaxMana * 2 then
      useItem(slot)
    end if
  end if
  if id = 4 then
    hasPoison = 1
    if objectiveBuild = 0 and bestId <> 0 then
      useItem(slot)
    end if
  end if
  if id > 4 then
    hasGear = 1
  end if
  if id = 11 then
    hasDagger = 1
  end if
  if id = 13 then
    hasSword = 1
  end if
  if id = 16 then
    hasArmor = 1
  end if
  if id = 18 then
    hasAxe = 1
  end if
  if id = 20 then
    hasBook = 1
  end if
  slot = slot + 1
wend
if selfHp * 2 < selfMaxHp and hasHeal = 0 then
  if selfGold >= 50 then
    buyItem(2)
  end if
  if selfGold >= 30 then
    buyItem(1)
  end if
end if
if objectiveBuild = 0 then
if selfMaxMana > 0 then
  if selfMana * 2 < selfMaxMana and hasMana = 0 then
    if selfGold >= 45 then
      buyItem(3)
    end if
  end if
end if
if bestId <> 0 and hasPoison = 0 then
  if selfGold >= 40 then
    buyItem(4)
  end if
end if
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
    if hasGear = 0 and selfGold >= 70 then
      buyItem(7)
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
    if hasGear = 0 and selfGold >= 100 then
      buyItem(8)
    end if
    if selfGold >= 150 then
      buyItem(14)
    end if
    if selfGold >= 180 then
      buyItem(19)
    end if
  end if
  if magic = 1 then
    if hasGear = 0 and selfGold >= 140 then
      buyItem(12)
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
else
  if emptySlot <> 0 then
    if hasDagger = 0 and selfGold >= 110 then
      buyItem(11)
    end if
    if hasSword = 0 and selfGold >= 150 then
      buyItem(13)
    end if
    if hasArmor = 0 and selfGold >= 160 then
      buyItem(16)
    end if
    if hasAxe = 0 and selfGold >= 180 then
      buyItem(18)
    end if
    if hasBook = 0 and selfGold >= 190 then
      buyItem(20)
    end if
  end if
end if
if combatDecision = 1 then
  if selfTeam = 0 then
    walkTo(mapWidth - 10, 10)
  else
    walkTo(10, mapHeight - 10)
  end if
end if
if combatDecision = 2 then
  if objectiveId <> 0 and objectiveDistance <= 300 then
    attackTarget(objectiveId)
  else
    if heroId <> 0 and heroDistance <= 700 then
      attackTarget(heroId)
    else
      if selfTeam = 0 then
        if worldTick < 3500 and groupDeparture = 0 then
          walkTo(71, 12)
        else
          if worldTick < 4500 then
            walkTo(9, 33)
          else
            walkTo(11, 106)
          end if
        end if
      else
        if worldTick < 3500 and groupDeparture = 0 then
          walkTo(45, 104)
        else
          if worldTick < 4500 then
            walkTo(107, 83)
          else
            walkTo(105, 10)
          end if
        end if
      end if
    end if
  end if
end if
if combatDecision >= 3 and combatDecision <= 6 then
  if bestId <> 0 then
    castTarget(combatDecision - 3, bestId)
  else
    castTarget(combatDecision - 3, selfId)
  end if
end if
if combatDecision = 7 then
  walkTo(allyX, allyY)
end if

' Answer a visible in-range attacker while committed to a nearby tower siege.
' Preserve retreat/regroup actions and let home defense override this below.
if (combatDecision = 2 or combatDecision = 8) and objectiveKind = 4 and objectiveDistance <= 300 and siegeThreatId <> 0 then
  attackTarget(siegeThreatId)
end if

' Use observed home geometry to reserve the nearest living defender after
' a home guard falls. Never elect a role from player IDs or runner seats.
reserveHome = 0
reserveIndex = 0
while reserveIndex < objectCount()
  if objectKind(reserveIndex) = 1 and objectTeam(reserveIndex) = selfTeam and objectHp(reserveIndex) > 0 then
    reserveHome = 1
    reserveHomeId = objectId(reserveIndex)
    reserveX = objectX(reserveIndex)
    reserveY = objectY(reserveIndex)
  end if
  reserveIndex = reserveIndex + 1
wend
if reserveHome <> 0 then
  reserveGuards = 0
  reserveGuardCritical = 0
  reserveNearest = 1
  reserveDx = selfX - reserveX
  reserveDy = selfY - reserveY
  reserveDistance = reserveDx * reserveDx + reserveDy * reserveDy
  reserveTarget = 0
  reserveTargetDistance = 401
  reserveDirect = 0
  reserveDirectDistance = 401
  reserveHero = 0
  reserveHeroDistance = 401
  reserveFinish = 0
  reserveIndex = 0
  while reserveIndex < objectCount()
    reserveDx = objectX(reserveIndex) - reserveX
    reserveDy = objectY(reserveIndex) - reserveY
    reserveObjectHome = reserveDx * reserveDx + reserveDy * reserveDy
    if objectTeam(reserveIndex) = selfTeam then
      if objectKind(reserveIndex) = 4 and objectHp(reserveIndex) > 0 and reserveObjectHome <= 100 then
        reserveGuards = reserveGuards + 1
        ' Current pinned mechanics give home guards 1950 HP. Use the final
        ' fifth of HP only when the elected defender is close enough to arrive.
        if objectHp(reserveIndex) <= 390 then
          reserveGuardCritical = 1
        end if
      end if
      if objectKind(reserveIndex) = 2 and objectAlive(reserveIndex) and reserveObjectHome < reserveDistance then
        reserveNearest = 0
      end if
    else
      if objectAlive(reserveIndex) then
        if (objectKind(reserveIndex) = 2 or objectKind(reserveIndex) = 3) and reserveObjectHome < reserveDirectDistance then
          if objectTarget(reserveIndex) = reserveHomeId then
            reserveDirect = objectId(reserveIndex)
            reserveDirectDistance = reserveObjectHome
          end if
        end if
        if objectKind(reserveIndex) = 2 and reserveObjectHome < reserveHeroDistance then
          reserveHero = objectId(reserveIndex)
          reserveHeroDistance = reserveObjectHome
        end if
        if (objectKind(reserveIndex) = 2 or objectKind(reserveIndex) = 3) and reserveObjectHome < reserveTargetDistance then
          reserveTargetDistance = reserveObjectHome
          reserveTarget = objectId(reserveIndex)
        end if
        if objectKind(reserveIndex) = 1 and objectHp(reserveIndex) <= selfAttackDamage then
          reserveDx = objectX(reserveIndex) - selfX
          reserveDy = objectY(reserveIndex) - selfY
          reserveRange = selfAttackRange / 1000
          if (reserveDx * reserveDx + reserveDy * reserveDy) * 3600 <= reserveRange * reserveRange then
            reserveFinish = 1
          end if
        end if
      end if
    end if
    reserveIndex = reserveIndex + 1
  wend
  ' Intercept a visible home intruder before it starts attacking the fort.
  if reserveHero <> 0 then
    reserveTarget = reserveHero
  end if
  ' Direct damage to home outranks an approaching or distracted hero.
  if reserveDirect <> 0 then
    reserveTarget = reserveDirect
  end if
  if (reserveGuards <= 1 or (reserveGuardCritical <> 0 and reserveDistance <= 900)) and reserveNearest <> 0 and reserveFinish = 0 then
    if reserveDistance <= 400 and reserveTarget <> 0 then
      attackTarget(reserveTarget)
    else
      walkTo(reserveX, reserveY)
    end if
  end if
end if

' End only the recovery after an observed basic hit, never its windup.
if recoveryInitialized <> 0 and selfAttacksLanded > recoveryLastHit then
  walkTo(selfX, selfY)
end if
recoveryLastHit = selfAttacksLanded
recoveryInitialized = 1
