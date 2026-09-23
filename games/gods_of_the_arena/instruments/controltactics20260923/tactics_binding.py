"""Use control against reachable heroes before retreat stops, preserving heal mana."""
from dataclasses import replace
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PARENT = ROOT / 'examples/gods_of_the_arena/players/ir/forks/control20260923-local/control-legality'
sys.path.insert(0, str(HERE.parent / 'control20260923'))
import control_binding as parent

ir, host = parent.ir, parent.host
VERSION = 'gota-bassy/control-tactics-2026-09-23-r61a'


def configure():
    specs = dict(parent.configure())
    old = specs['lifecycle']
    marker = '    if slot >= 0 then\n      levelAbility(slot)'
    assert old.template.count(marker) == 1
    specs['lifecycle'] = replace(old, template=old.template.replace(marker, '''    if selfClass = Warlock or selfClass = Lich then
      if selfLevel >= 2 and abilityLevel(2) = 0 and canLevelAbility(2) = 1 then
        slot = 2
      end if
    end if
''' + marker), meaning=old.meaning + ' Warlock and Lich unlock E control with their next available point from level2 after preserving the level1 primary. Other rank priorities remain.')
    old = specs['observe']
    setup = '''ccSlot = -1
ccTarget = 0
ccScore = -1000000
ccRadius = 0
ccDelay = 24
if selfClass = VanguardKnight then
  ccSlot = 3
  ccRadius = 3
  ccDelay = 6
end if
if selfClass = Warlock then
  ccSlot = 2
  ccRadius = 5
end if
if selfClass = DruidWarden then
  ccSlot = 3
  ccRadius = 5
end if
if selfClass = Lich then
  ccSlot = 2
  ccRadius = 6
end if
'''
    marker = '        if kind = 2 and distance < recallHeroDistance then'
    assert old.template.count(marker) == 1
    selection = '''          if ccSlot >= 0 and kind = 2 and objectAlive(idx) = 1 then
            if distance <= ccRadius * ccRadius then
              ccHeld = objectStunTicks(idx)
              if selfClass = Warlock then
                if objectSilenceTicks(idx) > ccHeld then
                  ccHeld = objectSilenceTicks(idx)
                end if
              end if
              if selfClass = Lich or selfClass = DruidWarden then
                if objectRootTicks(idx) > ccHeld then
                  ccHeld = objectRootTicks(idx)
                end if
              end if
              ccFinish = 0
              if hp <= abilityDamage(ccSlot) then
                ccFinish = 1
              end if
              ccThreat = 0
              if objectTarget(idx) = selfId then
                ccThreat = 1
              end if
              if selfClass = Warlock then
                ccMage = objectClass(idx)
                if ccMage = Arcanist or ccMage = Warlock or ccMage = Lich or ccMage = DruidWarden then
                  if objectMana(idx) >= 15 then
                    ccThreat = 1
                  end if
                end if
              end if
              if ccHeld <= ccDelay + 6 or ccFinish = 1 then
                ccValue = 1000 - distance * 10 - hp
                if ccThreat = 1 then
                  ccValue = ccValue + 1000
                end if
                if ccFinish = 1 then
                  ccValue = ccValue + 2000
                end if
                if ccValue > ccScore then
                  ccScore = ccValue
                  ccTarget = id
                  ccTargetHp = hp
                  ccTargetThreat = ccThreat
                end if
              end if
            end if
          end if
'''
    specs['observe'] = replace(old, template=setup + old.template.replace(marker, selection + marker),
        meaning=old.meaning + ' Within the same bounded public scan, rank nearby visible hero control opportunities by immediate spell finish, current attacker or mana-bearing caster, proximity and health. Read appropriate stun/silence/root remaining duration. Do not reapply redundant control beyond cast delay plus one decision unless spell damage can finish. Coarse integer-tile radius is a prefilter; castTarget remains the exact range/shape validator.')
    specs['control_hero'] = host.contract('''
if selfSilenceTicks = 0 and ccSlot >= 0 and ccTarget > 0 then
  if abilityLevel(ccSlot) > 0 and abilityCooldown(ccSlot) = 0 and abilityCharges(ccSlot) > 0 then
    ccUseful = 0
    if ccTarget = bestId or ccTargetThreat = 1 or ccTargetHp <= abilityDamage(ccSlot) then
      ccUseful = 1
    end if
    if ccUseful = 1 then
      ccReserve = 0
      if selfHp * 100 < selfMaxHp * 65 then
        ccHeal = 0
        while ccHeal < 4
          if abilityLevel(ccHeal) > 0 and abilityHeal(ccHeal) > 0 and abilityCharges(ccHeal) > 0 then
            if abilityCooldown(ccHeal) <= tickRate * 2 and abilityManaCost(ccHeal) > ccReserve then
              ccReserve = abilityManaCost(ccHeal)
            end if
          end if
          ccHeal = ccHeal + 1
        wend
      end if
      if selfMana >= abilityManaCost(ccSlot) + ccReserve then
        castTarget(ccSlot, ccTarget)
      end if
    end if
  end if
end if
''', {}, (), (), ('castTarget',),
        'Cast the selected hero control before retreat/tower movement claims stopped. Require learned, charged, ready, unsilenced and affordable. Preserve the largest affordable imminent healing cost below65percent HP. This skill never changes movement or basic attack target, never blocks escape, and never initiates during an existing channel/stun. Keep useful damage finishes even under existing control.', ())
    old = specs['combat']
    marker = 'if selfSilenceTicks = 0 and abilityLevel(slot) > 0 and abilityCooldown(slot) = 0 then'
    assert old.template.count(marker) == 1
    specs['combat'] = replace(old, template=old.template.replace(marker, 'if selfSilenceTicks = 0 and (slot <> ccSlot or bestKind <> 2) and abilityLevel(slot) > 0 and abilityCooldown(slot) = 0 then'),
        meaning=old.meaning + ' Hero control slots are scheduled by the earlier dedicated skill; prevent the generic loop from overriding overlap/resource decisions. Other spells, creep finishing and structure casts retain baseline behavior.')
    order = [k for k in specs if k != 'control_hero']
    order.insert(order.index('portal_context'), 'control_hero')
    specs = {k: specs[k] for k in order}
    host.VERSION = ir.VERSION = VERSION
    host.CONTRACTS.clear()
    host.CONTRACTS.update({'cctactics_' + k: v for k, v in specs.items()})
    return specs
