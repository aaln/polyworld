"""Kiting grounded in the published 2026.9.15.3 hit event, not elapsed time."""
from dataclasses import replace

def confirmed_hit_contract(timed):
    source=timed.template
    start=source.index('if worldTick <> kiteLastTick + 1 or bestId <> kiteLastTarget')
    end=source.index('kiteRanged = 0',start)
    source=source[:start]+'''if kiteLastTick = 0 or worldTick <> kiteLastTick + 1 then
  kiteUntil = 0
  kiteReady = 0
  kiteLastHits = selfAttacksLanded
end if
if bestId = 0 then
  kiteUntil = 0
end if
'''+source[end:]
    source=source.replace('bestId <> 0 and kiteThreat <> 0 and worldTick >= kiteReady','bestId <> 0 and kiteThreat <> 0')
    source=source.replace('selfHp * 100 < selfMaxHp * param_critical_percent and kiteThreatDistance <= 36 and selfHp < kiteLastHp',
        'worldTick >= kiteReady and worldTick >= kiteUntil and selfHp * 100 < selfMaxHp * param_critical_percent and kiteThreatDistance <= 36 and selfHp < kiteLastHp')
    source=source.replace('kiteStillTicks >= param_burst_ticks','selfAttacksLanded > kiteLastHits and selfAttackCooldown > 0')
    source=source.replace('  kiteReady = kiteUntil + param_burst_ticks','  if kiteTrigger = 2 then\n    kiteReady = kiteUntil + param_escape_rearm_ticks\n  end if')
    source=source.replace('  kiteStillTicks = kiteStillTicks + 1\nelse\n  kiteStillTicks = 0\n','')
    source=source.replace('kiteLastTarget = bestId\nkiteLastX = selfX\nkiteLastY = selfY','kiteLastHits = selfAttacksLanded')
    parameters=dict(timed.parameters);parameters.pop('burst_ticks');parameters['escape_rearm_ticks']=(18,1,48);parameters['critical_percent']=(35,0,70)
    memory=tuple(m for m in timed.memory if m not in ['kiteLastTarget','kiteLastX','kiteLastY','kiteStillTicks'])+('kiteLastHits',)
    return replace(timed,template=source,parameters=parameters,memory=memory,
        meaning='On published 2026.9.15.3, retreat a bounded number of ticks after a newly observed successful basic hit when a ranged hero has a close visible mobile target. The lifetime hit counter and positive attack cooldown confirm the hit event; do not cancel a windup based only on proximity or a timer. Every class also has a bounded escape when critically injured and losing HP. Rearm that emergency escape only after an attack opportunity. Move away from the nearest observed threat, including protected towers. Check terrain and restore attack intent if movement fails. Reset hit-event memory on decision gaps so respawns cannot create phantom hits. Keep target selection, buying and no-target wave following separate.')


def targeted_hit_contract(confirmed):
    source=confirmed.template.replace(
        'if kiteKind = 2 or kiteKind = 3 or kiteKind = 4 then',
        'if (kiteKind = 2 or kiteKind = 3 or kiteKind = 4) and objectTarget(kiteIndex) = selfId then')
    return replace(confirmed,template=source,meaning=confirmed.meaning+' Only treat a visible mobile enemy or standing tower as a retreat threat when its exposed current target ID equals selfId. This is observed attack intent, not proof of future damage. Other nearby enemies do not cause a retreat.')


def spell_hit_contract(confirmed):
    source=confirmed.template.replace('    kiteMoveTicks = kiteMoveTicks + 1','''    kiteMoveTicks = kiteMoveTicks + 1
    kiteSpellSlot = 3
    kiteSpellCast = 0
    while kiteSpellSlot >= 1 and kiteSpellCast = 0
      if selfClass <> 3 or kiteSpellSlot = 3 then
        if abilityCharges(kiteSpellSlot) > 0 and abilityCooldown(kiteSpellSlot) = 0 then
          kiteSpellCast = castTarget(kiteSpellSlot, bestId)
        end if
      end if
      kiteSpellSlot = kiteSpellSlot - 1
    wend
    if kiteSpellCast then
      kiteSpellCasts = kiteSpellCasts + 1
    end if''')
    return replace(confirmed,template=source,actions=confirmed.actions+('castTarget',),memory=confirmed.memory+('kiteSpellCasts',),
        meaning=confirmed.meaning+' After an accepted retreat movement, explicitly attempt one offensive spell, in descending slot3,2,1 priority, when charged and off cooldown; host checks live mana, target and range. Skip Druid healing slots1/2; automatic support/passives stay enabled. This restores an offensive opportunity that walking otherwise suppresses by clearing attack intent. Resource timing can differ from automatic casting; validate accepted casts, lifetime XP, survival and wins.')
