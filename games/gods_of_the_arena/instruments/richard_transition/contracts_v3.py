"""Reject stale hit counters when entering focus or returning after a gap."""
from dataclasses import replace
from binding import CONTRACTS
from games.gods_of_the_arena.instruments.richard_transition import contracts_v2

ATTACK='richard_transition_focus_v3'
parent=CONTRACTS[contracts_v2.ATTACK]
old='if selfAttacksLanded > motionLastHits and selfClass <> 9 then'
new='if worldTick = motionLastTick + 1 and selfAttacksLanded > motionLastHits and selfClass <> 9 then'
assert parent.template.count(old)==1
CONTRACTS[ATTACK]=replace(parent,template=parent.template.replace(old,new),
    meaning=parent.meaning+' V3 requires the remembered hit counter to come '
        'from the immediately preceding decision. First focus entry, a dense '
        'fast-path gap or respawn cannot interpret old accumulated hits as a '
        'fresh recovery opportunity. That boundary uses ordinary attack, then '
        'starts maintaining fresh focus memory.')
