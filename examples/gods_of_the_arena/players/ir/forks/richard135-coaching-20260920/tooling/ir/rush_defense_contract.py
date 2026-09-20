"""React to shared visible enemy groups before resuming ordinary wave pressure."""
from motion_contract import directions
from dataclasses import replace


def observer(contract, baseline):
    detect = '''
defActive = 0
if worldTick <> defLastTick + 1 then
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
defFrontD = param_home_tiles * param_home_tiles + 1
defI = 0
while defI < objectCount() and defI < 64
  if objectKind(defI) = 2 and objectTeam(defI) <> selfTeam and objectAlive(defI) and objectHp(defI) > 0 then
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
  defI = defI + 1
wend
if defFront <> 0 then
  defCount = 0
  defAnchor = 0
  defAnchorD = param_tower_tiles * param_tower_tiles + 1
  defI = 0
  while defI < objectCount() and defI < 64
    defKind = objectKind(defI)
    if objectHp(defI) > 0 then
      defDx = objectX(defI) - defFrontX
      defDy = objectY(defI) - defFrontY
      defD = defDx * defDx + defDy * defDy
      if objectTeam(defI) <> selfTeam and defKind = 2 and objectAlive(defI) and defD <= param_cluster_tiles * param_cluster_tiles then
        defCount = defCount + 1
      end if
      if objectTeam(defI) = selfTeam and (defKind = 4 or defKind = 1) and defD <= param_tower_tiles * param_tower_tiles then
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
    defI = defI + 1
  wend
  if defCount >= param_group_size and defAnchor <> 0 then
    defUntil = worldTick + param_hold_ticks
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
      defPointX = defAnchorX + defDx * param_behind_tiles / defScale
      defPointY = defAnchorY + defDy * param_behind_tiles / defScale
    else
      defPointX = defHomeX + param_behind_tiles
      defPointY = defHomeY + param_behind_tiles
      if selfTeam = 1 then
        defPointX = defHomeX - param_behind_tiles
        defPointY = defHomeY - param_behind_tiles
      end if
    end if
    defenseRefreshes = defenseRefreshes + 1
  end if
end if
if worldTick < defUntil then
  defActive = 1
end if
'''
    choose = '''
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
    if defD <= param_intercept_tiles * param_intercept_tiles and (defGroupD <= 400 or defD <= 9) then
      defScore = defD * 10 + objectHp(defI) * param_hp_weight
      if (param_creep_first = 1 and defKind = 3) or (param_creep_first = 0 and defKind = 2) then
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
defenseDecisions = defenseDecisions + 1
'''
    indent = lambda text: '\n'.join('  ' + line for line in text.splitlines())
    source = detect + '\nif defActive then\n' + indent(choose) + '\nelse\n' + indent(baseline.template) + '\nend if'
    return contract(source, baseline.parameters | {
        'group_size': (3, 3, 5), 'home_tiles': (80, 24, 100), 'tower_tiles': (14, 8, 24),
        'cluster_tiles': (12, 8, 20), 'hold_ticks': (960, 120, 1440), 'behind_tiles': (4, 2, 8),
        'intercept_tiles': (10, 6, 14), 'creep_first': (0, 0, 1), 'hp_weight': (1, 0, 4)},
        [], ['candidate', 'defense'], [],
        'On published release .5, shared team vision exposes the same enemy group to all allied heroes. '
        'Find the visible living enemy hero closest to the observed friendly god within home_tiles. '
        'When group_size visible enemy heroes lie within cluster_tiles of that hero and a standing '
        'friendly tower or god lies within tower_tiles, retain a defense commitment for hold_ticks. '
        'Prefer a directly targeted friendly structure, otherwise the closest. Rally behind it toward '
        'home. While committed, suspend offensive structure selection and select local mobile enemies '
        'near the last observed group, or immediate path blockers. Declared creep/hero preference and '
        'HP weight govern focus. Missing enemies do not imply death; commitment expires by time and '
        'resets on decision gaps. Outside defense: ' + baseline.meaning +
        ' Detection inspects the first64 visible objects: the pinned map has two forts,34buildings '
        'and10heroes, enumerated before creeps. This bound covers all visible heroes and structures '
        'on this source; the operator is release-specific. The active combat scan is untruncated.',
        ['defLastTick', 'defUntil', 'defThreatX', 'defThreatY', 'defPointX', 'defPointY',
         'defenseRefreshes', 'defenseDecisions'])


