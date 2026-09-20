"""Replay-grounded movement contracts; all decisions use public observations."""
from textwrap import dedent


def directions(prefix):
    return dedent(f"""
        {prefix}DirX = 0
        {prefix}DirY = 0
        if {prefix}direction = 0 or {prefix}direction = 1 or {prefix}direction = 7 then
          {prefix}DirX = 1
        end if
        if {prefix}direction = 3 or {prefix}direction = 4 or {prefix}direction = 5 then
          {prefix}DirX = -1
        end if
        if {prefix}direction = 1 or {prefix}direction = 2 or {prefix}direction = 3 then
          {prefix}DirY = 1
        end if
        if {prefix}direction = 5 or {prefix}direction = 6 or {prefix}direction = 7 then
          {prefix}DirY = -1
        end if
    """).strip()


def motion_contract(contract):
    source = dedent('''
        motionActive = 0
        kiteMoved = 0
        kiteTrigger = 0
        mNew = 0
        if motionLastTick = 0 or worldTick <> motionLastTick + 1 then
          motionUntil = 0
          motionReady = 0
          motionLastHits = selfAttacksLanded
          motionLastHp = selfHp
          motionLoss = 0
        end if
        motionLoss = motionLoss * 23 / 24
        if selfHp < motionLastHp then
          motionLoss = motionLoss + motionLastHp - selfHp
        end if
        mThreat = 0
        mSecond = 0
        mDistance = 2147483647
        mSecondDistance = 2147483647
        mTower = 0
        mTowerDistance = 2147483647
        mAlly = 0
        mAllyDistance = 2147483647
        mEnemies = 0
        mAllies = 0
        mAttackers = 0
        mTracked = 0
        mFacingX = 0
        mFacingY = 0
        mIndex = 0
        while mIndex < objectCount()
          mId = objectId(mIndex)
          mKind = objectKind(mIndex)
          mX = objectX(mIndex)
          mY = objectY(mIndex)
          mDx = mX - selfX
          mDy = mY - selfY
          mD = mDx * mDx + mDy * mDy
          if mId = selfId then
            mFacingX = objectFacingX(mIndex)
            mFacingY = objectFacingY(mIndex)
          end if
          if objectHp(mIndex) > 0 then
            if mKind = 4 and mD < mTowerDistance then
              mTower = mId
              mTowerX = mX
              mTowerY = mY
              mTowerDistance = mD
            end if
            if objectTeam(mIndex) = selfTeam and mId <> selfId then
              if mKind = 2 or mKind = 3 then
                if mD <= 36 then
                  mAllies = mAllies + 1
                  if mKind = 2 then
                    mAllies = mAllies + 2
                  end if
                end if
                if mKind = 2 and mD < mAllyDistance then
                  mAlly = mId
                  mAllyX = mX
                  mAllyY = mY
                  mAllyDistance = mD
                end if
              end if
            end if
            if objectTeam(mIndex) <> selfTeam and (mKind = 2 or mKind = 3 or mKind = 4) then
              if mD <= 36 then
                mEnemies = mEnemies + 1
                if mKind = 2 then
                  mEnemies = mEnemies + 2
                end if
                if objectTarget(mIndex) = selfId then
                  mAttackers = mAttackers + 1
                end if
              end if
              if mId = motionThreat then
                mTracked = 1
                mTrackedX = mX
                mTrackedY = mY
              end if
              if param_targeted = 0 or objectTarget(mIndex) = selfId then
                if mD < mDistance then
                  mSecond = mThreat
                  mSecondX = mThreatX
                  mSecondY = mThreatY
                  mSecondDistance = mDistance
                  mThreat = mId
                  mThreatX = mX
                  mThreatY = mY
                  mDistance = mD
                else
                  if mD < mSecondDistance then
                    mSecond = mId
                    mSecondX = mX
                    mSecondY = mY
                    mSecondDistance = mD
                  end if
                end if
              end if
            end if
          end if
          mIndex = mIndex + 1
        wend
        if worldTick < motionUntil and worldTick >= motionStart + param_min_ticks then
          mSepX = selfX - mTrackedX
          mSepY = selfY - mTrackedY
          if mSepX < 0 then
            mSepX = -mSepX
          end if
          if mSepY < 0 then
            mSepY = -mSepY
          end if
          if mTracked = 0 or mSepX + mSepY >= motionStartSeparation + param_gain_tiles then
            motionUntil = 0
            motionCompletions = motionCompletions + 1
            motionReady = worldTick + 8
          end if
        end if
        if worldTick >= motionUntil and worldTick >= motionReady and mThreat <> 0 then
          if param_risk_hp > 0 and mAttackers > 0 and mDistance <= 36 then
            if (selfHp * 100 < selfMaxHp * param_risk_hp and selfHp < motionLastHp) or selfHp < motionLoss * 3 then
              kiteTrigger = 2
            end if
          end if
          if kiteTrigger = 0 and param_normal = 1 and bestId <> 0 and mDistance <= param_threat_tiles * param_threat_tiles then
            if selfClass = 1 or selfClass = 2 or selfClass = 3 or selfClass = 6 or selfClass = 7 or selfClass = 8 then
              if selfAttacksLanded > motionLastHits and selfAttackCooldown > 0 then
                kiteTrigger = 1
              end if
            end if
          end if
          if kiteTrigger > 0 then
            motionStart = worldTick
            motionUntil = worldTick + param_max_ticks
            motionThreat = mThreat
            mSepX = selfX - mThreatX
            mSepY = selfY - mThreatY
            if mSepX < 0 then
              mSepX = -mSepX
            end if
            if mSepY < 0 then
              mSepY = -mSepY
            end if
            motionStartSeparation = mSepX + mSepY
            mNew = 1
            mBestScore = -2147483647
            mFound = 0
            mdirection = 0
            while mdirection < 8
                DIRECTIONS
              mLegal = 1
              mStep = 1
              while mStep <= param_step_tiles
                mTryX = selfX + mDirX * mStep
                mTryY = selfY + mDirY * mStep
                if terrainWalkable(mTryX, mTryY) = 0 then
                  mLegal = 0
                end if
                if mTower <> 0 then
                  mDx = mTryX - mTowerX
                  mDy = mTryY - mTowerY
                  mTD = mDx * mDx + mDy * mDy
                  if mTD < 4 and mTD <= mTowerDistance then
                    mLegal = 0
                  end if
                end if
                mStep = mStep + 1
              wend
              if mLegal then
                mDx = mTryX - mThreatX
                mDy = mTryY - mThreatY
                mMin = mDx * mDx + mDy * mDy
                mSum = mMin
                if mSecond <> 0 and mSecondDistance <= 64 then
                  mDx = mTryX - mSecondX
                  mDy = mTryY - mSecondY
                  mD = mDx * mDx + mDy * mDy
                  mSum = mSum + mD
                  if mD < mMin then
                    mMin = mD
                  end if
                end if
                mScore = mMin * 8 + mSum
                mScore = mScore + (mDirX * mFacingX + mDirY * mFacingY) / 15000
                if param_support = 1 and mAlly <> 0 and mAllyDistance <= 144 then
                  mDx = mTryX - mAllyX
                  mDy = mTryY - mAllyY
                  mScore = mScore - mDx * mDx - mDy * mDy
                end if
                if mScore > mBestScore then
                  mBestScore = mScore
                  motionX = mTryX
                  motionY = mTryY
                  mFound = 1
                end if
              end if
              mdirection = mdirection + 1
            wend
            if mFound = 0 then
              motionUntil = 0
              motionFailures = motionFailures + 1
            end if
          end if
        end if
        if worldTick < motionUntil then
          kiteMoved = walkTo(motionX, motionY)
          if kiteMoved then
            motionActive = 1
            kiteMoveTicks = kiteMoveTicks + 1
            if mNew then
              kiteBursts = kiteBursts + 1
              if kiteTrigger = 2 then
                kiteEscapes = kiteEscapes + 1
              end if
            end if
            if param_spells = 1 and bestId <> 0 then
              mSpell = 3
              mCast = 0
              while mSpell >= 1 and mCast = 0
                if selfClass <> 3 or mSpell = 3 then
                  if abilityCharges(mSpell) > 0 and abilityCooldown(mSpell) = 0 then
                    mCast = castTarget(mSpell, bestId)
                  end if
                end if
                mSpell = mSpell - 1
              wend
              if mCast then
                kiteSpellCasts = kiteSpellCasts + 1
              end if
            end if
          else
            motionUntil = 0
            motionFailures = motionFailures + 1
          end if
        end if
        if motionActive = 0 and bestId <> 0 then
          attackTarget(bestId)
        end if
        motionLastTick = worldTick
        motionLastHits = selfAttacksLanded
        motionLastHp = selfHp
    ''').replace('DIRECTIONS', directions('m'))
    return contract(source, {
        'normal':(1,0,1),'targeted':(1,0,1),'risk_hp':(0,0,80),
        'min_ticks':(12,9,32),'max_ticks':(64,32,120),'gain_tiles':(2,1,4),
        'step_tiles':(3,2,5),'threat_tiles':(5,3,7),'support':(1,0,1),'spells':(1,0,1),
    }, ['candidate'], ['motion'], ['walkTo','attackTarget','castTarget'],
        'A public-observation retreat controller. Normal ranged retreats require a newly observed basic hit. '
        'Optional earlier danger escape uses recent HP losses and observed attackers. Select a stable, terrain-checked '
        'destination that separates from the two closest eligible threats and avoids the closest tower footprint; '
        'optionally favor nearby allied heroes. Spend at least min_ticks turning/moving, then resume only after '
        'the tracked threat disappears or observed Manhattan separation increases by gain_tiles; max_ticks bounds '
        'the retreat. The endpoint stays fixed during the retreat. Keep one offensive spell opportunity after '
        'accepted movement. Stop fallback from overriding active retreat, even without an attackable candidate. '
        'Rounded map tiles and selected threats are imperfect danger/progress estimates, not a safety guarantee.',
        ['motionLastTick','motionLastHits','motionLastHp','motionLoss','motionStart','motionUntil','motionReady',
         'motionThreat','motionStartSeparation','motionX','motionY','motionCompletions','motionFailures',
         'kiteBursts','kiteEscapes','kiteMoveTicks','kiteSpellCasts'])


