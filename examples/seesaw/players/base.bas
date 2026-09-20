' Seesaw cooperative rider.
'
' You are one child on a two-seat seesaw. Every decision runs from the top
' of this file with a fresh instruction budget. Globals survive; registers
' do not. The pair score is 2*min(fun) + sum/4, so making the other rider
' sick loses the match even if you are having a blast.
'
' READ-ONLY VALUES
'   selfSlot worldTick remainingTicks decisionPeriod
'   angleMilli omegaMilli          board: +angle is Lila (slot 0) down
'   myLean myPump myFun myNausea mySick myFunDelta mySeated
'   tempBand windBand wetBand      0-based public weather bands
'   partnerLean partnerPump partnerExpr partnerExprAge
'   expressionCount
'
' FACES
'   0 clear  1 smile  2 frown  3 delighted  4 anxious  5 nauseous
'   6 tired  7 hot    8 cold   9 nervous   10 strain  11 content
'   12 dizzy 13 bliss 14 grimace 15 cheer
'
' COMMANDS, all return 1 when accepted and 0 when refused.
'   lean(dir)    -2 .. 2, toward lowering your own side when positive
'   pump(on)     1 pumps (push going down, lighten going up), 0 stops
'   express(id)  send a face the partner can see
'   rest()       get off and walk to a bench; lean or pump walks you back
'   absVal(n) signOf(n)
'
' THE PLAYBOOK. Pump in rhythm with the board. Smile when fun is rising.
' If you feel sick, frown, get off, and sit until the queasy feeling
' fades. If the partner frowns, nauseates, or grimaces, stop pumping
' and sit lighter even if you wanted more.

if lastFace = 0 then
  lastFace = 1
end if

goingDown = 0
if selfSlot = 0 then
  if omegaMilli > 6 then
    goingDown = 1
  end if
else
  if omegaMilli < -6 then
    goingDown = 1
  end if
end if

wild = absVal(omegaMilli)
partnerUpset = 0
if partnerExpr = 2 then
  partnerUpset = 1
end if
if partnerExpr = 5 then
  partnerUpset = 1
end if
if partnerExpr = 12 then
  partnerUpset = 1
end if
if partnerExpr = 14 then
  partnerUpset = 1
end if
if partnerUpset = 1 then
  if partnerExprAge > 72 then
    partnerUpset = 0
  end if
end if

if mySick = 1 or myNausea > 300 then
  r = rest()
  if mySick = 1 then
    r = express(5)
    lastFace = 5
  else
    r = express(12)
    lastFace = 12
  end if
else
  if mySeated = 0 then
    if myNausea > 120 then
      r = rest()
      r = express(11)
      lastFace = 11
    else
      r = lean(0)
      r = express(1)
      lastFace = 1
    end if
  else
    if partnerUpset = 1 or wild > 48 then
      r = lean(0)
      r = pump(0)
      r = express(11)
      lastFace = 11
    else
      if goingDown = 1 then
        r = lean(1)
        r = pump(1)
      else
        r = lean(-1)
        r = pump(1)
      end if
      if myNausea > 160 then
        r = express(4)
        lastFace = 4
      else
        if myFunDelta > 4 then
          r = express(1)
          lastFace = 1
        else
          if myFunDelta <= 1 then
            r = express(9)
            lastFace = 9
          end if
        end if
      end if
    end if
  end if
end if
