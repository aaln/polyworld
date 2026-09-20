"""Coached two-hero rear guard and three-hero center counterpush.

Only composed into the red branch. Existing contracts remain immutable.
"""
from dataclasses import replace


def observe(parent):
    source = parent.template.replace('defActive = 0', '''cpLarge = 0
cpContact = 0
cpAnchorSeen = 0
cpCoreHp = 0
cpAdvance = 0
cpBack = selfClass = param_split_guard or selfClass = 8
if worldTick <= defLastTick then
  cpAssigned = 0
  cpMode = 0
  cpQuiet = worldTick
  cpAnchor = 0
  cpCorePrevious = 0
end if
defActive = 0''', 1)
    token = '    defUntil = worldTick + defHoldTicks'
    assert source.count(token) == 1
    source = source.replace(token, '''    cpAssigned = 1
    cpAnchor = defAnchor
    cpX = defAnchorX
    cpY = defAnchorY
    if defCount >= defGroupSize then
      cpLarge = 1
      cpMode = 0
      cpQuiet = worldTick
    end if
''' + token, 1)
    # This is shared team-visible evidence; never interpret fog as enemy death.
    transition = '''
cpI = 0
while cpI < objectCount() and cpI < 64
  cpKind = objectKind(cpI)
  if cpKind = 3 then
    cpI = 64
  else
    if objectTeam(cpI) = selfTeam and objectHp(cpI) > 0 then
      if objectId(cpI) = cpAnchor then
        cpAnchorSeen = 1
      end if
      if cpKind = 1 then
        cpCoreHp = objectHp(cpI)
      end if
    end if
  end if
  cpI = cpI + 1
wend
if cpAssigned and cpAnchorSeen = 0 then
  cpX = defHomeX
  cpY = defHomeY
  defPointX = defHomeX
  defPointY = defHomeY
  defThreatX = defHomeX
  defThreatY = defHomeY
end if
cpI = 0
while cpI < objectCount() and cpI < 64
  cpKind = objectKind(cpI)
  if cpKind = 3 then
    cpI = 64
  else
    if cpKind = 2 then
      if objectTeam(cpI) <> selfTeam and objectAlive(cpI) and objectHp(cpI) > 0 then
        cpDx = objectX(cpI) - cpX
        cpDy = objectY(cpI) - cpY
        cpHx = objectX(cpI) - defHomeX
        cpHy = objectY(cpI) - defHomeY
        if cpDx * cpDx + cpDy * cpDy <= 256 or cpHx * cpHx + cpHy * cpHy <= 324 then
          cpContact = 1
        end if
      end if
    end if
  end if
  cpI = cpI + 1
wend
if cpContact then
  cpQuiet = worldTick
end if
if cpCorePrevious > cpCoreHp and cpCoreHp > 0 then
  cpMode = 0
  cpQuiet = worldTick
  defUntil = worldTick + 120
  defPointX = defHomeX
  defPointY = defHomeY
  defThreatX = defHomeX
  defThreatY = defHomeY
end if
cpCorePrevious = cpCoreHp
if cpAssigned and cpMode = 0 and cpLarge = 0 and cpContact = 0 then
  if worldTick - cpQuiet >= param_split_quiet then
    cpMode = 1
    cpTransitions = cpTransitions + 1
    rushStage = 0
    escortId = 0
  end if
end if
'''
    token = 'if worldTick < defUntil then\n'
    assert source.count(token) == 1
    source = source.replace(token, transition + token, 1)
    token = '\nif defActive then\n'
    assert source.count(token) == 1
    source = source.replace(token, '''
if cpAssigned and cpMode then
  if cpBack then
    defActive = 1
  else
    defActive = 0
    cpAdvance = 1
  end if
end if
if defActive then
''', 1)
    source += '''
if cpAdvance and bestId <> 0 then
  cpI = 0
  while cpI < objectCount() and cpI < 64
    if objectId(cpI) = bestId then
      cpKind = objectKind(cpI)
      if cpKind = 4 or cpKind = 5 then
        if (bestId < 19 or bestId > 21) and bestId <> 30 and bestId <> 31 then
          bestId = 0
        end if
      end if
    end if
    cpI = cpI + 1
  wend
end if
'''
    return replace(parent, template=source,
        parameters=parent.parameters | {'split_guard': (7, 5, 7), 'split_quiet': (120, 120, 720)},
        memory=parent.memory + ('cpAssigned', 'cpMode', 'cpQuiet', 'cpAnchor', 'cpX', 'cpY',
                                'cpCorePrevious', 'cpTransitions', 'rushStage'),
        meaning=parent.meaning + ' Superseding post-defense allocation on red: after a real '
        'group alarm, retain the original threat deadline but distinguish active emergency '
        'from residual watch. Once no living visible enemy hero lies within16tiles of the '
        'saved anchor or18tiles of the friendly god for split_quiet ticks, assign exactly '
        'the two fixed classes split_guard and Warlock(8) to rear defense; the remaining '
        'three roles resume ordinary combat selection and coordinated middle-lane routing. '
        'During that push, ignore off-lane building candidates; middle towers19-21, '
        'enemy god guards30-31 and the enemy god remain offensive structures. '
        'A fresh original four-hero alarm or observed friendly god HP loss ends the split. '
        'Current enemy contact delays initial release but does not cancel an established '
        'split unless a group or god damage is observed. Hidden heroes are not known dead. '
        'Surviving friendly structures are always exposed in observations even if protected; '
        'a missing/dead saved friendly anchor transfers duty to the god without deleting '
        'the assignment. Initial target range and rally geometry remain unchanged. '
        'Two means two assigned classes, not a guarantee both are alive or locally present. '
        'No permanent stationary three-sentry fallback. Validate actual travel and wins.')


