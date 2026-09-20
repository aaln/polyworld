"""Remember observed home pressure through temporary visibility gaps."""
from dataclasses import replace
from binding import CONTRACTS
from games.gods_of_the_arena.instruments.richard_coaching import contracts as v1
from games.gods_of_the_arena.instruments.richard_coaching import contracts_v4 as v4

NAME='richard_coached_formation_v5'
parent=CONTRACTS[v4.NAME]
source=parent.template


def swap(old,new):
    global source
    old='\n'.join('  '+x for x in v1.lower_storage(old).splitlines())
    new='\n'.join('  '+x for x in v1.lower_storage(new).splitlines())
    assert source.count(old)==1,old
    source=source.replace(old,new)


swap('defUntil = 0\nbestId = 0','bestId = 0')
swap('''gaEmergency = 0
if gaHomeThreats >= 2 or gaHomeHp < 400 then
  gaEmergency = 1
end if
if worldTick <= gaLastTick or worldTick > gaLastTick + 1 then
  gaEntryUntil = 0
  gaProbeSince = 0
  gaBreachUntil = 0
end if''',
'''if worldTick <= gaLastTick or worldTick > gaLastTick + 1 then
  gaEntryUntil = 0
  gaProbeSince = 0
  gaBreachUntil = 0
  defUntil = 0
end if
if gaHomeThreats >= 2 or gaHomeHp < 400 then
  defUntil = worldTick + param_home_commit_ticks
  defThreatX = gaFrontX
  defThreatY = gaFrontY
end if
gaEmergency = 0
if worldTick < defUntil then
  gaEmergency = 1
  gaFrontX = defThreatX
  gaFrontY = defThreatY
end if''')
swap('''gaDx = selfX - gaX
gaDy = selfY - gaY''',
'''if gaEmergency and (gaX - gaFrontX) * (gaX - gaFrontX) + (gaY - gaFrontY) * (gaY - gaFrontY) > 784 then
  bestId = 0
end if
gaDx = selfX - gaX
gaDy = selfY - gaY''')
CONTRACTS[NAME]=replace(parent,template=source,
    parameters=parent.parameters|{'home_commit_ticks':(1200,480,1800)},
    memory=tuple(dict.fromkeys(parent.memory+('defUntil','defThreatX','defThreatY'))),
    meaning=parent.meaning+' V5 home-pressure belief: positive observed home '
    'pressure stores the last visible threat coordinate and a1200tick deadline. '
    'Temporary loss of vision does not cancel the team return. Expiry or a '
    'decision discontinuity clears it; subsequent positive sightings refresh '
    'the deadline and coordinate. While the group is farther than28tiles from '
    'that remembered front, home transit suppresses all attack pursuit. Once '
    'nearby, normal observed shared targeting resumes. Remembered positions '
    'are used for navigation only, never attacks on invisible entities. The '
    'evaluated candidate begins at2400; the4800 timing in the V4 experiment is '
    'not retained in this candidate because the home threat precedes it.')
