"""Compose explicitly parameterized red and blue semantic skills."""
import re


def split(contract,red,blue):
    red_source=re.sub(r'\bparam_(\w+)\b',lambda m:'param_redbranch_'+m[1],red.template)
    indent=lambda s:'\n'.join('  '+l for l in s.splitlines())
    source='if selfTeam = 0 then\n'+indent(red_source)+'\nelse\n'+indent(blue.template)+'\nend if'
    union=lambda a,b:tuple(dict.fromkeys(a+b))
    return contract(source,{('redbranch_'+k):v for k,v in red.parameters.items()}|blue.parameters,
        union(red.reads,blue.reads),union(red.writes,blue.writes),union(red.actions,blue.actions),
        'Choose by the public fixed team/hero lineup. On red execute exactly this skill with '
        'its separately prefixed parameters: '+red.meaning+' On blue execute: '+blue.meaning+
        ' Only the selected branch runs; inactive branch memory and actions are not evaluated. '
        'This composition follows a measured color interaction, not an overall improvement '
        'claim. Verify complete red/blue gameplay parity with each source parent.',union(red.memory,blue.memory))
