"""Read-only replay59 audit of the coached khors179 game and a fixed recent sample."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import gzip,json,subprocess,hashlib,shutil
import return_hosted as study
h=study.h
RAW=study.ROOT.parent/'polyworld/tmp/gota-khors179-audit-20260923'
VERSION='346416a0-78f9-401f-b0d3-fed3f840af8d'
FOCAL='ereq_e3471c64-b38e-4bfc-927e-e0e3f3076d9d'
BIN=study.STUDY/'bin'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def collect(c,ep):
    out=RAW/'episodes'/ep['id'];out.mkdir(parents=True,exist_ok=True)
    if ep['id']==FOCAL:
        for n in ['episode.json','results.json','game.log','replay.bin','player-status.json','spec.json','episode-v2.json','economy.json','combat-audit.json','stalls.json','command-hash.json']:
            if (RAW/n).exists() and not (out/n).exists():shutil.copy2(RAW/n,out/n)
    if not (out/'episode.json').exists():h.freeze(out/'episode.json',h.get(c,'/v2/episode-requests/'+ep['id']))
    full=h.read(out/'episode.json');assert full['coworld_id']==h.GAME and full['coworld_version']==h.VERSION
    assert VERSION in full['policy_version_ids']
    for kind,name in [('results','results.json'),('logs','game.log'),('replay','replay.bin'),('player-status','player-status.json'),('spec','spec.json')]:
        p=out/name
        if p.exists():continue
        r=c.get('/v2/episode-requests/'+ep['id']+'/artifacts/'+kind);r.raise_for_status();data=r.content
        if kind=='replay' and data.startswith(b'\x1f\x8b'):data=gzip.decompress(data)
        p.write_bytes(data)
    for name in ['episode-v2','economy','combat-audit','stalls','command-hash']:
        dest=out/(name+'.json')
        if dest.exists():continue
        args=[str(BIN/name),str(out/'replay.bin')] if name=='command-hash' else [str(BIN/name),'--replay',str(out/'replay.bin')]
        p=subprocess.run(args,capture_output=True,text=True,timeout=600);(out/(name+'.stderr.log')).write_text(p.stderr)
        assert p.returncode==0,p.stderr[-1500:];h.freeze(dest,json.loads(p.stdout.splitlines()[-1]))
    a,e,b,r,s=[h.read(out/n) for n in ['episode-v2.json','economy.json','combat-audit.json','results.json','player-status.json']]
    assert a['hash_mismatches']==e['hash_mismatches']==b['hash_mismatches']==0
    assert [x['xp'] for x in a['heroes']]==[x['total_xp'] for x in e['heroes']]==[x['xp'] for x in b['heroes']]==r['total_xp']
    assert [max(0,x*1440-200*r['ticks'])//1440 for x in r['total_xp']]==r['scores']
    slot=full['policy_version_ids'].index(VERSION)
    row={'episode':ep['id'],'slot':slot,'score':r['scores'][slot],'hero':e['heroes'][slot],
         'source_sha256':h.read(out/'spec.json')['players'][slot]['content_hash'],
         'failed_slots':[p['slot'] for p in s['players'] if p.get('exit_code')!=0],
         'ticks':r['ticks'],'all_state_hashes_equal':True,'all_xp_scores_equal':True,
         'hashes':{p.name:sha(p) for p in out.iterdir() if p.is_file() and not p.name.endswith('.log') and p.name!='verified.json'}}
    h.freeze(out/'verified.json',row);print(json.dumps({k:row[k] for k in ['episode','slot','score','failed_slots']}),flush=True);return row

def main():
    listing=study.STUDY/'preflight-listings'/f'{VERSION}.json'
    rows=h.read(listing)['entries']
    eligible=sorted([r for r in rows if r['coworld_id']==h.GAME and r['status']=='completed' and r['id']!=FOCAL],key=lambda r:(r['created_at'],r['id']),reverse=True)[:12]
    plan={'frozen_at':h.research.now(),'selection':'User-selected high-score episode separately, plus up to12 latest other completed khors179 episodes on replay59 from the already captured listing; no outcome filtering. No forecast/proxy or causal claim.','coached_episode':FOCAL,'comparison_episodes':eligible,'listing_sha256':sha(listing),'hosted_games_created':0}
    if (RAW/'plan.json').exists():plan=h.read(RAW/'plan.json')
    else:h.freeze(RAW/'plan.json',plan);shutil.copy2(listing,RAW/'listing.json')
    with h.client() as c,ThreadPoolExecutor(3) as pool:
        result=list(pool.map(lambda ep:collect(c,ep),[{'id':FOCAL}]+plan['comparison_episodes']))
    assert len({r['source_sha256'] for r in result})==1
    h.freeze(RAW/'verified.json',{'rows':result,'plan':plan,'runtime_provenance_sha256':sha(study.STUDY/'runtime-provenance.json')})
if __name__=='__main__':main()
