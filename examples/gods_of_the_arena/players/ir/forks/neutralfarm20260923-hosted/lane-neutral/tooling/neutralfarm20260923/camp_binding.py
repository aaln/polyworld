"""Visible neutral fallback and bounded camp-to-wave pulling on release62."""
from dataclasses import replace
from copy import deepcopy
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PARENT = ROOT / 'examples/gods_of_the_arena/players/ir/forks/lanefarm20260923-hosted/lane-occupancy'
sys.path.insert(0, str(HERE.parent/'lanefarm20260923'))
import occupancy_binding as parent
ir, host = parent.ir, parent.host
VERSION = 'gota-bassy/lane-neutral-farming-2026-09-23-r62b'


def configure():
    specs = dict(parent.configure())
    old = specs['lifecycle']
    specs['lifecycle'] = replace(old, template=old.template.replace('    initialized = 0', '    initialized = 0\n    nPullStage = 0'),
        meaning=old.meaning+' Death cancels any neutral pull; camp IDs are not treated as permanent mob identities.')
    old = specs['observe']
    setup = '''nCampId = 0
nCampScore = -1000000
nWaveId = 0
nWaveDistance = 1000000
nWaveCount = 0
nOnUs = 0
nHandoff = 0
'''
    ally = '''
        if kind = 3 and distance <= 100 then
          nWaveCount = nWaveCount + 1
          if nPullStage > 0 and objectTarget(idx) = nPullMob then
            nHandoff = 1
          end if
          if objectTarget(idx) = 0 then
            nWaveDx = x - selfX
            nWaveDy = y - selfY
            if nPullStage > 0 then
              nWaveDx = x - nPullCenterX
              nWaveDy = y - nPullCenterY
            end if
            nWaveGap = nWaveDx * nWaveDx + nWaveDy * nWaveDy
            if nWaveGap < nWaveDistance then
              nWaveDistance = nWaveGap
              nWaveId = id
              nWaveX = x
              nWaveY = y
            end if
          end if
        end if
'''
    neutral = '''
        if kind = 6 and objectReturning(idx) = 0 and objectAlive(idx) = 1 then
          nCampNumber = objectCamp(idx)
          if nPullStage > 0 and nCampNumber = nPullCamp then
            nLastSeen = worldTick
            if objectTarget(idx) = selfId then
              nOnUs = 1
            end if
            if objectTarget(idx) <> 0 and objectTarget(idx) <> selfId then
              nHandoff = 1
            end if
          end if
          if nCampNumber >= 0 and nCampNumber < campCount() and distance <= 64 then
            nTier = campTier(nCampNumber)
            if selfLevel >= 1 + (nTier - 1) * 3 then
              nValue = 1000 - distance * 4 - hp
              if id = selfTarget then
                nValue = nValue + 100
              end if
              if nValue > nCampScore then
                nCampScore = nValue
                nCampId = id
                nCampHp = hp
                nCampX = x
                nCampY = y
                nCampDistance = distance
                nChosenCamp = nCampNumber
                nCampTarget = objectTarget(idx)
              end if
            end if
          end if
        end if
'''
    marker = '      if team = selfTeam then'
    enemy = '        if kind = 1 then\n          enemyX = x'
    target = 'if distance <= 324 and objectAlive(idx) = 1 then'
    assert all(old.template.count(x) == 1 for x in [marker, enemy, target])
    template = setup+old.template.replace(marker, marker+ally).replace(enemy, neutral+enemy).replace(target, 'if kind <> 6 and distance <= 324 and objectAlive(idx) = 1 then')
    specs['observe'] = replace(old, template=template,
        meaning=old.meaning+' Recognize visible neutral kind6/faction2 separately; returning mobs are immune and never selected. Retain lane/hero target priority. In the same96object scan, remember a nearby eligible-tier neutral, nearby allied creeps and idle wave coordinates. Active pulls track visible camp targets and release when another actor takes aggro. Static camp geometry is public; no hidden spawn/life state is inferred.')
    specs['neutral_farm'] = host.contract('''
if nPullStage > 0 then
  if stopped = 1 or retreat = 1 or selfHp * 2 < selfMaxHp or selfRootTicks > 0 then
    nPullStage = 0
    nPullReady = worldTick + tickRate * 20
  end if
end if
if stopped = 0 then
  nSafe = 0
  if retreat = 0 and towerAggro = 0 and enemyPower = 0 and selfRootTicks = 0 then
    if selfHp * 2 >= selfMaxHp and (bestId = 0 or bestKind = 1 or bestKind = 4 or bestKind = 5) then
      nSafe = 1
    end if
  end if
  if nPullStage > 0 then
    if nSafe = 0 or worldTick >= nPullUntil or worldTick - nLastSeen > tickRate * 2 or nHandoff = 1 then
      nPullStage = 0
      nPullReady = worldTick + tickRate * 20
    end if
  end if
  if nPullStage = 0 and nSafe = 1 and nCampId > 0 and nWaveId > 0 and nWaveCount >= 2 then
    if worldTick >= nPullReady and selfHp * 10 >= selfMaxHp * 7 and nCampTarget = 0 then
      nCx = campX(nChosenCamp)
      nCy = campY(nChosenCamp)
      nDx = nWaveX - nCx
      nDy = nWaveY - nCy
      nGap = nDx * nDx + nDy * nDy
      if nGap >= 16 and nGap <= 81 then
        nPullStage = 1
        nPullCamp = nChosenCamp
        nPullMob = nCampId
        nPullX = nCampX
        nPullY = nCampY
        nPullCenterX = nCx
        nPullCenterY = nCy
        nPullUntil = worldTick + tickRate * 15
        nLastSeen = worldTick
      end if
    end if
  end if
  if nPullStage > 0 then
    if nWaveId = 0 or nWaveCount < 2 then
      nPullStage = 0
      nPullReady = worldTick + tickRate * 20
    else
      if nOnUs = 1 then
        nPullStage = 2
      end if
      nGoalX = nPullX
      nGoalY = nPullY
      if nPullStage = 2 then
        nGoalX = nWaveX
        nGoalY = nWaveY
        nDx = nGoalX - nPullCenterX
        nDy = nGoalY - nPullCenterY
        if nDx * nDx >= nDy * nDy then
          if nDx >= 0 then
            nGoalX = nGoalX + 2
          else
            nGoalX = nGoalX - 2
          end if
        else
          if nDy >= 0 then
            nGoalY = nGoalY + 2
          else
            nGoalY = nGoalY - 2
          end if
        end if
      end if
      nDx = nGoalX - nPullCenterX
      nDy = nGoalY - nPullCenterY
      if nDx * nDx + nDy * nDy <= 100 then
        if walkTo(nGoalX, nGoalY) = 1 then
          stopped = 1
        else
          nPullStage = 0
          nPullReady = worldTick + tickRate * 20
        end if
      else
        nPullStage = 0
        nPullReady = worldTick + tickRate * 20
      end if
    end if
  end if
  if stopped = 0 and nSafe = 1 and nCampId > 0 and selfHp * 10 >= selfMaxHp * 7 then
    bestId = nCampId
    bestKind = 6
    bestHp = nCampHp
    bestX = nCampX
    bestY = nCampY
    bestDistance = nCampDistance
  end if
end if
''', {}, (), (), ('walkTo',),
        'Prefer existing visible lane/hero combat. When safe, >=70percent HP and sufficient tier level, farm a nearby visible nonreturning neutral instead of an empty route or structure target. If two nearby allied creeps and an idle wave4to9tiles from camp are present, walk into aggro then two tiles beyond the wave, keeping goal within10tiles of camp versus12tile leash. Stop on handoff, lost wave/sight, danger, root, <50percent HP, invalid route or15second timeout; retry after20seconds. Claim stopped only for an accepted walk, suppressing the later combat spell/item loop while baiting. No hidden camp state, teammate identities or private XP are used.', ())
    order = [k for k in specs if k != 'neutral_farm']
    order.insert(order.index('xp_close'), 'neutral_farm')
    specs = {k:specs[k] for k in order}
    host.VERSION = ir.VERSION = VERSION
    host.GAME_VERSIONS = ir.GAME_VERSIONS = ('2026.9.23.4',)
    facts = deepcopy(ir.temporal_facts('2026.9.23.3'))
    facts.update(
        neutral_camps='Replay62 adds14static camp clearings; kind6/faction2 mobs. Tier1/2/3 health100/180/300, XP20/35/50 and gold10/20/30; leaders double health/rewards and1.5times damage. Visible returning mobs are immune. Public geometry never reveals hidden life or respawn.',
        neutral_rewards='Only the last-hitting unit team receives neutral XP; eligible living heroes within6tiles on same floor share the pool with15percent reserved for eligible hero last hitter. Hero last hit gets gold. Full clear respawns after60seconds unless any living hero within10tiles.',
        neutral_engagement='Idle acquisition ignores resting camps. Deliberate attacks, spells and attack-move can engage; approach within2tiles and LOS also engages.12tile leash resets surviving mobs and heals them on arrival; returning is immune to damage/control. Missing target under fog is unknown.',
    )
    ir.temporal_facts = lambda version: deepcopy(facts)
    host.CONTRACTS.clear()
    host.CONTRACTS.update({'neutralfarm_'+k:v for k,v in specs.items()})
    return specs
