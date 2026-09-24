"""Blue lead ranged hero seeks central opportunities; versioned IR binding."""
from pathlib import Path
from dataclasses import replace
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PARENT = ROOT / 'examples/gods_of_the_arena/players/ir/forks/core-buyback20260923/core-buyback'
if (HERE.parent / 'adaptive20260922').exists():
    sys.path.insert(0, str(HERE.parent / 'adaptive20260922'))
import buyback_binding as parent
ir, host = parent.ir, parent.binding
VERSION = 'gota-bassy/blue-center-2026-09-23-r2'

def configure():
    specs = dict(parent.configure())
    old = specs['advance']
    marker = '  dx = selfX - goalX'
    assert old.template.count(marker) == 1
    source = old.template.replace(marker, '''  if selfTeam = 1 and ordinal = 0 then
    if selfClass = Ranger or selfClass = Crossbowman then
      goalX = mapWidth \\ 2
      goalY = mapHeight \\ 2
    end if
  end if
''' + marker)
    specs['advance'] = replace(old, template=source, meaning=old.meaning +
        ' Before crossing the route waypoint, blue public team ordinal zero on Ranger or Crossbowman uses the map center instead of the northwest outer corner. Existing target engagement, retreat, nearby defense, forward portal and post-waypoint advance still arbitrate normally. Other ordinals/classes and all red commands retain parent behavior. Earlier access to hero XP is a hypothesis, not an observed promise.')
    old = specs['base_recovery_intent']
    marker = 'retreat = 1'
    assert old.template.count(marker) == 1
    source = old.template.replace(marker, '''  if selfTeam = 1 and ordinal = 0 and retreat = 0 then
    if selfClass = Ranger or selfClass = Crossbowman then
      active = 1
      moveTick = worldTick
    end if
  end if
''' + marker)
    specs['base_recovery_intent'] = replace(old, template=source, meaning=old.meaning +
        ' For the blue lead ranged route, a newly critical hero already in the keep immediately triggers a decision and releases the movement throttle. This replaces a persisted outward advance with local recovery before leaving the keep; prevents the route/recovery handoff from wasting a town scroll. Other classes/ordinals and red retain the parent guard.')
    host.VERSION = ir.VERSION = VERSION
    host.CONTRACTS.clear()
    host.CONTRACTS.update({'bluecenter_' + key: value for key, value in specs.items()})
    return specs
