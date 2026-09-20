' Seesaw selfish rider.
'
' Ignores the partner's face and pumps for a lively ride. Useful as a
' contrast baseline: it can look exciting and still lose the pair score
' when the other child gets sick.

goingDown = 0
if selfSlot = 0 then
  if omegaMilli > 4 then
    goingDown = 1
  end if
else
  if omegaMilli < -4 then
    goingDown = 1
  end if
end if

if goingDown = 1 then
  r = lean(2)
else
  r = lean(1)
end if
r = pump(1)
if myFunDelta > 3 then
  r = express(15)
else
  r = express(10)
end if
