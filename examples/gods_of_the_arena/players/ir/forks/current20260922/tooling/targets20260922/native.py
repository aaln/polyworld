"""Responsive native screens; candidate selection only, no hosted verdict."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'week20260921'))
import local

STUDY=local.ROOT/'tmp/gota-targets-20260922'
local.STUDY=STUDY

def run(case):
    row=local.run_case(case)
    if row['valid']:
        live=json.loads((STUDY/'local'/case['name']/str(case['seed'])/str(case['side'])/'live.json').read_text())
        scores=[max(0,h['xp']-200*live['ticks']/1440) for h in live['heroes']]
        side=case['side']
        row={**row,'own_score':sum(scores[side*5:side*5+5])/5,'opponent_score':sum(scores[(1-side)*5:(1-side)*5+5])/5,'runtime_margin':row['max_instructions']<=19000 and row['max_work']<=50000}
    return row

if __name__=='__main__':
    plan=json.loads((STUDY/'local-plan.json').read_text())
    with ThreadPoolExecutor(2) as pool:rows=list(pool.map(run,plan['cases']))
    local.write(STUDY/'local-result.json',{'rows':rows,'complete':len(rows)==len(plan['cases'])})
