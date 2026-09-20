"""Versioned equivalent mobile distance work reduction; no target changes."""
from dataclasses import replace
from binding import CONTRACTS
import autoresearch_middle_transit_v3

OLD = '''dx = objectX(index) - selfX
dy = objectY(index) - selfY
if dx < 0 then
  dx = -dx
end if
if dy < 0 then
  dy = -dy
end if
buildingInset = 0
buildingWeight = PARAMunit_weight
if objectKind(index) = 4 or objectKind(index) = 5 then
  buildingInset = PARAMedge_tiles
  buildingWeight = PARAMbuilding_weight
end if
if objectKind(index) = 1 then
  buildingInset = PARAMfort_tiles
  buildingWeight = PARAMbuilding_weight
end if
dx = dx - buildingInset
dy = dy - buildingInset
if dx < 0 then
  dx = 0
end if
if dy < 0 then
  dy = 0
end if
distance = (dx * dx + dy * dy) * buildingWeight'''

NEW = '''dx = objectX(index) - selfX
dy = objectY(index) - selfY
distanceKind = objectKind(index)
if distanceKind = 1 or distanceKind = 4 or distanceKind = 5 then
  if dx < 0 then
    dx = -dx
  end if
  if dy < 0 then
    dy = -dy
  end if
  buildingInset = PARAMedge_tiles
  if distanceKind = 1 then
    buildingInset = PARAMfort_tiles
  end if
  dx = dx - buildingInset
  dy = dy - buildingInset
  if dx < 0 then
    dx = 0
  end if
  if dy < 0 then
    dy = 0
  end if
  distance = (dx * dx + dy * dy) * PARAMbuilding_weight
else
  distance = (dx * dx + dy * dy) * PARAMunit_weight
end if'''

def compact(parent):
    source = parent.template
    for prefix in ['param_redbranch_', 'param_']:
        old='\n'.join('            '+s for s in OLD.replace('PARAM',prefix).splitlines())
        new='\n'.join('            '+s for s in NEW.replace('PARAM',prefix).splitlines())
        assert source.count(old)==1
        source=source.replace(old,new)
    return replace(parent,template=source,
        meaning=parent.meaning+' Equivalent target-distance arithmetic: for mobile '
        'objects with zero footprint inset, square signed displacements directly; '
        'for god, tower and barracks preserve absolute displacement, footprint '
        'inset and zero clamp. Preserve all configured weights and strict-distance '
        'tie ordering. No scan truncation, observation or command changes. '
        'Native differential and complete replay equivalence are mandatory.')

name='lineup_deployed_cached_v4'
value=compact(CONTRACTS['lineup_deployed_cached_v3'])
if name in CONTRACTS and CONTRACTS[name]!=value: raise ValueError('Conflicting transit V4 contract')
CONTRACTS[name]=value
