"""Require observed depleted pressure plus allied assembly before splitting."""
from copy import deepcopy
import sys
import g002_watch as workflow
import coach_split as first
from binding import CONTRACTS
from policy_ir import read, digest, refresh_grounding

STUDY=first.STUDY/'assembled-followup'
VARIANTS=('deployed','assembled5','assembled15')


def make(name):
    if name=='deployed': return first.make(name)
    assert name in VARIANTS
    p=first.make('supports');parent=deepcopy(p)
    p['id']='gota_coached_'+name
    s=p['skill']['observe'];s['operator']='lineup_coached_assembled'
    s['parameters']={k:s['parameters'].get(k,v[0]) for k,v in CONTRACTS[s['operator']].parameters.items()}
    s['parameters']['redbranch_split_quiet']=24*int(name[9:])
    p['situation']['notes']+=' Followup: at least3friendly living heroes within28home, fewer3visible living enemies within60home, and nonewithin10home must hold for '+name[9:]+'seconds. This revises the rejected anchor-contact predicate.'
    p['belief']['claims']['B_coached_split']={'status':'untested','claim':'Initial split fired while5enemies were advancing between towers. Requiring allied assembly and a depleted observed assault may preserve defense while releasing3heroes forcenterpressure. Test both mechanism and hostedwins.','evidence':[{'artifact':str(STUDY/'prospective.json'),'sha256':digest((STUDY/'prospective.json').read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Assembly-qualified split '+name)
    refresh_grounding(p);return p


if __name__=='__main__':
    workflow.STUDY=STUDY;workflow.VARIANTS=VARIANTS;workflow.make=make
    workflow.local(819600) if sys.argv[1]=='local' else workflow.remote()
