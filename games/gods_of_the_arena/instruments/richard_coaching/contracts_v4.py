"""Preserve a four-hero cohort when the fifth ally is far away."""
from dataclasses import replace
from binding import CONTRACTS
from games.gods_of_the_arena.instruments.richard_coaching import contracts as v1
from games.gods_of_the_arena.instruments.richard_coaching import contracts_v3 as v3

NAME='richard_coached_formation_v4'
parent=CONTRACTS[v3.NAME]
source=parent.template


def swap(old,new):
    global source
    old='\n'.join('  '+x for x in v1.lower_storage(old).splitlines())
    new='\n'.join('  '+x for x in v1.lower_storage(new).splitlines())
    assert source.count(old)==1,old
    source=source.replace(old,new)


# Only forts and heroes contribute to the initial team/threat census. Avoid
# fetching four irrelevant properties for each creep; this funds the bounded
# cohort pass inside the real VM budget.
swap('''  gaKind = objectKind(gaI)
  gaTeam = objectTeam(gaI)
  gaHp = objectHp(gaI)
  gaOx = objectX(gaI)''',
'''  gaKind = objectKind(gaI)
  if gaKind = 1 or gaKind = 2 then
  gaTeam = objectTeam(gaI)
  gaHp = objectHp(gaI)
  gaOx = objectX(gaI)''')
swap('''  gaI = gaI + 1
wend
if gaAlive > 0 then''',
'''  end if
  gaI = gaI + 1
wend
if gaAlive > 0 then''')
swap('''gaNear = 0
gaHero = 0''',
'''if gaAlive = 5 then
  gaEntryScore = 0
  gaNavX = gaX
  gaNavY = gaY
  gaI = 0
  while gaI < gaN and gaI < 64
    if objectKind(gaI) = 2 and objectTeam(gaI) = selfTeam and objectHp(gaI) > 0 then
      gaOx = objectX(gaI)
      gaOy = objectY(gaI)
      gaD = (gaOx - gaX) * (gaOx - gaX) + (gaOy - gaY) * (gaOy - gaY)
      if gaD > gaEntryScore then
        gaEntryScore = gaD
        gaNavX = gaOx
        gaNavY = gaOy
      end if
    end if
    gaI = gaI + 1
  wend
  if gaEntryScore > param_group_radius * param_group_radius then
    gaX = (gaX * 5 - gaNavX) / 4
    gaY = (gaY * 5 - gaNavY) / 4
  end if
end if
gaNear = 0
gaHero = 0''')

CONTRACTS[NAME]=replace(parent,template=source,
    meaning=parent.meaning+' V4 cohort center: when five allies are alive and '
    'one lies outside the group radius from the team mean, remove the farthest '
    'ally from the centroid calculation. Readiness still independently requires '
    'four healthy allies within group_radius of that center; scattered teams '
    'remain unready. The outlier follows the same tether back to the group. '
    'The initial census ignores creep properties, preserving the VM budget. '
    'The evaluated candidate delays the whole macro until tick4800 to preserve '
    'early and middle laning, matching the coach late-game qualification.')
