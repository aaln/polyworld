"""Visibility-complete group probe and earlier observed structure defense.

V1's audited Richard loss stopped after tower20: no exposed objective was
visible, so creep cover repeatedly committed to a default staging coordinate.
An absent target now means a coordinated forward scout, never a breach. A
visible lone structure attacker also warrants the gathered team's return.
"""
from dataclasses import replace
from binding import CONTRACTS
from games.gods_of_the_arena.instruments.richard_coaching import contracts as v1
from games.gods_of_the_arena.instruments.richard_coaching import contracts_v2 as v2

NAME = 'richard_coached_formation_v3'
parent = CONTRACTS[v2.NAME]
source = parent.template


def swap(old, new):
    global source
    old = v1.lower_storage(old)
    new = v1.lower_storage(new)
    old = '\n'.join('  ' + line for line in old.splitlines())
    new = '\n'.join('  ' + line for line in new.splitlines())
    assert source.count(old) == 1, old
    source = source.replace(old, new)


# Stable map geometry supplies a heading, not knowledge of an unseen enemy.
# Visible targets resume normal phase selection on the next decision. The
# discovery move still requires readiness and remains subject to the tether.
swap('''  if gaPhase = 3 and gaObjectiveD <= 784 and (gaSpread or gaCover >= 2) then''',
'''  if gaEmergency = 0 and gaObjective = 0 then
    gaPhase = 2
    gaMoveX = 11
    gaMoveY = 105
    gaBreachUntil = 0
  end if
  if gaPhase = 3 and gaObjectiveD <= 784 and (gaSpread or gaCover >= 2) then''')

# Enemy target IDs below100 are fixed map structures in this pinned release;
# the target is reported only for currently visible enemies. Do not call a
# remote hero threatening based only on its class or presumed policy.
swap('''      if gaD <= param_home_radius * param_home_radius then
        gaHomeThreats = gaHomeThreats + 1
      end if''',
'''      if gaD <= param_home_radius * param_home_radius then
        gaHomeThreats = gaHomeThreats + 1
        if objectTarget(gaI) > 0 and objectTarget(gaI) < 100 then
          gaHomeThreats = gaHomeThreats + 1
        end if
      end if''')

CONTRACTS[NAME] = replace(parent, template=source,
    meaning=parent.meaning + ' V3 visibility completion: if no exposed enemy '
    'objective is currently visible, a ready group moves toward the public '
    'enemy-base coordinate to obtain new vision; it does not commit to an '
    'absent target or remain at the old staging point. Local combat and the '
    'cohesion tether remain active. A visible enemy attacking a map structure '
    'within home_radius counts as two home threats, enabling a gathered '
    'interception before multiple enemies reach the god. This uses observed '
    'objectTarget and fixed structure IDs, never hidden enemy positions.')
