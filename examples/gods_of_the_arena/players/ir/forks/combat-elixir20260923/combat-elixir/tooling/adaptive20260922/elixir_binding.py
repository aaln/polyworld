"""Spend the health-consumable slot on immediate combat recovery."""
from dataclasses import replace
import adaptive_binding as parent
HERE,ROOT,PARENT=parent.HERE,parent.ROOT,parent.PARENT
ir,binding=parent.ir,parent.binding
VERSION='gota-bassy/combat-elixir-2026-09-23-r1'
def configure():
    baseline=parent.parent.configure()
    parent.configure()
    specs=dict(baseline);old=specs['economy'];s=old.template
    assert s.count('if item = 1 then')==1
    s=s.replace('if item = 1 then','if item = 2 then')
    old_use='''if healSlot >= 0 and inOwnSpawn() = 0 then
  if itemCooldown(healSlot) = 0 and selfMaxHp - selfHp >= 70 and threatDistance > 64 then
    if worldTick - hurtTick > tickRate then
      useItem(healSlot)
    end if
  end if
end if'''
    new_use='''if healSlot >= 0 and inOwnSpawn() = 0 then
  if itemCooldown(healSlot) = 0 and selfMaxHp - selfHp >= 70 then
    if useItem(healSlot) = 1 then
      healCount = healCount - 1
      if healCount = 0 then
        empty = empty + 1
      end if
    end if
  end if
end if'''
    assert old_use in s;s=s.replace(old_use,new_use)
    start=s.index('  if healCount = 0 and budget >= 30 and empty > 0 then')
    end=s.index('\nelse\n',start)
    s=s[:start]+'''  healLimit = 2
  healReserve = 0
  if gearCount >= 4 then
    healLimit = 6
    healReserve = 200
  end if
  buys = 0
  while healCount < healLimit and budget >= 75 + healReserve and buys < 6
    if healCount > 0 or empty > 0 then
      if buyItem(2) = 1 then
        if healCount = 0 then
          empty = empty - 1
        end if
        healCount = healCount + 1
        budget = budget - 75
      else
        buys = 6
      end if
    else
      buys = 6
    end if
    buys = buys + 1
  wend'''+s[end:]
    specs['economy']=replace(old,template=s,meaning='Keep dagger, armor, axe, crossbow and portal priorities. Spend health slot on Vitality Elixir(item2,cost75,instant90HP), usable with nearby enemies or recent damage at missingHP>=70 outside spawn. Host enforces shared10second health cooldown. No potion-regeneration assumption. After core stock<=6 retaining200gold; before core<=2. At most6 buys/decision; full inventory/no-funds/failed-buy stop safely. Update consumed stack/empty state before shopping. Portal channel and stun ownership remain earlier gates; healing does not claim movement/combat. Does not establish improved score.')
    binding.VERSION=ir.VERSION=VERSION
    binding.CONTRACTS.clear();binding.CONTRACTS.update({'elixir_'+k:v for k,v in specs.items()})
    return specs
