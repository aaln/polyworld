"""Constant-work, observed post-hit recovery for crowded combat."""
from dataclasses import replace

def dense_cadence(parent):
    old='''if objectCount() > defMotionLimit then
  motionActive = 0
  if bestId <> 0 then
    attackTarget(bestId)
  end if
else'''
    assert parent.template.count(old)==1
    new='''if objectCount() > defMotionLimit then
  motionActive = 0
  if bestId <> 0 and selfClass <> param_plain_class then
    if param_dense_all_classes = 1 or selfClass = 1 or selfClass = 2 or selfClass = 3 or selfClass = 6 or selfClass = 7 or selfClass = 8 then
      if worldTick = denseLastTick + 1 and denseLastTick > 0 and selfAttacksLanded > denseLastHits and selfAttackCooldown > 0 then
        mTryX = selfX
        mTryY = selfY
        if defHomeX > selfX then
          mTryX = selfX + 1
        end if
        if defHomeX < selfX then
          mTryX = selfX - 1
        end if
        if defHomeY > selfY then
          mTryY = selfY + 1
        end if
        if defHomeY < selfY then
          mTryY = selfY - 1
        end if
        if mTryX <> selfX or mTryY <> selfY then
          if terrainWalkable(mTryX, mTryY) then
            motionActive = walkTo(mTryX, mTryY)
            if motionActive then
              denseSteps = denseSteps + 1
            end if
          end if
        end if
      end if
    end if
  end if
  if motionActive = 0 and bestId <> 0 then
    attackTarget(bestId)
  end if
else'''
    source=parent.template.replace(old,new,1)+'''\ndenseLastTick = worldTick
denseLastHits = selfAttacksLanded'''
    return replace(parent,template=source,parameters=parent.parameters|{'dense_all_classes':(1,0,1)},
        memory=parent.memory+('denseLastTick','denseLastHits','denseSteps'),
        writes=tuple(dict.fromkeys(parent.writes+('mTryX','mTryY'))),
        meaning=parent.meaning+' In the dense fallback only, after a newly observed basic hit '
        'on consecutive living decisions with positive attack cooldown and a nonzero selected '
        'target, move one coordinate tile toward the currently observed home fort on each '
        'nonzero axis if that destination is walkable. Exclude plain_class; optionally restrict '
        'to source-enumerated ranged classes1,2,3,6,7,8. The accepted movement owns this decision '
        'and prevents fallback navigation. On the next tick without a new hit, or on blocked/'
        'failed movement, attack the original selected target. No extra object scan, private '
        'information, remembered unseen target or new automatic spell policy. Track hit/tick '
        'on sparse decisions too; respawn/nonconsecutive ticks cannot trigger stale recovery. '
        'This is a bounded gameplay experiment; movement may turn only or lose attack range.')
