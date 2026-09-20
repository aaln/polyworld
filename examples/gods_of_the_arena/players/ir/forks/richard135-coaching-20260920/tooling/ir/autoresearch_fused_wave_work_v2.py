"""Versioned cache with no duplicate target lookup or needless wave work."""
from dataclasses import replace
import re
from autoresearch_fused_wave_work_v1 import observe, ALLY


def observe_v2(parent):
    p=observe(parent)
    source=p.template
    pattern=r'(?m)^( *)bestDistance = distance\n\1bestId = id$'
    assert len(re.findall(pattern,source))==4
    source=re.sub(pattern,lambda m:m[0]+'\n'+m[1]+'macroSelectedKind = objectKind(index)\n'+m[1]+'macroSelectedX = objectX(index)\n'+m[1]+'macroSelectedY = objectY(index)',source)
    prune=r'(?m)^( *)macroIndex = 0\n\1while bestId <> 0 and macroIndex < objectCount\(\)\n.*?\n\1wend'
    matches=list(re.finditer(prune,source,re.S));assert len(matches)==2
    params=[]
    for m in matches:
        parameter=re.search(r'> (param_\w+) \* \1',m[0])[1]
        params.append(parameter)
    def replace_prune(m):
        param=re.search(r'> (param_\w+) \* \1',m[0])[1]
        lines=['if bestId <> 0 then','  if macroSelectedKind = 2 or macroSelectedKind = 3 then','    macroDx = macroSelectedX - selfX','    macroDy = macroSelectedY - selfY',f'    if macroDx * macroDx + macroDy * macroDy > {param} * {param} then','      bestId = 0','    end if','  end if','end if']
        return '\n'.join(m[1]+line for line in lines)
    source=re.sub(prune,replace_prune,source,flags=re.S)
    # A target score below this bound cannot later turn into an out-of-range
    # mobile target: the nearest score only decreases, and mobile weight is
    # constant. Therefore fallback will not consume a cache on such a path.
    for i,m in reversed(list(enumerate(re.finditer(r'(?m)^( *)if objectHp\(index\) > 0 and objectAlive\(index\) then\n',source)))):
        indent=m[1]
        block='\n'.join(indent+line for line in ALLY.splitlines())
        assert source[m.start():].startswith(block)
        pursuit=params[i//2]
        weight=('param_redbranch_unit_weight' if i<2 else 'param_unit_weight') if i%2 else '1'
        wrapper=f'{indent}if bestId = 0 or bestDistance > {pursuit} * {pursuit} * {weight} then\n'+'\n'.join('  '+line for line in block.splitlines())+f'\n{indent}else\n{indent}  waveCached = 0\n{indent}end if'
        source=source[:m.start()]+wrapper+source[m.start()+len(block):]
    return replace(p,template=source,writes=p.writes+('macroSelectedKind','macroSelectedX','macroSelectedY'),
        meaning=p.meaning+' Capture selected target kind and coordinates at the '
        'same winning scan index and validate its pursuit range directly, avoiding '
        'a second lookup. Stop wave-cache work once a target score guarantees '
        'a valid final target under the fixed mobile weight and pursuit radius; '
        'mark the unused cache invalid. No view truncation or changed rankings. '
        'The cache is consumed only when valid; retain original fallback otherwise.')
