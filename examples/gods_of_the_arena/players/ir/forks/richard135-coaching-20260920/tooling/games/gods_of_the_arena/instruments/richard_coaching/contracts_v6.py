"""Reserve instruction headroom for the complete late-game cohort controller."""
from dataclasses import replace
from binding import CONTRACTS
from games.gods_of_the_arena.instruments.richard_coaching import contracts as v1
from games.gods_of_the_arena.instruments.richard_coaching import contracts_v5 as v5

NAME='richard_coached_formation_v6_bounded'
parent=CONTRACTS[v5.NAME]
source=parent.template
old=v1.lower_storage('while gaI < gaN and gaI < 160')
new=v1.lower_storage('while gaI < gaN and gaI < 128')
assert source.count(old)==1
source=source.replace(old,new)
old=v1.lower_storage('''    if objectKind(gaI) = 2 and objectTeam(gaI) = selfTeam and objectHp(gaI) > 0 then''')
new=v1.lower_storage('''    if objectKind(gaI) = 2 then
    if objectTeam(gaI) = selfTeam and objectHp(gaI) > 0 then''')
assert source.count(old)==1
source=source.replace(old,new)
old=v1.lower_storage('''    gaI = gaI + 1
  wend
  if gaEntryScore > param_group_radius * param_group_radius then''')
new=v1.lower_storage('''    end if
    gaI = gaI + 1
  wend
  if gaEntryScore > param_group_radius * param_group_radius then''')
old='\n'.join('  '+x for x in old.splitlines());new='\n'.join('  '+x for x in new.splitlines())
assert source.count(old)==1
source=source.replace(old,new)
CONTRACTS[NAME]=replace(parent,template=source,
    meaning=parent.meaning+' Bounded-cost revision: examine at most128objects in '
    'the detailed selection/cover pass, down from160; the pinned enumeration '
    'places all forts/buildings/heroes before creeps, so the reduction limits '
    'creep evidence while retaining all hero/structure observations. Skip team '
    'and HP getters for non-heroes in the cohort pass. Require native checks '
    'and complete local games below19000instructions before live comparison. '
    'The final candidate combines tick4800 timing with the V5 remembered '
    'return and all-class ordered equipment; this supersedes the V5 timing.')
