"""Current-map macro decisions: limit pursuit, choose objectives, follow lanes."""
from dataclasses import replace

def bounded_pursuit(parent):
    return replace(parent, template=parent.template + '''
macroIndex = 0
while macroIndex < objectCount()
  if objectId(macroIndex) = bestId then
    if objectKind(macroIndex) = 2 or objectKind(macroIndex) = 3 then
      macroDx = objectX(macroIndex) - selfX
      macroDy = objectY(macroIndex) - selfY
      if macroDx * macroDx + macroDy * macroDy > param_pursuit_tiles * param_pursuit_tiles then
        bestId = 0
      end if
    end if
  end if
  macroIndex = macroIndex + 1
wend''', parameters=parent.parameters | {'pursuit_tiles': (12, 4, 32)},
      meaning=parent.meaning + ' Reject the selected mobile target beyond pursuit_tiles center distance; permit the no-target navigation rule. Structures are unaffected. This is a pursuit bound, not a visibility bound.')

def objectives(contract):
    return contract('''
bestId = 0
bestDistance = 2147483647
macroIndex = 0
while macroIndex < objectCount()
  if objectTeam(macroIndex) <> selfTeam and objectAlive(macroIndex) and objectHp(macroIndex) > 0 then
    macroKind = objectKind(macroIndex)
    macroDx = objectX(macroIndex) - selfX
    macroDy = objectY(macroIndex) - selfY
    macroD = macroDx * macroDx + macroDy * macroDy
    macroAllowed = 0
    macroInset = 0
    macroWeight = param_unit_weight
    if macroKind = 2 or macroKind = 3 then
      if macroD <= param_pursuit_tiles * param_pursuit_tiles then
        macroAllowed = 1
      end if
    else
      if macroD <= param_structure_tiles * param_structure_tiles then
        macroAllowed = 1
      end if
      macroInset = 2
      macroWeight = 1
      if macroKind = 1 then
        macroInset = 4
      end if
    end if
    if macroAllowed then
      if macroDx < 0 then
        macroDx = -macroDx
      end if
      if macroDy < 0 then
        macroDy = -macroDy
      end if
      macroDx = macroDx - macroInset
      macroDy = macroDy - macroInset
      if macroDx < 0 then
        macroDx = 0
      end if
      if macroDy < 0 then
        macroDy = 0
      end if
      macroScore = (macroDx * macroDx + macroDy * macroDy) * macroWeight
      if macroKind = 1 then
        macroScore = -1
      end if
      if macroScore < bestDistance then
        bestDistance = macroScore
        bestId = objectId(macroIndex)
      end if
    end if
  end if
  macroIndex = macroIndex + 1
wend
''', {'pursuit_tiles':(10,4,32), 'structure_tiles':(32,8,64), 'unit_weight':(6,1,32)}, [], ['candidate'], [],
      'Within declared pursuit bounds, score exposed positive-HP enemies by approximate footprint-edge squared distance, with mobile-unit penalty. Exposed visible forts outrank other targets within structure_tiles. Visibility and objectAlive remain host-authoritative; no inference that unseen buildings are destroyed.')

def lanes(contract):
    # Coordinates are public waypoints of the 116-tile competition arena.
    # Mirroring swaps the outer lanes; no unseen state enters this route.
    points=[[(76,12),(23,12),(8,42),(8,74),(8,83),(11,105)],
            [(81,30),(64,43),(51,73),(35,86),(20,94),(11,105)],
            [(108,44),(108,69),(96,104),(50,104),(32,108),(11,105)]]
    lines=['laneSlot = selfId - 100 - selfTeam * 5','laneChoice = 1',
           'if laneSlot = 0 or laneSlot = 1 then','  laneChoice = 0','end if',
           'if laneSlot = 3 or laneSlot = 4 then','  laneChoice = 2','end if',
           'laneX = selfX','laneY = selfY','if selfTeam = 1 then','  laneX = 116 - selfX','  laneY = 116 - selfY','end if',
           'laneDx = laneX - 105','laneDy = laneY - 11',
           'if laneDx * laneDx + laneDy * laneDy < 144 then','  laneStage = 0','end if',
           'lanePass = 0','while lanePass < 2','  laneMoveX = 11','  laneMoveY = 105']
    for lane,route in enumerate(points):
        for stage,(x,y) in enumerate(route):
            lines += [f'  if laneChoice = {lane} and laneStage = {stage} then', f'    laneMoveX = {x}',f'    laneMoveY = {y}','  end if']
    lines += ['  laneDx = laneX - laneMoveX','  laneDy = laneY - laneMoveY',
              '  if laneStage < 5 and laneDx * laneDx + laneDy * laneDy <= param_arrival_tiles * param_arrival_tiles then',
              '    laneStage = laneStage + 1','  end if','  lanePass = lanePass + 1','wend',
              'if selfTeam = 1 then','  laneMoveX = 116 - laneMoveX','  laneMoveY = 116 - laneMoveY','end if',
              'moveAccepted = walkTo(laneMoveX, laneMoveY)','laneDecisions = laneDecisions + 1']
    return contract('\n'.join(lines), {'arrival_tiles':(8,2,12)}, [], [], ['walkTo'],
        'Use public fixed competition-map waypoints, mirrored by team, with 2/1/2 hero-slot allocation. Advance when within arrival_tiles; reset near own spawn. Walk only in the no-candidate/no-motion rule. Routes do not assert structure destruction or guaranteed path acceptance.', ['laneStage','laneDecisions'])

def budgeted_cadence(parent):
    return replace(parent, template='''if objectCount() > param_motion_object_limit then
  motionActive = 0
  if bestId <> 0 then
    attackTarget(bestId)
  end if
else
''' + '\n'.join('  '+line for line in parent.template.splitlines()) + '\nend if',
        parameters=parent.parameters | {'motion_object_limit':(80,40,120)},
        meaning=parent.meaning + ' Above motion_object_limit observed objects, skip the expensive recovery scan and issue an ordinary attack; clear per-decision motionActive. On resuming, the existing decision-gap reset invalidates stale recovery memory. This bounds combat-controller work, not the host object count.')
