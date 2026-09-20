"""Versioned priority for creeps visibly targeting the watched base anchor."""
from dataclasses import replace

def core_focus(parent):
    source=parent.template
    reset='defActive = 0'
    anchor='          defAnchorY = objectY(defI)'
    score='        if defScore < bestDistance then'
    assert source.count(reset)==source.count(anchor)==source.count(score)==1
    source=source.replace(reset,'coreFocusAnchor = 0\n'+reset,1)
    source=source.replace(anchor,anchor+'''
          coreFocusAnchor = 0
          coreFocusDx = defAnchorX - defHomeX
          coreFocusDy = defAnchorY - defHomeY
          if coreFocusDx * coreFocusDx + coreFocusDy * coreFocusDy <= param_focus_radius * param_focus_radius then
            coreFocusAnchor = defAnchor
          end if''',1)
    source=source.replace(score,'''        if coreFocusAnchor <> 0 and defKind = 3 then
          if objectTarget(defI) = coreFocusAnchor then
            defScore = defScore - 20000
          end if
        end if
'''+score,1)
    return replace(parent,template=source,
        parameters=parent.parameters|{'focus_radius':(20,1,40)},
        writes=tuple(dict.fromkeys(parent.writes+('coreFocusAnchor','coreFocusDx','coreFocusDy'))),
        meaning=parent.meaning+' While original defense is active, score an otherwise eligible '
        'living hostile creep ahead of heroes if its observed target equals the freshly selected '
        'positive-HP friendly anchor within focus_radius of own fort. Reset eligibility each '
        'decision and each replacement anchor; absent fronts never reuse a stale priority anchor. '
        'Keep original target geometry and all alarm, hold and route logic. This may expose heroes '
        'to more damage; it is an untested whole-policy tradeoff, not a guaranteed improvement.')
