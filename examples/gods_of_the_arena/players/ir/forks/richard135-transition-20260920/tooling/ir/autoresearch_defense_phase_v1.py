"""Versioned physical recovery arbitration by observed defense pressure."""
from dataclasses import replace


def defense_phase(parent):
    old = '  if bestId <> 0 and selfClass <> param_plain_class then'
    new = old[:-5] + ' and (defActive = 0 or (param_dense_defense_ceiling > 0 and defCount <= param_dense_defense_ceiling)) then'
    assert parent.template.count(old) == 1
    return replace(parent, template=parent.template.replace(old, new, 1),
        parameters=parent.parameters | {'dense_defense_ceiling': (0, 0, 3)},
        meaning=parent.meaning + ' Additional dense recovery scope: when the inherited '
        'observed defense alarm is active, ceiling zero suppresses new recovery; a '
        'positive ceiling permits it only when the current observed defCount is at '
        'most that ceiling. All other decisions retain the physical recovery rule. '
        'Suppression falls through to the original selected-target attack. This '
        'does not alter alarm detection, persistence, navigation, class eligibility, '
        'sparse recovery, equipment, or hit/tick memory updates. No extra scans or '
        'private information. defCount is an observed local count, not total enemies.')
