"""Minute snapshots and typed kill events in the prospectively selected effect subset."""
from pathlib import Path
import argparse,json,statistics
p=argparse.ArgumentParser();p.add_argument('--trial',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
read=lambda p:json.loads(p.read_text())
plan=read(a.trial/'effects-plan.json');rows=[]
for c in plan['cases']:
    d=read(a.trial/'effects'/c['episode']/'audit.json');own=c['slot'];rival=0 if c['side'] else 5
    early=[e for e in d['moments'] if e['kind']=='hero_kill' and e['tick']<=3*1440]
    allkills=[e for e in d['moments'] if e['kind']=='hero_kill']
    row={**c,'class':d['heroes'][own]['class'],'rival_class':d['heroes'][rival]['class'],'first_minute_own_level':d['frames'][0]['heroes'][own]['level'],'first_minute_rival_level':d['frames'][0]['heroes'][rival]['level'],'first_minute_own_xp':d['frames'][0]['heroes'][own]['xp'],'first_minute_rival_xp':d['frames'][0]['heroes'][rival]['xp'],'own_kills_first3min':sum(e['actor']==own for e in early),'rival_kills_first3min':sum(e['actor']==rival for e in early),'rival_kills_own_first3min':sum(e['actor']==rival and e['target']==own for e in early),'rival_kills_teammates_first3min':sum(e['actor']==rival and e['target']//5==c['side'] and e['target']!=own for e in early),'first_own_kill_tick':next((e['tick'] for e in allkills if e['actor']==own),None),'first_rival_kill_tick':next((e['tick'] for e in allkills if e['actor']==rival),None)}
    rows.append(row)
cells=[]
for name,side in dict.fromkeys((r['name'],r['side']) for r in rows):
    rr=[r for r in rows if r['name']==name and r['side']==side]
    keys=[k for k in rr[0] if k.startswith(('first_minute','own_kills','rival_kills'))]
    cells.append({'name':name,'side':side,'games':len(rr),'means':{k:statistics.mean(r[k] for r in rr) for k in keys}})
result={'scope':'Retrospective truth in the first4lexical UUIDs per arm chosen before effect analysis. Not policy-observed features, matched trajectories, or independent competitive evidence. Ticks include draft. Earlier contact alone is not the selection metric.','cells':cells,'rows':rows}
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(cells,indent=2))
