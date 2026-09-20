"""Restore one historical red support mechanism while preserving current recall."""
from dataclasses import replace
from binding import CONTRACTS
from ally_assist_contract import ally_assist, caster_assist, caster_assist_bound
from anchored_support_contract import anchored_support
from games.gods_of_the_arena.instruments.jordan268_counter import contracts as parent_contracts

NAME = 'lineup_j268_restored_idle_support'
parent = CONTRACTS['lineup_j268_both_local_recall']
red, blue = parent.template.split('\nelse\n', 1)
red_contract = replace(parent, template=red)
support = anchored_support(caster_assist_bound(caster_assist(ally_assist(red_contract))))
new = replace(support, template=support.template + '\nelse\n' + blue,
              meaning=support.meaning + ' This restoration is applied only to the red '
              'branch of the deployed both-local-recall observer. The blue template '
              'is byte identical; existing 28-tile defense cancellation on both sides '
              'is preserved. Thus expanded support is possible only when ordinary '
              'defense remains active. This is a separately tested restoration, not '
              'evidence of transfer from the historical Richard78 result.')
assert new.template.split('\nelse\n', 1)[1] == blue
assert new.template.count('aaCommitted = 0') == 1
if NAME in CONTRACTS and CONTRACTS[NAME] != new:
    raise ValueError('Conflicting support restoration contract')
CONTRACTS[NAME] = new
