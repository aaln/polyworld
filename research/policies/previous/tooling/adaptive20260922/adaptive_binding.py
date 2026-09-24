"""Independent reachable hero spell attempts; public-only host-authorized targets."""
from dataclasses import replace
from pathlib import Path
from copy import deepcopy
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
PARENT=ROOT/'examples/gods_of_the_arena/players/ir/forks/portal-coaching20260922-hosted'
DEPS=HERE.parent/'portals20260922'
if not (DEPS/'portal_binding.py').exists():DEPS=PARENT/'tooling/portals20260922'
sys.path.insert(0,str(DEPS))
import portal_binding as parent
ir,binding=parent.ir,parent.binding
VERSION='gota-bassy/adaptive-score-2026-09-22-r1'


def configure():
    specs=parent.configure()
    facts=ir.temporal_facts('2026.9.22.2')
    facts['rewards']+=' Enemy god destruction grants500XP once to every teammate including dead/distant heroes. Hero kill150XP; building100XP. Score charges200/minute including draft.'
    ir.temporal_facts=lambda version:deepcopy(facts)
    binding.GAME_VERSIONS=ir.GAME_VERSIONS=('2026.9.22.3',)
    old=specs['observe']
    source='spellHeroId = 0\nspellHeroDistance = 82\n'+old.template
    marker='        if distance <= 324 and objectAlive(idx) = 1 then'
    assert marker in source
    source=source.replace(marker,'''        if kind = 2 and objectAlive(idx) = 1 and distance < spellHeroDistance then
          spellHeroId = id
          spellHeroDistance = distance
        end if
'''+marker)
    assert 'score = score + 80' in source
    source=source.replace('score = score + 80','score = score + param_hero_priority_bonus')
    specs['observe']=replace(old,template=source,parameters={**old.parameters,'hero_priority_bonus':(80,80,480)},meaning=old.meaning+' Also retain nearest publicly visible living enemy hero within9 integer-coordinate tiles as a spell candidate. This does not reveal hidden heroes or identify opponent policy versions. Hero basic-target bonus is an explicit80..480 parameter; all other target geometry, finishing and current-target preferences remain.')
    old=specs['combat']
    source=old.template
    old_block='''          if abilityDamage(slot) > 0 then
            if bestKind <> 3 or bestHp <= abilityDamage(slot) then
              castTarget(slot, bestId)
            end if
          end if'''
    # Contract source uses two spaces less than compiled guarded BASIC.
    if old_block not in source:
        old_block='\n'.join(line[2:] for line in old_block.splitlines())
    assert old_block in source,source
    new='''          if abilityRestore(slot) > 0 then
            if selfMaxMana - selfMana >= abilityRestore(slot) then
              castTarget(slot, selfId)
            end if
          else
            if abilityDamage(slot) > 0 then
              spellAccepted = 0
              if spellHeroId > 0 then
                spellAccepted = castTarget(slot, spellHeroId)
              end if
              if spellAccepted = 0 and bestId <> spellHeroId then
                if bestKind <> 3 or bestHp <= abilityDamage(slot) then
                  castTarget(slot, bestId)
                end if
              end if
            end if
          end if'''
    if old_block.startswith('        if'):new='\n'.join(line[2:] for line in new.splitlines())
    source=source.replace(old_block,new)
    specs['combat']=replace(old,template=source,meaning='Preserve basic targeting and post-hit timing. For each learned ready affordable ability: heal self when useful; restore mana when an entire restoration fits; otherwise attempt damage on the nearest public enemy hero within9 observation tiles. The actual host validates exact range, floor, visibility and target legality; only on rejected hero cast try the original basic target, retaining lethal-creep restriction. A rejected attempt spends no mana/charge. This is a heuristic, not inferred kill credit. Recovery, tower safety and complete portal-channel ownership precede combat unchanged.')
    binding.VERSION=ir.VERSION=VERSION
    binding.CONTRACTS.clear();binding.CONTRACTS.update({'adaptive_'+k:v for k,v in specs.items()})
    return specs