def navigation(contract, baseline):
    move = '''
defNavX = defPointX
defNavY = defPointY
defNavFound = terrainWalkable(defNavX, defNavY)
defdirection = 0
while defdirection < 8 and defNavFound = 0
  DIRECTIONS
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
'''.replace('DIRECTIONS', directions('def'))
    indent = lambda text: '\n'.join('  ' + line for line in text.splitlines())
    return contract('if defActive then\n' + indent(move) + '\nelse\n' + indent(baseline.template) + '\nend if',
                    baseline.parameters, ['defense'], [], ['walkTo'],
                    'In an active defense, move to the shared rally tile after ordinary combat/recovery '
                    'has declined a target or motion. Try nearby terrain tiles when blocked; if movement '
                    'is rejected, approach the last observed enemy group. This does not guarantee safe '
                    'aggro or a complete path. Outside defense: ' + baseline.meaning, baseline.memory)


def bounded_observer(contract, baseline):
    """Version the budget fix so previously captured IR/BASIC remains extractable."""
    original = observer(contract, baseline)
    source = original.template.replace(
        '  if objectKind(defI) = 2 and objectTeam(defI) <> selfTeam and objectAlive(defI) and objectHp(defI) > 0 then',
        '  if objectKind(defI) = 3 then\n    defI = 64\n  else\n  if objectKind(defI) = 2 then\n  if objectTeam(defI) <> selfTeam and objectAlive(defI) and objectHp(defI) > 0 then')
    source = source.replace('  defI = defI + 1\nwend\nif defFront <> 0 then',
                            '  end if\n  end if\n  defI = defI + 1\nwend\nif defFront <> 0 then')
    source = source.replace('    if objectHp(defI) > 0 then',
                            '    if defKind = 3 then\n      defI = 64\n    else\n    if objectHp(defI) > 0 then')
    source = source.replace('    defI = defI + 1\n  wend\n  if defCount',
                            '    end if\n    defI = defI + 1\n  wend\n  if defCount')
    return replace(original, template=source, meaning=original.meaning +
                   ' The detector stops at the first creep because the pinned source enumerates '
                   'all structures and heroes before creeps; nested hero filtering avoids costly '
                   'queries for unrelated objects. This preserves the detection set on the locked map.')


def persistent_observer(contract, baseline):
    parent = bounded_observer(contract, baseline)
    source = parent.template.replace(
        'if defCount >= param_group_size and defAnchor <> 0 then',
        'if defAnchor <> 0 and (defCount >= param_group_size or (worldTick < defUntil and defFrontD <= param_continue_home * param_continue_home)) then')
    regroup = '''
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
if defMates < param_gather_heroes then
  bestId = 0
end if
'''
    source = source.replace('  defenseDecisions = defenseDecisions + 1',
                            '\n'.join('  '+line for line in regroup.splitlines()) +
                            '\n  defenseDecisions = defenseDecisions + 1')
    return replace(parent, template=source,
                   parameters=parent.parameters | {'continue_home': (48, 24, 64), 'gather_heroes': (0, 0, 5)},
                   meaning=parent.meaning + ' After the first group trigger, any visible living enemy '
                   'hero within continue_home of home and near a standing friendly anchor refreshes '
                   'the defense. Killing or losing vision of some group members does not imply the '
                   'remaining rush is safe. Before attacking, optionally require gather_heroes '
                   'visible living allied heroes within14tiles of self (self counts when visible); '
                   'otherwise continue to the rally. This is local cohesion, not a guarantee of '
                   'equal arrival times or combat superiority.')


