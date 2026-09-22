"""Crossbow-specific learned intervention; all other hero action paths retain parent."""
from dataclasses import replace
import adaptive_binding as parent
HERE,ROOT,PARENT=parent.HERE,parent.ROOT,parent.PARENT
ir,binding=parent.ir,parent.binding
VERSION='gota-bassy/class-score-2026-09-22-r1'

def configure():
    baseline=parent.parent.configure()
    adaptive=parent.configure()
    specs=dict(baseline)
    observe=adaptive['observe']
    text=observe.template.replace('score = score + param_hero_priority_bonus', '''if selfClass = 6 then
              score = score + 480
            else
              score = score + 80
            end if''')
    specs['observe']=replace(observe,template=text,parameters={k:v for k,v in observe.parameters.items() if k!='hero_priority_bonus'},meaning='Use the original bounded public observation and target utilities. Only Crossbowman raises the hero basic-target bonus80→480. The extra nearest living visible hero cache writes only new spellHero fields and has no effect on other heroes. No policy identity or hidden position input.')
    changed=adaptive['combat'];unchanged=baseline['combat']
    assert changed.parameters==unchanged.parameters
    text='if selfClass = 6 then\n'+'\n'.join('  '+line for line in changed.template.splitlines())+'\nelse\n'+'\n'.join('  '+line for line in unchanged.template.splitlines())+'\nend if'
    specs['combat']=replace(changed,template=text,meaning='Dispatch by public own hero class. Crossbowman uses independent nearest-public-hero damaging spell attempts with real-host rejection fallback and raised attack priority. Every other class executes the unchanged portal-parent combat template, including original healing/damaging target rules. All draft, lifecycle, geometry, economy, recovery and portal components remain parent-identical. The earlier broad fallback-hero regression is not included.')
    binding.VERSION=ir.VERSION=VERSION
    binding.CONTRACTS.clear();binding.CONTRACTS.update({'class_'+k:v for k,v in specs.items()})
    return specs
