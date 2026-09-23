"""Bounded lane recovery instead of an unconditional health-only base trip."""
from dataclasses import replace
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / 'bluekhors20260923'))
import blue_binding as parent

ir, host = parent.ir, parent.host
VERSION = 'gota-bassy/lane-recovery-2026-09-23-r1'
PARENT = ROOT / 'examples/gods_of_the_arena/players/ir/forks/blue-center20260923-hosted/blue-center'


def configure():
    specs = dict(parent.configure())
    old = specs['lifecycle']
    specs['lifecycle'] = replace(
        old, template=old.template.replace('    retreat = 0', '    retreat = 0\n    laneUntil = 0\n    laneHealUntil = 0'),
        memory=old.memory + ('laneUntil', 'laneHealUntil'))
    old = specs['economy']
    assert old.template.count('useItem(healSlot)') == 1
    specs['economy'] = replace(old, template=old.template.replace(
        'useItem(healSlot)', '''if useItem(healSlot) = 1 then
        laneHealUntil = worldTick + tickRate * 10
      end if'''), memory=old.memory + ('laneHealUntil',),
        meaning=old.meaning + ' Remember only an accepted health potion for its ten-second recovery duration; an empty consumed stack does not hide ongoing healing.')
    specs['lane_recovery'] = host.contract('''
if inBase = 1 then
  laneUntil = 0
  laneHealUntil = 0
end if
if inBase = 0 and retreat = 1 then
  shoppingDue = 0
  if empty > 0 then
    if has11 = 0 and selfGold >= 110 then
      shoppingDue = 1
    end if
    if has16 = 0 and selfGold >= 160 then
      shoppingDue = 1
    end if
    if has18 = 0 and selfGold >= 180 then
      shoppingDue = 1
    end if
    if has19 = 0 and selfGold >= 180 then
      shoppingDue = 1
    end if
  end if
  if shoppingDue = 1 then
    restock = 1
  end if
  if restock = 0 then
    laneSafe = 0
    if recallHeroDistance > 100 and recallCreepDistance > 36 and towerDistance > 100 and towerAggro = 0 then
      laneSafe = 1
      warnings = spellCount()
      if warnings > 24 then
        laneSafe = 0
      end if
      w = 0
      while w < warnings and w < 24
        dx = spellX(w) - selfX
        dy = spellY(w) - selfY
        if spellCasterId(w) <> selfId then
          if dx * dx + dy * dy <= 64 and spellImpactTick(w) <= worldTick + tickRate then
            laneSafe = 0
          end if
        end if
        w = w + 1
      wend
    end if
    if laneSafe = 1 then
      if selfHp * 100 >= selfMaxHp * 60 and selfMana * 100 >= selfMaxMana * 20 then
        retreat = 0
        laneUntil = 0
        laneHealUntil = 0
        resumeTarget = 0
        moveTick = worldTick
        if selfRootTicks = 0 then
          walkTo(selfX, selfY)
        end if
      else
        laneCanHeal = 0
        laneSlot = -1
        laneAmount = 0
        if worldTick < laneHealUntil then
          laneCanHeal = 1
        end if
        s = 0
        while s < 4
          if abilityLevel(s) > 0 and abilityHeal(s) > 0 and abilityCharges(s) > 0 then
            if selfMana >= abilityManaCost(s) and abilityCooldown(s) <= tickRate * 8 then
              laneCanHeal = 1
              if abilityCooldown(s) = 0 and abilityHeal(s) > laneAmount then
                if selfMaxHp - selfHp >= abilityHeal(s) / 2 then
                  laneSlot = s
                  laneAmount = abilityHeal(s)
                end if
              end if
            end if
          end if
          s = s + 1
        wend
        if laneCanHeal = 1 then
          if laneUntil = 0 then
            laneUntil = worldTick + tickRate * 12
          end if
          if worldTick < laneUntil then
            if laneSlot >= 0 then
              if castTarget(laneSlot, selfId) = 1 then
                if laneHealUntil < worldTick + 18 then
                  laneHealUntil = worldTick + 18
                end if
              end if
            end if
            resumeTarget = 0
            if selfRootTicks = 0 then
              walkTo(selfX, selfY)
            end if
            moveTick = worldTick
            stopped = 1
          end if
        end if
      end if
    end if
  end if
end if
''', {}, (), (), ('castTarget', 'walkTo'),
        'During a health-only field retreat, prefer a safe stationary lane heal over completing the base path. An affordable missing core item with an empty slot preserves the shopping trip. Otherwise no nearby enemy hero/creep/tower or imminent non-self warning permits a maximum twelve-second hold for an accepted potion, pending self-heal or learned charged affordable heal ready within eight seconds. Cast a useful strongest ready heal; resume normal play at sixty percent HP and twenty percent mana. Danger, no usable recovery or expired hold falls through to the existing escape. Current keep replenishment and active channels retain ownership. No extra heal casts outside this recovery state.',
        ('laneUntil', 'laneHealUntil', 'retreat', 'restock', 'resumeTarget', 'moveTick'))
    order = [key for key in specs if key != 'lane_recovery']
    order.insert(order.index('replenish'), 'lane_recovery')
    specs = {key: specs[key] for key in order}
    host.VERSION = ir.VERSION = VERSION
    host.CONTRACTS.clear()
    host.CONTRACTS.update({'lane_' + key: value for key, value in specs.items()})
    return specs
