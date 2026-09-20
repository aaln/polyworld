"""Prioritize the terminal objective chain without changing wave navigation."""
from dataclasses import replace


def finish(parent):
    return replace(parent,template=parent.template+'''
if param_finish_class = 10 or selfClass = param_finish_class then
  finishGuard = 0
  finishGod = 0
  finishGuardScore = 2147483647
  finishBlocked = 0
  finishIndex = 0
  while finishIndex < objectCount()
    if objectTeam(finishIndex) <> selfTeam and objectHp(finishIndex) > 0 and objectAlive(finishIndex) then
      finishId = objectId(finishIndex)
      finishKind = objectKind(finishIndex)
      finishDx = objectX(finishIndex) - selfX
      finishDy = objectY(finishIndex) - selfY
      finishD = finishDx * finishDx + finishDy * finishDy
      if finishId = bestId and (finishKind = 2 or finishKind = 3) and finishD <= param_defense_tiles * param_defense_tiles then
        finishBlocked = 1
      end if
      if finishKind = 1 and finishD <= param_god_tiles * param_god_tiles then
        finishGod = finishId
      end if
      if param_guard_tiles > 0 and finishKind = 4 and finishId >= 28 and finishId <= 31 and finishD <= param_guard_tiles * param_guard_tiles then
        finishScore = finishD * 100 + objectHp(finishIndex) * param_guard_hp_weight
        if finishScore < finishGuardScore then
          finishGuard = finishId
          finishGuardScore = finishScore
        end if
      end if
    end if
    finishIndex = finishIndex + 1
  wend
  if finishGuard <> 0 and finishBlocked = 0 then
    bestId = finishGuard
  end if
  if finishGod <> 0 then
    bestId = finishGod
  end if
end if
''',parameters=parent.parameters|{'finish_class':(7,0,10),'guard_tiles':(16,0,32),'god_tiles':(24,8,40),'defense_tiles':(4,0,8),'guard_hp_weight':(0,0,10)},
        meaning=parent.meaning+' After normal selection, selected class(or allclasses when finish_class10) favors a visible exposed enemy god within god_tiles. Otherwise favor an exposed nearby guard(ID28..31), unless the existing mobile target is within defense_tiles. Guard score combines squared distance times100 and HP times guard_hp_weight. Existing wave escort, purchases and combat recovery remain unchanged. This is a priority override, not a new guarantee of creep cover or safe tower aggro.')
