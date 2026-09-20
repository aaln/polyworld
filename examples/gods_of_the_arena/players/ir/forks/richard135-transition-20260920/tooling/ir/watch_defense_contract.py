"""Separate remembered defensive responsibility from physically waiting at a rally."""
from dataclasses import replace


def watch_defense(parent):
    source = parent.template.replace('defActive = 0', '''watchPressure = 0
if worldTick <= defLastTick then
  watchAdvance = 0
  watchQuiet = worldTick
  watchAnchor = 0
end if
defActive = 0''', 1)
    token = '    defUntil = worldTick + defHoldTicks'
    assert source.count(token) == 1
    source = source.replace(token, '''    watchPressure = 1
    watchAdvance = 0
    watchQuiet = worldTick
    watchAnchor = defAnchor
    watchX = defAnchorX
    watchY = defAnchorY
    defUntil = worldTick + defHoldTicks''', 1)
    # Revalidate during the existing bounded pass, without dropping pressure memory.
    token = 'while defI < objectCount() and defI < 64\n'
    first = source.index(token) + len(token)
    source = source[:first] + '''  if watchAnchor <> 0 and objectId(defI) = watchAnchor and objectHp(defI) <= 0 then
    watchAnchor = 0
    watchX = defHomeX
    watchY = defHomeY
    defPointX = defHomeX
    defPointY = defHomeY
  end if
''' + source[first:]
    source = source.replace('if defActive then\n', '''if watchAdvance and watchPressure = 0 then
  defActive = 0
end if
if defActive then
''', 1)
    token = '    if defD <= param_intercept_tiles * param_intercept_tiles and (defGroupD <= 400 or defD <= 9) then'
    assert source.count(token) == 1
    source = source.replace(token, '''    watchDx = objectX(defI) - watchX
    watchDy = objectY(defI) - watchY
    watchAdmit = defD <= param_watch_reach * param_watch_reach and watchDx * watchDx + watchDy * watchDy <= param_watch_radius * param_watch_radius
    if watchAdmit or (defD <= param_intercept_tiles * param_intercept_tiles and (defGroupD <= 400 or defD <= 9)) then''', 1)
    source += '''
if defActive then
  watchDx = selfX - defPointX
  watchDy = selfY - defPointY
  if bestId <> 0 or watchPressure or watchDx * watchDx + watchDy * watchDy > param_watch_arrival * param_watch_arrival then
    watchQuiet = worldTick
  end if
  if bestId = 0 and watchPressure = 0 and worldTick - watchQuiet >= param_watch_quiet then
    watchAdvance = 1
    defActive = 0
    watchReleases = watchReleases + 1
  end if
end if
'''
    return replace(parent, template=source,
        parameters=parent.parameters | {'watch_reach': (32, 20, 40), 'watch_radius': (24, 14, 30),
            'watch_arrival': (8, 4, 12), 'watch_quiet': (480, 240, 1440)},
        memory=parent.memory + ('watchAnchor', 'watchX', 'watchY', 'watchAdvance', 'watchQuiet', 'watchReleases'),
        meaning=parent.meaning + ' Superseding physical waiting: remember the refreshed standing '
        'anchor and target visible living mobile enemies within watch_radius of it and watch_reach '
        'of self. A destroyed anchor transfers the rally to the friendly god without cancelling '
        'the defensive commitment. After watch_quiet ticks without a selected target or fresh '
        'observed pressure, counted only within watch_arrival of the rally, resume normal offense. '
        'Keep defUntil and the ordinary survivor alarm while advancing: a fresh observed threat '
        'can recall immediately, even if fewer heroes remain than the initial group threshold. '
        'This differs from clearing the defense clock and requiring a new full group. No inference '
        'that hidden enemies died. Distinct rally destinations come from the navigation skill. '
        'Validate complete game outcomes; lease retention is not a guarantee of timely rescue.')


def quiet_watch(parent):
    """Narrow followup: retain exact original engagement range and rally geometry."""
    broad = watch_defense(parent)
    start = broad.template.index('    watchDx = objectX(defI) - watchX\n')
    end = broad.template.index('\n', broad.template.index('    if watchAdmit or ',start))
    source = broad.template[:start] + '    if defD <= param_intercept_tiles * param_intercept_tiles and (defGroupD <= 400 or defD <= 9) then' + broad.template[end:]
    return replace(broad,template=source,
        parameters={k:v for k,v in broad.parameters.items() if k not in ('watch_reach','watch_radius')},
        meaning=parent.meaning + ' Superseding prolonged waiting: after watch_quiet ticks of '
        'no selected target or fresh pressure while within watch_arrival of the rally, resume '
        'ordinary offensive selection. Retain defUntil so a single returning survivor near a '
        'friendly standing anchor can immediately recall the team. During travel or fresh combat '
        'the quiet timer resets. A destroyed saved anchor transfers the rally home without '
        'cancelling the pressure lease. Original target admission, scoring, and rally geometry '
        'are preserved; no enlarged engagement range. No assumption that unseen heroes are dead. '
        'Validate both actual transitions and competitive outcomes.')


def protected_watch(parent):
    base=quiet_watch(parent)
    source=base.template.replace('defFront = 0\n','watchGuards = 0\ndefFront = 0\n',1)
    token='while defI < objectCount() and defI < 64\n'
    source=source.replace(token,token+'''  if objectId(defI) = 28 or objectId(defI) = 29 then
    if objectTeam(defI) = selfTeam and objectHp(defI) >= param_watch_guard_hp then
      watchGuards = watchGuards + 1
    end if
  end if
''',1)
    token='if watchAdvance and watchPressure = 0 then\n'
    source=source.replace(token,'''watchCoreGuard = 0
if watchGuards < 2 and watchAnchor <> 0 and defSentry then
  watchCoreGuard = 1
  watchAdvance = 0
  watchQuiet = worldTick
  defActive = 1
  if defUntil < worldTick + 120 then
    defUntil = worldTick + 120
  end if
  defPointX = defHomeX
  defPointY = defHomeY
  defThreatX = defHomeX
  defThreatY = defHomeY
end if
'''+token,1)
    return replace(base,template=source,parameters=base.parameters|{'watch_guard_hp':(975,1,1950)},
        meaning=base.meaning+' Safety condition for the three sentries after an observed defensive '
        'assignment: on this pinned map red god guards have IDs28and29. Count protected as well '
        'as exposed friendly guards with HP at least watch_guard_hp. If fewer than two qualify, '
        'cancel offensive advance, hold the god itself, refresh the target reference to the god '
        'and retain at least120ticks duty. Quiet release is blocked while this condition holds. '
        'The two nonsentries retain their offensive role. Both guards healthy permits ordinary '
        'quiet counterpush. This uses public friendly structure state, not hidden enemy knowledge. '
        'The policy must only bind this operator to published2026.9.16.5 red.')
