"""Isolated historical red caster assistance on the current deployed observer."""
from dataclasses import replace
from binding import CONTRACTS
import autoresearch_scoped_core_response_v3

parent = CONTRACTS['lineup_deployed_cached_v5']
historical = CONTRACTS['lineup_anchored_support']
start = historical.template.index('    if selfClass = 7 or selfClass = 8 then\n    aaReady')
end = historical.template.index('    defenseDecisions = defenseDecisions + 1', start)
block = historical.template[start:end].replace('objectCount()', 'observedObjectCount')
token = '    defenseDecisions = defenseDecisions + 1'
assert parent.template.count(token) == 2
source = parent.template.replace(token, block + token, 1)
names = ['assist_tiles', 'frontline_only', 'idle_only', 'anchor_required', 'wait_support']
parameters = {f'redbranch_{n}': historical.parameters[f'redbranch_{n}'] for n in names}
value = replace(parent, template=source, parameters=parent.parameters | parameters,
    meaning=parent.meaning + ' Restore only the historical anchored assistance block '
    'inside active red defense. Idle actual red Lich7/Warlock8 with at least25percent '
    'HP may join the visible leading enemy within22tiles when a living other ally '
    'within12tiles with at least120HP publicly targets that enemy, and the enemy has '
    'a standing friendly defense anchor in the existing14tile perimeter. This is '
    'not literal tower firing range. Preserve current recall, routing, creep-first '
    'targeting, all noncaster and blue behavior. Historical outcomes against '
    'Richard78/Jordan186 do not establish present-target strength. Do not infer '
    'survival from earlier orders; evaluate complete reacting games.')
name = 'lineup_deployed_anchor_restore_v1'
if name in CONTRACTS and CONTRACTS[name] != value:
    raise ValueError('Conflicting anchored restoration contract')
CONTRACTS[name] = value
