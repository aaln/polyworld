' Generated from gota_combat_elixir20260923; gota-semantic-policy/1; gota-bassy/combat-elixir-2026-09-23-r1
' @rule comments identify regions only; the extractor reads all executable statements.

' @rule R_portal_state
if selfChannelTicks > 0 then
  portalBusy = 1
end if
if selfPortalCooldown > 0 or selfHp <= 0 then
  portalBusy = 0
end if

' @rule R_draft
active = 0
if drafting = 1 then
  if draftTurnId = selfId then
    pick = -1
    pickScore = -10000
    c = 0
    while c < 10
      if heroAvailable(c) = 1 then
        score = 100
        if c = Ranger then
          score = 180
        end if
        if c = Arcanist then
          score = 170
        end if
        if c = Crossbowman then
          score = 160
        end if
        if c = Lich then
          score = 150
        end if
        if c = DruidWarden then
          score = 140
        end if
        if c = DeathKnight then
          score = 130
        end if
        if c = Warlock then
          score = 120
        end if
        if c = Crossbowman then
          score = score + 300
        end if
        p = 0
        while p < draftPlayerCount()
          if draftPlayerTeam(p) = selfTeam then
            other = draftedClass(draftPlayerId(p))
            if other >= 0 then
              if heroRole(other) = heroRole(c) then
                score = score - 25
              end if
            end if
          end if
          p = p + 1
        wend
        if score > pickScore then
          pickScore = score
          pick = c
        end if
      end if
      c = c + 1
    wend
    if pick >= 0 then
      draftHero(pick)
    end if
  end if
end if
if drafting = 0 then
  if selfHp > 0 then
    if portalBusy = 0 and selfChannelTicks = 0 and selfStunTicks = 0 then
      if worldTick >= nextThink then
        nextThink = worldTick + 6
        active = 1
      end if
    end if
  end if
end if

' @rule R_recovery_intent
if drafting = 0 and selfHp > 0 and portalBusy = 0 and selfChannelTicks = 0 and selfStunTicks = 0 and canShop() = 0 and selfHp * 100 < selfMaxHp * 30 then
  if retreat = 0 then
    active = 1
  end if
  retreat = 1
  resumeTarget = 0
end if

' @rule R_base_recovery_intent
if drafting = 0 and selfHp > 0 and portalBusy = 0 and selfChannelTicks = 0 and canShop() = 1 and selfHp * 100 < selfMaxHp * 30 then
  retreat = 1
  resumeTarget = 0
end if

' @rule R_timing
if selfHp <= 0 then
  resumeTarget = 0
end if
if drafting = 0 and selfHp > 0 then
  if portalBusy = 0 and selfChannelTicks = 0 and selfStunTicks = 0 and selfRootTicks = 0 then
    if resumeTarget > 0 then
      if retreat = 0 and selfTarget = 0 then
        attackTarget(resumeTarget)
      end if
      resumeTarget = 0
    else
      if retreat = 0 and selfTarget > 0 and selfAttacksLanded > previousHits then
        previousHits = selfAttacksLanded
        resumeTarget = selfTarget
        walkTo(selfX + 0.25, selfY + 0.25)
        active = 0
      end if
    end if
  end if
end if

' @rule R_lifecycle
if drafting = 0 then
  if selfHp <= 0 then
    initialized = 0
    retreat = 0
    price = buybackPrice()
    if price > 0 and selfRespawnTicks > tickRate * 25 then
      if selfGold >= price + 200 then
        buyback()
      end if
    end if
  end if
