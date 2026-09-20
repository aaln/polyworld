"""Observed inventory profiles arbitrate complete, versioned strategy components."""
from dataclasses import replace
from pathlib import Path
import json

from binding import CONTRACTS, contract, guarded
from games.gods_of_the_arena.instruments.richard_coaching import contracts as formation
import autoresearch_tower_handoff_v3

INPUTS = Path(__file__).resolve().parents[4] / 'tmp/gota-ir/formation-adaptive-20260920/inputs'
POLICIES = {n: json.loads((INPUTS/n/'policy.ir.json').read_text())
            for n in ('formation', 'legacy', 'jordan', 'handoff')}

# All detector scratch is overwritten by the subsequent observer; adMode alone
# persists. Every vote comes from a distinct visible object in this snapshot.
DETECT = '''if adMode = 0 and worldTick <= 1800 and (worldTick / 24) * 24 = worldTick then
  defCount = 0
  defMates = 0
  defSentry = 0
  defI = 0
  while defI < objectCount() and defI < 64
    if objectKind(defI) = 2 and objectTeam(defI) <> selfTeam and objectAlive(defI) and objectHp(defI) > 0 then
      defDx = 0
      defDy = 0
      defScore = 0
      defFront = 0
      defKind = 0
      while defKind < 6
        defD = objectItemId(defI, defKind)
        if defD <> 0 then
          defDx = defDx + 1
        end if
        if defD = 8 then
          defDy = defDy + 1
        end if
        if defD = 2 then
          defScore = defScore + 1
        end if
        if defD = 11 then
          defFront = defFront + 1
        end if
        defKind = defKind + 1
      wend
      if defDx = 2 and defDy = 1 and defScore = 1 then
        defCount = defCount + 1
      end if
      if defDx = 1 and defDy = 1 then
        defMates = defMates + 1
      end if
      if defDx = 1 and defFront = 1 then
        defSentry = defSentry + 1
      end if
    end if
    defI = defI + 1
  wend
  if defCount >= 2 and defMates = 0 and defSentry = 0 then
    adMode = 1
  end if
  if defMates >= 2 and defCount = 0 and defSentry = 0 then
    adMode = 2
  end if
  if defSentry >= 2 and defCount = 0 and defMates = 0 then
    adMode = 3
  end if
end if'''


def frozen(name, skill):
    spec = POLICIES[name]['skill'][skill]
    return CONTRACTS[spec['operator']].source(spec['parameters'])


def register():
    handoff = POLICIES['handoff']['skill']['observe']
    base = CONTRACTS[handoff['operator']]
    source = base.template
    # Same critical exception as formation3600, conditional on an unresolved or
    # dagger profile. Only current public alarm observations refresh the clock.
    alarm = '(adMode = 0 or adMode = 3) and defFrontD <= 3600 and defCount >= 2'
    assert source.count('if defAnchor <> 0 and (') == 2
    source = source.replace('if defAnchor <> 0 and (', 'if defAnchor <> 0 and ((' + alarm + ') or ')
    token = 'defUntil = worldTick + defHoldTicks'
    assert source.count(token) == 2
    source = source.replace(token, token + '\n      if ' + alarm + ' then\n        criticalUntil = worldTick + 1200\n      end if')
    for radius in ('red_recall_radius', 'recall_radius'):
        token = f'if defDx * defDx + defDy * defDy > param_{radius} * param_{radius} then'
        assert source.count(token) == 1
        condition = ' and worldTick >= criticalUntil'
        if radius == 'recall_radius':
            condition = ' and adMode <> 1' + condition
        source = source.replace(token, token[:-5] + condition + ' then')
    # The legacy Alex-blue reference's creep_first=0 is essential. Keep the
    # selected priority and the observer together instead of copying its name.
    token = '(param_creep_first = 1 and defKind = 3) or (param_creep_first = 0 and defKind = 2)'
    assert source.count(token) == 1
    source = source.replace(token, '(adMode <> 1 and defKind = 3) or (adMode = 1 and defKind = 2)')
    source = replace(base, template=source).source(handoff['parameters'])
    macro = formation.lower_storage(formation.MACRO)
    for name, value in POLICIES['formation']['skill']['observe']['parameters'].items():
        import re
        macro = re.sub(r'\bparam_' + name + r'\b', str(value), macro)
    assert 'param_' not in macro
    complete = DETECT + '\ngaActive = 0\n' + guarded(
        'selfTeam = 0 and worldTick >= 3600 and (adMode = 0 or adMode = 3)', macro)
    complete += '\n' + guarded('gaActive = 0', source)
    parent = CONTRACTS[POLICIES['formation']['skill']['observe']['operator']]
    CONTRACTS['formation_profile_observe_v1'] = replace(parent, template=complete, parameters={},
        memory=tuple(dict.fromkeys(parent.memory + base.memory + ('adMode',))),
        writes=tuple(dict.fromkeys(parent.writes + base.writes)),
        meaning='Sample the first64 public objects every24ticks through1800. Two distinct visible living '
        'enemies with exact boots+elixir, boots-only, or dagger-only inventories and no conflicting '
        'recognized profile latch adMode1,2,3 respectively. No identity, seed, enemy memory or hidden '
        'inventory is available. This is a provisional inventory profile, shared by other policies. '
        'Unknown/dagger retains60tile critical recall and late3600 red formation. Boots-only uses '
        '28tile local recall. Boots+elixir restores historical blue remote defense and hero-first '
        'defense priority. Red ordinary observation uses the frozen caster-transit/tower-handoff '
        'reference; its complete early package is tested with the late conditional formation. '
        'Mode is episode-latched and retained through death; repeated frames add no evidence. '
        'All original parent alarms, targeting order and visibility semantics otherwise remain.')
    route = CONTRACTS[POLICIES['formation']['skill']['fallback']['operator']]
    # Keep formation routing exactly and use the handoff's transit-aware ordinary route.
    original = CONTRACTS['lineup_perimeter_route'].template
    assert route.template.count(original) == 0  # original is indented inside the wrapper
    tail = '\n'.join('  '+line for line in original.splitlines())
    assert route.template.count(tail) == 1
    new_route = route.template.replace(tail, '\n'.join('  '+line for line in frozen('handoff','fallback').splitlines()))
    new_route = replace(route, template=new_route).source(POLICIES['formation']['skill']['fallback']['parameters'])
    CONTRACTS['formation_profile_route_v1'] = replace(route, template=new_route, parameters={},
        meaning=route.meaning+' Outside active formation retain the frozen handoff caster-transit route.')
    for skill in ('transit_state', 'tower_handoff'):
        spec = POLICIES['handoff']['skill'][skill]
        parent = CONTRACTS[spec['operator']]
        body = frozen('handoff', skill)
        condition = 'selfTeam = 0 and gaActive = 0'
        if skill == 'transit_state':
            condition += ' and adMode <> 3'
            body = 'transitActive = 0\n' + guarded(condition, body)
        else:
            body = guarded(condition, body)
        CONTRACTS['formation_profile_'+skill+'_v1'] = replace(parent, template=body, parameters={},
            meaning='Conditional component of the observed-profile formation fork. '+parent.meaning)


register()
