"""Versioned binding for the complete September20 coached team assault.

The grouping, shared target, perimeter probe, breach commitment and movement
tether are one coordinated mechanism. Only public per-decision objects enter it.
Blue retains the exact critical60 controller; early red retains its parent.
"""
from dataclasses import replace
from textwrap import dedent
import re
from binding import CONTRACTS, contract
from games.gods_of_the_arena.instruments.richard_counter import contracts as parent_contracts

NAME = 'richard_coached_formation_v1'

# Red macro and inherited observer are mutually exclusive. Reuse their scratch
# storage to stay within the real 256-global VM limit. The five persistent
# backdoor fields are otherwise blue-only; each hero has a separate VM.
ALIASES = dict(zip(
    ('gaEntry gaEntryUntil gaLastTick gaProbeSince gaBreachUntil gaX gaY gaMoveX gaMoveY '
     'gaPhase gaEmergency gaNear gaSpread gaN gaAlive gaEnemyN gaMinX gaMaxX gaMinY gaMaxY '
     'gaHomeThreats gaFrontX gaFrontY gaFrontD gaHomeHp gaI gaKind gaTeam gaHp gaOx gaOy '
     'gaDx gaDy gaD gaHero gaHeroScore gaObjective gaObjectiveD gaObjectiveX gaObjectiveY '
     'gaCover gaLocal gaLocalD gaEntry0 gaEntry1 gaEntry2 gaSx gaSy gaSelfD gaScore gaBaseD '
     'gaEntryScore gaNavX gaNavY gaFound gaDirection gaStepX gaStepY gaMoved').split(),
    ('backdoorWatched backdoorGroupUntil backdoorLastSeen backdoorFirstSeen backdoorCommitted '
     'defPointX defPointY defGoalX defGoalY defSentryRole defSentry defMates pairedRush '
     'macroIndex defGroupSize defCount coreDx coreDy coreX coreY coreRespond '
     'defFrontX defFrontY defFrontD coreValue defI defKind coreTarget pairAnchorHp '
     'perimeterObjX perimeterObjY defDx defDy defD defFront defScore coreId coreD '
     'backdoorX backdoorY backdoorHelpers backdoorAlly backdoorD perimeterBoundSq '
     'perimeterRadiusSq perimeterReachSq backdoorSelfX backdoorSelfY backdoorSelfD '
     'coreScore perimeterBound perimeterAdmit defNavX defNavY defNavFound defdirection '
     'defDirX defDirY defMoveAccepted').split(), strict=True))
assert len(set(ALIASES.values())) == len(ALIASES)


def lower_storage(source):
    return re.sub(r'\bga\w+\b', lambda m: ALIASES.get(m[0],m[0]), source)

