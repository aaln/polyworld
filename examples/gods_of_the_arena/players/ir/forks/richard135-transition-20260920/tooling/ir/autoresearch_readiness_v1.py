"""Versioned physical recovery arbitration at the first public level-up."""
from dataclasses import replace


def readiness(parent):
    old = '  if bestId <> 0 and selfClass <> param_plain_class then'
    new = old[:-5] + ' and (selfLevel >= 2 or (param_level_defense_only = 1 and defActive = 0)) then'
    assert parent.template.count(old) == 1
    return replace(parent, template=parent.template.replace(old, new, 1),
        parameters=parent.parameters | {'level_defense_only': (0, 0, 1)},
        meaning=parent.meaning + ' Additional dense recovery requires observed '
        'selfLevel >= 2, the first actual level-up. With level_defense_only=1, '
        'the level gate applies only while the inherited observed defense alarm '
        'is active; outside that alarm, recovery remains eligible at level1. '
        'Suppression falls through to the original selected-target attack. '
        'No change to sparse recovery, physical-class eligibility, targets, '
        'hit/tick memory, alarm detection, paths or equipment. No extra scans, '
        'private state, identity, opponent or seed conditions.')