end if
if active = 1 then
  if initialized = 0 then
    initialized = 1
    spawnX = selfX
    spawnY = selfY
    homeX = selfX
    homeY = selfY
    enemyX = mapWidth - 1 - selfX
    enemyY = mapHeight - 1 - selfY
    crossed = 0
    previousHp = selfHp
    previousHits = selfAttacksLanded
    role = heroRole(selfClass)
    ordinal = 0
    p = 0
    while p < draftPlayerCount()
      if draftPlayerTeam(p) = selfTeam then
        if draftPlayerId(p) < selfId then
          ordinal = ordinal + 1
        end if
      end if
      p = p + 1
    wend
    lane = ordinal mod 3
  end if
  justHit = 0
  if selfAttacksLanded > previousHits then
    justHit = 1
  end if
  previousHits = selfAttacksLanded
  if selfHp < previousHp then
    hurtTick = worldTick
  end if
  previousHp = selfHp
  stopped = 0
  upgraded = 0
  while upgraded < 4 and abilityPoints() > 0
    slot = -1
    if canLevelAbility(0) = 1 then
      slot = 0
    end if
    if canLevelAbility(2) = 1 then
      slot = 2
    end if
    if canLevelAbility(1) = 1 then
      slot = 1
    end if
    if canLevelAbility(3) = 1 then
      slot = 3
    end if
    if slot >= 0 then
      levelAbility(slot)
    end if
    upgraded = upgraded + 1
  wend
end if

' @rule R_observe
if active = 1 then
  bestId = 0
  bestScore = -1000000
  bestDistance = 1000000
  threatDistance = 1000000
  recallHeroDistance = 1000000
  recallCreepDistance = 1000000
  homeAnchorDistance = 1000000
  towerDistance = 1000000
  towerAggro = 0
  friendPower = selfLevel + 2
  enemyPower = 0
  tanks = 0
  homeThreat = 0
  homeEnemyHeroes = 0
  homeDefenders = 0
  hitReach = selfAttackRange \ 60000 + 1
  forwardScore = 1000000
  objects = objectCount()
  i = 0
  while i < 96 and i < objects
    idx = i
    if i >= 48 then
      idx = i + scanOffset
    end if
    if idx < objects then
      hp = objectHp(idx)
      if hp > 0 then
        id = objectId(idx)
        kind = objectKind(idx)
        team = objectTeam(idx)
        x = objectX(idx)
        y = objectY(idx)
        dx = x - selfX
        dy = y - selfY
        distance = dx * dx + dy * dy
        if team = selfTeam then
          if kind = 1 then
            homeX = x
            homeY = y
            enemyX = mapWidth - 1 - x
            enemyY = mapHeight - 1 - y
          end if
          if kind = 2 and id <> selfId then
    hx = x - homeX
    hy = y - homeY
    if hx * hx + hy * hy < 400 then
      homeDefenders = homeDefenders + 1
    end if
  end if
  if kind = 2 and id <> selfId and distance <= 100 then
            friendPower = friendPower + objectLevel(idx) + 2
          end if
          if kind = 3 and distance <= 64 then
            tanks = tanks + 1
          end if
          if kind = 4 then
            homeDx = x - spawnX
            homeDy = y - spawnY
            homeGap = homeDx * homeDx + homeDy * homeDy
            if homeGap < homeAnchorDistance then
              homeAnchorDistance = homeGap
            end if
            farmX = mapWidth \ 2
  farmY = mapHeight \ 2
  if lane = 0 then
    farmX = mapWidth \ 10
    farmY = mapHeight \ 10
  end if
  if lane = 2 then
    farmX = mapWidth * 9 \ 10
    farmY = mapHeight * 9 \ 10
  end if
  dx = x - farmX
  dy = y - farmY
            score = dx * dx + dy * dy
            if score < forwardScore then
              forwardScore = score
              forwardX = x
              forwardY = y
            end if
          end if
        else
          if kind = 1 then
            enemyX = x
            enemyY = y
          end if
          if kind = 2 and distance < recallHeroDistance then
            recallHeroDistance = distance
          end if
          if kind = 3 and distance < recallCreepDistance then
            recallCreepDistance = distance
          end if
          if kind = 2 or kind = 3 then
            if distance < threatDistance then
              threatDistance = distance
            end if
            if kind = 2 and distance <= 100 then
              enemyPower = enemyPower + objectLevel(idx) + 2
            end if
            dx = x - homeX
            dy = y - homeY
            if kind = 2 and dx * dx + dy * dy < 225 then
    homeEnemyHeroes = homeEnemyHeroes + 1
  end if
  if dx * dx + dy * dy < 144 then
              homeThreat = homeThreat + 1
            end if
          end if
          if kind = 4 and distance < towerDistance then
            towerDistance = distance
            towerX = x
            towerY = y
            towerTarget = objectTarget(idx)
          end if
          if kind = 4 and objectTarget(idx) = selfId then
            towerAggro = 1
          end if
          if distance <= 324 and objectAlive(idx) = 1 then
            score = 1000 - distance * 3
            if kind = 3 then
              score = score + 200
              if hp <= selfAttackDamage and distance <= hitReach * hitReach then
                score = score + 650
              end if
              if objectClass(idx) = 1 then
                score = score + 25
              end if
            end if
            if kind = 2 then
              score = score + 80
              if hp < selfAttackDamage * 4 then
                score = score + 300
              end if
            end if
            if kind = 1 then
              score = score + 500
            end if
            if id = selfTarget then
              score = score + 70
            end if
            if score > bestScore then
              bestScore = score
              bestId = id
              bestKind = kind
              bestHp = hp
              bestX = x
              bestY = y
              bestDistance = distance
            end if
          end if
        end if
      end if
    end if
    i = i + 1
  wend
  scanOffset = scanOffset + 96 - 48
  if scanOffset >= objects - 48 then
    scanOffset = 0
  end if
