"""Versioned mana purchase threshold; old sustain contracts remain unchanged."""
from dataclasses import replace


def aligned_purchase(parent):
    token = 'selfMana * 2 < selfMaxMana'
    assert parent.template.count(token) == 1
    return replace(parent,
        template=parent.template.replace(token, 'selfMana * 5 < selfMaxMana * 2', 1),
        meaning=parent.meaning + ' Superseding mana purchase condition: require '
        'starting mana strictly below40%, matching the unchanged consume threshold. '
        'Healing, gold checks, inventory presence and execution order are unchanged. '
        'Regeneration or death can still strand a purchased potion. Fewer purchases '
        'and improved equipment or fort wins are hypotheses, not guarantees.')