def lineup_observer(contract, baseline):
    parent = persistent_observer(contract, baseline)
    source = parent.template.replace('param_group_size', 'defGroupSize').replace(
        'param_hold_ticks', 'defHoldTicks').replace('param_continue_home', 'defContinueHome')
    setup = '''defGroupSize = param_group_size
defHoldTicks = param_hold_ticks
defContinueHome = param_continue_home
if selfTeam = 1 then
  defGroupSize = param_blue_group
  defHoldTicks = param_blue_hold
  defContinueHome = param_blue_continue
end if
'''
    return replace(parent, template=setup+source,
                   parameters=parent.parameters | {'blue_group': (3, 3, 5), 'blue_hold': (960, 120, 1440),
                                                    'blue_continue': (0, 0, 64)},
                   meaning=parent.meaning + ' The fixed blue hero lineup uses the separately '
                   'declared blue_group, blue_hold and blue_continue values. Zero continuation '
                   'radius disables survivor refresh except at the exact home tile. Red keeps '
                   'the original three parameters. This branches on public team, not rival identity.')


def defense_cadence(parent):
    source = '''defMotionLimit = param_motion_object_limit
if defActive then
  defMotionLimit = param_defense_motion_limit
end if
''' + parent.template.replace('objectCount() > param_motion_object_limit', 'objectCount() > defMotionLimit')
    return replace(parent, template=source,
                   parameters=parent.parameters | {'defense_motion_limit': (40, 20, 80)},
                   reads=tuple(dict.fromkeys(parent.reads+('defense',))),
                   meaning=parent.meaning + ' During active shared defense, use defense_motion_limit '
                   'instead of the ordinary motion scan limit to reserve VM capacity for regrouping. '
                   'Outside defense the parent combat controller is unchanged.')


def defensive_recovery(parent):
    source = parent.template.replace('param_targeted', 'defTargeted').replace('param_risk_hp', 'defRiskHp')
    setup = '''defTargeted = param_targeted
defRiskHp = param_risk_hp
if defActive then
  defTargeted = param_defense_targeted
  defRiskHp = param_defense_risk_hp
end if
'''
    return replace(parent, template=setup+source,
                   parameters=parent.parameters | {'defense_targeted': (1, 0, 1), 'defense_risk_hp': (35, 0, 60)},
                   meaning=parent.meaning + ' While defense is active, separately configure the '
                   'existing targeted-hit recovery and low-health/recent-damage escape thresholds. '
                   'Outside defense their original values remain intact. Existing motion scan '
                   'limits still apply; enabling a threshold does not guarantee a retreat occurs.')


def opening_guard(parent):
    move = '''openingX = 72
openingY = 37
if selfTeam = 1 then
  openingX = 44
  openingY = 79
end if
openingAccepted = 0
if terrainWalkable(openingX, openingY) then
  openingAccepted = walkTo(openingX, openingY)
end if
'''
    indent = lambda text: '\n'.join('  '+line for line in text.splitlines())
    source = 'if defActive = 0 and worldTick < param_opening_ticks then\n'+indent(move)+\
             '\n  if openingAccepted = 0 then\n'+indent(indent(parent.template))+\
             '\n  end if\nelse\n'+indent(parent.template)+'\nend if'
    return replace(parent, template=source, parameters=parent.parameters | {'opening_ticks': (720, 240, 1200)},
                   meaning='During the first opening_ticks, when no active defense and ordinary '
                   'combat/recovery have declined action, rendezvous behind the friendly middle '
                   'outer tower at the published map waypoint (72,37) for red or(44,79) for blue. '
                   'If terrain/path acceptance fails, use the ordinary navigation. The timeout '
                   'releases the opening rendezvous; an observed rush immediately uses normal '
                   'defensive navigation. The intent is shorter response travel, not advance '
                   'knowledge of an unseen enemy strategy. Otherwise: '+parent.meaning)


