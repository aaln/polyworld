"""Revalidate the coached macro on the live two-guard release."""
from binding import CONTRACTS
from coached_range import make as range_make
from policy_ir import digest,refresh_grounding
from release_workspace import RUN,VERSION,SOURCE

STUDY=RUN/'coached-lanes/r5-guards'
VARIANTS={'outer':(2,2,330000,12),'reverse':(0,0,330000,12),
          'team':(2,0,330000,12),'lich':(2,0,300000,12),
          'focus':(2,0,300000,5)}


def make(name):
    parent=range_make('outer');p=range_make('outer');p['id']='gota_coached_guards_'+name
    red,blue,safe,defense=VARIANTS[name]
    p['execution']['game_version']=VERSION
    p['skill']['observe']={'operator':'coached_guards','parameters':CONTRACTS['coached_guards'].defaults()|{'primary_lane':red,'blue_lane':blue,'safe_range':safe,'siege_defense_tiles':defense}}
    p['goal']['G_fort']['preference']='Win by destroying the enemy god. Commit to the assigned lane until a breach exposes god guards; destroy both guards with shared target selection, then immediately finish the exposed god. Other lanes and barracks are optional. Local defense protects the push; no global champion hunting.'
    p['goal']['G_base']['preference']='Observed exposed god first, then exposed guards, then the committed lane tower; local mobile threats interrupt according to the configured siege-defense radius.'
    p['goal']['G_wave']['preference']='Persist in one assigned lane. Melee attacks towers with creep cover; qualifying ranged heroes may siege while not targeted. Lane rotation is disabled in these candidates because one breach is enough to expose the guards.'
    p['goal']['G_cadence']['preference']='Retain class combat recovery and purchasing. Resume the committed lane route when no visible objective or local blocker and no recovery movement exists.'
    evidence=RUN/'coached-lanes/live-change.json'
    p['belief']['claims']['B_guard_release']={'claim':f'Live{VERSION}, source{SOURCE}: two gate-stat godguards added. Any cleared lane exposes guards; both must die before the god is vulnerable. Earlier .3 win outcomes do not validate this release. Ranged geometry and melee support remain hypotheses requiring freshgames.', 'status':'supported','evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Coaching plus live guard objective chain: '+name,needs_review=['belief/B_candidate','belief/B_safe_range','goal/G_fort'])
    refresh_grounding(p);return p