MACRO = dedent('''
gaActive = 1
defActive = 0
defUntil = 0
bestId = 0
bestDistance = 2147483647
gaN = objectCount()
gaAlive = 0
gaX = 0
gaY = 0
gaEnemyN = 0
gaMinX = 116
gaMaxX = 0
gaMinY = 116
gaMaxY = 0
gaHomeThreats = 0
gaFrontD = 2147483647
gaFrontX = 105
gaFrontY = 11
gaHomeHp = 400
gaI = 0
while gaI < gaN and gaI < 64
  gaKind = objectKind(gaI)
  gaTeam = objectTeam(gaI)
  gaHp = objectHp(gaI)
  gaOx = objectX(gaI)
  gaOy = objectY(gaI)
  if gaKind = 1 and gaTeam = selfTeam then
    gaHomeHp = gaHp
  end if
  if gaKind = 2 and gaHp > 0 and objectAlive(gaI) then
    if gaTeam = selfTeam then
      gaAlive = gaAlive + 1
      gaX = gaX + gaOx
      gaY = gaY + gaOy
    else
      gaEnemyN = gaEnemyN + 1
      if gaOx < gaMinX then
        gaMinX = gaOx
      end if
      if gaOx > gaMaxX then
        gaMaxX = gaOx
      end if
      if gaOy < gaMinY then
        gaMinY = gaOy
      end if
      if gaOy > gaMaxY then
        gaMaxY = gaOy
      end if
      gaDx = gaOx - 105
      gaDy = gaOy - 11
      gaD = gaDx * gaDx + gaDy * gaDy
      if gaD <= param_home_radius * param_home_radius then
        gaHomeThreats = gaHomeThreats + 1
      end if
      if gaD < gaFrontD then
        gaFrontD = gaD
        gaFrontX = gaOx
        gaFrontY = gaOy
      end if
    end if
  end if
  gaI = gaI + 1
wend
if gaAlive > 0 then
  gaX = gaX / gaAlive
  gaY = gaY / gaAlive
else
  gaX = selfX
  gaY = selfY
end if
gaNear = 0
gaHero = 0
gaHeroScore = 2147483647
gaObjective = 0
gaObjectiveD = 2147483647
gaObjectiveX = 28
gaObjectiveY = 79
gaCover = 0
gaLocal = 0
gaLocalD = 2147483647
gaEntry0 = (gaX - 8) * (gaX - 8) + (gaY - 70) * (gaY - 70)
gaEntry1 = (gaX - 28) * (gaX - 28) + (gaY - 79) * (gaY - 79)
gaEntry2 = (gaX - 48) * (gaX - 48) + (gaY - 103) * (gaY - 103)
gaI = 0
while gaI < gaN and gaI < 160
  gaKind = objectKind(gaI)
  gaTeam = objectTeam(gaI)
  gaHp = objectHp(gaI)
  if gaHp > 0 and objectAlive(gaI) then
    gaOx = objectX(gaI)
    gaOy = objectY(gaI)
    gaDx = gaOx - gaX
    gaDy = gaOy - gaY
    gaD = gaDx * gaDx + gaDy * gaDy
    gaSx = gaOx - selfX
    gaSy = gaOy - selfY
    gaSelfD = gaSx * gaSx + gaSy * gaSy
    if gaTeam = selfTeam then
      if gaKind = 2 and gaHp >= param_ready_hp and gaD <= param_group_radius * param_group_radius then
        gaNear = gaNear + 1
      end if
      if gaKind = 3 and gaD <= 144 then
        gaCover = gaCover + 1
      end if
    else
      if gaKind = 2 then
        gaScore = gaD * 4 + gaHp
        if gaD <= 484 and gaScore < gaHeroScore then
          gaHero = objectId(gaI)
          gaHeroScore = gaScore
        end if
        if (gaOx - 8) * (gaOx - 8) + (gaOy - 70) * (gaOy - 70) <= 784 then
          gaEntry0 = gaEntry0 + gaHp * 4
        end if
        if (gaOx - 28) * (gaOx - 28) + (gaOy - 79) * (gaOy - 79) <= 784 then
          gaEntry1 = gaEntry1 + gaHp * 4
        end if
        if (gaOx - 48) * (gaOx - 48) + (gaOy - 103) * (gaOy - 103) <= 784 then
          gaEntry2 = gaEntry2 + gaHp * 4
        end if
      end if
      if gaKind = 1 or gaKind = 4 then
        if gaD < gaObjectiveD then
          gaObjective = objectId(gaI)
          gaObjectiveD = gaD
          gaObjectiveX = gaOx
          gaObjectiveY = gaOy
        end if
      end if
      if gaKind = 2 or gaKind = 3 then
        if gaSelfD <= 36 and gaSelfD < gaLocalD then
          gaLocal = objectId(gaI)
          gaLocalD = gaSelfD
        end if
      end if
    end if
  end if
  gaI = gaI + 1
wend
gaReady = 0
if gaNear >= 4 then
  gaReady = 1
end if
gaSpread = 0
if gaEnemyN >= 3 and ((gaMaxX - gaMinX) * (gaMaxX - gaMinX) + (gaMaxY - gaMinY) * (gaMaxY - gaMinY)) >= 1024 then
  gaSpread = 1
end if
gaBaseD = (gaX - 11) * (gaX - 11) + (gaY - 105) * (gaY - 105)
gaEmergency = 0
if gaHomeThreats >= 2 or gaHomeHp < 400 then
  gaEmergency = 1
end if
if worldTick <= gaLastTick or worldTick > gaLastTick + 1 then
  gaEntryUntil = 0
  gaProbeSince = 0
  gaBreachUntil = 0
end if
gaLastTick = worldTick
gaMoveX = gaX
gaMoveY = gaY
gaPhase = 1
if gaReady then
  if gaEmergency then
    gaPhase = 4
    gaMoveX = gaFrontX
    gaMoveY = gaFrontY
    gaProbeSince = 0
  else
    gaPhase = 2
    gaMoveX = gaObjectiveX
    gaMoveY = gaObjectiveY
    if gaBaseD <= 3600 then
      if gaProbeSince = 0 then
        gaProbeSince = worldTick
      end if
      if worldTick >= gaEntryUntil then
        if gaEntryUntil > 0 then
          if gaEntry = 0 then
            gaEntry0 = gaEntry0 + 800
          end if
          if gaEntry = 1 then
            gaEntry1 = gaEntry1 + 800
          end if
          if gaEntry = 2 then
            gaEntry2 = gaEntry2 + 800
          end if
        end if
        gaEntry = 0
        gaEntryScore = gaEntry0
        if gaEntry1 < gaEntryScore then
          gaEntry = 1
          gaEntryScore = gaEntry1
        end if
        if gaEntry2 < gaEntryScore then
          gaEntry = 2
        end if
        gaEntryUntil = (worldTick / 240 + 1) * 240
      end if
      gaMoveX = 8
      gaMoveY = 70
      if gaEntry = 1 then
        gaMoveX = 28
        gaMoveY = 79
      end if
      if gaEntry = 2 then
        gaMoveX = 48
        gaMoveY = 103
      end if
      if gaCover >= 2 or gaSpread or worldTick - gaProbeSince >= param_probe_ticks then
        gaBreachUntil = worldTick + 240
      end if
      if worldTick < gaBreachUntil then
        gaPhase = 3
        gaMoveX = gaObjectiveX
        gaMoveY = gaObjectiveY
      end if
    else
      gaProbeSince = 0
      gaPhase = 3
    end if
  end if
  if gaHero <> 0 then
    bestId = gaHero
    bestDistance = gaHeroScore
  else
    if gaPhase = 3 and gaObjectiveD <= 784 then
      bestId = gaObjective
      bestDistance = gaObjectiveD
    end if
  end if
else
  gaBreachUntil = 0
end if
if bestId = 0 and gaLocal <> 0 then
  bestId = gaLocal
  bestDistance = gaLocalD
end if
gaDx = selfX - gaX
gaDy = selfY - gaY
gaTethered = 0
if gaDx * gaDx + gaDy * gaDy > param_tether_radius * param_tether_radius then
  bestId = 0
  gaMoveX = gaX
  gaMoveY = gaY
  gaTethered = 1
end if
''').strip()


