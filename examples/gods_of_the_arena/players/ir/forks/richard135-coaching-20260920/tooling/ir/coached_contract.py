"""Coached wave-supported lane pressure, with explicit observations and memory."""
from dataclasses import replace


def observe(contract):
    return contract('''
if pushInitialized = 0 then
  pushLane = param_primary_lane
  pushInitialized = 1
end if
pushNextLane = pushLane - 1
if pushNextLane < 0 then
  pushNextLane = 2
end if
pushBase = 13 + 6 * pushLane
pushNextBase = 13 + 6 * pushNextLane
if selfTeam = 1 then
  pushBase = 10 + 6 * (2 - pushLane)
  pushNextBase = 10 + 6 * (2 - pushNextLane)
end if
bestId = 0
pushFort = 0
pushTower = 0
pushTier = 10
pushAltTower = 0
pushAltTier = 10
pushTowerTarget = 0
pushIndex = 0
while pushIndex < objectCount()
  if objectTeam(pushIndex) <> selfTeam and objectHp(pushIndex) > 0 and objectAlive(pushIndex) then
    pushId = objectId(pushIndex)
    if objectKind(pushIndex) = 1 then
      pushFort = pushId
    end if
    if objectKind(pushIndex) = 4 then
      if pushId >= pushBase and pushId <= pushBase + 2 then
        if pushId - pushBase < pushTier then
          pushTower = pushId
          pushTier = pushId - pushBase
          pushTx = objectX(pushIndex)
          pushTy = objectY(pushIndex)
          pushTowerTarget = objectTarget(pushIndex)
        end if
      end if
      if pushId >= pushNextBase and pushId <= pushNextBase + 2 then
        if pushId - pushNextBase < pushAltTier then
          pushAltTower = pushId
          pushAltTier = pushId - pushNextBase
          pushAltX = objectX(pushIndex)
          pushAltY = objectY(pushIndex)
        end if
      end if
    end if
  end if
  pushIndex = pushIndex + 1
wend
pushCreeps = 0
pushAltCreeps = 0
pushTargetCreep = 0
pushSupportRadius = 4 + pushTier / 2
pushAltRadius = 4 + pushAltTier / 2
pushIndex = 0
while pushIndex < objectCount()
  if objectTeam(pushIndex) = selfTeam and objectKind(pushIndex) = 3 and objectHp(pushIndex) > 0 and objectAlive(pushIndex) then
    if pushTower <> 0 then
      pushDx = objectX(pushIndex) - pushTx
      pushDy = objectY(pushIndex) - pushTy
      if pushDx * pushDx + pushDy * pushDy <= pushSupportRadius * pushSupportRadius then
        pushCreeps = pushCreeps + 1
        if objectId(pushIndex) = pushTowerTarget then
          pushTargetCreep = 1
        end if
      end if
    end if
    if pushAltTower <> 0 then
      pushDx = objectX(pushIndex) - pushAltX
      pushDy = objectY(pushIndex) - pushAltY
      if pushDx * pushDx + pushDy * pushDy <= pushAltRadius * pushAltRadius then
        pushAltCreeps = pushAltCreeps + 1
      end if
    end if
  end if
  pushIndex = pushIndex + 1
wend
pushSupported = 0
if pushCreeps >= param_min_creeps then
  if pushTowerTarget = 0 or pushTargetCreep = 1 or param_require_creep_target = 0 then
    pushSupported = 1
  end if
end if
if pushTower <> 0 and rushStage < pushTier + 2 then
  rushStage = pushTier + 2
end if
if pushTower <> pushWaitTower or pushSupported then
  pushWaitStart = worldTick
  pushWaitTower = pushTower
end if
pushHold = 0
if pushTower <> 0 and pushSupported = 0 then
  pushHold = 1
end if
if param_rotate_ticks > 0 and pushHold and pushTier >= 1 and pushAltCreeps >= param_min_creeps then
  if worldTick - pushWaitStart >= param_rotate_ticks then
    pushLane = pushNextLane
    rushStage = 0
    pushTower = 0
    pushHold = 0
    pushWaitTower = 0
    pushRotations = pushRotations + 1
  end if
end if
pushUnit = 0
pushUnitScore = 2147483647
pushIndex = 0
while pushIndex < objectCount()
  if objectTeam(pushIndex) <> selfTeam and objectHp(pushIndex) > 0 and objectAlive(pushIndex) then
    pushKind = objectKind(pushIndex)
    if pushKind = 2 or pushKind = 3 then
      pushDx = objectX(pushIndex) - selfX
      pushDy = objectY(pushIndex) - selfY
      pushD = pushDx * pushDx + pushDy * pushDy
      pushAllowed = 1
      if pushHold then
        pushDx = objectX(pushIndex) - pushTx
        pushDy = objectY(pushIndex) - pushTy
        if pushDx * pushDx + pushDy * pushDy <= 81 then
          pushAllowed = 0
        end if
      end if
      if pushAllowed and pushD <= param_clear_tiles * param_clear_tiles then
        pushScore = pushD * 10 + objectHp(pushIndex)
        if pushKind = 2 then
          pushScore = pushScore - 1000
        end if
        if pushScore < pushUnitScore then
          pushUnit = objectId(pushIndex)
          pushUnitScore = pushScore
        end if
      end if
    end if
  end if
  pushIndex = pushIndex + 1
wend
if pushSupported and pushTower <> 0 then
  bestId = pushTower
end if
if pushUnit <> 0 then
  bestId = pushUnit
end if
if pushFort <> 0 then
  bestId = pushFort
  pushHold = 0
end if
''', {'primary_lane':(2,0,2),'min_creeps':(1,1,4),'clear_tiles':(6,3,9),
       'require_creep_target':(1,0,1),'rotate_ticks':(0,0,1440)}, [], ['candidate','push_state'], [],
       'Coached LanePush: retain one mirrored lane across decisions and respawns. Observe its first exposed tower and count living allied creeps in a conservative integer approximation of its aggro circle. Optionally require no current target or a supported creep target, since towers retain hero aggro. Clear nearby lane blockers; never chase globally. Without support, exclude unit targets inside9tiles of that tower and hold outside. An observed exposed fort outranks all targets. Optional rotation only after an exposed inner/gate proves outer progress, the current tower lacks support for rotate_ticks, and the next lane has a visible exposed tower with creeps. No absent tower is assumed destroyed.',
       ['pushInitialized','pushLane','pushWaitTower','pushWaitStart','pushRotations','rushStage'])


