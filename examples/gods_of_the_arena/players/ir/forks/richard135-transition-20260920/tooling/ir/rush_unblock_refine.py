"""Narrow emergency response and isolate quiet release after the first screen."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import digest, read, refresh_grounding
from rush_unblock import STUDY, make as original

VARIANTS=['deployed_parent','spread','near_core','near_release_20','near_release_60',
          'quiet_20','quiet_30','quiet_60']


def make(name):
    if name in ('deployed_parent','spread'): return original(name)
    p=deepcopy(original('spread'));parent=deepcopy(p)
    p['id']='gota_defense_unblock_'+name
    operator='reachable_core_defense' if name=='near_core' else (
        'released_sentry_defense' if name.startswith('quiet_') else 'released_reachable_defense')
    parameters=CONTRACTS[operator].defaults() | p['skill']['observe']['parameters']
    if name!='near_core': parameters['quiet_ticks']=int(name.split('_')[-1])*24
    p['skill']['observe']={'operator':operator,'parameters':parameters}
    evidence=STUDY/'screen/result.json'
    p['belief']['claims']['B_narrow_response']={
        'claim':'First6case/arm local screen: parent6wins, spread6, broadcore3, combined4, '
                'widetogether3, release20/30/60withbroadcore2/1/2. This rejects those broad '
                'combinations on local opponents. Test emergency response only by heroes '
                'already within24tiles of home, for enemies targeting the god or within6tiles; '
                'also isolate quiet release without the failed broadcore override. '
                'Shared-rally stalls occur in winning replays too; they are not the sole '
                'explanation of losses. None of these new candidates has hosted evidence.',
        'status':'untested','evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
    p['goal']['G_defense']['preference']+=' Release stale duty after configured quiet time; keep distant attackers on offense during small core emergencies.'
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),
                       change='Refine emergency scope and isolate release: '+name)
    refresh_grounding(p);return p
