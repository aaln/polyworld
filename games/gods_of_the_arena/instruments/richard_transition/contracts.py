"""Versioned combined response to the 19:10 Richard coaching session.

All extra state reuses globals from the mutually exclusive inherited branch.
The previously evaluated operators and their BASIC bytes remain immutable.
"""
from dataclasses import replace
from binding import CONTRACTS
from games.gods_of_the_arena.instruments.richard_coaching import contracts as aliases
from games.gods_of_the_arena.instruments.richard_coaching import contracts_v6, contracts_v7

NAME='richard_transition_observe_v1'
ATTACK='richard_transition_focus_v1'
EQUIPMENT='richard_transition_equipment_v1'
parent=CONTRACTS[contracts_v6.NAME]
assert parent.template.count('\nelse\n')==1
source,preserved_branch=parent.template.split('\nelse\n')


def swap(old,new):
    global source
    old='\n'.join('  '+x for x in aliases.lower_storage(old).splitlines())
    new='\n'.join('  '+x for x in aliases.lower_storage(new).splitlines())
    assert source.count(old)==1,old
    source=source.replace(old,new)


# backdoorNearer: currently observed hostile count in our inner perimeter.
# criticalUntil: continuous observed-clear start; perimeterLastCombat: last
# visible enemy-hero tick; perimeterAnchor: previous observed home-core HP.
# backdoorActive: dominant ranged focus; perimeterEnabled: designated scout.
swap('gaHomeThreats = 0','''gaHomeThreats = 0
backdoorNearer = 0
backdoorActive = 0
perimeterEnabled = 0''')

# Presence far down a lane no longer sends the entire group home. A currently
# observed structure attacker within the authored interception radius does.
swap('''      if gaD <= param_home_radius * param_home_radius then
        gaHomeThreats = gaHomeThreats + 1
        if objectTarget(gaI) > 0 and objectTarget(gaI) < 100 then
          gaHomeThreats = gaHomeThreats + 1
        end if
      end if''','''      if gaD <= param_home_radius * param_home_radius then
        gaHomeThreats = gaHomeThreats + 1
      end if
      if gaD <= 1600 then
        if objectTarget(gaI) > 0 and objectTarget(gaI) < 100 then
          gaHomeThreats = gaHomeThreats + 2
        end if
      end if''')

# Reuse the detailed scan. No claim of clearance is made if it was truncated.
swap('''      if gaKind = 2 then
        gaScore = gaD * 4 + gaHp''','''      if gaKind = 2 or gaKind = 3 then
        if (gaOx - 105) * (gaOx - 105) + (gaOy - 11) * (gaOy - 11) <= 1296 then
          backdoorNearer = backdoorNearer + 1
        end if
      end if
      if gaKind = 2 then
        gaScore = gaD * 4 + gaHp
        if objectClass(gaI) = 1 and (gaOx - 105) * (gaOx - 105) + (gaOy - 11) * (gaOy - 11) <= 1600 then
          gaScore = gaScore - 100000
        end if''')

swap('''if worldTick <= gaLastTick or worldTick > gaLastTick + 1 then
  gaEntryUntil = 0
  gaProbeSince = 0
  gaBreachUntil = 0
  defUntil = 0
end if
if gaHomeThreats >= 2 or gaHomeHp < 400 then
  defUntil = worldTick + param_home_commit_ticks
  defThreatX = gaFrontX
  defThreatY = gaFrontY
end if
gaEmergency = 0
if worldTick < defUntil then
  gaEmergency = 1
  gaFrontX = defThreatX
  gaFrontY = defThreatY
end if''','''if worldTick <= gaLastTick or worldTick > gaLastTick + 1 then
  gaEntryUntil = 0
  gaProbeSince = 0
  gaBreachUntil = 0
  defUntil = 0
  criticalUntil = 0
  perimeterLastCombat = worldTick
  perimeterAnchor = gaHomeHp
end if
if gaEnemyN > 0 then
  perimeterLastCombat = worldTick
end if
if gaHomeThreats >= 2 or gaHomeHp < perimeterAnchor then
  defUntil = worldTick + param_home_commit_ticks
  defThreatX = gaFrontX
  defThreatY = gaFrontY
  criticalUntil = 0
else
  if gaN <= 128 and backdoorNearer = 0 then
    if criticalUntil = 0 then
      criticalUntil = worldTick
    end if
    if worldTick - criticalUntil >= param_clear_ticks then
      defUntil = 0
    end if
  else
    criticalUntil = 0
  end if
end if
perimeterAnchor = gaHomeHp
gaEmergency = 0
if worldTick < defUntil then
  gaEmergency = 1
  gaFrontX = defThreatX
  gaFrontY = defThreatY
end if''')

