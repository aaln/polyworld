"""Cache the unchanged wave choice in the existing nondefense object pass."""
from dataclasses import replace
import re


RESET = '''waveCached = 1
waveChosen = 0
waveDistance = 2147483647
waveRetained = 0
waveHomeX = 64
waveHomeY = 64'''

ALLY = '''if objectHp(index) > 0 and objectAlive(index) then
  if objectKind(index) = 1 then
    waveHomeX = objectX(index)
    waveHomeY = objectY(index)
  end if
  if objectKind(index) = 3 then
    dx = objectX(index) - selfX
    dy = objectY(index) - selfY
    distance = dx * dx + dy * dy
    choose = 0
    if id = escortId then
      choose = 1
      waveRetained = 1
    end if
    if waveRetained = 0 then
      if distance < waveDistance or (distance = waveDistance and id < waveChosen) then
        choose = 1
      end if
    end if
    if choose then
      waveChosen = id
      waveDistance = distance
      waveX = objectX(index)
      waveY = objectY(index)
    end if
  end if
end if'''


def observe(parent):
    pattern = r'(?m)^( *)index = 0\n\1while index < objectCount\(\)\n(.*?)\n\1wend'
    matches=list(re.finditer(pattern,parent.template,re.S))
    assert len(matches)==4
    def replace_loop(m):
        indent=m[1];body=m[2].splitlines()
        assert body[0].strip()=='id = objectId(index)'
        assert body[-1].strip()=='index = index + 1'
        enemy='\n'.join(line[len(indent)+2:] for line in body[1:-1])
        enemy=enemy.replace(' and objectTeam(index) <> selfTeam','')
        lines=RESET.splitlines()+['index = 0','while index < objectCount()','  id = objectId(index)','  if objectTeam(index) <> selfTeam then']
        lines+=['    '+line for line in enemy.splitlines()]
        lines+=['  else']+['    '+line for line in ALLY.splitlines()]
        lines+=['  end if','  index = index + 1','wend']
        return '\n'.join(indent+line for line in lines)
    source=re.sub(pattern,replace_loop,parent.template,flags=re.S)
    return replace(parent,template='waveCached = 0\n'+source,
        writes=parent.writes+('waveCached','waveChosen','waveDistance','waveRetained','waveHomeX','waveHomeY','waveX','waveY'),
        meaning=parent.meaning+' In the existing nondefense object pass, cache '
        'the original nearest/retained friendly-creep wave selection in separate '
        'scratch. Enemy target selection is unchanged. Cache is reset each '
        'decision, follows identical alive/HP/team/tie predicates, and is '
        'consumed only by the paired fallback binding. No scan truncation.')


def fallback(parent):
    pattern=r'(?m)^( *)chosenId = 0\n\1chosenDistance = 2147483647\n\1retained = 0\n\1homeX = .*?\n\1homeY = .*?\n\1index = 0\n\1while index < objectCount\(\)\n.*?\n\1wend'
    assert len(list(re.finditer(pattern,parent.template,re.S)))==2
    copy='''chosenId = waveChosen
chosenDistance = waveDistance
retained = waveRetained
homeX = waveHomeX
homeY = waveHomeY
if chosenId <> 0 then
  escortX = waveX
  escortY = waveY
end if'''
    def use_cache(m):
        indent=m[1]
        lines=['if waveCached then']+['  '+line for line in copy.splitlines()]+['else']+['  '+line[len(indent):] for line in m[0].splitlines()]+['end if']
        return '\n'.join(indent+line for line in lines)
    source=re.sub(pattern,use_cache,parent.template,flags=re.S)
    return replace(parent,template=source,
        reads=parent.reads+('waveCached','waveChosen','waveDistance','waveRetained','waveHomeX','waveHomeY','waveX','waveY'),
        meaning=parent.meaning+' Use the paired observation cache when available '
        'instead of re-scanning the unchanged object view. If defense was '
        'released after observation and no cache was built, run the original '
        'scan. Preserve escort selection, stall tracking, terrain fallback '
        'and movement commands exactly; validate complete replay equivalence.')
