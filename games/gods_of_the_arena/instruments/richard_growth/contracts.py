"""Source-informed red damage conversion; unchanged critical60 blue branch."""
from dataclasses import replace
from binding import CONTRACTS
from games.gods_of_the_arena.instruments.richard_counter import contracts as critical

ATTACK = 'richard_growth_inplace_recovery_v1'
EQUIPMENT = 'richard_growth_objective_equipment_v1'
SUSTAIN = 'richard_growth_healing_budget_v1'
OBSERVER = 'richard_growth_current_defenders_v1'


def red_else_blue(red, blue):
    return 'if selfTeam = 0 then\n' + '\n'.join('  ' + s for s in red.splitlines()) + '\nelse\n' + '\n'.join('  ' + s for s in blue.splitlines()) + '\nend if'


def register():
    parent = CONTRACTS['defense_cadence']
    red = '''motionActive = 0
if bestId <> 0 then
  attackTarget(bestId)
end if
if motionLastTick > 0 and worldTick = motionLastTick + 1 then
  if selfAttacksLanded > motionLastHits then
    kiteMoved = walkTo(selfX, selfY)
    if kiteMoved then
      motionActive = 1
      recoverySteps = recoverySteps + 1
      if param_spells = 1 and bestId <> 0 then
        mSpell = 3
        mCast = 0
        while mSpell >= 1 and mCast = 0
          if abilityCharges(mSpell) > 0 and abilityCooldown(mSpell) = 0 then
            mCast = castTarget(mSpell, bestId)
          end if
          mSpell = mSpell - 1
        wend
      end if
    end if
  end if
end if
motionLastTick = worldTick
motionLastHits = selfAttacksLanded
motionLastHp = selfHp'''
    CONTRACTS[ATTACK] = replace(parent, template=red_else_blue(red, parent.template),
        meaning=parent.meaning + ' Superseding red behavior: issue the selected attack, then only '
        'after a newly landed basic hit on consecutive living decisions request a walk to the '
        'current position. This cancels recovery without choosing an outward escape destination. '
        'Never infer a fresh hit on cold start or after a decision gap. Accepted recovery blocks '
        'fallback movement for this decision. Retain the parent descending charged-spell attempts '
        'during recovery. All red classes use this rule, including Berserker. Blue is the exact '
        'parent combat. Source-informed hypothesis, not proof of improved damage or survival.')

    parent = CONTRACTS['selective_loadout']
    red = '''ownsfirst = 0
ownssecond = 0
ownsthird = 0
ownsfourth = 0
ownsfifth = 0
loadoutSlot = 0
while loadoutSlot < 6
  loadoutItem = itemId(loadoutSlot)
  if loadoutItem = 11 then
    ownsfirst = 1
  end if
  if loadoutItem = 13 then
    ownssecond = 1
  end if
  if loadoutItem = 16 then
    ownsthird = 1
  end if
  if loadoutItem = 18 then
    ownsfourth = 1
  end if
  if loadoutItem = 20 then
    ownsfifth = 1
  end if
  loadoutSlot = loadoutSlot + 1
wend
if ownsfirst = 0 and selfGold >= 110 then
  buyItem(11)
end if
if ownssecond = 0 and selfGold >= 150 then
  buyItem(13)
end if
if ownsthird = 0 and selfGold >= 160 then
  buyItem(16)
end if
if ownsfourth = 0 and selfGold >= 180 then
  buyItem(18)
end if
if ownsfifth = 0 and selfGold >= 190 then
  buyItem(20)
end if'''
    CONTRACTS[EQUIPMENT] = replace(parent, template=red_else_blue(red, parent.template),
        meaning=parent.meaning + ' Superseding red equipment on every class: ordered missing-item '
        'attempts for dagger11, sword13, HP armor16, axe18 and spellbook20, matching the observed '
        'Richard objective build. Each uses predecision gold; actual affordability and space are '
        'host-validated after prior purchases. Armor adds120 current and maximumHP, not damage '
        'reduction. The book adds basic damage even on noncasters. Retain blue equipment exactly. '
        'This is not a guaranteed one-purchase-per-turn saving policy.')

    parent = CONTRACTS['buy_sustain_only']
    red = '''if selfHp * 2 < selfMaxHp and hasHeal = 0 then
  if selfGold >= 50 then
    buyItem(2)
  end if
  if selfGold >= 30 then
    buyItem(1)
  end if
end if'''
    CONTRACTS[SUSTAIN] = replace(parent, template=red_else_blue(red, parent.template),
        meaning=parent.meaning + ' Red retains healing purchases before equipment but omits '
        'mana-potion purchases, matching the observed objective economy. Both healing attempts '
        'may succeed; healing still competes with equipment gold. Blue is unchanged.')

    parent = CONTRACTS['lineup_critical_recall']
    red, blue = parent.template.split('\nelse\n', 1)
    token = '\n  if defActive then\n'
    assert red.count(token) == 1
    assignment = '''
  if defActive then
    mDx = selfX - defHomeX
    mDy = selfY - defHomeY
    mDistance = mDx * mDx + mDy * mDy
    mAllies = 0
    mIndex = 0
    while mIndex < objectCount() and mIndex < 64
      mKind = objectKind(mIndex)
      if mKind = 2 and objectTeam(mIndex) = selfTeam then
        if objectAlive(mIndex) and objectHp(mIndex) > 0 then
          mDx = objectX(mIndex) - defHomeX
          mDy = objectY(mIndex) - defHomeY
          mD = mDx * mDx + mDy * mDy
          if mD < mDistance or (mD = mDistance and objectId(mIndex) < selfId) then
            mAllies = mAllies + 1
          end if
        end if
      end if
      mIndex = mIndex + 1
    wend
    coreRespond = param_growth_defenders
    if defFront <> 0 and defFrontD <= 400 and defCount >= 2 then
      coreRespond = 2
    end if
    if mAllies >= coreRespond then
      defActive = 0
      defUntil = 0
      criticalUntil = 0
    end if
  end if
'''
    CONTRACTS[OBSERVER] = replace(parent,
        template=red.replace(token, assignment + token, 1) + '\nelse\n' + blue,
        parameters=parent.parameters | {'growth_defenders': (1, 1, 3)},
        meaning=parent.meaning + ' Superseding red recall allocation: among currently observed '
        'living allies in the first64objects, rank distance to own home, breaking equal-distance '
        'ties by public actor ID. Retain remembered recall only for growth_defenders nearest '
        'heroes, or the nearest two when a fresh visible enemy front is within20tiles of home '
        'and its cluster contains at least two enemies. Others clear commitment and immediately '
        'use ordinary offensive targeting and routing. Recompute each living decision; no '
        'persistent role lock, player identity or hidden enemy position. Missing allies may '
        'increase defenders; this is not a strict simultaneous cap across sequential decisions. '
        'Existing blue critical recall is unchanged. Source-inspired allocation hypothesis.')


register()
