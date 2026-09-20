"""Test central opening position to reduce the observed defensive return journey."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import digest, read, refresh_grounding
from rush_defense import STUDY

VARIANTS = ['defense_parent','opening20','opening30','opening40']


def make(name):
    parent=read(STUDY/'local/context-feedback/blue_memory/policy.ir.json')
    if name=='defense_parent':return parent
    p=deepcopy(parent);p['id']='gota_rush_'+name
    p['skill']['fallback']={'operator':'opening_guard','parameters':
        CONTRACTS['opening_guard'].defaults() | parent['skill']['fallback']['parameters'] |
        {'opening_ticks':int(name.removeprefix('opening'))*24}}
    p['goal']['G_defense']['preference'] += ' Start near the middle-lane defensive junction for a bounded opening, shortening the return path if a rush is observed.'
    paths=[STUDY/'red-kite-review/positions.json',STUDY/'hosted/blue_memory/matchups/red_kite/result.json']
    p['belief']['claims']['B_opening_defense']={
        'claim':'Observed red-kite control losses: by40s, our heroes have advanced far along both '
                'outer lanes while four/five attackers are visible near the middle tower. '
                'Reactive defense improves hosted wins from0/80to47/80 but misses the frozen '
                'blue-side24/40target with23/40. Test a20/30/40second central opening rendezvous '
                'before ordinary wave following, preserving observed-threat defense and combat. '
                'This is a separate hypothesis; the uploaded candidate and its full benchmark stay frozen.',
        'status':'untested','evidence':[{'artifact':str(p),'sha256':digest(p.read_bytes())} for p in paths]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),
                        change='Bounded middle opening before reactive defense: '+name,
                        needs_review=['belief/B_opening_defense','goal/G_defense','goal/G_wave'])
    refresh_grounding(p);return p
