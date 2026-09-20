"""Earlier response to public early middle-lane pressure on the pinned map."""
from dataclasses import replace


def early_middle(parent):
    token = '  if defAnchor <> 0 and (defCount >= defGroupSize or (worldTick < defUntil and defFrontD <= defContinueHome * defContinueHome)) then'
    assert parent.template.count(token) == 1
    gate = '''  middleRush = 0
  if selfTeam = 1 and worldTick <= param_middle_opening_ticks and defCount >= param_middle_group then
    if defAnchor = 19 or defAnchor = 20 or defAnchor = 21 then
      middleRush = 1
    end if
  end if
  if defAnchor <> 0 and (middleRush or defCount >= defGroupSize or (worldTick < defUntil and defFrontD <= defContinueHome * defContinueHome)) then'''
    return replace(parent, template=parent.template.replace(token, gate, 1),
        parameters=parent.parameters | {'middle_group': (3, 3, 4),
                                       'middle_opening_ticks': (1800, 1200, 2400)},
        meaning=parent.meaning + ' On published .5 blue, during middle_opening_ticks, '
        'a currently visible living enemy cluster of middle_group near a standing '
        'friendly middle-lane tower also initiates existing recall. The existing '
        'structure scan establishes a standing anchor; IDs19/20/21 come from the '
        'pinned map, not an opponent identity. Other lanes and later times retain '
        'the original group threshold. Missing heroes remain unknown. Retain '
        'existing class commitments, target selection, spacing and quiet release. '
        'This represents suspected early lane concentration, not proof of a named '
        'opponent or a guaranteed five-hero push.')
