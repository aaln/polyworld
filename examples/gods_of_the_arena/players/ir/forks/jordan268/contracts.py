"""Additive native IR bindings for the isolated Jordan268 experiment.

Import after selecting the pinned primary compiler; no existing contract changes.
"""
from dataclasses import replace

from binding import CONTRACTS


def register():
    parent = CONTRACTS['lineup_perimeter_route']
    opening = '''if selfTeam = 1 and worldTick <= param_assembly_ticks and defActive = 0 then
  moveAccepted = walkTo(param_assembly_x, param_assembly_y)
else
'''
    source = opening + '\n'.join('  ' + line for line in parent.template.splitlines()) + '\nend if'
    assembled = replace(
        parent, template=source,
        parameters=parent.parameters | {'assembly_ticks': (1200, 240, 2400),
                                       'assembly_x': (91, 1, 114),
                                       'assembly_y': (104, 1, 114)},
        meaning='Opening formation on blue: for assembly_ticks, when the caller has no '
        'combat target or motion action and no active defense, walk toward the authored '
        'public-map assembly coordinates instead of selecting separate creep escorts. '
        'All five classes share the rally. A current defense alarm retains its existing '
        'route and combat always takes precedence. After the deadline resume the parent '
        'route. This is an opponent-specific opening hypothesis, not hidden enemy tracking. '
        'Red behavior is exactly the parent route. Parent: ' + parent.meaning)
    name = 'lineup_j268_opening_assembly'
    if name in CONTRACTS and CONTRACTS[name] != assembled:
        raise ValueError('Conflicting opening assembly binding')
    CONTRACTS[name] = assembled

    parent = CONTRACTS['lineup_paired_legacy']
    red, blue = parent.template.split('\nelse\n', 1)
    gate = '\n  if defActive then\n'
    assert blue.count(gate) == 1
    release = '''
  if selfTeam = 1 then
    defDx = selfX - defHomeX
    defDy = selfY - defHomeY
    if defDx * defDx + defDy * defDy > param_recall_radius * param_recall_radius then
      defActive = 0
      defUntil = 0
      backdoorUntil = 0
      backdoorActive = 0
    end if
  end if
'''
    counterrace = replace(parent, template=red + '\nelse\n' + blue.replace(gate, release + gate, 1),
        parameters=parent.parameters | {'recall_radius': (28, 14, 48)},
        meaning=parent.meaning + ' Superseding blue remote recall: a hero farther than '
        'recall_radius integer tiles from its own god clears active defense and solo '
        'backdoor commitment before target selection. That hero executes the existing '
        'ordinary offensive targeting and creep escort; heroes within the radius retain '
        'all prior defense logic, including local god protection. Red is unchanged. '
        'This tests counterpressure against Jordan268 hero contact, not a claim that '
        'abandoning remote defense is generally safe. The decision uses own position '
        'and the public friendly god location, never hidden enemies.')
    name = 'lineup_j268_local_recall'
    if name in CONTRACTS and CONTRACTS[name] != counterrace:
        raise ValueError('Conflicting local recall binding')
    CONTRACTS[name] = counterrace

    parent = counterrace
    red, blue = parent.template.split('\nelse\n', 1)
    assert red.count(gate) == 1
    release_red = '''
  defDx = selfX - defHomeX
  defDy = selfY - defHomeY
  if defDx * defDx + defDy * defDy > param_red_recall_radius * param_red_recall_radius then
    defActive = 0
    defUntil = 0
  end if
'''
    redrace = replace(parent, template=red.replace(gate, release_red + gate, 1) + '\nelse\n' + blue,
        parameters=parent.parameters | {'red_recall_radius': (28, 14, 48)},
        meaning=parent.meaning + ' Red also declines remote group recall: beyond '
        'red_recall_radius from its friendly god, clear active defense and its deadline '
        'before choosing ordinary targets. Nearby heroes keep the original red defense. '
        'This preserves distant offensive groups, testing the same counterpressure '
        'hypothesis with different fixed classes. Blue execution is unchanged.')
    name = 'lineup_j268_both_local_recall'
    if name in CONTRACTS and CONTRACTS[name] != redrace:
        raise ValueError('Conflicting red local recall binding')
    CONTRACTS[name] = redrace


register()
