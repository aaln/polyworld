"""Versioned red recall for observed smaller raids damaging a friendly tower."""
from dataclasses import replace


def damaged_pair(parent):
    token = '          defAnchorY = objectY(defI)'
    assert parent.template.count(token) == 1
    source = parent.template.replace(token, token + '\n          pairAnchorHp = objectHp(defI)', 1)
    gate = '  if defAnchor <> 0 and (defCount >= defGroupSize or (worldTick < defUntil and defFrontD <= defContinueHome * defContinueHome)) then'
    assert source.count(gate) == 1
    source = source.replace(gate, '''  pairedRush = 0
  pairMaxHp = 0
  if defAnchor = 10 or defAnchor = 16 or defAnchor = 22 then
    pairMaxHp = 950
  end if
  if defAnchor = 11 or defAnchor = 17 or defAnchor = 23 then
    pairMaxHp = 1300
  end if
  if defAnchor = 12 or defAnchor = 18 or defAnchor = 24 then
    pairMaxHp = 1950
  end if
  if worldTick <= param_raid_opening and defCount >= 2 then
    if pairMaxHp > 0 and pairAnchorHp <= pairMaxHp - param_raid_damage then
      pairedRush = 1
    end if
  end if
  if defAnchor <> 0 and (pairedRush or defCount >= defGroupSize or (worldTick < defUntil and defFrontD <= defContinueHome * defContinueHome)) then''', 1)
    return replace(parent, template=source,
        parameters=parent.parameters | {'raid_damage': (150, 1, 500), 'raid_opening': (7200, 1200, 14400)},
        meaning=parent.meaning + ' Additional red damaged-tower raid alarm: before '
        'raid_opening, at least two currently visible living clustered enemies '
        'near a standing friendly lane tower missing at least raid_damage HP '
        'initiate the original recall. All three red lanes are eligible. The '
        'published .5 tower IDs and tier max HP establish damage; a structure '
        'must remain observed and positive HP. Cumulative damage is not an '
        'estimate of current damage rate. Existing group alarm, survivor refresh, '
        'role commitments, target selection, equipment and navigation remain. '
        'Used only in the red team branch; no enemy policy identity is read.')
