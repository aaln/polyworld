"""Summarize exact color-separated scores and repeated command streams."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import argparse
import json
from pathlib import Path
import subprocess
from hosted import STUDY, read, write, sha

def one(path):
    out=path.parent/'command-hash.json'
    if not out.exists():
        p=subprocess.run([str(STUDY/'bin/command-hash'),str(path.parent/'replay.bin')],capture_output=True,text=True,check=True)
        write(out,json.loads(p.stdout))
    return path.parent.name,read(out)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--kind',choices=('hosted','field'),default='hosted')
    kind=parser.parse_args().kind
    cells=[]
    for folder in sorted((STUDY/kind).glob('*/*')):
        path=folder/'result.json'
        if not path.exists():continue
        result=read(path)
        with ThreadPoolExecutor(4) as pool:
            hashes=dict(pool.map(one,folder.glob('artifacts/*/result.json')))
        counts=Counter(h['canonical_commands_sha1'] for h in hashes.values())
        write(folder/'trajectory-correlation.json',{'streams':hashes,'counts':dict(counts),
          'distinct':len(counts),'games':len(hashes),'interpretation':'Complete command streams may repeat across generated seeds; distinct streams are not necessarily independent.'})
        metrics=('games','mean_score','invalid','subject_invalid','wins','losses','draws') if kind=='hosted' else ('games','mean_score_all','mean_score_clean','clean_games','subject_invalid','tainted')
        own=result['arm'].get('own_slots',list(range(result['arm']['side']*5,result['arm']['side']*5+5)))
        subjects=[]
        for audit_path in folder.glob('artifacts/*/audit.json'):
            audit=read(audit_path)
            for slot in own:
                hero=audit['heroes'][slot]
                subjects.append({k:hero[k] for k in ('class','level','xp','deaths','gold','ranks')})
        observed={'hero_games':len(subjects),'drafted_classes':dict(Counter(h['class'] for h in subjects)),
          'mean_terminal':{k:sum(h[k] for h in subjects)/max(1,len(subjects)) for k in ('level','xp','deaths','gold')},
          'heroes_with_upgrades':sum(sum(h['ranks'])>0 for h in subjects)}
        cells.append({'name':result['arm']['name'],'side':result['arm']['side'],
          **{k:result[k] for k in metrics},
          'distinct_command_streams':len(counts),'observed':observed,
          'failed_versions':dict(Counter(result['arm']['roster'][slot] for row in result['rows'] for slot in row.get('failed_slots',[])))})
    write(STUDY/('review.json' if kind=='hosted' else 'field-review.json'),{'cells':cells,'complete':len(cells)==4,
      'score':('mean over five subject heroes: ' if kind=='hosted' else 'one subject hero: ')+'max(0, XP - 200 * elapsed world ticks / 1440)',
      'limits':'Fixed rosters, correlated trajectories; universal leaderboard superiority not established.'})
    print(json.dumps(cells,indent=2))

if __name__=='__main__':main()
