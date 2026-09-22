"""Individual XP target allocation on the frozen portal controller."""
from dataclasses import replace
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PARENT = ROOT / 'examples/gods_of_the_arena/players/ir/forks/portal-coaching20260922-hosted'
# Portable bundles place their frozen dependencies beside this module.
DEPS = HERE.parent / 'portals20260922'
if not (DEPS / 'portal_binding.py').exists():
    DEPS = PARENT / 'tooling/portals20260922'
sys.path.insert(0, str(DEPS))
import portal_binding as parent
ir, binding = parent.ir, parent.binding
VERSION = 'gota-bassy/score-opportunities-2026-09-22-r3'


def assign(prefix):
    return '\n'.join(f'{prefix}{field} = {value}' for field, value in
                     [('Id','id'),('Score','score'),('Kind','kind'),('Hp','hp'),
                      ('X','x'),('Y','y'),('Distance','distance')])


def configure():
    specs = parent.configure()
    from copy import deepcopy
    facts = ir.temporal_facts('2026.9.22.2')
    facts['rewards'] += ' Enemy god destruction grants500XP once to every teammate, including dead/distant heroes; no timeout bonus. Hero kill150XP, building100XP.'
    ir.temporal_facts = lambda version: deepcopy(facts)
    binding.GAME_VERSIONS = ir.GAME_VERSIONS = ('2026.9.22.3',)
    old = specs['observe']
    source = old.template
    reset = '\n'.join(f'{p}Id = 0\n{p}Score = -1000000' for p in ('heroPick','farmPick','structurePick'))
    source = reset + '\n' + source
    start = source.index('        if distance <= 324 and objectAlive(idx) = 1 then')
    end = source.index('\n      end if\n    end if', start)
    source = source[:start] + r'''
        if distance <= 324 and objectAlive(idx) = 1 then
          score = 1000 - distance * 3
          if kind = 3 then
            score = score + 200
            if hp <= selfAttackDamage and distance <= hitReach * hitReach then
              score = score + 650
            end if
            if objectClass(idx) = 1 then
              score = score + 25
            end if
            if id = selfTarget then
              score = score + 70
            end if
            if score > farmPickScore then
''' + assign('farmPick') + '''
            end if
          end if
          if kind = 2 and distance <= 100 then
            score = 1550 - distance * 6 - hp * 70 \\ (selfAttackDamage + 1)
            if hp <= selfAttackDamage * 2 and distance <= hitReach * hitReach then
              score = score + 900
            end if
            if id = selfTarget then
              score = score + 70
            end if
            if score > heroPickScore then
''' + assign('heroPick') + '''
            end if
          end if
          if kind = 1 or kind = 4 or kind = 5 then
            score = 250 - distance * 3
            if hp <= selfAttackDamage * 2 then
              score = score + 200
            end if
            if kind = 1 then
              score = 600 - distance * 3
              if hp <= selfAttackDamage * 4 and distance <= hitReach * hitReach then
                score = score + 2400
              end if
            end if
            if score > structurePickScore then
''' + assign('structurePick') + '''
            end if
          end if
        end if''' + source[end:]
    specs['observe'] = replace(old, template=source, meaning=
        'Bounded public scan retains portal/threat context and separate best hero, creep and structure opportunities. Hero pursuits are limited to10tiles; raw HP per basic hit and travel distance discount expensive fights. Nearly defeated heroes within basic reach receive finishing priority. Creep last-hit and XP-proximity behavior remains. Under2026.9.22.3, an exposed enemy god within basic reach and four raw hits receives finishing priority for500 own XP; healthy gods remain behind productive living targets. Utility is heuristic, not expected XP or guaranteed kill credit.')
    select = '''
if heroPickId > 0 then
  if enemyPower * 2 > friendPower * 3 then
    if heroPickHp > selfAttackDamage * 2 or heroPickDistance > hitReach * hitReach then
      heroPickScore = -1000000
    end if
  end if
  if towerDistance < 144 then
    dx = heroPickX - towerX
    dy = heroPickY - towerY
    if dx * dx + dy * dy < 64 and (towerTarget = 0 or towerTarget = selfId) then
      heroPickScore = -1000000
    end if
  end if
end if
'''
    for p in ('structurePick','farmPick','heroPick'):
        select += f'if {p}Id > 0 and {p}Score > bestScore then\n'
        for field in ('Id','Score','Kind','Hp','X','Y','Distance'):
            select += f'  best{field} = {p}{field}\n'
        select += 'end if\n'
    specs['select_opportunity'] = parent.spec(select,
        'After the complete bounded scan, reject a non-finishing hero chase when visible enemy level power exceeds allies by50%, and reject chasing a hero under a nearby unoccupied or self-targeting tower. Compare remaining hero, creep and fallback-structure utilities. Selection uses public snapshots only. Critical recovery and portal ownership still override combat.')
    order = list(specs)
    order.remove('select_opportunity')
    order.insert(order.index('observe')+1, 'select_opportunity')
    specs = {k:specs[k] for k in order}
    binding.VERSION = ir.VERSION = VERSION
    binding.CONTRACTS.clear()
    binding.CONTRACTS.update({'score_'+k:v for k,v in specs.items()})
    return specs
