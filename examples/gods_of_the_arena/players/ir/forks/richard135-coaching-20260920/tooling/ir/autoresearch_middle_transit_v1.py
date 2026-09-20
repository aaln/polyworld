"""Additive contracts for one-time initial middle transit from deployed lineage."""
from dataclasses import replace
from binding import CONTRACTS, contract
from autoresearch_target_work_v1 import target_work
from autoresearch_fused_wave_work_v2 import observe_v2


def register():
    observation = observe_v2(target_work(CONTRACTS['lineup_j268_both_local_recall']))
    state = contract('''
        transitActive = 0
        transitX = param_transit_x
        transitY = param_transit_y
        if selfTeam = 0 and (selfClass = param_first_class or selfClass = param_second_class) then
          if worldTick <= param_transit_deadline and transitDone = 0 then
            transitDx = selfX - transitX
            transitDy = selfY - transitY
            if transitDx * transitDx + transitDy * transitDy <= param_arrival_radius * param_arrival_radius then
              transitDone = 1
            else
              if defActive = 0 then
                transitActive = 1
              end if
            end if
          end if
        end if
        ''', {'transit_x':(58,1,114), 'transit_y':(56,1,114),
              'first_class':(8,5,9), 'second_class':(8,5,9),
              'transit_deadline':(1800,240,2400), 'arrival_radius':(6,1,12)},
        ['defActive'], ['transitActive','transitX','transitY'], [],
        'Track one initial public-map middle waypoint for the authored red classes. '
        'At each decision, independent of current combat, mark transit permanently '
        'complete when the observed own coordinates enter arrival_radius. The memory '
        'persists across respawns and never restarts after arrival. The route is eligible '
        'only before transit_deadline, before arrival and outside active defense. '
        'This skill issues no commands, selects no enemies and infers no hidden state. '
        'The fallback consumes eligibility only when normal strategy has no combat '
        'candidate and no accepted motion; after arrival it immediately uses normal '
        'creep escort. Blue and all other classes remain outside this opening.',
        ['transitDone'])
    parent = CONTRACTS['lineup_fused_wave_route_v1']
    route = replace(parent,
        template='if transitActive then\n  moveAccepted = walkTo(transitX, transitY)\nelse\n'
                 + '\n'.join('  '+line for line in parent.template.splitlines()) + '\nend if',
        reads=parent.reads+('transitActive','transitX','transitY'),
        meaning=parent.meaning+' Superseding initial no-target fallback only while '
        'middle_transit_state_v1 is eligible: walk to its public waypoint. Combat, '
        'accepted motion and active defense retain precedence. There is no static '
        'guard interval; the unconditional state skill terminates this route on '
        'arrival or deadline. Normal behavior is otherwise unchanged.')
    for name, value in {'lineup_deployed_cached_v1':observation,
                        'middle_transit_state_v1':state,
                        'lineup_middle_transit_route_v1':route}.items():
        if name in CONTRACTS and CONTRACTS[name] != value:
            raise ValueError('Conflicting versioned transit contract: '+name)
        CONTRACTS[name] = value


register()
