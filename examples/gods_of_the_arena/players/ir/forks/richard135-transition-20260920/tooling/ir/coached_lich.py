"""Transfer validated coaching hypotheses only to the weak sampled Lich role."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import HERE,read,digest,refresh_grounding
from release_workspace import RUN

STUDY=RUN/'coached-lanes/r5-lich'
VARIANTS=['route','guards','convoy']


def make(name):
    parent=read(HERE/'win_bounded_0916.r5.evaluated.ir.json');p=deepcopy(parent);p['id']='gota_coached_lich_'+name
    original=p['skill']['fallback']['parameters']
    if name=='route':
        op='lich_lane_route'
        p['skill']['fallback']={'operator':op,'parameters':CONTRACTS[op].defaults()|original|{'lane':2}}
    else:
        op='lich_guard_observe' if name=='guards' else 'lich_convoy_observe'
        p['skill']['observe']={'operator':op,'parameters':CONTRACTS[op].defaults()|p['skill']['observe']['parameters']|{'primary_lane':2,'safe_range':300000,'siege_defense_tiles':5}}
        p['skill']['fallback']={'operator':'lich_push_route','parameters':CONTRACTS['lich_push_route'].defaults()|original}
    p['goal']['G_wave']['preference']='Lich commits to normalized lane2 across deaths, following published waypoints when no candidate or recovery movement exists. With guard/convoy variants, use the corresponding support/structure chain. All other classes retain their tested nearest-wave escort behavior.'
    p['goal']['G_base']['preference']='Preserve other classes. Lich either keeps existing bounded target selection with a persistent route, or uses the coached lane/guard objective chain with local defense. Exposed god takes priority in the coached observer; convoy optionally clears lane barracks first.'
    ref=RUN/'coached-lanes/r5-current-field/result.json';review=RUN/'coached-lanes/r5-current-field/review/ereq_4cea674e-4042-48a4-a3b7-f631b1b245b6-summary.json'
    p['belief']['claims']['B_lich_coaching']={'claim':'Complete100game sampledfield:75wins overall, Lich3/10. Inspected losses show Lich already starts on an outer lane; one switches to the other outer lane afterrespawn, and another reaches a guard after attacking barracks withoutdying. Test persistent lane routing and objective priority only for Lich. Small role samples and anecdotes do not establish causality. Other nine classes must retain command-trace parity.', 'status':'untested','evidence':[{'artifact':str(x),'sha256':digest(x.read_bytes())} for x in [ref,review]]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Lich-specific coaching transfer: '+name,needs_review=['belief/B_lich_coaching','goal/G_wave','goal/G_base'])
    refresh_grounding(p);return p
