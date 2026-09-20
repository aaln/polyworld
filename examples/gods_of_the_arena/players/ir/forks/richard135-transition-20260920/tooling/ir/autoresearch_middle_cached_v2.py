"""Equivalent paired target/wave caches for the critical recall branch."""
from binding import CONTRACTS
from autoresearch_target_work_v1 import target_work
from autoresearch_fused_wave_work_v2 import observe_v2
from autoresearch_fused_wave_work_v1 import fallback
import autoresearch_middle_opening_v1

def register():
    contracts={
        'lineup_critical_cached_v2':observe_v2(target_work(CONTRACTS['lineup_critical_recall'])),
        'lineup_middle_cached_v2':fallback(CONTRACTS['lineup_middle_opening_v1'])}
    for k,v in contracts.items():
        if k in CONTRACTS and CONTRACTS[k]!=v:raise ValueError('Conflicting critical cache binding')
        CONTRACTS[k]=v

register()
