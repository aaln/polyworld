"""Use a ready outbound scroll with a destination aligned to the active farm route."""
from dataclasses import replace
from copy import deepcopy
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
PARENT=ROOT/'examples/gods_of_the_arena/players/ir/forks/druid-lane20260923-hosted/druid-lane'
sys.path.insert(0,str(HERE.parent/'druidlane20260923'))
import druid_binding as parent
ir,host=parent.ir,parent.host
VERSION='gota-bassy/productive-return-2026-09-23-r59'

def configure():
    specs=dict(parent.configure())
    facts=ir.temporal_facts('2026.9.23.1')
    facts['balance']='Published d6827a4/replay59: Ranger HP/level29; Crossbowman base damage58; Gale Slash damage65; Sanguine Chalice heal45; Warlock Dread Totem damage87; no faction draft bonuses.'
    ir.temporal_facts=lambda version:deepcopy(facts)
    old=specs['observe']
    marker='dx = x - farmX\ndy = y - farmY'
    assert marker in old.template
    align='''  if selfTeam = 1 and ordinal = 0 then
    if selfClass = Ranger or selfClass = Crossbowman then
      farmX = mapWidth \\ 2
      farmY = mapHeight \\ 2
    end if
  end if
'''
    specs['observe']=replace(old,template=old.template.replace(marker,align+marker),meaning=old.meaning+' Choose the outbound friendly-tower anchor nearest the actual active lane waypoint, including the inherited blue opening central route. Preserve the other public scan facts and target scoring.')
    old=specs['advance']
    marker='portalCount >= 2';assert old.template.count(marker)==1
    specs['advance']=replace(old,template=old.template.replace(marker,'portalCount >= 1'),meaning=old.meaning+' A single ready scroll suffices for a safe outbound keep-to-field channel after recovery. Existing health/recovery, threat, cooldown, channel lock, known friendly anchor and distance-greater-than20-cell guards remain. Accept the tradeoff of consuming the last scroll; shopping still replenishes reserves. Compare XP-minus-time outcomes, not portal count.')
    host.VERSION=ir.VERSION=VERSION
    host.GAME_VERSIONS=ir.GAME_VERSIONS=tuple(dict.fromkeys((*ir.GAME_VERSIONS,'2026.9.23.1')))
    host.CONTRACTS.clear();host.CONTRACTS.update({'productive_'+k:v for k,v in specs.items()})
    return specs
