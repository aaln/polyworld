"""Coached assault arbitration after full-game V1 behavior review.

Keep exposed outer objectives on the approach; perimeter probing starts only
when the selected objective is actually at the base. A positively supported
breach overrides distant hero chasing. Unassembled home defense regroups at
the threatened home approach instead of a remote centroid.
"""
from dataclasses import replace
from binding import CONTRACTS
from games.gods_of_the_arena.instruments.richard_coaching import contracts as v1

NAME='richard_coached_formation_v2'
parent=CONTRACTS[v1.NAME]
source=parent.template
old=v1.lower_storage('if gaBaseD <= 3600 then')
new=v1.lower_storage('if gaBaseD <= 3600 and (gaObjectiveX - 11) * (gaObjectiveX - 11) + (gaObjectiveY - 105) * (gaObjectiveY - 105) <= 1024 then')
assert source.count(old)==1
source=source.replace(old,new)
old=v1.lower_storage('''  if gaHero <> 0 then
    bestId = gaHero
    bestDistance = gaHeroScore
  else
    if gaPhase = 3 and gaObjectiveD <= 784 then
      bestId = gaObjective
      bestDistance = gaObjectiveD
    end if
  end if
else
  gaBreachUntil = 0
end if''')
new=v1.lower_storage('''  if gaPhase = 3 and gaObjectiveD <= 784 and (gaSpread or gaCover >= 2) then
    bestId = gaObjective
    bestDistance = gaObjectiveD
  else
    if gaHero <> 0 then
      bestId = gaHero
      bestDistance = gaHeroScore
    else
      if gaPhase = 3 and gaObjectiveD <= 784 then
        bestId = gaObjective
        bestDistance = gaObjectiveD
      end if
    end if
  end if
else
  gaBreachUntil = 0
  if gaEmergency then
    gaMoveX = (gaFrontX + 105) / 2
    gaMoveY = (gaFrontY + 11) / 2
  end if
end if''')
# MACRO is indented once inside the public red-phase guard.
old='\n'.join('  '+x for x in old.splitlines())
new='\n'.join('  '+x for x in new.splitlines())
assert source.count(old)==1
source=source.replace(old,new)
old=v1.lower_storage('if gaDx * gaDx + gaDy * gaDy > param_tether_radius * param_tether_radius then')
new=v1.lower_storage('if gaDx * gaDx + gaDy * gaDy > param_tether_radius * param_tether_radius and (gaEmergency = 0 or gaReady) then')
assert source.count(old)==1
source=source.replace(old,new)
CONTRACTS[NAME]=replace(parent,template=source,
    meaning=parent.meaning+' V2 supersedes phase/arbitration: exposed outer objectives '
    'are approached as a team before perimeter probing; the chosen exposed '
    'structure must be within32tiles of the enemy god to enter perimeter mode. '
    'When four ready allies have nearby creep support or positive observed enemy '
    'dispersion, commit to the shared exposed structure ahead of distant hero '
    'chasing. An unready team facing a home emergency gathers halfway between '
    'the observed front and friendly god; suppress remote-centroid tether during '
    'that rendezvous, while still disallowing unready objective assaults.')
