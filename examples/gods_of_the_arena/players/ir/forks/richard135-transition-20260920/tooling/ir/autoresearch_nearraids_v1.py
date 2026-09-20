"""Versioned distance bound on new damaged-tower pair recruitment."""
from dataclasses import replace


def nearby_raid(parent):
    token='    if raidNearer >= param_raid_responders then\n'
    assert parent.template.count(token)==1
    source=parent.template.replace(token,
        '    if raidSelfD > param_raid_response * param_raid_response then\n'
        '      pairedRush = 0\n'
        '    end if\n'+token,1)
    return replace(parent,template=source,
        parameters=parent.parameters|{'raid_response':(40,16,96)},
        meaning=parent.meaning+' Further restrict new small-raid recruitment to '
        'heroes whose current squared coordinate distance to the observed '
        'damaged tower is at most raid_response squared. This is a geometric '
        'availability bound, not path distance or predicted arrival. Original '
        'larger-group triggers, survivor refresh and existing commitments remain '
        'unchanged. Distance can reject a remote small-raid recruit but never '
        'cancels an already active defensive commitment.')
