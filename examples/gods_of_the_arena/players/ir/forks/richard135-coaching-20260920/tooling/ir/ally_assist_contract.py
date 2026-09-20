"""React to visible allied attack intent without changing macro commitments."""
from dataclasses import replace


def ally_assist(parent):
    token = '  defenseDecisions = defenseDecisions + 1'
    assert parent.template.count(token) == 1
    source = parent.template.replace(token, '''  aaReady = 0
  aaCommitted = 0
  aaDx = defFrontX - selfX
  aaDy = defFrontY - selfY
  aaDistance = aaDx * aaDx + aaDy * aaDy
  if defFront <> 0 and aaDistance <= param_assist_tiles * param_assist_tiles then
    aaI = 0
    while aaI < objectCount() and aaI < 64
      aaKind = objectKind(aaI)
      if aaKind = 3 then
        aaI = 64
      else
        if aaKind = 2 and objectTeam(aaI) = selfTeam and objectHp(aaI) >= 120 and objectAlive(aaI) and objectId(aaI) <> selfId then
          aaDx = objectX(aaI) - selfX
          aaDy = objectY(aaI) - selfY
          if aaDx * aaDx + aaDy * aaDy <= 144 then
            aaReady = aaReady + 1
            if objectTarget(aaI) = defFront then
              aaCommitted = 1
            end if
          end if
        end if
      end if
      aaI = aaI + 1
    wend
    if aaCommitted and selfHp * 100 >= selfMaxHp * 25 then
      bestId = defFront
      bestDistance = aaDistance
    end if
    if param_wait_support and selfClass = 0 and bestId = defFront and aaReady = 0 and aaDistance > 16 then
      bestId = 0
    end if
  end if
''' + token, 1)
    return replace(parent, template=source, parameters=parent.parameters | {
        'assist_tiles': (18, 12, 22), 'wait_support': (0, 0, 1)},
        meaning=parent.meaning +
        ' During an existing defense only, inspect living allied heroes before creeps. '
        'A different allied hero within12tiles of self, with at least120HP, who is publicly '
        'targeting the current closest-to-home visible living enemy, supplies concrete attack '
        'intent. If that enemy is within assist_tiles of self and self has at least25percent '
        'HP, join the same target immediately despite the original10tile self-radius. '
        'Optional wait_support prevents DeathKnight initiating against that leading hero '
        'beyond4tiles without any healthy nearby ally. Immediate threats retain the parent '
        'response. No new recall, lease extension, or rally replacement; blue unchanged. '
        'Support intent does not guarantee ally arrival or survival; measure full games.')


def caster_assist(parent):
    source = parent.template.replace('  aaReady = 0', '  if selfClass = 2 or selfClass = 3 then\n  aaReady = 0', 1)
    source = source.replace('  defenseDecisions = defenseDecisions + 1', '  end if\n  defenseDecisions = defenseDecisions + 1', 1)
    source = source.replace('if aaCommitted and selfHp * 100 >= selfMaxHp * 25 then',
        'if aaCommitted and selfHp * 100 >= selfMaxHp * 25 and (param_idle_only = 0 or bestId = 0) then', 1)
    return replace(parent, template=source, parameters=parent.parameters | {
        'idle_only': (1, 0, 1), 'wait_support': (0, 0, 0)},
        meaning=parent.meaning + ' Caster-only restriction supersedes general participation: '
        'run this assistance extension only for red Lich and Warlock. DeathKnight, Crossbowman '
        'and Berserker retain their exact parent targeting and no wait gate is enabled. '
        'When idle_only=1, preserve any existing target and only fill no-target decisions. '
        'Do not extrapolate prior all-role results to this separately evaluated behavior.')


def caster_assist_bound(parent):
    # Preserve the historical incorrect operator for exact artifact extraction.
    # This new operator binds roles to the engine's global HeroClass ordinals.
    from hero_binding import CLASS_ID
    token = '  if selfClass = 2 or selfClass = 3 then\n  aaReady = 0'
    assert parent.template.count(token) == 1
    source = parent.template.replace(token,
        f'  if selfClass = {CLASS_ID["Lich"]} or selfClass = {CLASS_ID["Warlock"]} then\n  aaReady = 0', 1)
    return replace(parent, template=source, meaning=parent.meaning +
        ' Source-grounded role binding: selfClass is the global HeroClass ordinal, '
        'not the team slot. On release2026.9.16.5 red Lich=7 and Warlock=8; blue '
        'Arcanist=2 and Druid=3. The red-only branch must use7/8. This version '
        'repairs the previously inactive red caster condition; old artifacts remain unchanged.')
