"""Shared public-map lane objective and direct fort finishing on release .3."""


def objective(contract):
    return contract('''
bestId = 0
bestDistance = 2147483647
rushBase = 13 + 6 * param_lane
if selfTeam = 1 then
  rushBase = 10 + 6 * (2 - param_lane)
end if
rushFort = 0
rushTower = 0
rushTowerRank = 10
rushTowerDistance = 2147483647
rushUnit = 0
rushUnitDistance = 2147483647
rushIndex = 0
while rushIndex < objectCount()
  if objectTeam(rushIndex) <> selfTeam and objectHp(rushIndex) > 0 and objectAlive(rushIndex) then
    rushId = objectId(rushIndex)
    rushKind = objectKind(rushIndex)
    rushDx = objectX(rushIndex) - selfX
    rushDy = objectY(rushIndex) - selfY
    rushD = rushDx * rushDx + rushDy * rushDy
    if rushKind = 1 then
      rushFort = rushId
      rushStage = 5
    end if
    if rushKind = 4 and rushId >= rushBase and rushId <= rushBase + 2 then
      rushRank = rushId - rushBase
      if rushRank < rushTowerRank then
        rushTower = rushId
        rushTowerRank = rushRank
        rushTowerDistance = rushD
      end if
      if rushStage < rushRank + 2 then
        rushStage = rushRank + 2
      end if
    end if
    if param_clear_tiles > 0 and (rushKind = 2 or rushKind = 3) then
      if rushD <= param_clear_tiles * param_clear_tiles and rushD < rushUnitDistance then
        rushUnit = rushId
        rushUnitDistance = rushD
      end if
    end if
  end if
  rushIndex = rushIndex + 1
wend
bestId = rushTower
if rushUnit <> 0 and rushTowerDistance > 144 then
  bestId = rushUnit
end if
if rushFort <> 0 then
  bestId = rushFort
end if
''', {'lane': (2, 0, 2), 'clear_tiles': (0, 0, 8)}, [], ['candidate'], [],
        'All same-team copies select the same mirrored public-map lane. Attack its first observed exposed positive-HP tower, then immediately prioritize an observed exposed enemy fort. Never select barracks or another lane. Optional nearby-unit clearing applies only when the selected tower is more than12tiles away. Static tower IDs encode published topology, not hidden state; eligibility requires current team visibility and exposure.', ['rushStage'])


def route(contract):
    points = [
        [(76,12),(23,12),(8,47),(8,78),(5,87),(11,105)],
        [(81,30),(65,43),(51,73),(35,86),(19,97),(11,105)],
        [(108,44),(108,69),(95,104),(47,104),(30,111),(11,105)],
    ]
    lines = ['rushX = selfX', 'rushY = selfY', 'if selfTeam = 1 then',
             '  rushX = 116 - selfX', '  rushY = 116 - selfY', 'end if',
             'rushDx = rushX - 105', 'rushDy = rushY - 11',
             'if rushDx * rushDx + rushDy * rushDy < 100 then', '  rushStage = 0', 'end if',
             'rushPass = 0', 'while rushPass < 2', '  rushMoveX = 11', '  rushMoveY = 105']
    for lane, path in enumerate(points):
        for stage, (x, y) in enumerate(path):
            lines += [f'  if param_lane = {lane} and rushStage = {stage} then',
                      f'    rushMoveX = {x}', f'    rushMoveY = {y}', '  end if']
    lines += ['  rushDx = rushX - rushMoveX', '  rushDy = rushY - rushMoveY',
              '  if rushStage < 5 and rushDx * rushDx + rushDy * rushDy <= param_arrival_tiles * param_arrival_tiles then',
              '    rushStage = rushStage + 1', '  end if', '  rushPass = rushPass + 1', 'wend',
              'if selfTeam = 1 then', '  rushMoveX = 116 - rushMoveX', '  rushMoveY = 116 - rushMoveY', 'end if',
              'moveAccepted = walkTo(rushMoveX, rushMoveY)']
    return contract('\n'.join(lines), {'lane': (2, 0, 2), 'arrival_tiles': (6, 2, 12)}, ['candidate'], [], ['walkTo'],
        'Every class follows identical mirrored waypoints on the116tile competition map when no objective or eligible nearby blocker is visible. Progress persists; reset near own spawn. Observed exposed towers advance route progress. The final waypoint is the enemy fort; no barracks detour. Shared goals coordinate copies without assuming private policy identity or messages.', ['rushStage'])