def sentry_observer(contract, baseline):
    parent = lineup_observer(contract, baseline)
    setup = '''defSentryRole = param_red_sentry
if selfTeam = 1 then
  defSentryRole = param_blue_sentry
end if
defSentry = 0
if defSentryRole >= 2 and (selfClass = 2 or selfClass = 3 or selfClass = 7 or selfClass = 8) then
  defSentry = 1
end if
if (defSentryRole = 1 or defSentryRole = 3) and (selfClass = 0 or selfClass = 5) then
  defSentry = 1
end if
if defSentry then
  defHoldTicks = param_sentry_hold
end if
'''
    source = parent.template.replace('defActive = 0', setup+'defActive = 0', 1)
    source = source.replace('if worldTick <> defLastTick + 1 then',
                            'if worldTick <= defLastTick or (worldTick <> defLastTick + 1 and defSentry = 0) then', 1)
    return replace(parent, template=source,
                   parameters=parent.parameters | {'red_sentry': (3, 0, 3), 'blue_sentry': (3, 0, 3),
                                                    'sentry_hold': (3600, 1440, 14400)},
                   meaning=parent.meaning + ' After a genuinely observed group trigger, selected '
                   'sentries remember the threatened structure and rally for sentry_hold ticks, '
                   'including across their own death/respawn decision gaps. A nonincreasing clock '
                   'clears memory for a new episode. Role0 selects nobody,1 the tank(DK/Vanguard), '
                   '2 mage and healer(Lich/Warlock or Arcanist/Druid),3 all three. Red and blue roles '
                   'are separately configured. Other heroes keep the original shorter commitment '
                   'and resume wave pressure. The intent is to cover a returning second rush '
                   'after the first is repelled; memory is not knowledge of unseen enemy positions.')


def core_wave_observer(contract, baseline):
    parent=sentry_observer(contract,baseline)
    scan='''coreId = 0
coreScore = 2147483647
coreI = 0
while coreI < objectCount()
  coreKind = objectKind(coreI)
  if coreKind = 2 or coreKind = 3 then
    if objectTeam(coreI) <> selfTeam then
      if objectHp(coreI) > 0 and objectAlive(coreI) then
        coreDx = objectX(coreI) - defHomeX
        coreDy = objectY(coreI) - defHomeY
        coreD = coreDx * coreDx + coreDy * coreDy
        if coreD <= param_core_radius * param_core_radius then
          coreValue = coreD * 100 + objectHp(coreI)
          if objectTarget(coreI) = coreHomeId then
            coreValue = coreValue - 100000
          end if
          if coreValue < coreScore then
            coreScore = coreValue
            coreId = objectId(coreI)
            coreX = objectX(coreI)
            coreY = objectY(coreI)
          end if
        end if
      end if
    end if
  end if
  coreI = coreI + 1
wend
if coreId <> 0 then
  if defUntil < worldTick + param_core_hold then
    defUntil = worldTick + param_core_hold
  end if
  defThreatX = coreX
  defThreatY = coreY
  defPointX = coreX
  defPointY = coreY
end if
'''
    source=parent.template.replace('defHomeX = 105','coreHomeId = 1\nif selfTeam = 1 then\n  coreHomeId = 2\nend if\ndefHomeX = 105',1)
    source=source.replace('    defHomeX = objectX(defI)','    coreHomeId = objectId(defI)\n    defHomeX = objectX(defI)',1)
    source=source.replace('if worldTick < defUntil then',scan+'\nif worldTick < defUntil then',1)
    # An emergency already supplies the target. Do not scan the same crowded
    # base a second time through the ordinary defense/attack selector.
    source=source.replace('if defActive then\n',
                          'if coreId <> 0 then\n  bestId = coreId\n  bestDistance = coreScore\nelse\nif defActive then\n',1)
    source+='\nend if\n'
    return replace(parent,template=source,parameters=parent.parameters | {'core_radius':(14,8,20),'core_hold':(120,24,480)},
                   meaning=parent.meaning+' Independently of remembered hero groups, inspect all visible '
                   'living enemy heroes and creeps within core_radius tiles of the observed own god. '
                   'Select the closest-to-god threat with HP as tie preference, strongly prioritizing '
                   'a unit whose observed attack target is the god. Activate defense for at least '
                   'core_hold ticks and override the ordinary target with this visible threat, even '
                   'when far from self or the old remembered group. Update the rally to its observed '
                   'position. Missing enemies still are not predicted. This is a base emergency '
                   'override; it may sacrifice offensive pressure and must be evaluated.')


