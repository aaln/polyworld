"""Carry focus preserves productive hit recovery rather than direct-fire cadence."""
from dataclasses import replace
from binding import CONTRACTS
from games.gods_of_the_arena.instruments.richard_transition import contracts as v1
from games.gods_of_the_arena.instruments.richard_coaching import contracts as aliases

OBSERVE='richard_transition_observe_v2'
ATTACK='richard_transition_focus_v2'
parent=CONTRACTS[v1.NAME]
old=aliases.lower_storage('''          gaHero = objectId(gaI)
          gaHeroScore = gaScore''')
new=old+'\n'+aliases.lower_storage('''          backdoorGuardA = gaOx
          backdoorGuardB = gaOy''')
old='\n'.join('  '+x for x in old.splitlines());new='\n'.join('  '+x for x in new.splitlines())
assert parent.template.count(old)==1
CONTRACTS[OBSERVE]=replace(parent,template=parent.template.replace(old,new),
    meaning=parent.meaning+' Retain the selected currently observed hero coordinates '
        'for the focus controller, using branch-exclusive backdoorGuardA/B scratch.')

parent=CONTRACTS[v1.ATTACK]
old='''  attackTarget(bestId)
else
'''
new='''  if selfAttacksLanded > motionLastHits and selfClass <> 9 then
    mDirX = 0
    mDirY = 0
    if selfX >= backdoorGuardA then
      mDirX = 1
    else
      mDirX = -1
    end if
    if selfY >= backdoorGuardB then
      mDirY = 1
    else
      mDirY = -1
    end if
    mTryX = selfX + mDirX
    mTryY = selfY + mDirY
    if terrainWalkable(mTryX, mTryY) then
      kiteMoved = walkTo(mTryX, mTryY)
      if kiteMoved then
        motionActive = 1
      end if
    end if
  end if
  if motionActive = 0 then
    attackTarget(bestId)
  end if
  motionLastHits = selfAttacksLanded
  motionLastTick = worldTick
  motionLastHp = selfHp
else
'''
assert parent.template.count(old)==1
CONTRACTS[ATTACK]=replace(parent,template=parent.template.replace(old,new),
    meaning=parent.meaning+' V2 overrides direct-fire-only recovery: after a '
        'newly observed own basic hit, non-Berserkers issue one legal outward '
        'movement decision, then resume the same visible shared target on the '
        'next decision. Rejected movement falls back to attack. No recovery '
        'move is issued without a new hit, and no phantom hit is inferred from '
        'an attack command. Range and actual progress remain engine-verified. '
        'The observed Ranger nine-tick pattern motivates this combined change; '
        'it does not establish counter-policy efficacy.')
