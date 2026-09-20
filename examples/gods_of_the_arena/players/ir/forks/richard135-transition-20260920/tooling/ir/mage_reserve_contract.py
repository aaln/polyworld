"""Keep consumable space for red mage sentries without changing other loadouts."""


def mage_reserve(contract,parent,reserved):
    indent=lambda s:'\n'.join('  '+line for line in s.splitlines())
    source=('if selfTeam = 0 and (selfClass = 2 or selfClass = 3) then\n'+
        indent(reserved.template.replace('param_equipment_cap','param_reserve_cap'))+
        '\nelse\n'+indent(parent.template)+'\nend if')
    union=lambda a,b:tuple(dict.fromkeys(a+b))
    return contract(source,parent.parameters|{'reserve_cap':(5,4,5)},
        union(parent.reads,reserved.reads),union(parent.writes,reserved.writes),
        union(parent.actions,reserved.actions),
        'Only red Lich and Warlock limit permanent equipment to reserve_cap, counting live '
        'inventory and successful purchases. Preserve their existing baseline purchase order; '
        'other classes and the entire blue loadout execute the unchanged parent. Empty slots '
        'can accept healing/mana consumables, but existing consumables can still occupy them. '
        'There is no selling or replacement. Fewer permanent stats are a tradeoff requiring '
        'full-game comparison. Original unscoped equipment behavior: '+parent.meaning,
        union(parent.memory,reserved.memory))
