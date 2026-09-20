"""Equivalent observation-count and friendly-kind reuse for VM headroom."""
from dataclasses import replace
from binding import CONTRACTS
import autoresearch_scoped_core_response_v2

def cached_reads(parent):
    # Observation performs no commands. The object list is stable throughout this
    # read-only skill; later command-emitting skills retain their original calls.
    source='observedObjectCount = objectCount()\n'+parent.template.replace('objectCount()','observedObjectCount')
    token='if objectHp(index) > 0 and objectAlive(index) then\n'
    assert source.count(token)==4
    import re
    pattern=r'(?m)^( *)if objectHp\(index\) > 0 and objectAlive\(index\) then\n'
    for m in reversed(list(re.finditer(pattern,source))):
        start=m.end();end=source.index('\n'+m[1]+'end if',start)
        part=source[start:end]
        assert part.count('objectKind(index)')==2
        part=m[1]+'  waveKind = objectKind(index)\n'+part.replace('objectKind(index)','waveKind')
        source=source[:start]+part+source[end:]
    return replace(parent,template=source,
      meaning=parent.meaning+' Equivalent read reuse inside observation only: cache '
      'the stable public object count once, and the kind of each eligible friendly '
      'object once for god/creep dispatch. The observer emits no commands, so these '
      'values cannot change during this skill. Eligibility, rank, full scan bounds, '
      'memory and all commands remain unchanged. Native differential and full '
      'unchanged-control replay equivalence are required.')

for name,parent_name in [('lineup_deployed_cached_v5','lineup_deployed_cached_v4'),
                         ('lineup_scoped_core_response_v3','lineup_scoped_core_response_v2')]:
    value=cached_reads(CONTRACTS[parent_name])
    if name in CONTRACTS and CONTRACTS[name]!=value:raise ValueError('Conflicting scoped cached-read contract')
    CONTRACTS[name]=value
