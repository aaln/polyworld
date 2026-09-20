"""Allow idle support defenders to join the attack; retain real rear threats."""
from copy import deepcopy
import sys
import g002_watch as workflow
import coach_assembled as previous
from binding import CONTRACTS
from policy_ir import read,digest,refresh_grounding

STUDY=previous.STUDY.parent/'mobile-followup'
VARIANTS=('deployed','mobile30','mobile45')


def make(name):
    if name=='deployed': return previous.make(name)
    assert name in VARIANTS
    p=previous.make('assembled15');parent=deepcopy(p);p['id']='gota_coached_'+name
    s=p['skill']['observe'];s['operator']='lineup_coached_mobile'
    s['parameters']={k:s['parameters'].get(k,v[0]) for k,v in CONTRACTS[s['operator']].parameters.items()}
    s['parameters']['redbranch_rear_radius']=int(name[6:])
    p['goal']['G_defense']['preference']='After defending, allocate at most two support rear guards only while nearby visible hero or core-creep pressure warrants it. Otherwise supports join the three attackers on center offense. Fresh three-hero near-home pressure recalls all. Preserve blue and original red first-rush combat.'
    p['situation']['notes']='Coaching session2026-09-18t23-13-38-249zf154ac, actualepisode0806a449 onpublished.5. Start split after15seconds withfewer3livingvisible enemyheroeswithin60home, nonewithin10home, and3friendlyheroeswithin28home. Once split, rear coverage requires actualhero within'+name[6:]+'home or recentenemycreepwithin14home; otherwiseall5attack. Missing remains unobserved, notdead.'
    p['belief']['claims']['B_coached_split']={'status':'untested','claim':'Keeping two supports idle allgame caused draws despite offensive lane progress. Use two as an upperbound and let supports contribute when rear pressure is absent; restoreteamdefense against returning3heroformation.','evidence':[{'artifact':str(STUDY/'prospective.json'),'sha256':digest((STUDY/'prospective.json').read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Pressure-dependent rear guard '+name)
    refresh_grounding(p);return p


if __name__=='__main__':
    workflow.STUDY=STUDY;workflow.VARIANTS=VARIANTS;workflow.make=make
    workflow.local(819700) if sys.argv[1]=='local' else workflow.remote()
