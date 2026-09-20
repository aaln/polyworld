"""Scope added blue recall persistence to the new side-siege alarm."""
from dataclasses import replace


def scoped_pair(parent):
    source=parent.template
    token='  if defAnchor <> 0 and (pairedRush or middleRush or defCount >= defGroupSize or (worldTick < defUntil and defFrontD <= defContinueHome * defContinueHome)) then'
    assert source.count(token)==1
    source=source.replace(token,'''  if pairedRush then
    if defSentry = 0 then
      defHoldTicks = param_pair_hold
    end if
    pairArrivalUntil = worldTick + defHoldTicks
  end if
'''+token,1)
    token='if perimeterEnabled and defActive then\n  arrivalDx = selfX - perimeterX'
    assert source.count(token)==1
    source=source.replace(token,'if perimeterEnabled and defActive and worldTick < pairArrivalUntil then\n  arrivalDx = selfX - perimeterX',1)
    # Use the same per-hero reset semantics as ordinary defense memory.
    token='if worldTick <= defLastTick or (worldTick <> defLastTick + 1 and defSentry = 0) then'
    assert source.count(token)==1
    source=source.replace(token,token+'\n  pairArrivalUntil = 0',1)
    return replace(parent,template=source,parameters=parent.parameters|{'pair_hold':(1440,120,1440)},
       memory=parent.memory+('pairArrivalUntil',),
       meaning=parent.meaning+' Scope the extra arrival protection and pair_hold carry commitment '
       'to an actually fired paired side-siege alarm. During that alarm sentry hold stays unchanged, '
       'non-sentry hold uses pair_hold and arrival protection expires with its remembered deadline. '
       'Other alarms keep their baseline hold and quiet-release behavior unless still within an '
       'existing side-alarm deadline. Reset the deadline on the same gaps/resets as ordinary defense.')