# A visible threatening Ranger must not wait for four healthy defenders to
# respawn. Shared selection remains identical for heroes observing the same
# team state. Local range bounds prevent a cross-map pursuit.
swap('''gaDx = selfX - gaX
gaDy = selfY - gaY''','''if gaHero <> 0 and gaHeroScore < 0 then
  bestId = gaHero
  bestDistance = gaHeroScore + 100000
  backdoorActive = 1
end if
gaDx = selfX - gaX
gaDy = selfY - gaY''')
swap('''if gaDx * gaDx + gaDy * gaDy > param_tether_radius * param_tether_radius and (gaEmergency = 0 or gaReady) then''',
'''if gaDx * gaDx + gaDy * gaDy > param_tether_radius * param_tether_radius and (gaEmergency = 0 or gaReady) and backdoorActive = 0 then''')

# Scout is a bounded lead from the current group center, not an invisible
# attack target. Low HP or any observed enemy cancels the scouting exception.
scout=aliases.lower_storage('''
if gaEmergency = 0 and gaEnemyN = 0 and backdoorNearer = 0 and gaN <= 128 then
  if worldTick - perimeterLastCombat >= param_scout_quiet_ticks then
    if selfClass = 6 and selfHp * 5 >= selfMaxHp * 3 then
      if (gaX - 105) * (gaX - 105) + (gaY - 11) * (gaY - 11) <= 3600 then
        gaMoveX = gaX - 10
        gaMoveY = gaY + 10
        bestId = 0
        gaTethered = 1
        perimeterEnabled = 1
      end if
    end if
  end if
end if
''').strip()
source+='\n'+'\n'.join('  '+x for x in scout.splitlines())+'\nelse\n'+preserved_branch
CONTRACTS[NAME]=replace(parent,template=source,
    parameters=parent.parameters|{'home_radius':(28,20,36),'home_commit_ticks':(360,120,600),
        'clear_ticks':(72,12,240),'scout_quiet_ticks':(240,120,480)},
    memory=tuple(dict.fromkeys(parent.memory+('criticalUntil','perimeterLastCombat','perimeterAnchor'))),
    meaning='Coached red controller with bounded defense and proactive transition. '
        'Inherits the versioned group/perimeter behavior. Two visible enemy heroes '
        'inside home_radius, an observed structure attacker inside40tiles, or a '
        'new core-HP decrease renew the short defense deadline. Old damage alone '
        'never renews it. A complete128-object scan with no hostile hero/creep '
        'inside36tiles for clear_ticks ends defense; incomplete scans are unknown. '
        'The finite deadline still expires without fresh positive pressure. '
        'After scout_quiet_ticks without visible enemy heroes, a healthy Crossbowman '
        'may lead14tiles diagonally from the team center while near home. Any '
        'observed hero, perimeter hostile or low HP cancels that exception. '
        'A visible Ranger within40tiles of home and22tiles of the group center '
        'wins shared hero selection and bypasses the four-healthy readiness/tether '
        'block. Class is a public threat cue, not measured hidden DPS or identity. '
        'Blue and red before the selected phase retain the exact parent behavior.')

attack=CONTRACTS[contracts_v7.NAME]
focus='''if gaActive and backdoorActive and bestId <> 0 then
  motionActive = 0
  motionUntil = 0
  mSpell = 1
  if selfClass = 6 then
    mSpell = 2
  end if
  if abilityCharges(mSpell) > 0 and abilityCooldown(mSpell) = 0 then
    mCast = castTarget(mSpell, bestId)
  end if
  attackTarget(bestId)
else
'''
CONTRACTS[ATTACK]=replace(attack,
    template=focus+'\n'.join('  '+x for x in attack.template.splitlines())+'\nend if',
    meaning=attack.meaning+' A shared visible Ranger focus issues legal available '
        'class strikes and attack commands in the same host decision, releasing '
        'stale recovery. This coordinates initiation; the engine has no dash '
        'or stun attached to these selected strikes, so none is claimed. '
        'Cast acceptance, mana, charge and range remain engine-enforced.')

equipment=CONTRACTS['buy_ordered_loadout']
red_equipment=equipment.template.replace('param_third_item','16').replace('param_fourth_item','18').replace('param_fifth_item','20')
CONTRACTS[EQUIPMENT]=replace(equipment,
    template='if selfTeam = 0 then\n'+'\n'.join('  '+x for x in red_equipment.splitlines())+
        '\nelse\n'+'\n'.join('  '+x for x in equipment.template.splitlines())+'\nend if',
    meaning='On red, retain the first two authored ordered items, then buy Knight '
        'Armor, Battle Axe and Arcane Spellbook. This benchmarks the observed '
        'Ranger progression; the combined survival/scaling benefit needs evaluation. '
        'Blue follows the unmodified configured ordered loadout. '+equipment.meaning)
