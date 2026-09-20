"""Release5 followup: release creep waves through barracks, then guard siege."""
from binding import CONTRACTS
from coached_guards import make as guard_make, STUDY as PARENT
from policy_ir import digest,refresh_grounding

STUDY=PARENT.parent/'r5-convoy'
VARIANTS={'barracks':(2,0,300000,5,1,1),
          'presence':(2,0,300000,5,0,1),
          'center':(1,1,300000,5,1,1),
          'center_wide':(1,1,330000,12,1,1),
          'center_direct':(1,1,300000,5,1,0)}


def make(name):
    parent=guard_make('focus');p=guard_make('focus');p['id']='gota_coached_convoy_'+name
    red,blue,safe,defense,target,open_wave=VARIANTS[name]
    p['skill']['observe']={'operator':'coached_convoy','parameters':CONTRACTS['coached_convoy'].defaults()|{'primary_lane':red,'blue_lane':blue,'safe_range':safe,'siege_defense_tiles':defense,'require_creep_target':target,'open_wave':open_wave}}
    p['goal']['G_base']['preference']='Exposed god first; when enabled, clear the committed lane barracks to free allied creeps before engaging god guards. Otherwise attack exposed guards, then the committed lane towers, with configured local defense.'
    p['goal']['G_wave']['preference']='Commit to one lane and preserve its allied creep push. Clear exposed barracks when configured so creeps can reach guards. Melee needs current support; qualifying ranged heroes can siege while not targeted.'
    ref=PARENT/'review/team-summary.json'
    p['belief']['claims']['B_convoy']={'claim':'In the failed guard screen the red team cleared one lane and one guard but lost with the other guard standing. Three melee/short-range heroes held behind the two ranged attackers. Source confirms creeps must clear lane barracks before choosing guards. Test releasing the creep wave, including center-lane and local-defense variants. Combined effects are unvalidated.', 'status':'untested','evidence':[{'artifact':str(ref),'sha256':digest(ref.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Coached creep convoy to god guards: '+name,needs_review=['belief/B_convoy','goal/G_base','goal/G_survival'])
    refresh_grounding(p);return p
