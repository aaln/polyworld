"""Separate a class-specific combat exception from the building-target hypothesis."""
from dataclasses import replace


def class_cadence(cadence):
    marker = 'if kiteTrigger = 0 and param_normal = 1 and bestId <> 0'
    assert cadence.template.count(marker) == 1
    return replace(cadence,
        template=cadence.template.replace(marker, marker + ' and selfClass <> param_plain_class'),
        parameters=cadence.parameters | {'plain_class': (9, 0, 9)},
        meaning=cadence.meaning + ' Disable normal post-hit recovery for plain_class; retain its ordinary '
        'attackTarget and automatic abilities. Other classes keep the parent controller. Optional emergency '
        'retreat remains separate (disabled in this experiment). This class exception needs fresh evidence.')


def class_building(contract, building, nearest):
    indent = lambda s: '\n'.join('  ' + line for line in s.splitlines())
    return contract('if selfClass = param_plain_class then\n' + indent(nearest.template) +
                    '\nelse\n' + indent(building.template) + '\nend if',
                    building.parameters | {'plain_class': (9, 0, 9)},
                    [], ['candidate'], [],
                    'For plain_class select the baseline nearest exposed enemy by center distance; '
                    'for every other class retain approximate building-edge targeting and declared weights. '
                    'Class routing is explicit and distinct from the combat recovery exception.')


def class_building_two(single):
    return replace(single,
        template=single.template.replace('if selfClass = param_plain_class then',
            'if selfClass = param_plain_class or selfClass = param_extra_class then'),
        parameters=single.parameters | {'extra_class': (7, 0, 9)},
        meaning='For plain_class and extra_class use baseline nearest-center targeting; '
        'retain approximate building-edge targeting for every other class. This operator '
        'does not change combat recovery: the attack skill controls that independently.')
