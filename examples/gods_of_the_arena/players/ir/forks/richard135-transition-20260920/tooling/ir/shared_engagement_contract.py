"""Shared visible threat, healthy support, and a bounded tower engagement zone."""
from dataclasses import replace


def shared_engagement(parent):
    # Insert before the existing active-defense test: only heroes already near
    # their own core are recalled by a small raid, with a four-second lease.
    token = 'if worldTick < defUntil then\n'
    assert parent.template.count(token) == 1
    source = parent.template.replace(token, '''seLocal = 0
seFriends = 0
seGo = 0
seTower = 0
seDx = selfX - defHomeX
seDy = selfY - defHomeY
if defFront <> 0 and defFrontD <= 576 and seDx * seDx + seDy * seDy <= 576 then
  if defUntil < worldTick + 96 then
    defUntil = worldTick + 96
  end if
end if
''' + token, 1)
    token = '  defenseDecisions = defenseDecisions + 1'
    assert source.count(token) == 1
    source = source.replace(token, '''  if defFront <> 0 then
    seDx = selfX - defFrontX
    seDy = selfY - defFrontY
    if seDx * seDx + seDy * seDy <= 400 then
      seLocal = 1
      seI = 0
      while seI < objectCount() and seI < 64
        seKind = objectKind(seI)
        if seKind = 3 then
          seI = 64
        else
          if seKind = 2 and objectTeam(seI) = selfTeam and objectAlive(seI) and objectHp(seI) >= param_ready_hp then
            seDx = objectX(seI) - defFrontX
            seDy = objectY(seI) - defFrontY
            if seDx * seDx + seDy * seDy <= 256 then
              seFriends = seFriends + 1
            end if
          end if
        end if
        seI = seI + 1
      wend
      seAnchorX = defHomeX
      seAnchorY = defHomeY
      if defAnchor <> 0 then
        seAnchorX = defAnchorX
        seAnchorY = defAnchorY
        seDx = defFrontX - defAnchorX
        seDy = defFrontY - defAnchorY
        if seDx * seDx + seDy * seDy <= 25 then
          seTower = 1
        end if
      end if
      seGo = seTower
      if seFriends >= param_ready_count and seFriends >= defCount then
        seGo = 1
      end if
      if defFrontTarget <> 0 and defFrontD <= 36 then
        seGo = 1
      end if
      bestId = 0
      if seGo and selfHp >= param_ready_hp then
        bestId = defFront
        bestDistance = 0
      end if
      seDx = defHomeX - seAnchorX
      seDy = defHomeY - seAnchorY
      seAx = seDx
      seAy = seDy
      if seAx < 0 then
        seAx = -seAx
      end if
      if seAy < 0 then
        seAy = -seAy
      end if
      seScale = seAx
      if seAy > seScale then
        seScale = seAy
      end if
      defPointX = defHomeX - 2
      defPointY = defHomeY - 2
      if seScale > 0 then
        defPointX = seAnchorX + seDx * 3 / seScale
        defPointY = seAnchorY + seDy * 3 / seScale
      end if
      if selfClass = 0 or selfClass = 4 then
        defPointX = defPointX - 1
      else
        defPointY = defPointY + (selfClass - 2) * 2
      end if
    end if
  end if
''' + token, 1)
    return replace(parent, template=source, parameters=parent.parameters | {
        'ready_hp': (150, 80, 250), 'ready_count': (3, 2, 6)},
        meaning=parent.meaning +
        ' Shared engagement override: a visible enemy within24tiles of the god recalls only '
        'allies already within24tiles of home for at least96ticks. Active defenders within20tiles '
        'of the same closest-to-home enemy count visible living allies with at least ready_hp '
        'HP within16tiles of that enemy. Attack that common hero when ready_count allies are '
        'available and at least equal the visible enemy cluster, or the enemy is within5tiles '
        'of its nearest standing friendly anchor, or is targeting something within6tiles of '
        'the god. Only heroes above ready_hp join. Otherwise rally behind the CURRENT observed '
        'friendly anchor (or home if none), with bounded role offsets. Do not renew the long '
        'sentry lease merely for choosing this shared rally. This is public-observation '
        'coordination, not synchronized arrival or knowledge of allies private policy intent. '
        'The nearest hero can mask other threats and low-HP defenders may yield: validate both '
        'limitations in full games. Original wave pressure, item purchase and blue branch remain.')