def released_defense(parent, has_core=True):
    # Long-lived sentries otherwise keep walking to a stale point for minutes.
    # A lone survivor must actually attack our anchor to extend that duty.
    source=('' if has_core else 'coreId = 0\n')+parent.template.replace(
        '(worldTick < defUntil and defFrontD <= defContinueHome * defContinueHome)',
        '(worldTick < defUntil and defFrontD <= defContinueHome * defContinueHome and defFrontTarget = defAnchor)')
    source=source.replace('defUntil = worldTick + defHoldTicks',
                          'defLastPressure = worldTick\n    defUntil = worldTick + defHoldTicks',1)
    source=source.replace('  defUntil = 0\nend if',
                          '  defUntil = 0\n  defLastPressure = 0\nend if',1)
    release='''if coreId <> 0 then
  defLastPressure = worldTick
end if
if coreId = 0 and worldTick - defLastPressure >= param_quiet_ticks then
  defUntil = 0
end if
'''
    source=source.replace('if worldTick < defUntil then',release+'if worldTick < defUntil then',1)
    return replace(parent,template=source,
                   parameters=parent.parameters | {'quiet_ticks':(720,120,1440)},
                   memory=tuple(dict.fromkeys(parent.memory+('defLastPressure',))),
                   meaning=parent.meaning+' Track the last observed credible pressure: a triggering '
                   'enemy group near a standing friendly anchor, a continuing lone hero actually '+
                   ('targeting that anchor, or a visible core threat. If none has been observed for '
                    if has_core else 'targeting that anchor. If none has been observed for ')+
                   'quiet_ticks, cancel the defense commitment for every role and resume normal '
                   'wave pressure. Do not refresh for a merely nearby isolated survivor. Reset the '
                   'pressure clock with defense memory. This deliberately shortens sentry duty '
                   'after quiet; it does not infer unseen enemies are dead and may expose a '
                   'returning rush, which must be tested against the old sentry policy.')


def reachable_core_defense(parent):
    source=parent.template.replace('coreId = 0\n', '''coreId = 0
coreSelfX = selfX - defHomeX
coreSelfY = selfY - defHomeY
coreRespond = 0
if coreSelfX * coreSelfX + coreSelfY * coreSelfY <= param_core_response_tiles * param_core_response_tiles then
  coreRespond = 1
end if
''',1)
    source=source.replace('while coreI < objectCount()', 'while coreI < objectCount() and coreRespond',1)
    source=source.replace('if coreD <= param_core_radius * param_core_radius then',
                          'if coreD <= param_core_radius * param_core_radius and (objectTarget(coreI) = coreHomeId or coreD <= 36) then',1)
    return replace(parent,template=source,
                   parameters=parent.parameters | {'core_response_tiles':(24,12,40)},
                   meaning=parent.meaning+' Restrict this emergency override to defenders already '
                   'within core_response_tiles of their god, and to visible enemies either '
                   'actively targeting the god or within6tiles of it. Faraway attackers continue '
                   'their normal mission. This narrows the parent detector after a broad all-team '
                   'retreat regressed local wins; it still does not predict hidden threats.')


