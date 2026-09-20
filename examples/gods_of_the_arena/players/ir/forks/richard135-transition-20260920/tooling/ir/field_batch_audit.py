"""Verify one completed N-episode cohort; never infer a paired treatment effect."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from policy_ir import read,write,digest
from hosted_wave_audit import verify

def main():
    ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);ap.add_argument('--workers',type=int,default=4)
    a=ap.parse_args();d=a.directory.resolve();plan=read(d/'plan.json');collection=read(d/'collection.json');binary=d/'audit'
    folders=[p.parent for p in (d/'artifacts').glob('*/.done')]
    if len(folders)!=collection['episodes']:raise ValueError('Incomplete collection')
    sha=digest(binary.read_bytes())
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        fs=[pool.submit(verify,f,binary,sha) for f in folders]
        for n,f in enumerate(as_completed(fs),1):f.result();print(f'Field replay audits: {n}/{len(fs)} verified',flush=True)
    rows=[]
    for folder in folders:
        ep,result,audit=[read(folder/n) for n in ['episode.json','results.json','audit.json']]
        if [h['total_xp'] for h in audit['heroes']]!=result['total_xp']:raise ValueError('Lifetime XP disagreement')
        slot=ep['policy_version_ids'].index(plan['policy_version']);h=audit['heroes'][slot]
        rows.append({'episode':ep['id'],'slot':slot,'class':h['class'],'win':h['score'],
                     'deaths':h['deaths'],'ticks':result['ticks'],'timeout':result['outcome']=='time_limit',
                     'xp':h['total_xp'],'glory':h['score']*(h['total_xp']-100*result['ticks']/1440),
                     'first_gear_tick':h['first_gear_tick']})
    write(d/'audited-result.json',{'request':collection['request_count'],'episodes':len(rows),'audited':len(rows),
          'policy_version':plan['policy_version'],'game_version':plan['game_version'],'rung':'directional field cohort',
          'promotion_eligible':False,'wins':sum(r['win'] for r in rows),'timeouts':sum(r['timeout'] for r in rows),
          'mean_glory':sum(r['glory'] for r in rows)/len(rows),'deaths':sum(r['deaths'] for r in rows),
          'bought_equipment_cases':sum(r['first_gear_tick']>=0 for r in rows),'rows':rows})
    print('Complete: '+str(d/'audited-result.json'),flush=True)
if __name__=='__main__':main()
