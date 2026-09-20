"""Versioned geometric allocation of a newly observed damaged-tower pair alarm."""
from dataclasses import replace


def ranked_raid(parent):
    gate='  if defAnchor <> 0 and (pairedRush or defCount >= defGroupSize or (worldTick < defUntil and defFrontD <= defContinueHome * defContinueHome)) then'
    assert parent.template.count(gate)==1
    allocation='''  raidNearer = 0
  if pairedRush then
    raidDx = selfX - defAnchorX
    raidDy = selfY - defAnchorY
    raidSelfD = raidDx * raidDx + raidDy * raidDy
    raidI = 0
    while raidI < objectCount() and raidI < 64
      if objectKind(raidI) = 3 then
        raidI = 64
      else
        if objectKind(raidI) = 2 and objectTeam(raidI) = selfTeam and objectHp(raidI) > 0 and objectAlive(raidI) then
          raidAlly = objectId(raidI)
          if raidAlly <> selfId then
            raidDx = objectX(raidI) - defAnchorX
            raidDy = objectY(raidI) - defAnchorY
            raidD = raidDx * raidDx + raidDy * raidDy
            if raidD < raidSelfD or (raidD = raidSelfD and raidAlly < selfId) then
              raidNearer = raidNearer + 1
            end if
          end if
        end if
      end if
      raidI = raidI + 1
    wend
    if raidNearer >= param_raid_responders then
      pairedRush = 0
    end if
  end if
  if pairedRush and worldTick >= defUntil then
    raidScoped = 1
  end if
  if defCount >= defGroupSize then
    raidScoped = 0
  end if
  if raidScoped and param_raid_hold > 0 then
    defHoldTicks = param_raid_hold
  end if
'''
    source=parent.template.replace(gate,allocation+gate,1)
    source=source.replace('defActive = 0','if worldTick >= defUntil then\n  raidScoped = 0\nend if\ndefActive = 0',1)
    source=source.replace('  defUntil = 0\nend if','  defUntil = 0\n  raidScoped = 0\nend if',1)
    return replace(parent,template=source,
        parameters=parent.parameters|{'raid_responders':(2,1,5),'raid_hold':(0,0,3600)},
        memory=parent.memory+('raidNearer','raidDx','raidDy','raidSelfD','raidI','raidAlly','raidD','raidScoped'),
        meaning=parent.meaning+' Superseding universal small-pair recruitment: only '
        'raid_responders living allies nearest the observed threatened tower, by '
        'squared coordinate distance and public hero-ID ties, may newly trigger '
        'the damaged-pair alarm. No path-distance or arrival claim. Original '
        'larger-group triggers and remembered survivor refresh remain available '
        'to everyone. When raid_hold is positive, a commitment begun solely by '
        'the small alarm and its survivor refresh uses that duration until '
        'expiration/reset or a larger-group trigger restores ordinary hold. '
        'Zero keeps the original hold. Re-ranking after movement/death can '
        'accumulate more remembered defenders than the recruitment rank limit.')
