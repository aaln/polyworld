"""Keep the front defender from initiating without nearby healthy support."""
from dataclasses import replace
from hero_binding import CLASS_ID


def supported_defense(parent):
    token = '  defenseDecisions = defenseDecisions + 1'
    assert parent.template.count(token) == 1
    source = parent.template.replace(token, f'''  dhHeld = 0
  if selfClass = {CLASS_ID['DeathKnight']} and defFront <> 0 and bestId = defFront then
    dhDx = defFrontX - selfX
    dhDy = defFrontY - selfY
    dhImmediate = 0
    if dhDx * dhDx + dhDy * dhDy <= 16 or defFrontD <= 36 then
      dhImmediate = 1
    end if
    if defAnchor <> 0 then
      dhDx = defFrontX - defAnchorX
      dhDy = defFrontY - defAnchorY
      if dhDx * dhDx + dhDy * dhDy <= 25 then
        dhImmediate = 1
      end if
    end if
    if dhImmediate = 0 then
      dhReady = 0
      dhI = 0
      while dhI < objectCount() and dhI < 64 and dhReady = 0
        dhKind = objectKind(dhI)
        if dhKind = 3 then
          dhI = 64
        else
          if dhKind = 2 and objectTeam(dhI) = selfTeam and objectAlive(dhI) and objectHp(dhI) >= 120 and objectId(dhI) <> selfId then
            dhDx = objectX(dhI) - selfX
            dhDy = objectY(dhI) - selfY
            if dhDx * dhDx + dhDy * dhDy <= 144 then
              dhReady = 1
            end if
          end if
        end if
        dhI = dhI + 1
      wend
      if dhReady = 0 then
        bestId = 0
        dhHeld = 1
      end if
    end if
  end if
''' + token, 1)
    return replace(parent, template=source, meaning=parent.meaning +
        ' Additional coordinated wait supersedes unchanged DeathKnight targeting: '
        'during existing red defense only, global class5 DeathKnight may initiate '
        'against the shared leading hero beyond4tiles only when another living '
        'ally with at least120HP is within12tiles. With no such ally, remove that '
        'hero target and use the existing defensive rally. Allow immediate defense '
        'when the leading enemy is within6tiles of home or5tiles of the standing '
        'friendly anchor. Never extend recall, replace rally geometry, or alter '
        'other noncaster targeting or blue behavior. Nearby health is only a proxy '
        'for support; casters separately follow public attack intent. Test combined '
        'effects and full-game activation; this is not a synchronized team command.')


def reachable_support(parent):
    token = '''            if dhDx * dhDx + dhDy * dhDy <= 144 then
              dhReady = 1
            end if'''
    assert parent.template.count(token) == 1
    source = parent.template.replace(token, '''            if dhDx * dhDx + dhDy * dhDy <= 144 then
              dhDx = objectX(dhI) - defFrontX
              dhDy = objectY(dhI) - defFrontY
              if dhDx * dhDx + dhDy * dhDy <= param_ready_tiles * param_ready_tiles or objectTarget(dhI) = defFront then
                dhReady = 1
              end if
            end if''', 1)
    return replace(parent, template=source, parameters=parent.parameters | {
        'ready_tiles': (10, 8, 14)}, meaning=parent.meaning +
        ' Readiness refinement: a nearby healthy ally counts as support only if '
        'also within ready_tiles of the leading enemy, or publicly already '
        'targeting that enemy. Mere proximity to DeathKnight does not establish '
        'timely participation. Tower/core/proximity emergency exceptions remain. '
        'This is a conservative distance estimate, not an exact arrival-time model.')
