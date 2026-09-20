"""Versioned hit-readiness override, without changing target arbitration."""
from dataclasses import replace

def hit_readiness(parent):
    token='selfLevel >= 2 or (param_level_defense_only = 1 and defActive = 0)'
    assert parent.template.count(token)==1
    source=parent.template.replace(token,'selfLevel >= 2 or (param_verified_hits > 0 and selfAttacksLanded >= param_verified_hits) or (param_level_defense_only = 1 and defActive = 0)',1)
    return replace(parent,template=source,parameters=parent.parameters|{'verified_hits':(0,0,64)},
        meaning=parent.meaning+' Superseding readiness only: positive verified_hits permits an '
        'otherwise eligible level1 physical hero after that many publicly observed lifetime '
        'basic hits. Zero disables this override. Lifetime hits persist across respawns and '
        'do not measure level, XP or safety. Preserve new-hit, consecutive living decision, '
        'cooldown, crowding, class, terrain, direction and command-acceptance checks. '
        'No target handoff override or new scan; no hidden inputs, rival labels or seed conditions.')
