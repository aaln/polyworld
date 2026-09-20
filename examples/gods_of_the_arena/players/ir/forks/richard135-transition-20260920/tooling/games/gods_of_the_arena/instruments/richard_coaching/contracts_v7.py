"""Coordinate the observer and combat budgets, including medium-density scenes."""
from dataclasses import replace
from binding import CONTRACTS
from games.gods_of_the_arena.instruments.richard_coaching import contracts_v6

NAME='richard_formation_combat_v2_budget'
parent=CONTRACTS['richard_formation_combat_v1']
old='defMotionLimit = param_motion_object_limit'
new='defMotionLimit = param_motion_object_limit\n    if gaActive then\n      defMotionLimit = 64\n    end if'
assert parent.template.count(old)==1
CONTRACTS[NAME]=replace(parent,template=parent.template.replace(old,new),
    meaning=parent.meaning+' During the coached macro, the existing direct-attack '
    'density fast path activates above64visible objects instead of80. Shared '
    'macro targeting and cohesion still apply; expensive reactive micro is '
    'reserved for smaller scenes. Blue and pre-coaching decisions retain the '
    'original80object threshold. This closes the medium-density runtime peak '
    'that a240object dense fixture missed; test both sides of64and80 and the '
    'complete regression game, keeping the19000instruction local gate.')