end if

' @rule R_economy
if active = 1 then
  gearCount = 0
  healSlot = -1
  healCount = 0
  portalSlot = -1
  portalCount = 0
  empty = 0
  has11 = 0
  has16 = 0
  has18 = 0
  has19 = 0
  s = 0
  while s < 6
    item = itemId(s)
    if item = 0 then
      empty = empty + 1
    end if
    if item = 11 then
      has11 = 1
      gearCount = gearCount + 1
    end if
    if item = 16 then
      has16 = 1
      gearCount = gearCount + 1
    end if
    if item = 18 then
      has18 = 1
      gearCount = gearCount + 1
    end if
    if item = 19 then
      has19 = 1
      gearCount = gearCount + 1
    end if
    if item = 2 then
      healSlot = s
      healCount = itemCount(s)
    end if
    if item = 21 then
      portalSlot = s
      portalCount = itemCount(s)
    end if
    s = s + 1
  wend
  if healSlot >= 0 and inOwnSpawn() = 0 then
    if itemCooldown(healSlot) = 0 and selfMaxHp - selfHp >= 70 then
      if useItem(healSlot) = 1 then
        healCount = healCount - 1
        if healCount = 0 then
          empty = empty + 1
        end if
      end if
    end if
  end if
  if canShop() = 1 then
    restock = 0
    budget = selfGold
    if has11 = 0 and budget >= 110 and empty > 0 then
      if buyItem(11) = 1 then
        budget = budget - 110
        empty = empty - 1
        gearCount = gearCount + 1
      end if
    end if
    if has16 = 0 and budget >= 160 and empty > 0 then
      if buyItem(16) = 1 then
        budget = budget - 160
        empty = empty - 1
        gearCount = gearCount + 1
      end if
    end if
    if portalCount = 0 and budget >= 100 and empty > 0 then
      if buyItem(21) = 1 then
        budget = budget - 100
        empty = empty - 1
      end if
    end if
    if has18 = 0 and budget >= 180 and empty > 0 then
      if buyItem(18) = 1 then
        budget = budget - 180
        empty = empty - 1
        gearCount = gearCount + 1
      end if
    end if
    if has19 = 0 and budget >= 180 and empty > 0 then
      if buyItem(19) = 1 then
        budget = budget - 180
        empty = empty - 1
        gearCount = gearCount + 1
      end if
    end if
    if gearCount >= 4 and budget >= 100 then
      reserveSlot = 0
      while reserveSlot < 6
        if itemId(reserveSlot) = 21 and itemCount(reserveSlot) = 1 then
          if buyItem(21) = 1 then
            budget = budget - 100
          end if
        end if
        reserveSlot = reserveSlot + 1
      wend
    end if
    healLimit = 2
    healReserve = 0
    if gearCount >= 4 then
      healLimit = 6
      healReserve = 200
    end if
    buys = 0
    while healCount < healLimit and budget >= 75 + healReserve and buys < 6
      if healCount > 0 or empty > 0 then
        if buyItem(2) = 1 then
          if healCount = 0 then
            empty = empty - 1
          end if
          healCount = healCount + 1
          budget = budget - 75
        else
          buys = 6
        end if
      else
        buys = 6
      end if
      buys = buys + 1
    wend
  else
    if gearCount < 4 and selfGold >= 500 and threatDistance > 225 then
      restock = 1
    end if
  end if
  if restock = 1 then
    retreat = 1
  end if
