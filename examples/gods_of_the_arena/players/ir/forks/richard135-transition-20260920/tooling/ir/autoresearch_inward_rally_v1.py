"""Versioned observed inward interception for distant defense responders."""
from dataclasses import replace
import re


def inward_rally(parent):
    body = '''relayId = 0
if param_relay_sentry_only = 0 or defSentry then
  defDx = selfX - defAnchorX
  defDy = selfY - defAnchorY
  if defDx < 0 then
    defDx = -defDx
  end if
  if defDy < 0 then
    defDy = -defDy
  end if
  relaySelfD = defDx + defDy
  if relaySelfD >= 48 then
    defDx = defHomeX - defAnchorX
    defDy = defHomeY - defAnchorY
    if defDx < 0 then
      defDx = -defDx
    end if
    if defDy < 0 then
      defDy = -defDy
    end if
    relayHomeD = defDx + defDy
    relayNearD = 2147483647
    relayIndex = 0
    while relayIndex < objectCount() and relayIndex < 64
      defKind = objectKind(relayIndex)
      if defKind = 3 then
        relayIndex = 64
      else
        if (defKind = 4 or defKind = 1) and objectTeam(relayIndex) = selfTeam and objectHp(relayIndex) > 0 then
          defDx = objectX(relayIndex) - defHomeX
          defDy = objectY(relayIndex) - defHomeY
          if defDx < 0 then
            defDx = -defDx
          end if
          if defDy < 0 then
            defDy = -defDy
          end if
          if defDx + defDy + 8 <= relayHomeD then
            defDx = objectX(relayIndex) - defAnchorX
            defDy = objectY(relayIndex) - defAnchorY
            defD = defDx * defDx + defDy * defDy
            if defD < relayNearD then
              relayNearD = defD
              relayId = objectId(relayIndex)
              relayX = objectX(relayIndex)
              relayY = objectY(relayIndex)
            end if
          end if
        end if
      end if
      relayIndex = relayIndex + 1
    wend
    if relayId <> 0 then
      defDx = selfX - relayX
      defDy = selfY - relayY
      if defDx < 0 then
        defDx = -defDx
      end if
      if defDy < 0 then
        defDy = -defDy
      end if
      if defDx + defDy + 16 <= relaySelfD then
        defDx = defHomeX - relayX
        defDy = defHomeY - relayY
        defAx = defDx
        defAy = defDy
        if defAx < 0 then
          defAx = -defAx
        end if
        if defAy < 0 then
          defAy = -defAy
        end if
        defScale = defAx
        if defAy > defScale then
          defScale = defAy
        end if
        if defScale > 0 then
          defPointX = relayX + defDx * 4 / defScale
          defPointY = relayY + defDy * 4 / defScale
          relayActive = 1
        end if
      end if
    end if
  end if
end if'''
    token = r'(?m)^( *)defenseRefreshes = defenseRefreshes \+ 1$'
    assert len(re.findall(token, parent.template)) == 2
    source = re.sub(token, lambda m: '\n'.join(m[1] + line for line in body.splitlines()) + '\n' + m[0], parent.template)
    return replace(parent, template='relayActive = 0\n' + source,
        parameters=parent.parameters | {'relay_sentry_only': (1, 0, 1)},
        writes=parent.writes + ('relayActive',),
        meaning=parent.meaning + ' On an actual inherited alarm refresh, a responder '
        'at least48 Manhattan tiles from the threatened anchor considers the nearest '
        'observed friendly positive-HP structure whose home Manhattan distance is '
        'at least8 smaller. Protected standing structures are eligible. It changes '
        'only the rally point to four tiles behind that structure if it saves at '
        'least16 self Manhattan tiles. Parameter relay_sentry_only restricts this '
        'to existing sentry roles. Threat and perimeter anchors, selected targets, '
        'alarm duration and release are retained. Zero relayActive on every '
        'decision; relay scratch is never used across decisions. Public integer '
        'geometry does not establish path distance, safe arrival or victory.')
