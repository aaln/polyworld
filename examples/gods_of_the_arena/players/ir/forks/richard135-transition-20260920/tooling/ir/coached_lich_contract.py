"""A class-local coaching branch preserving every other hero's control flow."""


def branch(contract,focal,other):
    overlap=set(focal.parameters)&set(other.parameters)
    if overlap:raise ValueError('Ambiguous branch parameters: '+str(overlap))
    indent=lambda s:'\n'.join('  '+l for l in s.splitlines())
    return contract('if selfClass = 7 then\n'+indent(focal.template)+'\nelse\n'+indent(other.template)+'\nend if',
        focal.parameters|other.parameters,sorted(set(focal.reads)|set(other.reads)),
        sorted(set(focal.writes)|set(other.writes)),sorted(set(focal.actions)|set(other.actions)),
        'Only Lich(stable class7) executes the coaching branch: '+focal.meaning+' Other nine classes execute the unchanged parent branch: '+other.meaning,
        sorted(set(focal.memory)|set(other.memory)))
