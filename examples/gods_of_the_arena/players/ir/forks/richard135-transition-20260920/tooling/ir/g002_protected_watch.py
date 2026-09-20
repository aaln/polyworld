"""Counterpush while the core is covered; assign sentries to an endangered god."""
from copy import deepcopy
import sys
import g002_watch as broad
from binding import CONTRACTS
from policy_ir import read,digest,refresh_grounding
STUDY=broad.STUDY/'protected-followup'
PARENT=broad.PARENT
VARIANTS=('deployed','guard20','guard30')

def make(name):
    parent=read(PARENT/'policy.ir.json')
    if name=='deployed':return parent
    assert name in VARIANTS
    p=deepcopy(parent);p['id']='gota_red_'+name
    o=p['skill']['observe'];o['operator']='lineup_protected_watch'
    o['parameters']={k:o['parameters'].get(k,v[0]) for k,v in CONTRACTS[o['operator']].parameters.items()}
    o['parameters']['redbranch_watch_quiet']=24*int(name[5:])
    p['goal']['G_defense']['preference']+=' Red: resume pushing after '+name[5:]+' seconds of quiet after arriving, while retaining survivor recall. Once assigned, three sentries may advance only while both god guard towers have at least975HP. Otherwise immediately rally at the god and cover nearby visible enemies; two attackers keep pushing. Preserve original combat ranges and navigation. Blue unchanged.'
    p['belief']['claims']['B_red_protected_watch']={'status':'untested','claim':'Unconditional narrow quietadvance lost to a creep-only god attack with allheroes faraway. Test quietadvance bounded by friendly coreguard health, retaining single-survivor recall and bringing sentries directly home when protection degrades.','evidence':[{'artifact':str(STUDY/'prospective.json'),'sha256':digest((STUDY/'prospective.json').read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Protected red quiet watch: '+name)
    refresh_grounding(p);return p

if __name__=='__main__':
    broad.STUDY=STUDY;broad.VARIANTS=VARIANTS;broad.make=make
    broad.local(819400) if sys.argv[1]=='local' else broad.remote()
