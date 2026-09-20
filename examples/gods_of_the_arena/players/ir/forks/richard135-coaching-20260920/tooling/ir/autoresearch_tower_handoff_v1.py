"""Red tower-target release as a final movement arbitration channel.

Motion m* scratch is reused only after all original skills have run. None of
their persistent motion* state is modified. Versioned, positive-witness search.
"""
from binding import CONTRACTS, contract

SOURCE = '''towerReleaseActive = 0
if selfTeam = 0 then
  if worldTick <> towerReleaseLastTick + 1 then
    towerReleaseUntil = 0
    towerReleaseReady = 0
  end if
  towerReleaseLastTick = worldTick
  if towerReleaseUntil > 0 and worldTick >= towerReleaseUntil then
    towerReleaseUntil = 0
    towerReleaseReady = worldTick + param_retry_ticks
  end if
  if worldTick < towerReleaseUntil or (worldTick >= towerReleaseReady and bestId <> 0 and selfHp * 100 <= selfMaxHp * param_hp_percent) then
    mThreat = bestId
    if worldTick < towerReleaseUntil then
      mThreat = towerReleaseId
    end if
    mFound = 0
    mIndex = 0
    while mIndex < objectCount() and mIndex < param_scan_limit and mFound = 0
      if objectId(mIndex) = mThreat then
        if objectKind(mIndex) = 4 and objectTeam(mIndex) <> selfTeam and objectHp(mIndex) > 0 and objectTarget(mIndex) = selfId then
          if worldTick < towerReleaseUntil or (objectHp(mIndex) > param_finish_hp and objectHp(mIndex) > selfAttackDamage * 2) then
            mFound = 1
            mThreatX = objectX(mIndex)
            mThreatY = objectY(mIndex)
          end if
        end if
        mIndex = param_scan_limit
      end if
      mIndex = mIndex + 1
    wend
    if mFound = 0 then
      if worldTick < towerReleaseUntil then
        towerReleaseReady = worldTick + param_retry_ticks
      end if
      towerReleaseUntil = 0
    else
      if worldTick >= towerReleaseUntil then
        if param_require_creep then
          mFound = 0
          mIndex = 0
          while mIndex < objectCount() and mIndex < param_scan_limit and mFound = 0
            if objectKind(mIndex) = 3 and objectTeam(mIndex) = selfTeam and objectAlive(mIndex) and objectHp(mIndex) > 0 then
              mDx = objectX(mIndex) - mThreatX
              mDy = objectY(mIndex) - mThreatY
              if mDx * mDx + mDy * mDy <= param_creep_tiles * param_creep_tiles then
                mFound = 1
              end if
            end if
            mIndex = mIndex + 1
          wend
        end if
        if mFound then
          mFound = 0
          mBestScore = 2147483647
          mdirection = 0
          while mdirection < 8
            mDirX = 0
            mDirY = 0
            if mdirection = 0 or mdirection = 1 or mdirection = 7 then
              mDirX = 1
            end if
            if mdirection = 3 or mdirection = 4 or mdirection = 5 then
              mDirX = -1
            end if
            if mdirection = 1 or mdirection = 2 or mdirection = 3 then
              mDirY = 1
            end if
            if mdirection = 5 or mdirection = 6 or mdirection = 7 then
              mDirY = -1
            end if
            mTryX = mThreatX + mDirX * param_release_tiles
            mTryY = mThreatY + mDirY * param_release_tiles
            if terrainWalkable(mTryX, mTryY) then
              mDx = mTryX - selfX
              mDy = mTryY - selfY
              mD = mDx * mDx + mDy * mDy
              if mD < mBestScore then
                mBestScore = mD
                towerReleaseX = mTryX
                towerReleaseY = mTryY
                mFound = 1
              end if
            end if
            mdirection = mdirection + 1
          wend
          if mFound then
            towerReleaseId = mThreat
            towerReleaseUntil = worldTick + param_hold_ticks
            towerReleaseStarts = towerReleaseStarts + 1
          else
            towerReleaseReady = worldTick + param_retry_ticks
          end if
        end if
      end if
      if worldTick < towerReleaseUntil then
        if walkTo(towerReleaseX, towerReleaseY) then
          towerReleaseActive = 1
          towerReleaseMoves = towerReleaseMoves + 1
        else
          towerReleaseUntil = 0
          towerReleaseReady = worldTick + param_retry_ticks
        end if
      end if
    end if
  end if
end if'''

value=contract(SOURCE,{'hp_percent':(50,20,70),'finish_hp':(150,0,400),
    'require_creep':(1,0,1),'creep_tiles':(4,2,6),'release_tiles':(8,7,10),
    'hold_ticks':(144,48,240),'retry_ticks':(48,24,120),'scan_limit':(64,32,64)},
    ['bestId'],['towerReleaseActive'],['walkTo'],
    'Final red-only movement override after the ordinary strategy. Initiate only '
    'when the selected observed enemy tower is standing, publicly targets self, '
    'self HP is at most hp_percent, and tower HP exceeds finish_hp and twice '
    'selfAttackDamage. Optional positive support witness: a living public allied '
    'creep within creep_tiles integer-coordinate tiles of that tower among the '
    'first scan_limit public objects. A missed witness never establishes absence. '
    'Choose the closest terrain-walkable one of eight compass destinations at '
    'release_tiles from the tower center. Retain that destination for at most '
    'hold_ticks; end immediately if the tower disappears, dies, or changes target, '
    'on a skipped living decision, failed walk, or deadline. Wait retry_ticks '
    'after completion/expiry/failure before another release. This last walk '
    'supersedes earlier target or movement orders; earlier purchases are retained. '
    'Frozen self HP is the predecision value even after same-tick healing. '
    'Accepted movement is not proof of arrival or safety. Reuse only m* scratch '
    'after its original users; preserve all persistent motion* and defense state. '
    'No blue commands, private states, opponent labels or seed checks.',
    ['towerReleaseId','towerReleaseX','towerReleaseY','towerReleaseUntil',
     'towerReleaseReady','towerReleaseLastTick','towerReleaseStarts','towerReleaseMoves'])
name='red_tower_handoff_v1'
if name in CONTRACTS and CONTRACTS[name]!=value:raise ValueError('Conflicting tower handoff V1')
CONTRACTS[name]=value