def navigate(parent, middle):
    indent = lambda s: '\n'.join('  ' + line for line in s.splitlines())
    source = ('if cpAdvance then\n' + indent(middle.template) + '\nelse\n' +
              indent(parent.template) + '\nend if')
    return replace(parent, template=source, parameters=parent.parameters | middle.parameters,
                   memory=tuple(dict.fromkeys(parent.memory + middle.memory)),
                   meaning='When the coached split observer assigns this hero to offense, '
                   'advance the middle-lane waypoints with the other two attacking roles. '
                   'Existing attack and recovery decisions take precedence over navigation. '
                   'A new split resets the route and old creep escort. Middle route: ' +
                   middle.meaning + ' Otherwise preserve: ' + parent.meaning)


def assembled(parent):
    """Version the corrected assault-clear predicate; keep first study frozen."""
    source = parent.template.replace('cpContact = 0\n', 'cpContact = 0\ncpNearbyEnemies = 0\ncpHomeAllies = 0\n', 1)
    token = '      if objectTeam(cpI) <> selfTeam and objectAlive(cpI) and objectHp(cpI) > 0 then\n'
    assert source.count(token) == 1
    source = source.replace(token, '''      if objectTeam(cpI) = selfTeam and objectAlive(cpI) and objectHp(cpI) > 0 then
        cpHx = objectX(cpI) - defHomeX
        cpHy = objectY(cpI) - defHomeY
        if cpHx * cpHx + cpHy * cpHy <= 784 then
          cpHomeAllies = cpHomeAllies + 1
        end if
      end if
''' + token, 1)
    source = source.replace('if cpDx * cpDx + cpDy * cpDy <= 256 or cpHx * cpHx + cpHy * cpHy <= 324 then', '''if cpHx * cpHx + cpHy * cpHy <= 3600 then
          cpNearbyEnemies = cpNearbyEnemies + 1
        end if
        if cpHx * cpHx + cpHy * cpHy <= 100 then''', 1)
    source = source.replace('if cpContact then\n', '''if cpNearbyEnemies >= 3 or cpHomeAllies < 3 then
  cpContact = 1
end if
if cpContact then
''', 1)
    # The VM bounds total globals across both branches. These scratch scans
    # execute sequentially, so reuse the existing observer's scratch registers.
    import re
    scratch = {'cpI':'defI', 'cpKind':'defKind', 'cpDx':'defDx', 'cpDy':'defDy',
               'cpHx':'defGx', 'cpHy':'defGy'}
    source = re.sub(r'\b(cpI|cpKind|cpDx|cpDy|cpHx|cpHy)\b', lambda m:scratch[m[0]], source)
    return replace(parent, template=source, meaning=parent.meaning +
        ' Revised quiet evidence supersedes the16/18tile contact predicate: '
        'do not start a split while at least3living visible enemies lie within60tiles '
        'of home, any living visible enemy is within10tiles of home, or fewer than3 '
        'living friendly heroes are assembled within28tiles of home. Count team-visible '
        'heroes, including self; do not confuse a gap between destroyed towers with '
        'an eliminated rush. Require the configured5or15second quiet interval. '
        'Retained two-guard allocation, center routing and group recall are unchanged.')


