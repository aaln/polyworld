"""Summarize source-verified macro tapes; command counts are not damage counts."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
from policy_ir import digest, write
from release_workspace import RUN, ROOT

def summarize(lines):
    header = json.loads(next(lines)); buildings = {b['id']: b for b in header['buildings']}
    hp = {i:b['hp'] for i,b in buildings.items()}
    counts = [Counter(),Counter()]; losses=[]; frames=[]; summary=None
    for line in lines:
        row=json.loads(line)
        if row['type']=='action' and row['kind']==2:
            target=row['first']; kind=buildings[target]['kind'] if target in buildings else 'Hero' if 100<=target<110 else 'Creep'
            counts[row['slot']//5][kind]+=1
        elif row['type']=='frame':
            for b in row['buildings']:
                if b['hp']<=0<hp[b['id']]:
                    losses.append({'observed_by_tick':row['tick'],'id':b['id'],'kind':b['kind'],'team':b['team'],'lane':b['lane'],'tier':b.get('tier')})
                hp[b['id']]=b['hp']
            frames.append({'tick':row['tick'],'heroes':[{k:v for k,v in h.items() if k!='visible_post_tick'} for h in row['heroes']]})
        elif row['type']=='summary': summary=row
    if summary is None or summary['hash_mismatches']: raise ValueError('Replay incomplete')
    return {'commands':counts,'building_losses':losses,'summary':summary,'frames':frames}

def run():
    root=RUN/'lich-followup/rival-matchups/codex_lanes'; out=RUN/'r3/macro-survey';out.mkdir(exist_ok=True)
    cases=[(color,p) for color in ['red','blue'] for p in sorted((root/color/'artifacts').iterdir())[:4]]
    def one(case):
        color,p=case; replay=p/'replay.bin'
        process=subprocess.Popen([str(RUN/'r3/macro-replay'),'--replay',str(replay)],cwd=ROOT,stdout=subprocess.PIPE,text=True)
        try: data=summarize(iter(process.stdout)); assert process.wait()==0
        finally:
            if process.poll() is None: process.kill();process.wait()
        data.update(episode=p.name,our_team=0 if color=='red' else 1,replay_sha256=digest(replay.read_bytes()))
        write(out/(p.name+'.json'),data); return data
    with ThreadPoolExecutor(2) as pool: rows=list(pool.map(one,cases))
    result={'selection':'First four lexicographically sorted episode IDs per color; 8 of the completed 80 losses, selected without inspecting their contents.',
        'instrument_sha256':digest(Path(__file__).read_bytes()),'decoder_sha256':digest((RUN/'r3/macro-replay').read_bytes()),
        'warning':'Attack request counts do not measure landed damage. Destruction timing sampled at 120 ticks.',
        'episodes':[{k:v for k,v in r.items() if k!='frames'} for r in rows]}
    write(out/'result.json',result)
    for side in ['ours','rival']:
        counts=Counter()
        for r in rows: counts.update(r['commands'][r['our_team'] if side=='ours' else 1-r['our_team']])
        print(side,dict(counts))
if __name__=='__main__':run()
