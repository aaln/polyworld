"""Use surplus post-core gold for earlier buyback; keep the field controller."""
from dataclasses import replace
import adaptive_binding as parent
HERE,ROOT,PARENT=parent.HERE,parent.ROOT,parent.PARENT
ir,binding=parent.ir,parent.binding
VERSION='gota-bassy/core-buyback-2026-09-23-r1'
def configure():
    baseline=parent.parent.configure();parent.configure();specs=dict(baseline)
    old=specs['lifecycle'];s=old.template
    marker='    price = buybackPrice()'
    assert s.count(marker)==1
    s=s.replace(marker,'''    buyWait = param_buyback_seconds
  buyReserve = param_buyback_reserve
  buyCore = 0
  buySlot = 0
  while buySlot < 6
    buyGear = itemId(buySlot)
    if buyGear = 11 or buyGear = 16 or buyGear = 18 or buyGear = 19 then
      buyCore = buyCore + 1
    end if
    buySlot = buySlot + 1
  wend
  if buyCore = 4 then
    buyWait = 5
    buyReserve = 100
  end if
'''+marker)
    assert s.count('selfRespawnTicks > tickRate * param_buyback_seconds')==1 and s.count('selfGold >= price + param_buyback_reserve')==1
    s=s.replace('selfRespawnTicks > tickRate * param_buyback_seconds','selfRespawnTicks > tickRate * buyWait').replace('selfGold >= price + param_buyback_reserve','selfGold >= price + buyReserve')
    specs['lifecycle']=replace(old,template=s,meaning=old.meaning+' While dead, scan6own inventory slots for the four unique core items11/16/18/19. With all4, use public buybackPrice and remaining respawn: buy back at>5seconds if gold>=price+100. Otherwise original>25seconds/price+200. Host forbids duplicate equipment, validates dead/alive/match-ended state, restores spawn HP/mana/learned charges, preserves potion/portal family cooldowns. No claim of saved future time or score. All field economy, targeting, draft and portal decisions unchanged.')
    binding.VERSION=ir.VERSION=VERSION
    binding.CONTRACTS.clear();binding.CONTRACTS.update({'buyback_'+k:v for k,v in specs.items()})
    return specs
