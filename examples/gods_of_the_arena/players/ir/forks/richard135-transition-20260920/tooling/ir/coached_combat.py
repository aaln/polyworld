"""Fresh combined follow-up after replay-observed loss of local blocker fights."""
from binding import CONTRACTS
from coached_candidates import make as parent_make,STUDY as PARENT
from policy_ir import HERE,digest,read,refresh_grounding

STUDY=PARENT/'combat-followup'
VARIANTS={'outer_combat':(2,True),'center_combat':(1,True),
          'outer_nearest':(2,False),'center_nearest':(1,False)}


def make(name):
    parent=parent_make('outer');p=parent_make('outer');p['id']='gota_coached_'+name
    lane,cadence=VARIANTS[name]
    p['skill']['observe']={'operator':'coached_blockers','parameters':CONTRACTS['coached_blockers'].defaults()|{'primary_lane':lane}}
    if cadence:
        baseline=read(HERE/'win_bounded_0916.evaluated.ir.json')
        p['skill']['attack']=baseline['skill']['attack']
        p['skill']['attack']['parameters']['motion_object_limit']=60
        for rule in p['strategy']:
            if rule['skill']=='attack':rule['when']='always'
            if rule['skill']=='fallback':rule['when']='no_candidate_no_motion'
    p['belief']['claims']['B_blocker_revision']={'claim':'Prior supported-lane candidates failed local qualification. Replay: outer lost without a single tower attack; close-range/overbroad tower exclusion prevented useful fights against defenders. Test broader12tile nearest-blocker selection, actual-range tower exclusion, and optionally existing bounded-policy cadence combat while keeping creep-gated siege and lane commitment. Combined effect untested.', 'status':'untested','evidence':[{'artifact':str(PARENT/'local/result.json'),'sha256':digest((PARENT/'local/result.json').read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Coached lane behavior plus revised local blocker combat: '+name,needs_review=['belief/B_blocker_revision','goal/G_fort'])
    refresh_grounding(p);return p
