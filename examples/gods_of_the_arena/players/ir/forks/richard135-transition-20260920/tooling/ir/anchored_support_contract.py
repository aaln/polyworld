"""Distinguish a defended engagement from a passing ally's target."""
from dataclasses import replace
from hero_binding import CLASS_ID


def anchored_support(parent):
    token = 'if objectTarget(aaI) = defFront then'
    assert parent.template.count(token) == 1
    source = parent.template.replace(token,
        f'if objectTarget(aaI) = defFront and (param_frontline_only = 0 or objectClass(aaI) = {CLASS_ID["DeathKnight"]}) then', 1)
    token = 'if aaCommitted and selfHp * 100 >= selfMaxHp * 25 and (param_idle_only = 0 or bestId = 0) then'
    assert source.count(token) == 1
    source = source.replace(token, token[:-4] + ' and (param_anchor_required = 0 or defAnchor <> 0) then', 1)
    return replace(parent, template=source, parameters=parent.parameters | {
        'frontline_only': (1, 0, 1), 'anchor_required': (1, 0, 1)},
        meaning=parent.meaning +
        ' Qualify expanded idle-caster assistance using current public context. '
        'With frontline_only, the committing healthy nearby ally must be the actual '
        'red DeathKnight (global class5), so Crossbowman or another caster cannot '
        'trigger a cascading pursuit. With anchor_required, the leading enemy must '
        'currently have a standing friendly tower/core within the existing14tile '
        'defensive perimeter. That perimeter does not guarantee tower firing range. '
        'These restrictions apply only to expanded caster support; preserve existing '
        'targets, ordinary defense, emergency responses, recall, rally, pressure roles '
        'and all blue behavior. Do not infer survival or winning from earlier orders.')
