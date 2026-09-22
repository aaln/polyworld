"""Read-only current-version VM checks; never use these as matchup evidence."""
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'week20260921'))
import hosted as h

ROOT=h.ROOT
STUDY=ROOT/'tmp/gota-targets-20260922'

def main():
    members=h.read(STUDY/'memberships.json')
    targets={m['player']['name'].lower():m for m in members if m['player']['name'].lower() in ('relh','jordan','richard')}
    selected={}
    for name,m in targets.items():
        v=m['policy_version']['id'];coverage=Counter()
        for e in h.read(STUDY/'preflight'/name/'episodes.json')['entries']:
            if e['status']!='completed' or e['coworld_id']!=h.GAME:continue
            own=[i for i,x in enumerate(e['policy_version_ids']) if x==v]
            if not any(coverage[i//5]<3 for i in own):continue
            selected[e['id']]=e;coverage.update(i//5 for i in own)
    h.freeze(STUDY/'preflight/plan.json',{'episodes':list(selected),'minimum_each_color':3,'scope':'Existing current-version VM health only, not competitive qualification'})
    def fetch(e):
        p=STUDY/'preflight/artifacts'/e['id'];h.freeze(p/'episode-list-row.json',e)
        with h.client() as c:
            full=h.get(c,'/v2/episode-requests/'+e['id'])
            assert full['coworld_version']==h.VERSION
            h.write(p/'episode.json',full)
            status=h.get(c,'/v2/episode-requests/'+e['id']+'/artifacts/player-status')
        h.write(p/'player-status.json',status)
        return e,status
    counts={};failures=[]
    versions={m['policy_version']['id']:name for name,m in targets.items()}
    with ThreadPoolExecutor(4) as pool:
        for e,status in pool.map(fetch,selected.values()):
            for s in status['players']:
                v=e['policy_version_ids'][s['slot']]
                if v not in versions:continue
                key=versions[v],s['slot']//5
                row=counts.setdefault(key,{'target':key[0],'side':key[1],'version':v,'games':0,'failures':0})
                row['games']+=1;row['failures']+=s.get('exit_code')!=0
                if s.get('exit_code')!=0:failures.append({'episode':e['id'],'version':v,**s})
    passed=len(counts)==6 and all(r['games']>=3 and not r['failures'] for r in counts.values())
    result={'passed':passed,'rows':list(counts.values()),'failures':failures}
    h.write(STUDY/'preflight/result.json',result)
    print(result)

if __name__=='__main__':main()