def fused_core_defense(parent):
    setup='''coreId = 0
coreScore = 2147483647
coreHomeId = 1
if selfTeam = 1 then
  coreHomeId = 2
end if
coreDx = selfX - defHomeX
coreDy = selfY - defHomeY
coreRespond = 0
if coreDx * coreDx + coreDy * coreDy <= param_core_response_tiles * param_core_response_tiles then
  coreRespond = 1
end if
'''
    scan='''if coreRespond then
  coreDx = objectX(defI) - defHomeX
  coreDy = objectY(defI) - defHomeY
  coreD = coreDx * coreDx + coreDy * coreDy
  if coreD <= param_core_radius * param_core_radius then
    coreTarget = objectTarget(defI)
    if coreTarget = coreHomeId or coreD <= 36 then
      coreValue = coreD * 100 + objectHp(defI)
      if coreTarget = coreHomeId then
        coreValue = coreValue - 100000
      end if
      if coreValue < coreScore then
        coreScore = coreValue
        coreId = objectId(defI)
        coreX = objectX(defI)
        coreY = objectY(defI)
      end if
    end if
  end if
end if
'''
    source=parent.template.replace('if defActive then\n',setup+'if defActive then\n',1)
    source=source.replace('      defDx = objectX(defI) - selfX',
                          '\n'.join('      '+line for line in scan.splitlines())+
                          '\n      defDx = objectX(defI) - selfX',1)
    source+='''
if coreId <> 0 then
  bestId = coreId
  bestDistance = coreScore
  defPointX = coreX
  defPointY = coreY
  defThreatX = coreX
  defThreatY = coreY
end if
'''
    return replace(parent,template=source,
                   parameters=parent.parameters | {'core_response_tiles':(24,12,40),'core_radius':(14,8,20)},
                   meaning=parent.meaning+' During an already active defense, heroes within '
                   'core_response_tiles of their god inspect core threats in the existing mobile '
                   'enemy scan. Among visible living enemies within core_radius, accept those '
                   'targeting the god or within6tiles. Prioritize god attackers, then proximity '
                   'and lowHP. Override local targeting and rally with that threat even outside '
                   'the old rally intercept radius. There is no additional object scan, no '
                   'independent inactive-defense recall, and no change to distant attackers. '
                   'Pinned release own god IDs1and2 follow public team. This targets stale '
                   'sentries ignoring a visible core wave after a previously observed rush.')


def solo_base_defense(parent):
    trigger='''backdoorActive = 0
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
end if
if defFront <> 0 and defFrontD <= param_backdoor_tiles * param_backdoor_tiles then
  if defAnchor = defFrontTarget and (defFrontTarget = backdoorGod or defFrontTarget = backdoorGuardA or defFrontTarget = backdoorGuardB) then
    backdoorActive = 1
    defThreatX = defFrontX
    defThreatY = defFrontY
    defPointX = defFrontX
    defPointY = defFrontY
    if defCount < defGroupSize then
      backdoorUntil = worldTick + param_backdoor_hold
    end if
  end if
end if
if backdoorUntil > 0 then
  defUntil = backdoorUntil
end if
'''
    source=parent.template.replace('  defUntil = 0\nend if',
                                   '  defUntil = 0\n  backdoorUntil = 0\nend if',1)
    source=source.replace('defFront = 0\n','defCount = 0\ndefFront = 0\n',1)
    source=source.replace('if worldTick < defUntil then',trigger+'if worldTick < defUntil then',1)
    source+='''
if backdoorActive and coreId = 0 then
  bestId = defFront
  bestDistance = defFrontD
end if
'''
    return replace(parent,template=source,
                   parameters=parent.parameters | {'backdoor_tiles':(24,16,40),'backdoor_hold':(480,120,1440)},
                   memory=tuple(dict.fromkeys(parent.memory+('backdoorUntil',))),
                   meaning=parent.meaning+' Independently of group size, react when the visible '
                   'enemy hero closest to home, within backdoor_tiles, is attacking the observed '
                   'standing own god or its two guards. Pin those structure IDs to this release. '
                   'All roles may return from anywhere, explicitly targeting that visible attacker '
                   'even beyond the ordinary10tile intercept radius. Move the rally to the attacker. '
                   'Visible core emergencies retain higher target priority. For a small group, '
                   'refresh only a backdoor_hold commitment; cap generic survivor refresh to that '
                   'deadline so a single intruder does not create a five-minute duty. A full '
                   'group rush clears this short mode and keeps the normal group commitment. '
                   'If no enemy is visible or no own core structure is being targeted, do not '
                   'invent an attack. This cannot command unrelated teammates or guarantee a '
                   'distant hero returns before a nearly dead god falls.')


