"""Objective-relative defense and explicit productive/quiet duty transitions."""
from dataclasses import replace


def perimeter_observer(parent):
    source=parent.template.replace('    defUntil = worldTick + defHoldTicks',
        '    perimeterAnchor = defAnchor\n    perimeterX = defAnchorX\n    perimeterY = defAnchorY\n    defUntil = worldTick + defHoldTicks',1)
    setup='''perimeterEnabled = 0
perimeterRadiusSq = param_perimeter_tiles * param_perimeter_tiles
perimeterReachSq = param_response_reach * param_response_reach
if param_perimeter_team = 2 or selfTeam = param_perimeter_team then
  perimeterEnabled = 1
end if
'''
    # The existing full active scan sees structures before mobile units. Do not
    # add another full object scan (a previous repair exceeded the VM budget).
    scan="""    defKind = objectKind(defI)
    if perimeterEnabled and (defKind = 1 or defKind = 4) then
      if objectId(defI) = perimeterAnchor and objectHp(defI) <= 0 then
        perimeterAnchor = coreHomeId
        perimeterX = defHomeX
        perimeterY = defHomeY
      end if
    end if
"""
    token='    defKind = objectKind(defI)\n    if (defKind = 2 or defKind = 3)'
    assert source.count(token)==1
    source=source.replace(token,scan+'    if (defKind = 2 or defKind = 3)',1)
    token='    if defD <= param_intercept_tiles * param_intercept_tiles and (defGroupD <= 400 or defD <= 9) then'
    assert source.count(token)==1
    gate='''    perimeterAdmit = 0
    if perimeterEnabled and defD <= perimeterReachSq then
      perimeterDx = objectX(defI) - perimeterX
      perimeterDy = objectY(defI) - perimeterY
      if perimeterDx * perimeterDx + perimeterDy * perimeterDy <= perimeterRadiusSq then
        perimeterAdmit = 1
      end if
    end if
    if perimeterAdmit or (defD <= param_intercept_tiles * param_intercept_tiles and (defGroupD <= 400 or defD <= 9)) then'''
    source=source.replace(token,gate,1)
    first=source.index('  while defI < objectCount()\n',source.index('if defActive then'))
    last=source.index('  wend',first)+len('  wend')
    block=source[first:last]
    block=block.replace('if (defKind = 2 or defKind = 3) and objectTeam(defI) <> selfTeam and objectAlive(defI) and objectHp(defI) > 0 then',
        'if defKind = 2 or defKind = 3 then\n    if objectTeam(defI) <> selfTeam then\n    if objectAlive(defI) and objectHp(defI) > 0 then\n      perimeterObjX = objectX(defI)\n      perimeterObjY = objectY(defI)')
    block=block.replace('    defI = defI + 1\n', '    end if\n    end if\n    defI = defI + 1\n')
    # Keep the two assignments themselves as queries, cache every later reuse.
    start=block.index('      if coreRespond then')
    block=block[:start]+block[start:].replace('objectX(defI)','perimeterObjX').replace('objectY(defI)','perimeterObjY')
    block=block.replace('      defGx = perimeterObjX - defThreatX\n      defGy = perimeterObjY - defThreatY\n      defGroupD = defGx * defGx + defGy * defGy\n','')
    block=block.replace('    if perimeterAdmit or (defD', '    defGroupD = 0\n    if perimeterAdmit = 0 then\n      defGx = perimeterObjX - defThreatX\n      defGy = perimeterObjY - defThreatY\n      defGroupD = defGx * defGx + defGy * defGy\n    end if\n    if perimeterAdmit or (defD')
    block=block.replace('    if objectAlive(defI) and objectHp(defI) > 0 then\n      perimeterObjX = objectX(defI)\n      perimeterObjY = objectY(defI)',
        '      perimeterObjX = objectX(defI)\n      perimeterObjY = objectY(defI)\n      defDx = perimeterObjX - selfX\n      defDy = perimeterObjY - selfY\n      defD = defDx * defDx + defDy * defDy\n    if defD <= perimeterBoundSq then\n    if objectAlive(defI) and objectHp(defI) > 0 then')
    repeated='      defDx = perimeterObjX - selfX\n      defDy = perimeterObjY - selfY\n      defD = defDx * defDx + defDy * defDy\n'
    where=block.index(repeated)+len(repeated)
    block=block[:where]+block[where:].replace(repeated,'',1)
    block=block.replace('    defI = defI + 1\n','    end if\n    defI = defI + 1\n')
    source=source[:first]+block+source[last:]
    bounds='''perimeterBound = param_response_reach
if param_intercept_tiles > perimeterBound then
  perimeterBound = param_intercept_tiles
end if
if coreRespond and param_core_response_tiles + param_core_radius > perimeterBound then
  perimeterBound = param_core_response_tiles + param_core_radius
end if
perimeterBoundSq = perimeterBound * perimeterBound
'''
    source=source.replace('if defActive then\n',bounds+'if defActive then\n',1)


    source=source.replace('if defActive then\n', 'if perimeterAnchor = 0 then\n  perimeterAnchor = coreHomeId\n  perimeterX = defHomeX\n  perimeterY = defHomeY\nend if\nif defActive then\n',1)
    source=setup+source+'''
if worldTick <= perimeterLastTick then
  perimeterLastCombat = 0
end if
perimeterLastTick = worldTick
if defActive = 0 or bestId <> 0 or perimeterLastCombat = 0 then
  perimeterLastCombat = worldTick
end if
if perimeterEnabled and defActive and bestId = 0 and param_release_mode > 0 then
  if param_release_mode = 2 or defSentry = 0 then
    if worldTick - perimeterLastCombat >= param_idle_ticks then
      defActive = 0
      defUntil = 0
      backdoorUntil = 0
      backdoorGroupUntil = 0
    end if
  end if
end if
'''
    return replace(parent,template=source,parameters=parent.parameters | {
        'perimeter_team':(2,0,2),'perimeter_tiles':(24,12,30),'response_reach':(32,20,48),
        'release_mode':(0,0,2),'idle_ticks':(480,120,1440)},
        memory=tuple(dict.fromkeys(parent.memory+('perimeterAnchor','perimeterX','perimeterY','perimeterLastTick','perimeterLastCombat'))),
        meaning=parent.meaning+' Objective-relative repair: remember the standing structure that '
        'triggered group defense and its position. During active defense, visible living enemy '
        'heroes/creeps within perimeter_tiles of that objective qualify even outside the hero '
        'intercept circle, provided self-to-target distance is at most response_reach. A destroyed '
        'remembered structure falls back to own god. Uses the existing object pass; direct god '
        'emergencies and solo response retain precedence. perimeter_team2 enables both colors; '
        '0or1 enables one. Track last decision with an actionable combat target. Optional '
        'release_mode1 releases only non-sentries, mode2 all roles after idle_ticks of no '
        'actionable target; mode0 keeps old duty. Clear commitment clocks on release so ordinary '
        'lane targeting resumes next tick. A fresh observed rush/solo attack can reacquire duty. '
        'This is a bounded quiet policy, never proof hidden enemies are gone.')


def forward_navigation(parent):
    source=parent.template.replace('defGoalX = defPointX\n  defGoalY = defPointY', '''defGoalX = defPointX
defGoalY = defPointY
if perimeterEnabled and param_forward_rally = 1 then
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
end if''',1)
    assert source!=parent.template
    return replace(parent,template=source,parameters=parent.parameters|{'forward_rally':(1,0,1)},
        meaning=parent.meaning+' Optional forward_rally1 uses the protected objective plus '
        'three tiles toward the last observed threat on each axis, before applying the class '
        'spacing and terrain fallback. This covers approaches instead of crowding behind the '
        'god. It is enabled only in the observer configured color(s), and gives no guarantee '
        'of winning a fight or of movement progress.')
