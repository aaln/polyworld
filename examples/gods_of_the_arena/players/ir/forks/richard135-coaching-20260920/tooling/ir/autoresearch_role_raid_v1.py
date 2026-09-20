"""Versioned role arbitration for newly recruited small-raid defenders."""
from dataclasses import replace


def sentry_raid(parent):
    token = '  raidNearer = 0\n'
    assert parent.template.count(token) == 1
    source = parent.template.replace(token,
        '  if defSentry = 0 then\n'
        '    pairedRush = 0\n'
        '  end if\n' + token, 1)
    return replace(parent, template=source,
        meaning=parent.meaning + ' Superseding small-pair eligibility: only the '
        'existing defSentry roles may newly activate this added alarm. All-ally '
        'geometric rank, distance and scoped duration remain unchanged. Ordinary '
        'larger-group alarms and remembered duties remain available to every '
        'class. If the nearest allies are attack roles, this gate may leave no '
        'new responder. No guarantee of defensive coverage or attack improvement.')
