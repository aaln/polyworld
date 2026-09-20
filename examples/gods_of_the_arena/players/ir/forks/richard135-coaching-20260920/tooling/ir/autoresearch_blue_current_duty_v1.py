"""Current shared-home ranking for additional blue defensive duty.

Versioned research contract. Previous admission contracts remain unchanged.
"""
from dataclasses import replace
from binding import CONTRACTS
import autoresearch_scoped_core_response_v3


def current_duty(parent):
    red, blue = parent.template.split('\nelse\n', 1)
    start = blue.index('    responseEligible = 0\n')
    end = blue.index('    if defAnchor <> 0 and (responseEligible or ', start)
    admission = blue[start:end]
    rank_start = admission.index('      responseDx = selfX - defAnchorX\n')
    rank_end = admission.index('      if responseRank < param_response_members then\n')
    rank = admission[rank_start:rank_end]
    # All living allies are public. A shared home point avoids observer-specific
    # nearest threatened anchors choosing incompatible defender sets.
    rank = '\n'.join(line[4:] for line in rank.rstrip().splitlines()) + '\n'
    rank = rank.replace('defAnchorX', 'defHomeX').replace('defAnchorY', 'defHomeY')
    admission = admission[:rank_start] + admission[rank_end:]
    blue = blue[:start] + admission + blue[end:]
    token = '  defCount = 0\n  defFront = 0\n'
    assert blue.count(token) == 1
    blue = blue.replace(token, rank + '''  if responseMode and responseRank >= param_response_members then
    responseUntil = 0
    responseMode = 0
    defUntil = 0
  end if
''' + token)
    return replace(
        parent,
        template=red+'\nelse\n'+blue,
        meaning=parent.meaning + ' CURRENT-DUTY REVISION: replace anchor-distance '
        'admission ranking with squared distance to the public friendly god, '
        'breaking ties by public hero ID. Recompute the saturated rank every '
        'decision, including decisions without a visible enemy. Before processing '
        'new alarms, clear responseMode, responseUntil and its defUntil when '
        'the hero is no longer among response_members closest living allies. '
        'No expiry or membership change infers hidden enemy death. Ordinary '
        'local defense remains available. Sequential observation changes can '
        'change rankings within a tick: measured per-decision assignment is the '
        'contract, not a claim about perfectly simultaneous decisions. Preserve '
        'all red statements, target selection, equipment and action skills.'
    )


name = 'lineup_blue_current_duty_v1'
value = current_duty(CONTRACTS['lineup_scoped_core_response_v3'])
if name in CONTRACTS and CONTRACTS[name] != value:
    raise ValueError('Conflicting current-duty V1 contract')
CONTRACTS[name] = value