def mobile(parent):
    """Rear guard is an upper bound: idle supports should join the offensive wave."""
    source=parent.template.replace('cpNearbyEnemies = 0\n','cpNearbyEnemies = 0\ncpRearNeeded = 0\n',1)
    source=source.replace('  cpCorePrevious = 0\n','  cpCorePrevious = 0\n  cpWaveUntil = 0\n  cpWaveCursor = 0\n',1)
    token='        if defGx * defGx + defGy * defGy <= 3600 then'
    assert source.count(token)==1
    source=source.replace(token,'''        if defGx * defGx + defGy * defGy <= param_rear_radius * param_rear_radius then
          cpRearNeeded = 1
        end if
'''+token,1)
    token='if cpNearbyEnemies >= 3 or cpHomeAllies < 3 then\n'
    assert source.count(token)==1
    source=source.replace(token,'''if cpMode and cpNearbyEnemies >= 3 then
  cpMode = 0
  cpQuiet = worldTick
  defUntil = worldTick + defHoldTicks
end if
if cpAssigned and cpTransitions > 0 then
  defI = 0
  while defI < 8 and defI < objectCount()
    if cpWaveCursor >= objectCount() then
      cpWaveCursor = 0
    end if
    if objectKind(cpWaveCursor) = 3 and objectTeam(cpWaveCursor) <> selfTeam and objectAlive(cpWaveCursor) and objectHp(cpWaveCursor) > 0 then
      defDx = objectX(cpWaveCursor) - defHomeX
      defDy = objectY(cpWaveCursor) - defHomeY
      if defDx * defDx + defDy * defDy <= 196 then
        cpWaveUntil = worldTick + 96
      end if
    end if
    cpWaveCursor = cpWaveCursor + 1
    defI = defI + 1
  wend
end if
if worldTick < cpWaveUntil then
  cpRearNeeded = 1
  if cpBack then
    defPointX = defHomeX
    defPointY = defHomeY
    defThreatX = defHomeX
    defThreatY = defHomeY
  end if
end if
'''+token,1)
    token='  if cpBack then\n    defActive = 1'
    assert source.count(token)==1
    source=source.replace(token,'  if cpBack and cpRearNeeded then\n    defActive = 1',1)
    return replace(parent,template=source,parameters=parent.parameters|{'rear_radius':(30,24,48)},
        memory=parent.memory+('cpWaveUntil','cpWaveCursor'),
        meaning=parent.meaning+' Superseding mandatory rear staffing: two is a maximum. '
        'During split, the two support classes remain on defense only if a living visible '
        'enemy hero is within rear_radius of home or a recently observed enemy creep '
        'is within14home. Otherwise they join the same middle offensive route, allowing '
        'five heroes to attack. A rotating8object scan provides creep coverage retained '
        'for96ticks, with home as the support rally. Re-enter whole-team defense when '
        'three visible living heroes lie within60home, even if the original clustered '
        'four-hero detector cannot find them. Initial defense before first split is '
        'unchanged. Fixed hero roles and local visibility only; validate loss of rear '
        'coverage, return times, team damage, all purchases, and full outcomes.')
