"""Current-release experiment: deliberately target enemy units, not buildings."""
from dataclasses import replace
from copy import deepcopy
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
PARENT=ROOT/'examples/gods_of_the_arena/players/ir/forks/druid-lane20260923-hosted/druid-lane'
sys.path.insert(0,str(HERE.parent/'druidlane20260923'))
import druid_binding as parent
ir,host=parent.ir,parent.host
VERSION='gota-bassy/unit-farming-2026-09-23-r59'
def configure():
    specs=dict(parent.configure())
    facts=ir.temporal_facts('2026.9.23.1')
    facts['balance']='Published d6827a4/replay59: Ranger HP/level29; Crossbowman base damage58; Gale Slash65; Sanguine Chalice45; Warlock Dread Totem87; no faction draft bonuses.'
    facts['score_rewards']='Hero kill150XP; building kill100XP to hero killer; enemy god destruction500XP to every teammate. Creeps share proximity XP. Final score subtracts200XP per elapsed minute including draft.'
    ir.temporal_facts=lambda version:deepcopy(facts)
    old=specs['observe'];marker='if distance <= 324 and objectAlive(idx) = 1 then'
    assert old.template.count(marker)==1
    specs['observe']=replace(old,template=old.template.replace(marker,'if distance <= 324 and objectAlive(idx) = 1 and (kind = 2 or kind = 3) then'),
        meaning=old.meaning+' Experimental unit-only deliberate target selection: only observed living enemy heroes(kind2) and creeps(kind3) enter best-target ranking. Preserve all structural observations for tower safety, home defense, routes and portal anchors. Current host attack-move automatically acquires creeps only. Incidental area damage to structures remains possible. Buildings award100XP and ending the god500team XP; this deliberately forgoes those opportunities and requires a fresh individual-score test.')
    host.VERSION=ir.VERSION=VERSION
    host.GAME_VERSIONS=ir.GAME_VERSIONS=tuple(dict.fromkeys((*ir.GAME_VERSIONS,'2026.9.23.1')))
    host.CONTRACTS.clear();host.CONTRACTS.update({'unitfarm_'+k:v for k,v in specs.items()})
    return specs
