"""Bounded independent creep emergency; keep captured observers unchanged."""
from dataclasses import replace


def rolling_core(parent):
    pre = '''creepCoreId = 0
creepHomeX = 105
creepHomeY = 11
creepHomeId = 1
creepI = 0
while creepI < objectCount() and creepI < 2
  if objectKind(creepI) = 1 and objectTeam(creepI) = selfTeam then
    creepHomeX = objectX(creepI)
    creepHomeY = objectY(creepI)
    creepHomeId = objectId(creepI)
  end if
  creepI = creepI + 1
wend
if worldTick <= creepLastTick then
  creepCursor = 0
  creepLastId = 0
end if
creepLastTick = worldTick
creepDx = selfX - creepHomeX
creepDy = selfY - creepHomeY
if creepDx * creepDx + creepDy * creepDy <= param_creep_response * param_creep_response then
  creepChecks = 0
  while creepChecks < param_creep_checks and creepChecks < objectCount() and creepCoreId = 0
    if creepCursor >= objectCount() then
      creepCursor = 0
    end if
    creepProbe = creepCursor
    if creepChecks = 0 and creepLastId <> 0 and creepLastIndex < objectCount() then
      creepProbe = creepLastIndex
    else
      creepCursor = creepCursor + 1
    end if
    if objectKind(creepProbe) = 3 then
    if objectTeam(creepProbe) <> selfTeam then
      creepX = objectX(creepProbe)
      creepY = objectY(creepProbe)
      creepDx = creepX - creepHomeX
      creepDy = creepY - creepHomeY
      if creepDx * creepDx + creepDy * creepDy <= param_creep_radius * param_creep_radius then
      if objectAlive(creepProbe) and objectHp(creepProbe) > 0 then
        creepCoreId = objectId(creepProbe)
        creepLastIndex = creepProbe
      end if
      end if
    end if
    end if
    creepChecks = creepChecks + 1
  wend
end if
creepLastId = creepCoreId
if creepCoreId <> 0 then
  bestId = creepCoreId
  bestDistance = 0
  defActive = 1
  defLastTick = worldTick
  if defUntil < worldTick + 120 then
    defUntil = worldTick + 120
  end if
  defHomeX = creepHomeX
  defHomeY = creepHomeY
  defPointX = creepX
  defPointY = creepY
  defThreatX = creepX
  defThreatY = creepY
else
'''
    indent=lambda text:'\n'.join('  '+line for line in text.splitlines())
    return replace(parent,template=pre+indent(parent.template)+'\nend if\n',
        parameters=parent.parameters|{'creep_response':(24,16,32),'creep_radius':(8,6,12),'creep_checks':(8,4,16)},
        memory=tuple(dict.fromkeys(parent.memory+('creepCursor','creepLastId','creepLastIndex','creepLastTick'))),
        meaning=parent.meaning+' Independently of hero-group commitment, a nearby red defender '
        'checks at most creep_checks visible object positions per decision for living hostile '
        'creeps inside creep_radius of its observed god. Rotate a persistent cursor so late '
        'spawned creeps are not permanently excluded by an index cap; recheck the previous '
        'target index first while still eligible. On discovery, prioritize that creep and rally '
        'to its observed position, keeping at least120ticks of defense. Otherwise run the exact '
        'parent observer. Only heroes within creep_response of home participate; blue is '
        'unchanged through branch composition. Detection can be delayed by a full cursor cycle '
        'and object-list changes; this does not claim instantaneous or complete threat coverage.')
