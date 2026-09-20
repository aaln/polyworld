"""Three-hero breach response without recalling for distant three-hero pressure."""
from dataclasses import replace


def breach_observer(parent):
    token = 'if defFront <> 0 then\n'
    assert parent.template.count(token) == 1
    source = parent.template.replace(token, '''if defFront <> 0 and defFrontD <= param_breach_radius * param_breach_radius then
  defGroupSize = param_breach_group
end if
if defFront <> 0 then
''', 1)
    return replace(parent, template=source, parameters=parent.parameters | {
        'breach_radius':(24,16,40), 'breach_group':(3,3,4)},
        meaning=parent.meaning + ' After finding the closest observed living enemy hero to home, '
        'use breach_group only when that hero is within breach_radius of home. Otherwise keep '
        'the ordinary group_size. A standing nearby friendly structure and the usual cluster '
        'count are still required to trigger recall. This distinguishes a small group nearing '
        'the base from pressure at a distant lane tower, without predicting hidden units. '
        'Only the red branch uses this rule in lineup_breach_observe; blue remains unchanged.')