end if

' @rule R_portal_context
if active = 1 then
  inBase = canShop()
  portalSlot = -1
  portalCount = 0
  portalReady = 0
  s = 0
  while s < 6
    if itemId(s) = 21 and itemCount(s) > 0 then
      portalSlot = s
      portalCount = itemCount(s)
      if itemCooldown(s) = 0 and selfPortalCooldown = 0 and selfChannelTicks = 0 then
        if selfRootTicks = 0 and selfStunTicks = 0 then
          portalReady = 1
        end if
      end if
    end if
    s = s + 1
  wend
end if

' @rule R_replenish
if active = 1 and inBase = 1 then
  if inOwnSpawn() = 1 then
    if selfHp * 10 >= selfMaxHp * 9 and selfMana * 10 >= selfMaxMana * 8 then
      retreat = 0
    else
      retreat = 1
      stopped = 1
      if selfRootTicks = 0 and worldTick >= moveTick then
        walkTo(spawnX, spawnY)
        moveTick = worldTick + 24
      end if
    end if
  end if
end if

' @rule R_channel_town_scroll
if active = 1 and stopped = 0 and retreat = 1 and inBase = 0 and portalReady = 1 then
  dx = selfX - spawnX
  dy = selfY - spawnY
  if dx * dx + dy * dy > 64 and homeAnchorDistance <= 400 then
    if recallHeroDistance > 100 and recallCreepDistance > 36 and towerDistance > 100 then
      if towerAggro = 0 and worldTick - hurtTick >= tickRate then
        warningSafe = 1
        warnings = spellCount()
        if warnings > 24 then
          warningSafe = 0
        end if
        w = 0
        while w < warnings and w < 24
          dx = spellX(w) - selfX
          dy = spellY(w) - selfY
          if dx * dx + dy * dy <= 64 and spellImpactTick(w) <= worldTick + tickRate * 3 then
            warningSafe = 0
          end if
          w = w + 1
        wend
        if warningSafe = 1 then
          if useItemAt(portalSlot, spawnX, spawnY) = 1 then
            stopped = 1
  portalBusy = 1
            resumeTarget = 0
          end if
        end if
      end if
    end if
  end if
end if

' @rule R_walk_to_base
if active = 1 and stopped = 0 and retreat = 1 then
  if selfRootTicks = 0 and worldTick >= moveTick then
    walkTo(spawnX, spawnY)
    moveTick = worldTick + 24
  end if
  stopped = 1
end if

' @rule R_home_portal
if active = 1 then
  if stopped = 0 and retreat = 0 and inBase = 0 and portalReady = 1 and homeAnchorDistance <= 400 then
    if ordinal <= 1 and homeEnemyHeroes > 0 and homeDefenders < 2 then
      dx = selfX - homeX
      dy = selfY - homeY
      if dx * dx + dy * dy > 625 and selfHp * 100 >= selfMaxHp * 60 then
        if selfPortalCooldown = 0 and threatDistance > 225 and worldTick - hurtTick > tickRate * 2 then
          if useItemAt(portalSlot, homeX, homeY) = 1 then
            stopped = 1
  portalBusy = 1
          end if
        end if
      end if
    end if
  end if
