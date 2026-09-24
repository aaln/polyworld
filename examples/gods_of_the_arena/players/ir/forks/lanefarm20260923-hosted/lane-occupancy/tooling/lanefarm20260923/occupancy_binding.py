"""One early lane choice from public allied commitment, with persistent routing."""
from dataclasses import replace
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PARENT = ROOT / 'examples/gods_of_the_arena/players/ir/forks/controltactics20260923-hosted/control-tactics'
sys.path.insert(0, str(HERE.parent / 'controltactics20260923'))
import tactics_binding as parent

ir, host = parent.ir, parent.host
VERSION = 'gota-bassy/lane-occupancy-2026-09-23-r61a'


def configure():
    specs = dict(parent.configure())
    old = specs['lifecycle']
    marker = '    lane = ordinal mod 3'
    assert old.template.count(marker) == 1
    specs['lifecycle'] = replace(old, template=old.template.replace(marker, marker + '''
    if laneDecisionStarted = 0 then
      laneDecisionStarted = 1
      laneDecisionStart = worldTick
    end if
    if laneAssigned = 1 then
      lane = laneStored
    end if'''), meaning=old.meaning + ' Start a single opening lane-decision window on first living activation; never restart it after death. Persist the selected lane across respawns.')
    old = specs['observe']
    marker = '      if team = selfTeam then'
    assert old.template.count(marker) == 1
    setup = '''laneCount0 = 0
laneCount1 = 0
laneCount2 = 0
laneKnown = 0
'''
    count = '''
        if laneAssigned = 0 and kind = 2 and id <> selfId and objectAlive(idx) = 1 then
          laneAx = x - homeX
          laneAy = y - homeY
          if laneAx * laneAx + laneAy * laneAy >= 144 then
            laneProjection = 0
            laneObserved = -1
            laneProbe = 0
            while laneProbe < 3
              lanePx = mapWidth \\ 2
              lanePy = mapHeight \\ 2
              if laneProbe = 0 then
                lanePx = mapWidth \\ 10
                lanePy = mapHeight \\ 10
              end if
              if laneProbe = 2 then
                lanePx = mapWidth * 9 \\ 10
                lanePy = mapHeight * 9 \\ 10
              end if
              laneVx = lanePx - homeX
              laneVy = lanePy - homeY
              laneDot = laneAx * laneVx + laneAy * laneVy
              laneNorm = laneVx * laneVx + laneVy * laneVy
              if laneDot > 0 and laneNorm > 0 then
                laneAlignment = laneDot / laneNorm * laneDot
                if laneAlignment > laneProjection then
                  laneProjection = laneAlignment
                  laneObserved = laneProbe
                end if
              end if
              laneProbe = laneProbe + 1
            wend
            if laneObserved = 0 then
              laneCount0 = laneCount0 + 1
            end if
            if laneObserved = 1 then
              laneCount1 = laneCount1 + 1
            end if
            if laneObserved = 2 then
              laneCount2 = laneCount2 + 1
            end if
            if laneObserved >= 0 then
              laneKnown = laneKnown + 1
            end if
          end if
        end if
'''
    specs['observe'] = replace(old, template=setup + old.template.replace(marker, marker + count),
        meaning=old.meaning + ' During the opening only, classify living allied heroes at least12tiles from home by maximum positive squared angular projection toward the three existing lane waypoints. Count each once in the same bounded scan. Allied positions are public even outside vision; heroes precede creeps. Near-home allies are uncommitted, not empty-lane evidence. This geometric lane intent is an estimate, not path or XP ground truth.')
    specs['choose_lane'] = host.contract('''
if laneAssigned = 0 then
  laneCurrent = lane
  if selfTeam = 1 and ordinal = 0 then
    if selfClass = Ranger or selfClass = Crossbowman then
      laneCurrent = 1
    end if
  end if
  if worldTick >= laneDecisionStart + tickRate * 12 and worldTick <= laneDecisionStart + tickRate * 35 then
    if laneKnown >= 2 and retreat = 0 and selfHp * 2 >= selfMaxHp then
      if threatDistance > 100 and bestDistance > 144 then
        laneCurrentCount = laneCount1
        if laneCurrent = 0 then
          laneCurrentCount = laneCount0
        end if
        if laneCurrent = 2 then
          laneCurrentCount = laneCount2
        end if
        laneChoice = laneCurrent
        laneChoiceCount = laneCurrentCount
        laneChoiceTravel = 1000000
        laneProbe = 0
        while laneProbe < 3
          laneN = laneCount1
          lanePx = mapWidth \\ 2
          lanePy = mapHeight \\ 2
          if laneProbe = 0 then
            laneN = laneCount0
            lanePx = mapWidth \\ 10
            lanePy = mapHeight \\ 10
          end if
          if laneProbe = 2 then
            laneN = laneCount2
            lanePx = mapWidth * 9 \\ 10
            lanePy = mapHeight * 9 \\ 10
          end if
          laneTravel = (selfX - lanePx) * (selfX - lanePx) + (selfY - lanePy) * (selfY - lanePy)
          if laneN < laneCurrentCount then
            if laneN < laneChoiceCount or (laneN = laneChoiceCount and laneTravel < laneChoiceTravel) then
              laneChoice = laneProbe
              laneChoiceCount = laneN
              laneChoiceTravel = laneTravel
            end if
          end if
          laneProbe = laneProbe + 1
        wend
        if laneChoice <> laneCurrent then
          lane = laneChoice
          laneStored = lane
          laneAssigned = 1
          laneChanged = 1
          crossed = 0
          moveTick = worldTick
          forwardScore = 1000000
        end if
      end if
    end if
  end if
  if laneAssigned = 0 and worldTick >= laneDecisionStart + tickRate * 35 then
    laneAssigned = 1
    laneStored = lane
  end if
end if
''', {}, (), (), (),
        'Between12and35seconds after first activation, change once to a strictly less allied-crowded lane after at leasttwo allies have visibly departed home. Preserve current lane on occupancy ties; among strictly better lanes prefer fewer allies then shorter straight-line waypoint distance. Require at least50percent HP, no retreat and no enemy within10tiles or selected target within12tiles. Reset crossed/move clock and invalidate old forward portal anchor for this frame. Store route across lives. At35seconds close the window without changing baseline routing if no safe improvement was observed. All outcomes are judged by individual XP-minus-time.', ())
    old = specs['advance']
    marker = 'if selfTeam = 1 and ordinal = 0 then'
    assert old.template.count(marker) == 1
    specs['advance'] = replace(old, template=old.template.replace(marker, 'if selfTeam = 1 and ordinal = 0 and laneChanged = 0 then'),
        meaning=old.meaning + ' Honor explicit occupancy-based lane choice instead of overriding it with the blue first-seat ranged center route. Preserve that center override when no actual adaptive change occurs.')
    order = [k for k in specs if k != 'choose_lane']
    order.insert(order.index('lane_recovery'), 'choose_lane')
    specs = {k: specs[k] for k in order}
    host.VERSION = ir.VERSION = VERSION
    host.CONTRACTS.clear()
    host.CONTRACTS.update({'lanefarm_' + k: v for k, v in specs.items()})
    return specs