def navigate(parent):
    template=parent.template.replace('param_lane','pushLane')
    template='''if pushHold then
  if pushHoldTower <> pushTower then
    pushDx = selfX - pushTx
    pushDy = selfY - pushTy
    pushAx = pushDx
    pushAy = pushDy
    if pushAx < 0 then
      pushAx = -pushAx
    end if
    if pushAy < 0 then
      pushAy = -pushAy
    end if
    pushScale = pushAx
    if pushAy > pushScale then
      pushScale = pushAy
    end if
    if pushScale = 0 then
      pushDx = 1
      pushScale = 1
    end if
    pushHoldX = pushTx + pushDx * param_hold_tiles / pushScale
    pushHoldY = pushTy + pushDy * param_hold_tiles / pushScale
    pushHoldTower = pushTower
  end if
  moveAccepted = walkTo(pushHoldX, pushHoldY)
else
  pushHoldTower = 0
'''+ '\n'.join('  '+line for line in template.splitlines())+'\nend if'
    return replace(parent,template=template,parameters={'arrival_tiles':(6,2,12),'hold_tiles':(9,8,14)},
                   reads=('candidate','push_state'),meaning='Hold a stable9tile-or-greater offset from an unsupported visible lane tower; issue movement to stop stale attacks. Otherwise follow the shared mirrored lane route. Holding resets for a new tower or when support returns. Waypoints and hold radius use published map coordinates; navigation success remains host-authoritative.',
                   memory=tuple(sorted(set(parent.memory)|{'pushHoldTower','pushHoldX','pushHoldY'})))


def blocker_revision(parent):
    return replace(parent,
        template=parent.template.replace('<= 81 then','<= (6 + pushTier / 2) * (6 + pushTier / 2) then')
            .replace('pushScore = pushD * 10 + objectHp(pushIndex)\n        if pushKind = 2 then\n          pushScore = pushScore - 1000\n        end if','pushScore = pushD'),
        parameters=parent.parameters|{'clear_tiles':(12,3,20)},
        meaning=parent.meaning+' Revised blocker combat: nearest local mobile enemy, no hero-class bonus. Permit fights outside the actual tower aggro circle plus integer safety margin(6/6/7tiles), instead of excluding all units inside9tiles. Bounds still prevent global chasing.')