end if

' @rule R_tower_safety
if active = 1 then
  if stopped = 0 then
    unsafe = 0
    if towerAggro = 1 and selfHp * 100 < selfMaxHp * 65 then
      unsafe = 1
    end if
    if bestKind = 4 and bestId <> 0 and tanks = 0 then
      if towerDistance < 64 and towerTarget = 0 then
        unsafe = 1
      end if
    end if
    if unsafe = 1 and selfRootTicks = 0 then
      dx = selfX - towerX
      dy = selfY - towerY
      if dx = 0 and dy = 0 then
        dx = homeX - selfX
        dy = homeY - selfY
      end if
      stepX = 3
      stepY = 3
      if dx < 0 then
        stepX = -3
      end if
      if dy < 0 then
        stepY = -3
      end if
      if worldTick >= moveTick then
        walkTo(selfX + stepX, selfY + stepY)
        moveTick = worldTick + 24
      end if
      stopped = 1
    end if
  end if
end if

' @rule R_xp_close
if active = 1 then
  if stopped = 0 and selfClass = Crossbowman and bestKind = 3 and bestId > 0 then
    if bestDistance > 25 and bestDistance <= 64 and enemyPower <= friendPower then
      if selfRootTicks = 0 then
        walkTo((selfX + bestX) / 2, (selfY + bestY) / 2)
        moveTick = worldTick + 6
      end if
      stopped = 1
    end if
  end if
end if

' @rule R_combat
if active = 1 then
  if stopped = 0 and bestId <> 0 then
    if justHit = 1 and 1 = 1 then
      if selfRootTicks = 0 then
        walkTo(selfX + 0.25, selfY + 0.25)
      end if
    end if
    if selfTarget <> bestId or justHit = 1 then
      attackTarget(bestId)
    end if
    slot = 0
    while slot < 4
      if abilityLevel(slot) > 0 and abilityCooldown(slot) = 0 then
        if abilityCharges(slot) > 0 and selfMana >= abilityManaCost(slot) then
          if abilityHeal(slot) > 0 then
            if selfMaxHp - selfHp >= abilityHeal(slot) \ 2 then
              castTarget(slot, selfId)
            end if
          else
            if abilityDamage(slot) > 0 then
              if bestKind <> 3 or bestHp <= abilityDamage(slot) then
                castTarget(slot, bestId)
              end if
            end if
          end if
        end if
      end if
      slot = slot + 1
    wend
    stopped = 1
  end if
end if

' @rule R_advance
if active = 1 then
  if stopped = 0 then
    goalX = mapWidth \ 2
    goalY = mapHeight \ 2
    if lane = 0 then
      goalX = mapWidth \ 10
      goalY = mapHeight \ 10
    end if
    if lane = 2 then
      goalX = mapWidth * 9 \ 10
      goalY = mapHeight * 9 \ 10
    end if
    dx = selfX - goalX
    dy = selfY - goalY
    if dx * dx + dy * dy <= 64 then
      crossed = 1
    end if
    if crossed = 1 then
      goalX = enemyX
      goalY = enemyY
    end if
    dx = selfX - homeX
    dy = selfY - homeY
    if homeThreat > 0 and dx * dx + dy * dy < 400 then
      goalX = homeX
      goalY = homeY
    end if
    if inBase = 1 and portalReady = 1 and portalCount >= 2 then
      if retreat = 0 and threatDistance > 144 and forwardScore < 1000000 then
        dx = selfX - forwardX
        dy = selfY - forwardY
        if dx * dx + dy * dy > 400 then
          if useItemAt(portalSlot, forwardX, forwardY) = 1 then
            stopped = 1
  portalBusy = 1
          end if
        end if
      end if
    end if
    if stopped = 0 and selfRootTicks = 0 and worldTick >= moveTick then
      attackMove(goalX, goalY)
      moveTick = worldTick + 24
    end if
  end if
end if
