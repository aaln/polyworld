"""Evidence-gated blue side-lane alarm for a partially visible siege."""
from dataclasses import replace


def paired_siege(parent):
    source=parent.template
    token='          defAnchorY = objectY(defI)'
    assert source.count(token)==1
    source=source.replace(token,token+'\n          pairAnchorHp = objectHp(defI)',1)
    gate='  if defAnchor <> 0 and (middleRush or defCount >= defGroupSize or (worldTick < defUntil and defFrontD <= defContinueHome * defContinueHome)) then'
    assert source.count(gate)==1
    source=source.replace(gate,'''  pairedRush = 0
  pairMaxHp = 0
  if defAnchor = 13 or defAnchor = 25 then
    pairMaxHp = 950
  end if
  if defAnchor = 14 or defAnchor = 26 then
    pairMaxHp = 1300
  end if
  if defAnchor = 15 or defAnchor = 27 then
    pairMaxHp = 1950
  end if
  if selfTeam = 1 and worldTick <= param_pair_opening and defCount >= 2 then
    if pairMaxHp > 0 and pairAnchorHp <= pairMaxHp - param_pair_damage then
      pairedRush = 1
    end if
  end if
  if defAnchor <> 0 and (pairedRush or middleRush or defCount >= defGroupSize or (worldTick < defUntil and defFrontD <= defContinueHome * defContinueHome)) then''',1)
    return replace(parent,template=source,
        parameters=parent.parameters|{'pair_damage':(50,1,400),'pair_opening':(3600,1200,7200)},
        meaning=parent.meaning+' Additional blue side-lane warning: before pair_opening, '
        'at least two visible living clustered enemy heroes near a standing friendly '
        'side-lane tower with at least pair_damage HP missing initiate ordinary recall. '
        'Side towers13/14/15/25/26/27 and950/1300/1950 maxHP are pinned release .5 '
        'mechanics. This uses current observed damage, not a damage-rate estimate; a '
        'previously damaged tower may trigger when a new pair approaches. Unseen '
        'enemies are not counted. Existing group/middle/solo/core behavior remains.')
