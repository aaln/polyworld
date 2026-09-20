"""Combined coaching refinement: safe ranged siege plus supported melee."""
from binding import CONTRACTS
from coached_combat import make as combat_make
from coached_candidates import STUDY as PARENT
from policy_ir import digest,refresh_grounding

STUDY=PARENT/'range-followup'
VARIANTS={'outer':2,'center':1,'reverse':0}


def make(name):
    parent=combat_make('outer_combat');p=combat_make('outer_combat');p['id']='gota_coached_range_'+name
    p['skill']['observe']={'operator':'coached_ranged','parameters':CONTRACTS['coached_ranged'].defaults()|{'primary_lane':VARIANTS[name]}}
    p['goal']['G_cadence']['preference']='Use existing class combat/recovery for local fights while pursuing one lane objective; shared navigation resumes when no candidate and no active recovery movement exist.'
    p['goal']['G_survival']['preference']='Melee waits for creep support before tower siege. Ranged heroes may exploit footprint range while the tower is not targeting them; withdraw if targeted. Fort wins remain primary.'
    evidence=PARENT/'jordan-red-hits.json'
    p['belief']['claims']['B_safe_range']={'claim':'Full audited Jordan probe distinguishes physical towerhits from commands. Ranger andArcanist had zero tower-target ticks in inspectedbluewin despite hits withoutcreeps; source uses building footprint for hero attackrange andcenter for towerattackrange. Test class-aware ranged siege with melee creep protection, persistentlane andlocalcombat. Numeric threshold and transfer unvalidated.', 'status':'untested','evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Coached lane push with safe ranged siege: '+name,needs_review=['belief/B_safe_range','goal/G_survival','goal/G_fort'])
    refresh_grounding(p);return p
