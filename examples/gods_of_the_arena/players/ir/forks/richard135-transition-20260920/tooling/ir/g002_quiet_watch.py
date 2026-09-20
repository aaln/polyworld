"""Narrow quiet-state followup after broad perimeter/spread failed hosted."""
from copy import deepcopy
import sys
import g002_watch as broad
from binding import CONTRACTS
from policy_ir import read,digest,refresh_grounding
STUDY=broad.STUDY/'quiet-followup'
PARENT=broad.PARENT
VARIANTS=('deployed','narrow20','narrow30')


def make(name):
    parent=read(PARENT/'policy.ir.json')
    if name=='deployed':return parent
    assert name in VARIANTS
    p=deepcopy(parent);p['id']='gota_red_'+name
    o=p['skill']['observe'];o['operator']='lineup_quiet_watch'
    o['parameters']={k:o['parameters'].get(k,v[0]) for k,v in CONTRACTS[o['operator']].parameters.items()}
    o['parameters']['redbranch_watch_quiet']=24*int(name[6:])
    p['goal']['G_defense']['preference']+=' Red: after '+name[6:]+' seconds of quiet after arriving, resume ordinary offense while retaining the original defensive threat lease and single-survivor recall. Transfer dead anchors home. Original target ranges and rally geometry are unchanged. Blue is unchanged.'
    p['belief']['claims']['B_red_quiet']={'status':'untested','claim':'Broad perimeter/spread/watch30 failed3/40RED versus20/40. A fully reconstructed loss never entered watchAdvance; isolate quiet advance while preserving original engagement and navigation. No claim that this narrower change wins yet.','evidence':[{'artifact':str(STUDY/'prospective.json'),'sha256':digest((STUDY/'prospective.json').read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Narrow red quiet watch: '+name)
    refresh_grounding(p);return p

if __name__=='__main__':
    broad.STUDY=STUDY;broad.VARIANTS=VARIANTS;broad.make=make
    broad.local(819300) if sys.argv[1]=='local' else broad.remote()
