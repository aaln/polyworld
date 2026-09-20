"""Equivalent compact wave choice; no altered eligibility, ranking or scan scope."""
from dataclasses import replace
import re
from binding import CONTRACTS
from autoresearch_fused_wave_work_v1 import ALLY
import autoresearch_middle_transit_v2

COMPACT = '''if objectHp(index) > 0 and objectAlive(index) then
  if objectKind(index) = 1 then
    waveHomeX = objectX(index)
    waveHomeY = objectY(index)
  end if
  if objectKind(index) = 3 then
    if id = escortId then
      waveRetained = 1
      waveChosen = id
      waveX = objectX(index)
      waveY = objectY(index)
      dx = waveX - selfX
      dy = waveY - selfY
      waveDistance = dx * dx + dy * dy
    else
      if waveRetained = 0 then
        dx = objectX(index) - selfX
        dy = objectY(index) - selfY
        distance = dx * dx + dy * dy
        if distance < waveDistance or (distance = waveDistance and id < waveChosen) then
          waveChosen = id
          waveDistance = distance
          waveX = objectX(index)
          waveY = objectY(index)
        end if
      end if
    end if
  end if
end if'''

def compact(parent):
    source=parent.template
    matches=list(re.finditer(r'(?m)^( *)if objectHp\(index\) > 0 and objectAlive\(index\) then\n',source))
    assert len(matches)==4
    for m in reversed(matches):
        old='\n'.join(m[1]+line for line in ALLY.splitlines())
        assert source[m.start():].startswith(old)
        new='\n'.join(m[1]+line for line in COMPACT.splitlines())
        source=source[:m.start()]+new+source[m.start()+len(old):]
    return replace(parent,template=source,
        meaning=parent.meaning+' Equivalent compact escort selection: a live '
        'retained ID wins immediately and stops distance work for later nonretained '
        'creeps; otherwise compare exact squared distance with the same lower-ID tie '
        'break. Eliminate choose scratch only; eligibility, selected coordinates, '
        'distance, retained flag and friendly god observation remain identical. '
        'No object truncation or altered target ranking. Differential fixtures and '
        'complete command/state equivalence are required.')

name='lineup_deployed_cached_v3'
value=compact(CONTRACTS['lineup_deployed_cached_v2'])
if name in CONTRACTS and CONTRACTS[name]!=value:raise ValueError('Conflicting transit V3 contract')
CONTRACTS[name]=value
