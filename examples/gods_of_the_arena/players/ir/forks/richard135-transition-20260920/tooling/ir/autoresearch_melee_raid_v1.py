"""Versioned heavy-ranged-carry exemption from an added small-raid alarm."""
from dataclasses import replace
from hero_binding import CLASS_ID


def melee_raid(parent):
    token = '  raidNearer = 0\n'
    assert parent.template.count(token) == 1
    source = parent.template.replace(token,
        f'  if selfClass = {CLASS_ID["Crossbowman"]} then\n'
        '    pairedRush = 0\n'
        '  end if\n' + token, 1)
    return replace(parent, template=source,
        meaning=parent.meaning + ' Superseding small-pair eligibility: exempt '
        'Crossbowman from the added alarm; retain Berserker and the existing '
        'sentry classes. Preserve all-ally rank, geometric distance, scoped '
        'duration and original larger-group defense for every class. This '
        'preserves ordinary ranged-carry small-skirmish commands but may miss '
        'defense when that hero is the only available responder.')
