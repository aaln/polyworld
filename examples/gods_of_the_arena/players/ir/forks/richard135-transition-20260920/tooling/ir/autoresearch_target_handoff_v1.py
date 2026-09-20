"""Versioned nonhero attack handoff priority with optional public-hit readiness."""
from dataclasses import replace


def target_handoff(parent):
    source = parent.template
    token = '        if mTryX <> selfX or mTryY <> selfY then'
    assert source.count(token) == 1
    guard = '''        if mTracked and mKind <> 2 and bestId <> selfTarget then
          if mTryX <> selfX or mTryY <> selfY then
            mTryX = selfX
            mTryY = selfY
            handoffSkips = handoffSkips + 1
          end if
        end if
'''
    source = source.replace(token,guard+token,1)
    token = 'selfLevel >= 2 or (param_level_defense_only = 1 and defActive = 0)'
    assert source.count(token) == 1
    source = source.replace(token,'selfLevel >= 2 or (param_verified_hits > 0 and selfAttacksLanded >= param_verified_hits) or (param_level_defense_only = 1 and defActive = 0)',1)
    return replace(parent,template=source,
        parameters=parent.parameters | {'verified_hits':(0,0,64)},
        memory=parent.memory+('handoffSkips',),
        meaning=parent.meaning+' Superseding recovery arbitration: after the current '
        'selected-target direction guard, if a remaining movement intent refers to '
        'a selected nonhero whose bestId differs from public selfTarget, cancel that '
        'intent and fall through to attackTarget(bestId). Count this intent cancellation '
        'in handoffSkips; it is not proof that terrain would have accepted movement. '
        'Hero-to-hero target switches and recovery against the same current target '
        'retain the original rule. selfTarget is the current ordered or automatically '
        'acquired target, not a guaranteed last-hit victim. Superseding readiness: '
        'verified_hits0 keeps the original level gate; a positive value also permits '
        'an otherwise eligible physical hero after that many publicly observed lifetime '
        'basic hits, even at level1. Lifetime hits persist across respawns. Consecutive '
        'living decisions, a new hit, positive cooldown, density, class, terrain and '
        'command-acceptance checks still apply. No extra object scan, private rival '
        'information, opponent/seed branch, altered target ranking, equipment, alarm '
        'or sparse recovery. These priorities do not establish better damage or wins.')