def assigned_solo_defense(parent):
    assign='''backdoorSelfX = selfX - defHomeX
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
if backdoorSelfD <= param_near_response * param_near_response or backdoorCommitted = defFront then
  backdoorAccept = 1
end if
if backdoorHelpers = 0 and worldTick >= backdoorFirstSeen + backdoorNearer * param_response_stagger then
  backdoorAccept = 1
end if
if backdoorAccept then
  backdoorCommitted = defFront
'''
    source=parent.template.replace('backdoorActive = 0\n',
        'backdoorActive = 0\nif worldTick >= backdoorUntil then\n  backdoorCommitted = 0\nend if\n',1)
    source=source.replace('  backdoorUntil = 0\nend if',
        '  backdoorUntil = 0\n  backdoorWatched = 0\n  backdoorFirstSeen = 0\n  backdoorLastSeen = 0\n  backdoorCommitted = 0\nend if',1)
    source=source.replace('    backdoorActive = 1\n',
                          '\n'.join('    '+line for line in assign.splitlines())+'\n    backdoorActive = 1\n',1)
    source=source.replace('end if\nif backdoorUntil > 0 then',
                          '  end if\nend if\nif backdoorUntil > 0 then',1)
    return replace(parent,template=source,
                   parameters=parent.parameters | {'near_response':(28,16,40),'response_stagger':(96,24,240)},
                   memory=tuple(dict.fromkeys(parent.memory+('backdoorFirstSeen','backdoorLastSeen','backdoorWatched','backdoorCommitted'))),
                   meaning=parent.meaning+' Assign the isolated-threat response rather than '
                   'recalling every remote hero at once. Heroes within near_response tiles of '
                   'home respond immediately, as do already committed defenders. For others, '
                   'count visible living allies nearer home (IDbreaksties) and stagger response '
                   'by response_stagger ticks per nearer ally. A remote hero responds only if '
                   'no other observed ally is actually targeting the intruder. If nearby '
                   'teammates ignore it, the delay expires and our remote hero can still return. '
                   'A gap of more than72ticks or changed intruder starts a new warning clock. '
                   'This uses observed ally actions, not assumptions about who controls them.')


def protected_solo_defense(parent):
    source=parent.template.replace('  backdoorUntil = 0\n',
                                   '  backdoorUntil = 0\n  backdoorGroupUntil = 0\n',1)
    source=source.replace('if defCount >= defGroupSize then\n  backdoorUntil = 0\nend if',
                          'if defCount >= defGroupSize then\n  backdoorUntil = 0\n  backdoorGroupUntil = defUntil\nend if',1)
    source=source.replace('if defCount < defGroupSize then',
                          'if defCount < defGroupSize and worldTick >= backdoorGroupUntil then',1)
    return replace(parent,template=source,
                   memory=tuple(dict.fromkeys(parent.memory+('backdoorGroupUntil',))),
                   meaning=parent.meaning+' Retain the original group-defense deadline when '
                   'a large rush dwindles to a single survivor. Capture defUntil at every '
                   'observed full-group trigger, and do not start a shorter solo commitment '
                   'until that captured deadline expires. The earlier experimental solo '
                   'rule shortened this already-established duty; this version prevents that '
                   'unintended transition while retaining the independent lone-intruder trigger.')


def nearby_solo_defense(parent):
    source=parent.template.replace('if defFront <> 0 and defFrontD <= param_backdoor_tiles * param_backdoor_tiles then',
        'if defFront <> 0 and defFrontD <= param_backdoor_tiles * param_backdoor_tiles and (selfX - defHomeX) * (selfX - defHomeX) + (selfY - defHomeY) * (selfY - defHomeY) <= param_near_only * param_near_only then',1)
    return replace(parent,template=source,parameters=parent.parameters | {'near_only':(28,16,48)},
                   meaning=parent.meaning+' Limit the new solo-trigger response to heroes '
                   'already within near_only tiles of home. Existing group responses remain '
                   'global. This addresses a nearby defender ignoring a lone guard attacker, '
                   'but does not recall a distant hero when the entire base is unattended.')


