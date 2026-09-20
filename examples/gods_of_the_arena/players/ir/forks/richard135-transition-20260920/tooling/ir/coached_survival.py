"""Repair the costly center-lane win using self-defense and health recovery."""
from binding import CONTRACTS
from coached_convoy import make as convoy_make,STUDY as PARENT
from policy_ir import digest,refresh_grounding

STUDY=PARENT.parent/'r5-survival'
VARIANTS={'defend':0,'recover30':30,'recover45':45}


def make(name):
    parent=convoy_make('center');p=convoy_make('center');p['id']='gota_coached_survival_'+name
    p['skill']['observe']['operator']='coached_defense'
    p['skill']['attack']={'operator':'coached_recovery','parameters':p['skill']['attack']['parameters']|{'recover_percent':VARIANTS[name]}}
    p['goal']['G_survival']['preference']='Keep melee tower initiation behind creep cover. Defend against mobile enemies already in personal range even while holding outside a tower. If configured, disengage from nearby threats at low health until healed; retain the lane plan and item purchases. An exposed god remains the immediate winning objective.'
    ref=PARENT/'screen/result.json'
    p['belief']['claims']['B_recovery']={'claim':'Completed center-convoy screen won4/4 against defaults and deployedteams, but caused110teamdeaths, with one default matchup lasting25826ticks. Test in-range self-defense at tower perimeter plus optional health recovery. Center offense is promising; survival and faster closure remain unvalidated.', 'status':'untested','evidence':[{'artifact':str(ref),'sha256':digest(ref.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Coached lane commitment with perimeter self-defense and recovery: '+name,needs_review=['belief/B_recovery','goal/G_survival'])
    refresh_grounding(p);return p