def register():
    parent = CONTRACTS['lineup_critical_recall']
    source = ('gaActive = 0\nif selfTeam = 0 and worldTick >= param_phase_tick then\n'
              + '\n'.join('  ' + x for x in MACRO.splitlines()) + '\nelse\n'
              + '\n'.join('  ' + x for x in parent.template.splitlines()) + '\nend if')
    CONTRACTS[NAME] = replace(parent, template=lower_storage(source),
        parameters=parent.parameters | {'phase_tick': (2400, 1200, 4800),
            'group_radius': (14, 10, 22), 'tether_radius': (20, 16, 28),
            'ready_hp': (120, 60, 180), 'probe_ticks': (480, 120, 960),
            'home_radius': (50, 28, 60)},
        writes=parent.writes + ('formation',),
        memory=tuple(dict.fromkeys(parent.memory + tuple(ALIASES[x] for x in
            ('gaEntry','gaEntryUntil','gaLastTick','gaProbeSince','gaBreachUntil')))),
        meaning='Red after phase_tick replaces split-lane selection with a shared '
        'centroid of observed living friendly heroes. Four heroes with at least '
        'ready_hp within group_radius establish team_assault_readiness. Select '
        'one visible nearby hero by centroid distance/HP, else an exposed structure. '
        'At the enemy base exterior, choose among three public-map staging entries '
        'every240ticks using centroid distance and visible defender HP, penalizing '
        'the previous entry to continue probing. Breach when two nearby allied '
        'creeps, observed dispersion of at least three enemies, or bounded probe '
        'time supplies a trigger; never infer dispersion from absent enemies. '
        'Losing readiness cancels breach. A home alarm of two visible heroes within '
        'home_radius or damaged friendly god redirects the gathered team to defense. '
        'An actor farther than tether_radius from the centroid must regroup. '
        'Only current public observations are used. No player identity or hidden '
        'intent. Blue and early red retain exact critical-recall parent behavior.')
    parent_attack = CONTRACTS['defense_cadence']
    CONTRACTS['richard_formation_combat_v1'] = replace(parent_attack,
        template='if gaActive and gaTethered then\n  motionActive = 0\nelse\n'
          + '\n'.join('  '+x for x in parent_attack.template.splitlines())+'\nend if',
        reads=parent_attack.reads+('formation',),
        meaning=parent_attack.meaning+' Formation tether supersedes inherited recovery/attack movement while rejoining.')
    parent_route = CONTRACTS['lineup_perimeter_route']
    route = '''if gaActive then
  gaNavX = gaMoveX
  gaNavY = gaMoveY
  gaFound = terrainWalkable(gaNavX, gaNavY)
  gaDirection = 0
  while gaDirection < 8 and gaFound = 0
    gaStepX = 0
    gaStepY = 0
    if gaDirection = 0 or gaDirection = 1 or gaDirection = 7 then
      gaStepX = 3
    end if
    if gaDirection = 3 or gaDirection = 4 or gaDirection = 5 then
      gaStepX = -3
    end if
    if gaDirection = 1 or gaDirection = 2 or gaDirection = 3 then
      gaStepY = 3
    end if
    if gaDirection = 5 or gaDirection = 6 or gaDirection = 7 then
      gaStepY = -3
    end if
    gaNavX = gaMoveX + gaStepX
    gaNavY = gaMoveY + gaStepY
    gaFound = terrainWalkable(gaNavX, gaNavY)
    gaDirection = gaDirection + 1
  wend
  gaMoved = 0
  if gaFound then
    gaMoved = walkTo(gaNavX, gaNavY)
  end if
  if gaMoved = 0 then
    gaMoved = walkTo(gaX, gaY)
  end if
else
'''
    CONTRACTS['richard_formation_route_v1'] = replace(parent_route,
        template=lower_storage(route)+'\n'.join('  '+x for x in parent_route.template.splitlines())+'\nend if',
        reads=parent_route.reads+('formation',),
        meaning='When coached formation is active, route to the group rendezvous, '
        'selected perimeter entry, shared exposed objective or home defense point. '
        'Terrain-check the point and eight nearby alternatives; use centroid on '
        'rejected movement. Otherwise retain the entire parent route.')


register()
