"""Versioned post-defense wave routing; no change to prior contracts."""
from dataclasses import replace


def wave_observer(mobile):
    marker = '\nif cpAdvance and bestId <> 0 then\n'
    assert mobile.template.count(marker) == 1
    return replace(mobile, template=mobile.template.split(marker)[0],
        meaning=mobile.meaning + ' Superseding center-only structure eligibility: '
        'after release retain ordinary bounded target selection and ordinary allied '
        'wave escort. Do not discard an exposed outer-lane structure. The mobile '
        'rear coverage and emergency recall predicates remain unchanged.')


def outer_observer(mobile):
    parent = wave_observer(mobile)
    token = '    cpTransitions = cpTransitions + 1\n'
    assert parent.template.count(token) == 1
    choose = '''    cpLane = 0
    defAnchorD = 2147483647
    defI = 0
    while defI < objectCount() and defI < 64
      if objectKind(defI) = 3 then
        defI = 64
      else
        if objectKind(defI) = 2 and objectTeam(defI) = selfTeam and objectHp(defI) > 0 and objectAlive(defI) then
          defDx = objectX(defI)
          defDy = objectY(defI)
          if defDx + defDy < 94 or defDx + defDy > 138 then
            defD = (defDx - 11) * (defDx - 11) + (defDy - 105) * (defDy - 105)
            if defD < defAnchorD then
              defAnchorD = defD
              cpLane = 0
              if defDx + defDy > 138 then
                cpLane = 2
              end if
            end if
          end if
        end if
      end if
      defI = defI + 1
    wend
'''
    filter_source = '''
if cpAdvance and bestId <> 0 then
  defI = 0
  while defI < objectCount() and defI < 64
    if objectId(defI) = bestId then
      defKind = objectKind(defI)
      if defKind = 4 or defKind = 5 then
        defD = 0
        if cpLane = 0 and bestId >= 13 and bestId <= 15 then
          defD = 1
        end if
        if cpLane = 2 and bestId >= 25 and bestId <= 27 then
          defD = 1
        end if
        if bestId = 30 or bestId = 31 then
          defD = 1
        end if
        if defD = 0 then
          bestId = 0
        end if
      end if
    end if
    defI = defI + 1
  wend
end if
'''
    return replace(parent, template=parent.template.replace(token, token + choose) + filter_source,
        memory=parent.memory + ('cpLane',),
        meaning=parent.meaning + ' Superseding free wave routing for this variant: '
        'at each release choose the outer lane containing the living allied hero '
        'closest to the enemy fort, using current shared ally positions. Classify '
        'the public upper corridor by x+y<94 and lower corridor by x+y>138; '
        'default to upper if neither contains a living ally. Retain that lane '
        'until the next release. During advance reject barracks and off-lane '
        'towers; keep selected-lane exposed towers, enemy guards, fort, and '
        'ordinary local mobile combat. Eligibility is observed, never inferred '
        'from an absent enemy. This operator is used only in the red branch.')


def outer_navigation(parent, route):
    nav = route.template.replace('param_lane', 'cpLane')
    indent = lambda s: '\n'.join('  ' + line for line in s.splitlines())
    return replace(parent,
        template='if cpAdvance then\n' + indent(nav) + '\nelse\n' + indent(parent.template) + '\nend if',
        parameters=parent.parameters | {k:v for k,v in route.parameters.items() if k != 'lane'},
        memory=tuple(dict.fromkeys(parent.memory + route.memory + ('cpLane',))),
        meaning='After observed defensive release, follow the outer lane chosen '
        'from living allied progress by the paired observer. Use published '
        'waypoints only when combat and recovery emit no action; stage resets '
        'at release and near spawn. Otherwise preserve parent defense/wave '
        'navigation. Accepted movement does not prove arrival. ' + parent.meaning)
