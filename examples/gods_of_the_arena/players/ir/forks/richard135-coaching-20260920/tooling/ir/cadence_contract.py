"""Separate short post-hit recovery steps from sustained danger retreats."""
from dataclasses import replace


def cadence_contract(motion):
    source = motion.template
    marker = 'motionUntil = worldTick + param_max_ticks'
    assert source.count(marker) == 1
    source = source.replace(marker, marker + '''
    if kiteTrigger = 1 then
      motionUntil = worldTick + param_recovery_ticks
      recoverySteps = recoverySteps + 1
    end if''')
    marker = 'if selfClass = 1 or selfClass = 2 or selfClass = 3 or selfClass = 6 or selfClass = 7 or selfClass = 8 then'
    assert source.count(marker) == 1
    source = source.replace(marker, marker.replace('if ', 'if param_all_classes = 1 or ', 1))
    parameters = motion.parameters | {'recovery_ticks': (1, 1, 8), 'all_classes': (0, 0, 1)}
    return replace(motion, template=source, parameters=parameters,
                   memory=motion.memory + ('recoverySteps',),
                   meaning='After a newly observed basic hit, issue a short terrain-checked movement order '
                   'for recovery_ticks before resuming attack. Optionally include melee classes. This '
                   'attempts to shorten attack recovery; brief commands may only turn and are not effective '
                   'kiting by themselves. Independently, configured recent-damage/low-HP danger triggers '
                   'retain the full min_ticks/max_ticks separation-based retreat. Preserve the parent '
                   'controller\'s destination selection, failed-move attack fallback, explicit offensive '
                   'spell attempt, respawn-event reset and no-target arbitration. Source-derived cadence '
                   'benefit is not a guarantee of damage, survival or wins.')