def ranged_revision(parent):
    return replace(parent,template=parent.template.replace(
        'if pushTower <> 0 and rushStage < pushTier + 2 then',
        '''if pushTower <> 0 and selfAttackRange >= param_safe_range and pushTowerTarget <> selfId then
  pushSupported = 1
end if
if pushTower <> 0 and rushStage < pushTier + 2 then'''),
        parameters=parent.parameters|{'safe_range':(330000,300000,390000)},
        meaning=parent.meaning+' Melee creep gate retained. Ranged heroes at or above safe_range may pressure the tower footprint without waiting for creeps; immediately hold if its observed target becomes self. This exploits footprint-versus-center range geometry on the published map. It is a tested hypothesis of safe range, not a universal guarantee from integer positions.')


def focus_revision(parent):
    return replace(parent,
        template=parent.template.replace('pushLane = param_primary_lane',
            'pushLane = param_primary_lane\n  if selfTeam = 1 then\n    pushLane = param_blue_lane\n  end if').replace(
            'if pushSupported and pushTower <> 0 then\n  bestId = pushTower',
            'if pushSupported and pushTower <> 0 then\n  if pushUnitScore > param_siege_defense_tiles * param_siege_defense_tiles then\n    pushUnit = 0\n  end if\n  bestId = pushTower'),
        parameters=parent.parameters|{'blue_lane':(0,0,2),'siege_defense_tiles':(12,3,12)},
        meaning=parent.meaning+' Team-specific initial lane assignment, then persistent commitment. During permitted siege, only mobile enemies within siege_defense_tiles interrupt tower focus; otherwise retain the broader local blocker search. This radius is about the hero, not the tower. The fort always overrides this combat choice.')


def guards_revision(parent):
    template=parent.template.replace('pushTower = 0\npushTier = 10',
        'pushTower = 0\npushGuard = 0\npushTier = 10')
    template=template.replace('if objectKind(pushIndex) = 4 then', '''if objectKind(pushIndex) = 4 then
      if pushId >= 28 and pushId <= 31 then
        if pushGuard = 0 or pushId < pushGuard then
          pushGuard = pushId
          pushGuardX = objectX(pushIndex)
          pushGuardY = objectY(pushIndex)
          pushGuardTarget = objectTarget(pushIndex)
        end if
      end if''',1)
    template=template.replace('pushCreeps = 0', '''if pushGuard <> 0 then
  pushTower = pushGuard
  pushTier = 2
  pushTx = pushGuardX
  pushTy = pushGuardY
  pushTowerTarget = pushGuardTarget
  rushStage = 5
end if
pushCreeps = 0''',1)
    return replace(parent,template=template,
        meaning=parent.meaning+' On release2026.9.16.5, an exposed enemy guard(ID28..31) overrides remaining lane towers. Select the lowest visible exposed guard ID for shared focus. Guards inherit gate-tier support/aggro checks. A lane breach exposes guards, not the god; the god is selected only when objectAlive confirms both guards have fallen. Barracks remain optional for hero victory, although clearing them can release allied creeps toward guards.')


def convoy_revision(parent):
    template=parent.template.replace('bestId = 0\npushFort = 0', '''pushBarracksFirst = 40
if pushLane = 2 then
  pushBarracksFirst = 44
end if
if pushLane = 1 then
  pushBarracksFirst = 48
end if
pushBarracksFirst = pushBarracksFirst + selfTeam
pushBarracks = 0
bestId = 0
pushFort = 0''',1)
    template=template.replace('if objectKind(pushIndex) = 4 then', '''if param_open_wave and objectKind(pushIndex) = 5 then
      if pushId = pushBarracksFirst or pushId = pushBarracksFirst + 2 then
        if pushBarracks = 0 or pushId < pushBarracks then
          pushBarracks = pushId
        end if
      end if
    end if
    if objectKind(pushIndex) = 4 then''',1)
    template=template.replace('if pushFort <> 0 then\n  bestId = pushFort', '''if pushBarracks <> 0 then
  bestId = pushBarracks
  pushHold = 0
end if
if pushFort <> 0 then
  bestId = pushFort''',1)
    return replace(parent,template=template,parameters=parent.parameters|{'open_wave':(1,0,1)},
        meaning=parent.meaning+' When open_wave is enabled, exposed barracks in the committed lane override guard siege and local blockers. Clear both in stable ID order to release the allied creep convoy toward guards. IDs come from the verified public116tile competition map: normalized lane0 pair40/42, lane2 pair44/46, lane1 pair48/50, plus1 forblue attackers. No barricade destruction is inferred from absence. An exposed god remains highest priority.')


