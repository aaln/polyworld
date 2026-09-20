"""Retire stale defense objectives and resume wave pressure after real quiet."""
from dataclasses import replace


def counterpush(parent):
    source = parent.template.replace(
        '(worldTick < defUntil and defFrontD <= defContinueHome * defContinueHome)',
        '(worldTick < defUntil and defFrontD <= defContinueHome * defContinueHome and defFrontTarget = defAnchor)')
    source = source.replace('  defUntil = 0\nend if',
                            '  defUntil = 0\n  cpLastPressure = 0\n  cpAnchor = 0\nend if', 1)
    source = source.replace('defFront = 0\n', 'cpRetired = 0\ndefFront = 0\n', 1)
    token = '  if objectKind(defI) = 3 then\n'
    assert source.count(token) == 1
    source = source.replace(token, '''  if cpAnchor <> 0 then
    if objectId(defI) = cpAnchor and objectHp(defI) <= 0 then
      cpRetired = 1
    end if
  end if
''' + token, 1)
    source = source.replace('    defUntil = worldTick + defHoldTicks',
                            '    cpLastPressure = worldTick\n    cpAnchor = defAnchor\n    defUntil = worldTick + defHoldTicks', 1)
    token = 'if worldTick < defUntil then\n'
    assert source.count(token) == 1
    source = source.replace(token, '''cpQuietTicks = param_counter_quiet
if selfClass = 0 then
  cpQuietTicks = param_tank_quiet
end if
if cpRetired and cpLastPressure <> worldTick then
  defUntil = 0
  cpAnchor = 0
end if
if worldTick - cpLastPressure >= cpQuietTicks then
  defUntil = 0
end if
''' + token, 1)
    # A real combat target keeps the duty alive; no-target walking does not.
    source += '''
if defActive and bestId <> 0 then
  cpLastPressure = worldTick
end if
'''
    return replace(parent, template=source, parameters=parent.parameters | {
        'counter_quiet': (480, 120, 1440), 'tank_quiet': (1440, 120, 2880)},
        memory=tuple(dict.fromkeys(parent.memory + ('cpAnchor', 'cpLastPressure'))),
        meaning=parent.meaning + ' Counterpush transition: remember the actual protected '
        'structure ID. Retire its commitment when that observed structure is destroyed, '
        'unless fresh pressure selected a new standing anchor this decision. A survivor '
        'refreshes duty only while actually targeting the standing anchor. A fresh group '
        'or actionable defensive combat target resets the pressure clock. After counter_quiet '
        'ticks without pressure, return to the ordinary wave objective selector. DeathKnight '
        'uses tank_quiet, allowing a longer rear guard while four roles return to attack. '
        'No-target rally walking never refreshes duty. Shared visible groups can recall '
        'heroes again; missing enemies are not assumed dead. Independent solo/core-creep '
        'coverage is unchanged from this parent and remains a limitation to evaluate.')


def counterpush_visible(parent):
    # Pinned sim.nim omits destroyed towers, but always exposes surviving own
    # structures. Absence of this OWN anchor is conclusive; enemy absence is not.
    source = parent.template.replace('cpRetired = 0\n', 'cpRetired = 0\ncpAnchorSeen = 0\n', 1)
    source = source.replace('    if objectId(defI) = cpAnchor and objectHp(defI) <= 0 then\n      cpRetired = 1\n    end if',
                            '    if objectId(defI) = cpAnchor and objectHp(defI) > 0 then\n      cpAnchorSeen = 1\n    end if', 1)
    source = source.replace('if defFront <> 0 then\n',
                            'if cpAnchor <> 0 and cpAnchorSeen = 0 then\n  cpRetired = 1\nend if\nif defFront <> 0 then\n', 1)
    return replace(parent, template=source, meaning=parent.meaning +
        ' Source-correct retirement: surviving own structures are always visible, while '
        'destroyed towers are omitted from the public list. Retire the saved OWN anchor '
        'when absent from the bounded structure-before-creep scan, not by waiting for '
        'a dead tower object the engine never exposes.')
