"""Expose the observed defense fact explicitly; preserve V1 bindings unchanged."""
from dataclasses import replace
from binding import CONTRACTS
import autoresearch_middle_transit_v1

observer = CONTRACTS['lineup_deployed_cached_v1']
state = CONTRACTS['middle_transit_state_v1']
contracts = {
    'lineup_deployed_cached_v2': replace(observer,
        template=observer.template+'\ntransitObservedDefense = defActive',
        writes=observer.writes+('transitObservedDefense',),
        meaning=observer.meaning+' Expose the final defActive scratch value as '
        'transitObservedDefense for a separately declared initial-transit state skill. '
        'This assignment issues no command and does not change target or defense choices.'),
    'middle_transit_state_v2': replace(state,
        template=state.template.replace('defActive', 'transitObservedDefense'),
        reads=('transitObservedDefense',),
        meaning=state.meaning+' The defense input is the explicit alias from '
        'lineup_deployed_cached_v2; no second observation or hidden input is introduced.')}
for name, value in contracts.items():
    if name in CONTRACTS and CONTRACTS[name] != value:
        raise ValueError('Conflicting transit V2 contract: '+name)
    CONTRACTS[name] = value
