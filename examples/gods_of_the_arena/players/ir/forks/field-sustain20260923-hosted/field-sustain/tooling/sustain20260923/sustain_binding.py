"""Interrupt health-only retreats after bounded, publicly observed field sustain."""
from dataclasses import replace
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / 'bluekhors20260923'))
import blue_binding as parent
ir, host = parent.ir, parent.host
VERSION = 'gota-bassy/field-sustain-2026-09-23-r2'
PARENT = ROOT / 'examples/gods_of_the_arena/players/ir/forks/blue-center20260923-hosted/blue-center'

def configure():
    specs = dict(parent.configure())
    old = specs['lifecycle']
    specs['lifecycle'] = replace(old, template=old.template.replace('    retreat = 0', '    retreat = 0\n    sustainUntil = 0'), memory=old.memory + ('sustainUntil',))
    specs['recovery_refresh'] = host.contract('''
if drafting = 0 and selfHp > 0 and retreat = 1 and restock = 0 then
  if portalBusy = 0 and selfChannelTicks = 0 and selfStunTicks = 0 and canShop() = 0 then
    if selfHp * 100 >= selfMaxHp * 75 and selfMana * 100 >= selfMaxMana * 20 then
      active = 1
      resumeTarget = 0
    end if
  end if
end if
''', {}, (), (), (), 'Reconsider a health-only retreat immediately when observed field HP reaches75% and mana20%. This only wakes observation; public threats must still permit release. Do not interrupt an active portal or stun.', ('retreat','restock','portalBusy','resumeTarget'))
    old = specs['observe']
    s = old.template.replace('  bestId = 0', '  bestId = 0')
    # Templates are unwrapped skill bodies; retain the complete parent scan.
    assert s.count('bestId = 0') == 1
    s = s.replace('bestId = 0', 'sustainAnchorDistance = 1000000\nsustainAnchorX = selfX\nsustainAnchorY = selfY\nbestId = 0', 1)
    marker = 'if team = selfTeam then'
    assert s.count(marker) == 1
    s = s.replace(marker, marker + '''
        if kind = 3 or kind = 4 then
          anchorHomeDx = homeX - selfX
          anchorHomeDy = homeY - selfY
          if (x - selfX) * anchorHomeDx + (y - selfY) * anchorHomeDy >= 0 then
            if distance < sustainAnchorDistance and distance <= 64 then
              sustainAnchorDistance = distance
              sustainAnchorX = x
              sustainAnchorY = y
            end if
          end if
        end if
''')
    specs['observe'] = replace(old, template=s, meaning=old.meaning + ' Also locate the nearest living allied creep/tower within8tiles on the homeward side for a bounded healing step; no hidden enemies or stale anchor persist across scans.')
    specs['field_appraisal'] = host.contract('''
sustainSafe = 0
canSustain = 0
baseFountainRequired = retreat
if inBase = 0 then
  if recallHeroDistance > 100 and recallCreepDistance > 36 and towerDistance > 100 and towerAggro = 0 then
    sustainSafe = 1
    w = 0
    warnings = spellCount()
    if warnings > 24 then
      sustainSafe = 0
    end if
    while w < warnings and w < 24
      dx = spellX(w) - selfX
      dy = spellY(w) - selfY
      if spellCasterId(w) <> selfId then
        if dx * dx + dy * dy <= 64 and spellImpactTick(w) <= worldTick + tickRate then
          sustainSafe = 0
        end if
      end if
      w = w + 1
    wend
  end if
  sustainSlot = -1
  sustainAmount = 0
  s = 0
  while s < 4
    if abilityLevel(s) > 0 and abilityCooldown(s) = 0 and abilityCharges(s) > 0 then
      if abilityHeal(s) > sustainAmount and selfMana >= abilityManaCost(s) then
        if selfMaxHp - selfHp >= abilityHeal(s) / 2 then
          sustainSlot = s
          sustainAmount = abilityHeal(s)
        end if
      end if
    end if
    s = s + 1
  wend
  if selfHp * 100 < selfMaxHp * 75 and worldTick >= sustainUntil and sustainSlot >= 0 then
    if castTarget(sustainSlot, selfId) = 1 then
      sustainUntil = worldTick + 18
    end if
  end if
  if sustainSafe = 1 and worldTick < sustainUntil then
    canSustain = 1
  end if
end if
''', {}, (), (), ('castTarget',), 'Recompute field danger and fountain need each decision. No enemy hero within10tiles, creep within6, enemy tower within10/targeting us, or near imminent non-self warning; overflow is unsafe. Own healing warnings are not hostile; unknown casters remain unsafe. Cast the strongest learned ready charged affordable self-heal below75%HP even while escaping danger. Wait at most18ticks for the accepted heal (current self-heals impact within12); do not infer success from availability or cooldown. No ready/active heal means no sustain hold.', ('sustainUntil', 'retreat'))
    specs['retreat_release'] = host.contract('''
retreat = 0
baseFountainRequired = 0
sustainUntil = 0
resumeTarget = 0
moveTick = worldTick
if selfRootTicks = 0 then
  walkTo(selfX, selfY)
end if
''', {}, (), (), ('walkTo',), 'End a health-only field retreat at75%HP/20%mana only in currently safe observed surroundings. Clear the persistent base path and attack-reacquisition memory, release navigation throttle, and allow combat/advance in this same decision. Preserve equipment restock, keep recovery, channel and unsafe retreats.', ('retreat','sustainUntil','resumeTarget','moveTick'))
    specs['field_sustain_and_push'] = host.contract('''
baseFountainRequired = 0
resumeTarget = 0
if selfRootTicks = 0 then
  sustainX = selfX
  sustainY = selfY
  shelterX = homeX
  shelterY = homeY
  if sustainAnchorDistance <= 64 then
    shelterX = sustainAnchorX
    shelterY = sustainAnchorY
  end if
  if shelterX > selfX then
    sustainX = selfX + 1
  end if
  if shelterX < selfX then
    sustainX = selfX - 1
  end if
  if shelterY > selfY then
    sustainY = selfY + 1
  end if
  if shelterY < selfY then
    sustainY = selfY - 1
  end if
  walkTo(sustainX, sustainY)
  moveTick = worldTick + 6
end if
stopped = 1
''', {}, (), (), ('walkTo',), 'During a safe accepted self-heal, replace long base navigation with a bounded one-cell-per-axis step toward a nearby homeward allied creep/tower, or homeward cover if none. Re-evaluate within6ticks; release at operational health or fall through to base retreat as soon as no heal is pending or threats appear. This is a short support action, never a wait for cooldown. Area healing is fixed in space; the short step remains within the current heal footprint at impact.', ('resumeTarget','moveTick'))
    order = list(specs)
    extras = ['recovery_refresh','field_appraisal','retreat_release','field_sustain_and_push']
    order = [k for k in order if k not in extras]
    order.insert(order.index('timing'), 'recovery_refresh')
    pos = order.index('replenish')
    order[pos:pos] = extras[1:]
    specs = {k: specs[k] for k in order}
    host.PREDICATES.update({
        'recovered_in_field': ('active = 1 and inBase = 0 and retreat = 1 and restock = 0 and sustainSafe = 1 and selfHp * 100 >= selfMaxHp * 75 and selfMana * 100 >= selfMaxMana * 20', (), 'Current safe field health>=75% and mana>=20%, no equipment restock; cancel a stale health retreat before reaching fountain.'),
        'can_sustain_in_lane': ('active = 1 and inBase = 0 and canSustain = 1 and restock = 0 and selfHp * 100 < selfMaxHp * 75', (), 'A self-heal was accepted within the bounded18tick impact window and current visible threats/warnings permit a short covered sustain step. Learned rank, charge, cooldown and mana were checked before acceptance; no speculative cooldown waiting.')
    })
    host.VERSION = ir.VERSION = VERSION
    host.CONTRACTS.clear()
    host.CONTRACTS.update({'sustain_' + k: v for k, v in specs.items()})
    return specs