def defense_revision(parent):
    template=parent.template.replace('pushUnit = 0\npushUnitScore',
        'pushThreatDistance = 2147483647\npushUnit = 0\npushUnitScore',1)
    template=template.replace('pushAllowed = 1\n      if pushHold then', '''if pushD < pushThreatDistance then
        pushThreatDistance = pushD
        pushThreatX = objectX(pushIndex)
        pushThreatY = objectY(pushIndex)
      end if
      pushAllowed = 1
      if pushHold then''',1)
    template=template.replace('if pushAllowed and pushD <=', '''if pushD <= (selfAttackRange / 60000) * (selfAttackRange / 60000) then
        pushAllowed = 1
      end if
      if pushAllowed and pushD <=''')
    return replace(parent,template=template,
        meaning=parent.meaning+' While holding outside an unsupported tower, still fight a nearby mobile enemy already within conservative personal attack range. This permits stationary self-defense without authorizing pursuit into the tower circle. Record the nearest visible mobile threat for optional health recovery.')


def recovery_revision(parent):
    prefix='''if selfHp * 100 >= selfMaxHp * (param_recover_percent + 20) then
  pushRecovering = 0
end if
if param_recover_percent > 0 and selfHp * 100 <= selfMaxHp * param_recover_percent and pushThreatDistance <= 100 then
  pushRecovering = 1
end if
if pushRecovering and pushThreatDistance <= 100 and pushFort = 0 then
  pushDx = selfX - pushThreatX
  pushDy = selfY - pushThreatY
  pushAx = pushDx
  pushAy = pushDy
  if pushAx < 0 then
    pushAx = -pushAx
  end if
  if pushAy < 0 then
    pushAy = -pushAy
  end if
  pushScale = pushAx
  if pushAy > pushScale then
    pushScale = pushAy
  end if
  if pushScale = 0 then
    pushDx = 1
    pushScale = 1
  end if
  moveAccepted = walkTo(selfX + pushDx * 5 / pushScale, selfY + pushDy * 5 / pushScale)
  motionActive = 1
else
'''
    return replace(parent,template=prefix+'\n'.join('  '+l for l in parent.template.splitlines())+'\nend if',
        parameters=parent.parameters|{'recover_percent':(30,0,60)},
        reads=tuple(sorted(set(parent.reads)|{'push_state'})),
        memory=tuple(sorted(set(parent.memory)|{'pushRecovering'})),
        meaning=parent.meaning+' Optional health recovery starts at recover_percent while a mobile threat is within10tiles. Step5tiles away from its observed position instead of attacking; stop recovery after healing20percentagepoints above the trigger. Exposed god finishing overrides recovery. Existing class combat handles healthy decisions. Movement remains host-authoritative and may fail; this is not a guaranteed escape.')


def strike_revision(parent):
    template=parent.template.replace('pushScore = pushD\n', '''pushScore = pushD
        if pushKind = 2 and pushD <= param_focus_tiles * param_focus_tiles then
          pushScore = objectHp(pushIndex) + pushD - 4000
        end if
''',1).replace('pushUnitScore = pushScore', 'pushUnitScore = pushScore\n          pushUnitDistance = pushD',1)
    template=template.replace('if pushUnitScore > param_siege_defense_tiles', 'if pushUnitDistance > param_siege_defense_tiles',1)
    return replace(parent,template=template,parameters=parent.parameters|{'focus_tiles':(6,3,8)},
        meaning=parent.meaning+' During local lane defense, prioritize a visible enemy hero within focus_tiles by HP plus squared distance minus4000. Otherwise retain nearest-mobile targeting. Store physical candidate distance separately from utility so siege-defense bounds still apply. This concentrates attacks on nearby vulnerable heroes without global roaming; it is an explicit scoring heuristic, not a guaranteed shared target.')
