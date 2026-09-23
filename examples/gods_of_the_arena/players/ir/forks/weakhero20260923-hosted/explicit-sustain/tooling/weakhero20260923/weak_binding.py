"""Replay60 explicit sustain, early unlocks, and bounded melee lane recovery."""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PARENT = ROOT / 'examples/gods_of_the_arena/players/ir/forks/druid-lane20260923-hosted/druid-lane'
sys.path.insert(0, str(HERE.parent / 'druidlane20260923'))
import druid_binding as parent

ir, host = parent.ir, parent.host
VERSION = 'gota-bassy/explicit-sustain-2026-09-23-r60e'
MELEE = '(selfClass = VanguardKnight or selfClass = DeathKnight)'
RESOURCE = '(' + MELEE + ' or selfClass = Arcanist or selfClass = Warlock)'


def configure():
    specs = dict(parent.configure())
    facts = ir.temporal_facts('2026.9.23.2')
    facts['explicit_abilities'] = 'Replay60/fd315c8: all abilities require explicit cast commands; there is no automatic spell fallback. Idle basic acquisition includes heroes, creeps and exposed structures.'
    facts['balance'] = 'Ranger HP growth29; Crossbowman base damage58; DeathKnight Chalice45; DemonHunter GaleSlash65; Warlock Totem87.'
    ir.temporal_facts = lambda version: deepcopy(facts)
    old = specs['lifecycle']
    text = old.template.replace('if selfClass = DruidWarden then', 'if selfClass = DruidWarden or ' + MELEE + ' then')
    marker = '    if slot >= 0 then\n      levelAbility(slot)'
    assert text.count(marker) == 1
    text = text.replace(marker, '''    if ''' + RESOURCE + ''' then
      if selfLevel >= 2 and abilityLevel(0) = 0 and canLevelAbility(0) = 1 then
        slot = 0
      end if
    end if
''' + marker)
    specs['lifecycle'] = replace(old, template=text, meaning=old.meaning + ' For Vanguard/DeathKnight and Arcanist/Warlock, preserve the level1 primary attack then unlock the free resource ability with the next available skill point from level2. Other rank priorities remain. Clear melee lane memory on death.')
    old = specs['economy']
    specs['economy'] = replace(old, template=old.template.replace('if selfClass = DruidWarden then', 'if selfClass = DruidWarden or ' + MELEE + ' then'), meaning=old.meaning + ' Record accepted potion duration for melee lane recovery too.')
    old = specs['observe']
    marker = 'recallHeroDistance = distance'
    assert old.template.count(marker) == 1
    specs['observe'] = replace(old, template=old.template.replace(marker, marker + '\n            recallHeroX = x\n            recallHeroY = y'), meaning=old.meaning + ' Remember the nearest currently visible enemy hero position for short melee disengagements; never use hidden opponent state.')
    specs['explicit_sustain'] = host.contract('''
if inOwnSpawn() = 0 then
  sustainSlot = 0
  while sustainSlot < 4
    if abilityLevel(sustainSlot) > 0 and abilityCharges(sustainSlot) > 0 and abilityCooldown(sustainSlot) = 0 then
      if selfMana >= abilityManaCost(sustainSlot) then
        sustainUseful = 0
        if abilityHeal(sustainSlot) > 0 and selfMaxHp - selfHp >= abilityHeal(sustainSlot) / 2 then
          sustainUseful = 1
        end if
        if abilityRestore(sustainSlot) > 0 and selfMaxMana - selfMana >= abilityRestore(sustainSlot) / 2 then
          sustainUseful = 1
        end if
        if sustainUseful = 1 then
          if castTarget(sustainSlot, selfId) = 1 and abilityHeal(sustainSlot) > 0 then
            if laneHealUntil < worldTick + 18 then
              laneHealUntil = worldTick + 18
            end if
          end if
        end if
      end if
    end if
    sustainSlot = sustainSlot + 1
  wend
end if
''', {}, (), (), ('castTarget',), 'Explicit self healing or mana restoration for Vanguard/DeathKnight and Arcanist/Warlock, before target-dependent combat and retreat stops. Require learned, charged, ready, affordable ability and at least half its recovery amount missing; skip own spawn. Accepted healing creates a short pending-effect window. Never stop movement here: dangerous escape and useful shopping continue. The normal active predicate preserves stun, death, draft and portal-channel locks.', ('laneHealUntil',))
    specs['lane_recovery'] = replace(specs['lane_recovery'], meaning=specs['lane_recovery'].meaning + ' Extended to Vanguard/DeathKnight under explicit-cast engine60. The same twelve-second bound, safety checks, shopping override and60percent HP release apply; no assumption of passive autoheal.')
    specs['melee_spacing'] = host.contract('''
if stopped = 0 and recallHeroDistance <= 25 then
  meleeDanger = 0
  if enemyPower > friendPower or selfHp * 100 < selfMaxHp * 55 then
    meleeDanger = 1
  end if
  if bestId > 0 and bestKind = 3 and bestHp <= selfAttackDamage and bestDistance <= hitReach * hitReach then
    if selfHp * 100 >= selfMaxHp * 40 then
      meleeDanger = 0
    end if
  end if
  if meleeDanger = 1 then
    resumeTarget = 0
    if selfRootTicks = 0 then
      dx = selfX - recallHeroX
      dy = selfY - recallHeroY
      span = dx
      if span < 0 then
        span = -span
      end if
      spanY = dy
      if spanY < 0 then
        spanY = -spanY
      end if
      if spanY > span then
        span = spanY
      end if
      if span = 0 then
        dx = homeX - selfX
        dy = homeY - selfY
        span = dx
        if span < 0 then
          span = -span
        end if
        spanY = dy
        if spanY < 0 then
          spanY = -spanY
        end if
        if spanY > span then
          span = spanY
        end if
      end if
      if span > 0 then
        walkTo(selfX + dx * 2 / span, selfY + dy * 2 / span)
        moveTick = worldTick + 6
      end if
    end if
    stopped = 1
  end if
end if
''', {}, (), (), ('walkTo',), 'For Vanguard/DeathKnight heroes only, disengage from a visible hero within five tiles when visible enemy level-power exceeds allied support or health is below55percent. Preserve an in-reach one-hit creep finish at40percent HP or higher. Otherwise cancel the attack target with a short two-tile move away, reconsider next decision, and do not set a base-retreat latch. Resource spells already ran; tower/escape priorities precede this. Both eight-tile and five-tile broad-melee bundles harmed Berserker XP in local screens. Exclude Berserker and DemonHunter changes from this source; target the historically weak Vanguard/DeathKnight cohort, with fresh validation required.', ('resumeTarget', 'moveTick'))
    old = specs['combat']
    text = old.template.replace('  slot = 0', '  creepFinishQueued = 0\n  slot = 0')
    marker = 'castTarget(slot, bestId)'
    assert text.count(marker) == 1
    text = text.replace(marker, '''if ''' + RESOURCE + ''' and bestKind = 3 then
              if creepFinishQueued = 0 then
                if castTarget(slot, bestId) = 1 then
                  creepFinishQueued = 1
                end if
              end if
            else
              castTarget(slot, bestId)
            end if''')
    specs['combat'] = replace(old, template=text, meaning=old.meaning + ' Vanguard/DeathKnight/Arcanist/Warlock only: once a lethal-on-observed-HP creep damage spell is accepted, do not queue additional damage slots at the same creep this decision. Keep healing and hero burst behavior. This avoids spending multiple cooldowns on the same one-HP creep in the public frozen observation.')
    order = list(specs)
    order.remove('explicit_sustain')
    order.insert(order.index('lane_recovery'), 'explicit_sustain')
    order.remove('melee_spacing')
    order.insert(order.index('combat'), 'melee_spacing')
    specs = {key: specs[key] for key in order}
    host.PREDICATES['active_resource_hero'] = ('active = 1 and ' + RESOURCE, (), 'Active Vanguard/DeathKnight or mana-restoring caster, preserving the existing portal/death/stun/draft lock.')
    host.PREDICATES['active_lane_healer'] = ('active = 1 and (selfClass = DruidWarden or ' + MELEE + ')', (), 'Active Druid or Vanguard/DeathKnight; carry and mana-only caster routing stays unchanged.')
    host.PREDICATES['active_melee'] = ('active = 1 and ' + MELEE, (), 'Active melee hero under the normal channel/death/stun/draft guard.')
    host.VERSION = ir.VERSION = VERSION
    host.GAME_VERSIONS = ir.GAME_VERSIONS = tuple(dict.fromkeys((*ir.GAME_VERSIONS, '2026.9.23.2')))
    host.CONTRACTS.clear()
    host.CONTRACTS.update({'weak_' + key: value for key, value in specs.items()})
    return specs
