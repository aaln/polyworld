"""Exploratory XP-per-work target ranking; separate from frozen control trial."""
from dataclasses import replace
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
PARENT=ROOT/'examples/gods_of_the_arena/players/ir/forks/control20260923-local/control-legality'
sys.path.insert(0,str(HERE.parent/'control20260923'))
import control_binding as parent
ir,host=parent.ir,parent.host
VERSION='gota-bassy/harvest-value-2026-09-23-r61a'


def configure():
    specs=dict(parent.configure())
    old=specs['observe']
    start=old.template.index('          score = 1000 - distance * 3')
    end=old.template.index('          if score > bestScore then',start)
    body='''            harvestReward = 100
            if kind = 1 then
              harvestReward = 500
            end if
            if kind = 2 then
              harvestReward = 150
            end if
            if kind = 3 then
              harvestReward = 15
            end if
            harvestDamage = selfAttackDamage
            if harvestDamage < 1 then
              harvestDamage = 1
            end if
            harvestHits = (hp + harvestDamage - 1) \\ harvestDamage
            harvestDx = x - selfX
            harvestDy = y - selfY
            if harvestDx < 0 then
              harvestDx = 0 - harvestDx
            end if
            if harvestDy < 0 then
              harvestDy = 0 - harvestDy
            end if
            harvestTravel = harvestDx
            if harvestDy > harvestTravel then
              harvestTravel = harvestDy
            end if
            harvestTravel = harvestTravel - hitReach
            if harvestTravel < 0 then
              harvestTravel = 0
            end if
            harvestWork = harvestHits + harvestTravel
            if harvestWork < 1 then
              harvestWork = 1
            end if
            score = harvestReward * 10000 \\ harvestWork
            if id = selfTarget then
              score = score + score \\ 20
            end if
'''
    specs['observe']=replace(old,template=old.template[:start]+body+old.template[end:],
        meaning=old.meaning+' Rank currently visible attackable targets by integer reward/work: hero150, creep15 pool upper bound, structure100, exposed god500 personal XP. Work=ceil(HP/basic damage)+max(0,Chebyshev tile gap-hitReach); 5percent incumbent-target tie resistance. This is an uncalibrated opportunity proxy, not time-to-kill, realized XP or hidden-state prediction. Preserve all observation, threat and tower safety channels. No team-win utility.')
    host.VERSION=ir.VERSION=VERSION
    host.CONTRACTS.clear();host.CONTRACTS.update({'harvest61_'+k:v for k,v in specs.items()})
    return specs
