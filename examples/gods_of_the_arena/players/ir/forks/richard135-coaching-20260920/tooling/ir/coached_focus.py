"""New combined hypotheses derived from the completed four-lineup range screen."""
from binding import CONTRACTS
from coached_range import STUDY as PARENT, make as range_make
from policy_ir import digest,refresh_grounding

STUDY=PARENT.parent/'focus-followup'
VARIANTS={'team_lane':(330000,12),'lich_range':(300000,12),
          'tower_focus':(330000,5),'combined':(300000,5)}


def make(name):
    parent=range_make('outer');p=range_make('outer');p['id']='gota_coached_focus_'+name
    safe,defense=VARIANTS[name]
    p['skill']['observe']={'operator':'coached_focus','parameters':CONTRACTS['coached_focus'].defaults()|{'safe_range':safe,'siege_defense_tiles':defense}}
    p['goal']['G_fort']['preference']='Commit all allied copies to the physical top lane (red normalized2, blue normalized0); destroy its exposed towers and then the exposed fort. Mobile enemies only interrupt for local defense. Do not require clearing all lanes or barracks before the fort.'
    ref=PARENT/'screen/result.json'
    p['belief']['claims']['B_lane_focus']={'claim':'The completed range screen won three of four fixed lineups with either mirrored lane, with complementary color weaknesses. Test a team-specific lane commitment, plus optional Lich range permission and narrower siege-defense radius. This is an adaptive combined hypothesis; the four-lineup screen is not broad competitive evidence.', 'status':'untested','evidence':[{'artifact':str(ref),'sha256':digest(ref.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Coached team lane and siege focus: '+name,needs_review=['belief/B_lane_focus','belief/B_safe_range','goal/G_fort'])
    refresh_grounding(p);return p
