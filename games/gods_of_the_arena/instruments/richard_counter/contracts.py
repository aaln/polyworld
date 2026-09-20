"""Critical friendly-core pressure can supersede the ordinary local recall rule."""
from dataclasses import replace
from binding import CONTRACTS
from games.gods_of_the_arena.instruments.jordan268_counter import contracts as jordan_contracts


def register():
    parent = CONTRACTS['lineup_j268_both_local_recall']
    source = parent.template
    alarm = ('defFrontD <= param_critical_radius * param_critical_radius '
             'and defCount >= param_critical_group')
    token = 'if defAnchor <> 0 and ('
    assert source.count(token) == 2
    source = source.replace(token, token + '(' + alarm + ') or ')
    # Only a fresh, anchor-qualified public alarm starts/renews the commitment.
    for token in ('defUntil = worldTick + defHoldTicks',):
        assert source.count(token) == 2
        source = source.replace(token, token + '\n      if ' + alarm + ' then\n'
            '        criticalUntil = worldTick + param_critical_hold\n      end if')
    for radius in ('red_recall_radius', 'recall_radius'):
        token = f'if defDx * defDx + defDy * defDy > param_{radius} * param_{radius} then'
        assert source.count(token) == 1
        source = source.replace(token, token[:-5] + ' and worldTick >= criticalUntil then')
    name = 'lineup_critical_recall'
    new = replace(parent, template=source,
        parameters=parent.parameters | {'critical_radius': (40, 20, 80),
            'critical_group': (2, 1, 4), 'critical_hold': (1200, 240, 2400)},
        memory=parent.memory + ('criticalUntil',),
        meaning=parent.meaning + ' Superseding critical-defense exception on both teams: '
        'when the nearest visible living enemy hero is within critical_radius of the '
        'friendly god, at least critical_group living enemies occupy its existing '
        'cluster neighborhood, and a standing friendly structure anchors that threat, '
        'accept the ordinary defense alarm and permit remote recall for critical_hold '
        'ticks. Refresh only on that same observed context. During the remembered '
        'commitment do not apply the 28-tile remote cancellation; all target, movement, '
        'equipment and ordinary alarm semantics remain the parent behavior. Missing '
        'enemy observations do not mean enemy death. This exception is a testable '
        'response to dispersed core pressure, not opponent identity detection.')
    if name in CONTRACTS and CONTRACTS[name] != new:
        raise ValueError('Conflicting critical recall binding')
    CONTRACTS[name] = new


register()
