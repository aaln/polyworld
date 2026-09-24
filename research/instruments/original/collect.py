"""Read-only, outcome-unfiltered current-release league replay collection."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse, gzip, hashlib, json, subprocess, sys

ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT.parent/'polyworld/tmp/gota-khors180-observations-20260924'
sys.path.insert(0, str(ROOT/'games/gods_of_the_arena/instruments/weakhero20260923'))
from weak_hosted import h
BIN = RAW.parent/'gota-lane-neutral62-20260923/bin'
VERSION = '564e4650-5efb-4b66-b9d4-a49070e1e68e'
COW = 'cow_a472c872-2b97-4b81-9961-e171304e5d63'

def cached(c, path, dest):
    if not dest.exists(): h.freeze(dest, h.get(c, path))
    return h.read(dest)

def discover():
    rounds = h.read(RAW/'rounds.json')['entries']
    with h.client() as c, ThreadPoolExecutor(4) as pool:
        def one(r):
            d=cached(c, '/v2/rounds/'+r['id']+'/episode-requests?limit=100',RAW/'round-listings'/(r['id']+'.json'))
            assert not d.get('next_cursor'), 'Paginate before selecting'
            return [dict(e, league_round=r['id'], round_number=r['round_number']) for e in d['entries']]
        groups=list(pool.map(one,rounds[:20]))
    episodes={e['id']:e for g in groups for e in g if e['status']=='completed' and e['coworld_id']==COW}
    plan={'selection':'All completed current-release episodes in the latest20 captured league rounds; fixed before outcomes. Additional recent request corpus is separate, never called league.',
          'created_at':h.research.now(),'episodes':list(episodes.values()),'new_games':0,'jev':'Skipped at user request',
          'authority':'Retrospective replay truth, submitted commands and effects, not private policy source or internal intent.',
          'purpose':'Describe khors180 and diagnose own deployment; no causal score comparison from unpaired league rounds.'}
    h.freeze(RAW/'plan.json',plan)
    print({'league_episodes':len(episodes),'khors':sum(VERSION in e['policy_version_ids'] for e in episodes.values())},flush=True)

def collect(ep):
    folder=RAW/'episodes'/ep['id'];folder.mkdir(parents=True,exist_ok=True)
    with h.client() as c:
        full=cached(c,'/v2/episode-requests/'+ep['id'],folder/'episode.json')
        for kind,name in [('results','results.json'),('replay','replay.bin'),('player-status','player-status.json'),('spec','spec.json')]:
            dest=folder/name
            if not dest.exists():
                r=c.get('/v2/episode-requests/'+ep['id']+'/artifacts/'+kind);r.raise_for_status();data=r.content
                if kind=='replay' and data.startswith(b'\x1f\x8b'): data=gzip.decompress(data)
                dest.write_bytes(data)
    for tool in ['episode','telemetry']:
        dest=folder/('audit.json' if tool=='episode' else tool+'.json')
        if not dest.exists():
            r=subprocess.run([str(BIN/tool),'--replay',str(folder/'replay.bin')],capture_output=True,text=True,timeout=900)
            (folder/(tool+'.stderr')).write_text(r.stderr)
            assert r.returncode==0, r.stderr[-2000:]
            h.freeze(dest,json.loads(r.stdout.splitlines()[-1]))
    a,t,result,status,spec=[h.read(folder/n) for n in ['audit.json','telemetry.json','results.json','player-status.json','spec.json']]
    assert t['hash_mismatches']==a['hash_mismatches']==0
    assert a['ticks']==result['ticks'] and [x['xp'] for x in a['heroes']]==result['total_xp']
    assert [x['total_xp'] for x in t['heroes']]==result['total_xp']
    assert [max(0,x*1440-200*result['ticks'])//1440 for x in result['total_xp']]==result['scores']
    row={'id':ep['id'],'created_at':full['created_at'],'round':ep.get('league_round'),
         'round_number':ep.get('round_number'),'ticks':result['ticks'],'scores':result['scores'],
         'versions':full['policy_version_ids'],'participants':full['participants'],'heroes':t['heroes'],
         'stream':t['canonical_commands_sha1'],'source_hashes':[x['content_hash'] for x in spec['players']],
         'failed_slots':[x['slot'] for x in status['players'] if x.get('exit_code')!=0],
         'replay_sha256':hashlib.sha256((folder/'replay.bin').read_bytes()).hexdigest()}
    h.write(folder/'verified.json',row)
    print(json.dumps({'episode':ep['id'],'round':row['round_number'],'failed':row['failed_slots']}),flush=True)
    return row

def main():
    p=argparse.ArgumentParser();p.add_argument('--discover',action='store_true');args=p.parse_args()
    if args.discover:discover();return
    with ThreadPoolExecutor(4) as pool:rows=list(pool.map(collect,h.read(RAW/'plan.json')['episodes']))
    h.write(RAW/'verified.json',{'rows':rows,'complete':True})

if __name__=='__main__':main()
