"""Current release: recurring unit targets with bounded structure finishes."""
from dataclasses import replace
from copy import deepcopy
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
PARENT=ROOT/'examples/gods_of_the_arena/players/ir/forks/druid-lane20260923-hosted/druid-lane'
sys.path.insert(0,str(HERE.parent/'druidlane20260923'))
import druid_binding as parent
ir,host=parent.ir,parent.host
VERSION='gota-bassy/selective-finish-2026-09-23-r59'
def configure():
    specs=dict(parent.configure())
    facts=ir.temporal_facts('2026.9.23.1')
    facts['balance']='Published d6827a4/replay59: Ranger HP/level29; Crossbowman base damage58; Gale Slash65; Sanguine Chalice45; Warlock Dread Totem87; no faction draft bonuses.'
    facts['score_rewards']='Hero kill150XP; building kill100XP to hero killer; enemy god destruction500XP to every teammate. Creeps share proximity XP. Final score subtracts200XP per elapsed minute including draft. Buildings stop spawning creeps when destroyed.'
    ir.temporal_facts=lambda version:deepcopy(facts)
    old=specs['observe'];marker='if distance <= 324 and objectAlive(idx) = 1 then'
    assert old.template.count(marker)==1
    gate='''finishEligible = 0
          if distance <= hitReach * hitReach then
            if (kind = 1 or kind = 4) and hp <= selfAttackDamage * 2 then
              finishEligible = 1
            end if
            if kind = 5 and hp <= selfAttackDamage then
              finishEligible = 1
            end if
          end if
          if distance <= 324 and objectAlive(idx) = 1 and (kind = 2 or kind = 3 or finishEligible = 1) then'''
    template=old.template.replace(marker,gate)
    target='score = 1000 - distance * 3'
    assert template.count(target)==1
    template=template.replace(target,target+'''
            if (kind = 4 or kind = 5) and hp <= selfAttackDamage then
              score = score + 300
            end if''')
    specs['observe']=replace(old,template=template,meaning=old.meaning+' SelectiveFinish: enemy heroes/creeps remain eligible. Exposed nearby towers/god may be ranked at <=two basic hits of HP; barracks at <=one. Nearby means existing public integer-tile basic-reach estimate; host acceptance is validated separately. Eligible one-hit tower/barracks gets +300 target score; all previous unit/god bonuses and structural safety observations remain. Finishing gives100building or500god XP, but lost recurring waves are an opportunity cost.')
    host.VERSION=ir.VERSION=VERSION
    host.GAME_VERSIONS=ir.GAME_VERSIONS=tuple(dict.fromkeys((*ir.GAME_VERSIONS,'2026.9.23.1')))
    host.CONTRACTS.clear();host.CONTRACTS.update({'finish_'+k:v for k,v in specs.items()})
    return specs
