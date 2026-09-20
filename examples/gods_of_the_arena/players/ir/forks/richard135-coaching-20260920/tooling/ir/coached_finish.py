"""Preserve successful wave behavior and test stronger guard/god priority."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import HERE,read,digest,refresh_grounding
from release_workspace import RUN

STUDY=RUN/'coached-lanes/r5-finish'
VARIANTS={'lich':(7,16,0),'all':(10,16,0),'god':(10,0,0),'weak_guard':(10,16,10)}


def make(name):
    parent=read(HERE/'win_bounded_0916.r5.evaluated.ir.json');p=deepcopy(parent);p['id']='gota_coached_finish_'+name
    cls,guards,hp=VARIANTS[name]
    p['skill']['observe']={'operator':'coached_finish','parameters':CONTRACTS['coached_finish'].defaults()|p['skill']['observe']['parameters']|{'finish_class':cls,'guard_tiles':guards,'guard_hp_weight':hp}}
    p['goal']['G_fort']['preference']='Favor the observed exposed enemy god when near enough to finish. Where configured, prioritize nearby exposed god guards over incidental barracks or distant mobile enemies; keep immediate local defense. Preserve existing wave escort and class combat.'
    ref=RUN/'coached-lanes/r5-lich/screen/result.json'
    p['belief']['claims']['B_finish_coaching']={'claim':'The successful baseline already follows an outer-lane wave in inspectedLich losses. All three Lich routing/combinedobserver variants lost the red local matchups, so that change was rejected. Test only stronger terminal-structure priority while preserving baseline navigation. This incorporates the coached goal of objective finishing without assuming wholesale lane routing is beneficial.', 'status':'untested','evidence':[{'artifact':str(ref),'sha256':digest(ref.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Coached guard/god priority with baseline movement: '+name,needs_review=['belief/B_finish_coaching','goal/G_fort'])
    refresh_grounding(p);return p
