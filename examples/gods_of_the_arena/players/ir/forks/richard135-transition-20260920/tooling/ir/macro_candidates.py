"""Independent macro hypotheses, separate from the frozen Lich confirmation."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import read, digest, refresh_grounding
from release_workspace import RUN, SOURCE, VERSION

VARIANTS={
    'bounded': 'Reject pursuit of selected mobile targets beyond12tiles; retain wave navigation and class combat.',
    'lanes': 'Bound pursuit plus explicit mirrored2/1/2lane navigation; retain class combat.',
    'objectives': 'Local mobile targets, stronger exposed structure priority and visible fort finish; retain wave navigation.',
    'objective_lanes': 'Combine objective priority with explicit mirrored2/1/2lane navigation; retain class combat and item buying.',
}

def make(name):
    parent=read(RUN/'r3-study/local/candidates/lich_nearest/policy.ir.json')
    p=deepcopy(parent);p['id']='gota_macro_'+name
    p['situation']['notes']=f'Current {VERSION}, source {SOURCE}; fixed116-tilecompetitionmap. Macro beliefs are untested; prior evidence retains original release.'
    p['skill']['attack']={'operator':'macro_cadence','parameters':parent['skill']['attack']['parameters'] | {'motion_object_limit':80}}
    if name == 'budget_control':
        p['belief']['claims']['B_macro']={'claim':'Dense-observation recovery fallback only; macro decisions unchanged.','status':'untested','evidence':[]}
        p['update']={'revision':parent['update']['revision']+1,'parent':digest(parent),'change':'Skip recovery scans above80objects to preserve VM budget.','needs_review':['goal/G_survival'],'evidence':[]}
        refresh_grounding(p);return p
    op='bounded_pursuit' if name in ['bounded','lanes'] else 'macro_objectives'
    p['skill']['observe']={'operator':op,'parameters':CONTRACTS[op].defaults()}
    if name in ['lanes','objective_lanes']:
        p['skill']['fallback']={'operator':'macro_lanes','parameters':CONTRACTS['macro_lanes'].defaults()}
        p['goal']['G_wave']['preference']='Maintain declared2/1/2lane coverage using public waypoints when no nearby target or accepted recovery movement exists.'
    p['goal']['G_base']['preference']=CONTRACTS[op].meaning
    p['belief']['claims']['B_macro']={'claim':VARIANTS[name]+' Hypothesis: reduce global target chasing and finish objectives earlier. Above80observedobjects all variants skip recovery scans and use ordinary attacks to preserve VM budget; budget_control isolates that shared change. Competitive effect and class survival remain untested.', 'status':'untested','evidence':[]}
    p['update']={'revision':parent['update']['revision']+1,'parent':digest(parent),'change':VARIANTS[name],
       'needs_review':['belief/B_macro','goal/G_base','goal/G_wave','goal/G_fort','goal/G_survival'],'evidence':[]}
    refresh_grounding(p);return p