def tower_contract(contract):
    source = dedent('''
        tTower = 0
        tDistance = 2147483647
        tTargetDistance = 2147483647
        tGoalX = moveX
        tGoalY = moveY
        tIndex = 0
        while tIndex < objectCount()
          tX = objectX(tIndex)
          tY = objectY(tIndex)
          tDx = tX - selfX
          tDy = tY - selfY
          tD = tDx * tDx + tDy * tDy
          if objectKind(tIndex) = 4 and objectHp(tIndex) > 0 and tD < tDistance then
            tTower = objectId(tIndex)
            tTowerX = tX
            tTowerY = tY
            tDistance = tD
          end if
          if objectId(tIndex) = bestId then
            tTargetDistance = tD
            tGoalX = tX
            tGoalY = tY
          end if
          tIndex = tIndex + 1
        wend
        tRange = selfAttackRange / 60000
        if tRange < 2 then
          tRange = 2
        end if
        if tTower <> 0 and tDistance <= param_guard_tiles * param_guard_tiles and tTargetDistance > tRange * tRange then
          tDx = tGoalX - selfX
          tDy = tGoalY - selfY
          tToX = tTowerX - selfX
          tToY = tTowerY - selfY
          tDot = tDx * tToX + tDy * tToY
          tCross = tDx * tToY - tDy * tToX
          tLength = tDx * tDx + tDy * tDy
          if tDot > 0 and tCross * tCross <= param_clearance * param_clearance * tLength then
            tBestScore = -2147483647
            tFound = 0
            tdirection = 0
            while tdirection < 8
                DIRECTIONS
              tLegal = 1
              tStep = 1
              while tStep <= 3
                tTryX = selfX + tDirX * tStep
                tTryY = selfY + tDirY * tStep
                if terrainWalkable(tTryX,tTryY) = 0 then
                  tLegal = 0
                end if
                tDx = tTryX - tTowerX
                tDy = tTryY - tTowerY
                tTD = tDx * tDx + tDy * tDy
                if tTD < param_clearance * param_clearance and tTD <= tDistance then
                  tLegal = 0
                end if
                tStep = tStep + 1
              wend
              if tLegal then
                tDx = tTryX - tGoalX
                tDy = tTryY - tGoalY
                tScore = 0 - tDx * tDx - tDy * tDy
                if tScore > tBestScore then
                  tBestScore = tScore
                  towerRouteX = tTryX
                  towerRouteY = tTryY
                  tFound = 1
                end if
              end if
              tdirection = tdirection + 1
            wend
            if tFound then
              towerMoved = walkTo(towerRouteX,towerRouteY)
              if towerMoved then
                towerDetours = towerDetours + 1
              end if
            end if
          end if
        end if
    ''').replace('DIRECTIONS', directions('t'))
    return contract(source, {'guard_tiles':(4,3,6),'clearance':(2,1,3)}, ['candidate'], [], ['walkTo'],
        'After ordinary movement/attack selection, divert a distant pursuit or wave route before it enters the '
        'nearest standing tower clearance, including friendly and protected towers. Use checked intermediate '
        'terrain tiles and preserve progress toward the original goal. Do not override attacks already within '
        'the rounded attack range. This is preventive routing; it cannot repair an existing engine path trap.',
        ['towerDetours'])


def ranged_weapon_contract(contract, equipment_source):
    return contract('''
        if (selfClass = 1 or selfClass = 6) and hasGear = 0 and selfGold >= 110 then
          weaponBought = buyItem(11)
          if weaponBought then
            hasGear = 1
            weaponStarts = weaponStarts + 1
          end if
        end if
    ''' + equipment_source().replace('if hasGear = 0 then', 'if hasGear = 0 then'),
    {}, ['inventory'], [], ['buyItem'],
    'Ranger and Crossbowman start with Crimson Dagger when affordable, trading initial boot speed for +8 basic '
    'damage to improve last hits and growth. Then retain existing class equipment purchases. Other classes '
    'and consumables are unchanged. Host return values establish accepted purchases.', ['weaponStarts'])