def isolated_solo_defense(parent):
    old='if defFront <> 0 and defFrontD <= param_backdoor_tiles * param_backdoor_tiles'
    if parent.template.count(old)!=1:raise ValueError('Solo trigger changed')
    source=parent.template.replace(old,
        'if defCount <= param_isolated_max and defFront <> 0 and defFrontD <= param_backdoor_tiles * param_backdoor_tiles',1)
    return replace(parent,template=source,parameters=parent.parameters | {'isolated_max':(1,1,2)},
                   meaning=parent.meaning+' Apply this added solo response only when at most '
                   'isolated_max visible enemy heroes occupy the existing cluster around the '
                   'nearest home threat. Larger groups retain ordinary group combat targeting, '
                   'rather than all defenders chasing its front hero. This gates the trigger '
                   'and target override together. Hidden reinforcements remain unknown. '
                   'Group deadlines and short isolated duty keep their existing semantics.')


def blue_solo_defense(parent):
    old='if defCount <= param_isolated_max and defFront <> 0'
    if parent.template.count(old)!=1:raise ValueError('Isolated trigger changed')
    return replace(parent,template=parent.template.replace(old,'if selfTeam = 1 and defCount <= param_isolated_max and defFront <> 0',1),
                   meaning=parent.meaning+' Enable this added isolated-attacker response only '
                   'for the fixed blue hero lineup (public selfTeam1). Red keeps the fused '
                   'parent group defense, core interception and rally spacing without this '
                   'new solo trigger. Local failures concentrated on red; blue response and '
                   'red action parity must be validated separately. This is a lineup-specific '
                   'experiment and does not claim to solve red unattended-base attacks.')


def blue_warning_defense(parent):
    old='worldTick > backdoorLastSeen + 72'
    if parent.template.count(old)!=1:raise ValueError('Warning clock changed')
    return replace(parent,template='backdoorWarningTicks = param_warning_ticks\n'+parent.template.replace(old,'worldTick > backdoorLastSeen + backdoorWarningTicks',1),
                   parameters=parent.parameters|{'warning_ticks':(480,96,960)},
                   meaning=parent.meaning+' Retain the same visible intruder warning across '
                   'brief gaps between attacks on a core structure for warning_ticks. Earlier '
                   'three-second expiry could reset the stagger clock before any remote '
                   'backup qualified. Only a current visible qualifying structure attack can '
                   'activate the response; memory alone does not invent a present attack. '
                   'Changed intruder, decision gaps and expiry still reset warning history. '
                   'The separate twenty-second defense duty is unchanged.')


def spread_navigation(parent):
    setup='''defGoalX = defPointX
defGoalY = defPointY
if selfClass = 0 or selfClass = 5 then
  defGoalX = defGoalX - param_rally_spacing
end if
if selfClass = 1 or selfClass = 6 then
  defGoalX = defGoalX + param_rally_spacing
end if
if selfClass = 2 or selfClass = 7 then
  defGoalY = defGoalY - param_rally_spacing
end if
if selfClass = 3 or selfClass = 8 then
  defGoalY = defGoalY + param_rally_spacing
end if
'''
    source=parent.template.replace('defPointX','defGoalX').replace('defPointY','defGoalY')
    source=source.replace('if defActive then','if defActive then\n'+'\n'.join('  '+line for line in setup.splitlines()),1)
    return replace(parent,template=source,parameters=parent.parameters | {'rally_spacing':(2,1,4)},
                   meaning='During defense, assign each public hero class a different rally offset: '
                   'tank west,rangedweapon east,mage north,healer south,melee carry center, spaced '
                   'by rally_spacing tiles. Terrain fallback searches around this individual point. '
                   'This reduces identical walk destinations; it does not prove collision-free routes '
                   'or change enemy targeting. Outside defense, original wave movement is unchanged. '
                   +parent.meaning)
