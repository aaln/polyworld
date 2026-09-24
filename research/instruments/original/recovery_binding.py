"""Weak-hero nearby-neutral income without speculative wave-pull movement."""
from dataclasses import replace
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
PARENT=ROOT/'examples/gods_of_the_arena/players/ir/forks/neutralfarm20260923-hosted/lane-neutral'
sys.path.insert(0,str(HERE.parent/'neutralfarm20260923'))
import camp_binding as parent
ir,host=parent.ir,parent.host
VERSION='gota-bassy/weak-neutral-income-2026-09-24-r1'

def configure():
    specs=dict(parent.configure())
    observe=specs['observe']
    t='weakFarm = 1\nif selfClass = Ranger or selfClass = Crossbowman then\n  weakFarm = 0\nend if\nnSearchRadius = 64\nif weakFarm = 1 then\n  nSearchRadius = 100\nend if\n'+observe.template
    assert t.count('nCampNumber < campCount() and distance <= 64')==1
    t=t.replace('nCampNumber < campCount() and distance <= 64','nCampNumber < campCount() and distance <= nSearchRadius')
    t=t.replace('if selfLevel >= 1 + (nTier - 1) * 3 then','nLevelNeeded = 1 + (nTier - 1) * 3\n            if weakFarm = 1 then\n              nLevelNeeded = 1 + (nTier - 1) * 4\n              if nTier = 2 then\n                nLevelNeeded = 6\n              end if\n            end if\n            if selfLevel >= nLevelNeeded then')
    specs['observe']=replace(observe,template=t,meaning=observe.meaning+' For non-Ranger/non-Crossbowman heroes, consider visible nonreturning camps within10tiles; require levels1/6/9 by tier. Ranged carry guards remain unchanged.')
    farm=specs['neutral_farm']
    t=farm.template
    # Existing carry behavior is byte-equivalent inside its branch. Weak heroes
    # deliberately damage a nearby mob instead of spending time baiting a wave.
    weak='''
if weakFarm = 1 then
  nPullStage = 0
  if stopped = 0 and retreat = 0 and towerAggro = 0 and enemyPower = 0 and selfRootTicks = 0 then
    if nCampId > 0 and recallCreepDistance > 36 then
      nFinishSafe = 0
      if selfHp * 10 >= selfMaxHp * 6 then
        nFinishSafe = 1
      end if
      if nCampHp <= selfAttackDamage * 2 and selfHp * 10 >= selfMaxHp * 4 then
        nFinishSafe = 1
      end if
      nCampPreferred = 0
      if bestId = 0 or bestKind = 1 or bestKind = 4 or bestKind = 5 then
        nCampPreferred = 1
      end if
      if bestDistance > 64 and nCampDistance < bestDistance then
        nCampPreferred = 1
      end if
      if nFinishSafe = 1 and nCampPreferred = 1 then
        bestId = nCampId
        bestKind = 6
        bestHp = nCampHp
        bestX = nCampX
        bestY = nCampY
        bestDistance = nCampDistance
      end if
    end if
  end if
else
'''
    specs['neutral_farm']=replace(farm,template=weak+t+'\nend if\n',meaning='Weak heroes (all except Ranger/Crossbowman) directly finish visible eligible-tier neutrals within10tiles when no hero is within10tiles, no tower targets self, no hostile lane creep is within6tiles, and health>=60percent (>=40percent for a two-basic finish). Prefer this income to structures or a farther unit beyond8tiles. Cancel speculative wave pulls for these heroes. Retain existing retreat/root guards, current spell/combat execution and carry behavior. Outcome hypothesis only until matched score and neutral-XP validation.')
    host.VERSION=ir.VERSION=VERSION
    host.CONTRACTS.clear();host.CONTRACTS.update({'weakneutral_'+k:v for k,v in specs.items()})
    return specs
