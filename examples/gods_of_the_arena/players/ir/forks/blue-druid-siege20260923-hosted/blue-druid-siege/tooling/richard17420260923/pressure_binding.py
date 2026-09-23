"""Transfer observed structure pressure and siege retaliation into our current IR."""
from dataclasses import replace
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
PARENT=ROOT/'examples/gods_of_the_arena/players/ir/forks/druid-lane20260923-hosted/druid-lane'
sys.path.insert(0,str(HERE.parent/'druidlane20260923'))
import druid_binding as parent
ir,host=parent.ir,parent.host
VERSION='gota-bassy/guarded-siege-2026-09-23-r2'

def configure():
    specs=dict(parent.configure())
    old=specs['observe']
    source='''pressureTowerId = 0
pressureTowerDistance = 101
pressureAttackerId = 0
pressureAttackerHp = 2147483647
pressureChoice = 0
'''+old.template
    marker='        if distance <= 324 and objectAlive(idx) = 1 then'
    assert marker in source
    source=source.replace(marker,r'''        if kind = 4 and distance < pressureTowerDistance and objectAlive(idx) = 1 then
          pressureTarget = objectTarget(idx)
          if pressureTarget <> 0 and pressureTarget <> selfId then
            pressureTowerId = id
            pressureTowerDistance = distance
            pressureTowerHp = hp
            pressureTowerX = x
            pressureTowerY = y
          end if
        end if
        if kind = 2 and hp < pressureAttackerHp and objectAlive(idx) = 1 then
          pressureReach = selfAttackRange \ 1000
          if distance * 3600 <= pressureReach * pressureReach and objectTarget(idx) = selfId then
            pressureAttackerId = id
            pressureAttackerHp = hp
            pressureAttackerX = x
            pressureAttackerY = y
            pressureAttackerDistance = distance
          end if
        end if
'''+marker)
    specs['observe']=replace(old,template=source,meaning=old.meaning+' Cache the nearest exposed enemy tower within ten observation cells already targeting someone else, and the lowest-HP visible living enemy hero currently attacking self within basic reach. These are public observations, not opponent identity or private memory.')
    specs['guarded_siege']=host.contract('''
if stopped = 0 then
  if bestKind = 3 and bestHp > selfAttackDamage then
    if pressureTowerId > 0 and tanks > 0 and towerAggro = 0 then
      if selfHp * 100 >= selfMaxHp * 65 and enemyPower <= friendPower then
        bestId = pressureTowerId
        bestKind = 4
        bestHp = pressureTowerHp
        bestDistance = pressureTowerDistance
        bestX = pressureTowerX
        bestY = pressureTowerY
        pressureChoice = 1
      end if
    end if
  end if
  if bestKind = 4 and bestId > 0 and pressureAttackerId > 0 then
    bestId = pressureAttackerId
    bestKind = 2
    bestHp = pressureAttackerHp
    bestDistance = pressureAttackerDistance
    bestX = pressureAttackerX
    bestY = pressureAttackerY
    pressureChoice = 2
  end if
end if
''',{},(),(),(),
        'After recovery, portal and existing tower safety have retained priority, prefer a nearby exposed tower with another target and allied creep cover over a nonlethal creep when healthy and not outnumbered. Preserve available creep last hits, selected heroes, gods and retreat. During a selected tower assault, retarget the lowest-HP visible in-range hero attacking self. Update every target field so existing spell, range and attack logic agree. Re-evaluate every normal decision; do not latch a chase.',())
    order=list(specs);order.remove('guarded_siege');order.insert(order.index('xp_close'),'guarded_siege');specs={k:specs[k] for k in order}
    host.VERSION=ir.VERSION=VERSION
    host.CONTRACTS.clear();host.CONTRACTS.update({'siege_'+k:v for k,v in specs.items()})
    return specs
