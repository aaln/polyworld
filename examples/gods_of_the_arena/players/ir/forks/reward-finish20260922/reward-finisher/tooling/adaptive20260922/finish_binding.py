"""Order nearby one-basic-hit finishes by current individual XP reward."""
from dataclasses import replace
import adaptive_binding as parent
HERE,ROOT,PARENT=parent.HERE,parent.ROOT,parent.PARENT
ir,binding=parent.ir,parent.binding
VERSION='gota-bassy/reward-finish-2026-09-22-r1'

def configure():
    baseline=parent.parent.configure()
    parent.configure()  # Install the current release facts; retain baseline skills.
    specs=dict(baseline);old=specs['observe']
    source=old.template.replace('hitReach = selfAttackRange \\ 60000 + 1','hitReach = selfAttackRange \\ 60000 + 1\nfinishReach = selfAttackRange \\ 60000')
    marker='          if id = selfTarget then'
    assert source.count(marker)==1
    source=source.replace(marker,'''          if hp <= selfAttackDamage and distance <= finishReach * finishReach then
            if kind = 2 then
              score = score + 1000
            end if
            if kind = 4 or kind = 5 then
              score = score + 1100
            end if
            if kind = 1 then
              score = score + 2000
            end if
          end if
'''+marker)
    specs['observe']=replace(old,template=source,meaning=old.meaning+' During the existing bounded scan, reward-order exposed enemy targets whose current public HP is within one raw basic hit and whose integer-position distance is within floor(basic range in tiles). Add1000for heroes (150XP),1100for towers/barracks (100XP),2000for enemy god (500ownXP). Together with original kind/finishing scores, this orders god>hero>building>creep at ordinary in-range distances. Host geometry, target movement and simultaneous kill credit can still defeat a finish; this is not guaranteed XP. Original heal, spell, chase, structure, recovery, tower, movement and draft rules remain.')
    binding.VERSION=ir.VERSION=VERSION
    binding.CONTRACTS.clear();binding.CONTRACTS.update({'finish_'+k:v for k,v in specs.items()})
    return specs
