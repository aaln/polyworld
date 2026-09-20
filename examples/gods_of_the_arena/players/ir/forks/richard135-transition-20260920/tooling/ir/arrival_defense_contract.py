"""Count quiet-defense release only after the recalled hero reaches its objective."""
from dataclasses import replace


def arrival_observer(parent):
    marker = 'if perimeterEnabled and defActive and bestId = 0 and param_release_mode > 0 then'
    assert parent.template.count(marker) == 1
    source = parent.template.replace(marker, '''if perimeterEnabled and defActive then
  arrivalDx = selfX - perimeterX
  arrivalDy = selfY - perimeterY
  arrivalDistanceSq = arrivalDx * arrivalDx + arrivalDy * arrivalDy
  if arrivalDistanceSq > param_arrival_tiles * param_arrival_tiles then
    perimeterLastCombat = worldTick
  end if
end if
''' + marker, 1)
    return replace(parent, template=source,
                   parameters=parent.parameters | {'arrival_tiles': (18, 8, 30)},
                   meaning=parent.meaning + ' Arrival-qualified quiet release: while an active defender '
                   'is farther than arrival_tiles from its remembered protected objective, reset the '
                   'quiet timer. Travel without a nearby combat target must not cancel recall. Once '
                   'inside that radius, the existing quiet timer may release eligible roles after '
                   'idle_ticks. Ordinary duty expiration, renewed threats and combat remain unchanged. '
                   'This adds no object scan and preserves the red branch exactly.')
