"""Pinned target matches, shared budget, exact replay audits and separate scores."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'week20260921'))
import hosted as h

PREVIOUS=h.STUDY
h.STUDY=STUDY=h.ROOT/'tmp/gota-targets-20260922'
h.CYCLE='interactive-targets-20260922-01'
BASELINE='9fc7f72e-0489-48f5-a5d3-c53fca44cff4'

def setup():
    (STUDY/'bin').mkdir(exist_ok=True)
    for name in ('episode','command-hash'):
        p=STUDY/'bin'/name
        if not p.exists():p.symlink_to(PREVIOUS/'bin'/name)

def reserve(c,body,out):
    """Cache only complete terminal requests; unknown states never permit spend."""
    with h.research.lock(h.CAMPAIGN/'xp-create.lock'):
        h.live(c)
        assert h.read(h.CAMPAIGN/'service.json')['state']=='paused'
        cfg=h.research.config(h.CAMPAIGN)
        journal=h.read(h.CAMPAIGN/'xp-ledger.json')
        cache_path=STUDY/'terminal-requests.json'
        cache=h.read(cache_path) if cache_path.exists() else {}
        check=[]
        for entry in journal.values():
            path=Path(entry['output'])/'created.json'
            assert path.exists(), 'Unreconciled reservation: '+str(path)
            ident=h.read(path)['id']
            if cache.get(ident,{}).get('games')!=entry['episodes']:
                check.append((ident,entry['episodes']))
        def status(item):
            ident,n=item;eps=h.episodes(c,ident)
            terminal=len(eps)==n and all(e['status'] in ('completed','failed','cancelled','error') for e in eps)
            return ident,n,terminal
        active=0
        with ThreadPoolExecutor(4) as pool:
            for ident,n,terminal in pool.map(status,check):
                if terminal:cache[ident]={'games':n,'terminal':True,'checked_at':h.research.now()}
                else:active+=1
        h.write(cache_path,cache)
        assert active<cfg['max_parallel_xp'] or (out/'created.json').exists()
        assert 40<=body['num_episodes']<=200
        assert body['target']=={'coworld_id':h.GAME,'variant_id':'competition'}
        expected={k:v for k,v in h.read(STUDY/'canonical-game.json')['manifest']['variants'][0]['game_config'].items() if k not in ('seed','players','tokens')}
        assert body['game_config_overrides']==expected
        h.create(c,body,out,dry_run=True)
        with h.research.lock(h.CAMPAIGN/'budget.lock'):
            journal=h.read(h.CAMPAIGN/'xp-ledger.json');key=body['idempotency_key']
            if key in journal:
                assert journal[key]['body_sha256']==h.research.fingerprint(body)
                assert journal[key]['output']==str(out.resolve())
            else:
                day=h.research.now()[:10]
                assert sum(r['episodes'] for r in journal.values() if r['day']==day)+body['num_episodes']<=cfg['daily_episode_limit']
                assert sum(r['episodes'] for r in journal.values() if r['cycle']==h.CYCLE)+body['num_episodes']<=cfg['cycle_episode_limit']
                journal[key]={'day':day,'cycle':h.CYCLE,'episodes':body['num_episodes'],'body_sha256':h.research.fingerprint(body),'output':str(out.resolve()),'reserved_at':h.research.now(),'new_release':h.VERSION,'engine':h.COMMIT}
                h.research.write(h.CAMPAIGN/'xp-ledger.json',journal)
        return h.create(c,body,out)

def prepare(label,version,source_path):
    path=STUDY/label/'plan.json'
    if path.exists():return h.read(path)
    assert h.read(STUDY/'preflight/result.json')['passed']
    source=Path(source_path).resolve();source_hash=h.sha(source.read_bytes())
    targets={m['player']['name'].lower():m['policy_version'] for m in h.read(STUDY/'memberships.json') if m['player']['name'].lower() in ('relh','jordan','richard')}
    cfg={k:v for k,v in h.read(STUDY/'canonical-game.json')['manifest']['variants'][0]['game_config'].items() if k not in ('seed','players','tokens')}
    arms=[]
    for name in ('relh','jordan','richard'):
        for side in (0,1):
            rival=targets[name]['id'];roster=[version if i//5==side else rival for i in range(10)]
            arm={'name':label,'target':name,'side':side,'version':version,'opponent':rival,'roster':roster,'games':40}
            body={'idempotency_key':'gota-targets0922-'+label+'-'+name+'-'+str(side)+'-'+source_hash[:10],
              'target':{'coworld_id':h.GAME,'variant_id':'competition'},'game_config_overrides':cfg,'num_episodes':40,
              'roster':[{'slot':i,'player':{'policy_ref':v}} for i,v in enumerate(roster)],
              'notes':'Frozen target matchup, both colors, uniform teams. Fort gate >=30/40; score gate strictly greater and >=1.10x opponent mean, each cell. All ten VMs and full replays audited; correlated trajectories. No league selection.'}
            folder=STUDY/label/name/str(side)
            h.freeze(folder/'arm.json',arm);h.freeze(folder/'request.json',body);arms.append(arm)
    plan={'label':label,'version':version,'source_sha256':source_hash,'source':str(source),'game':h.VERSION,'engine':h.COMMIT,'targets':targets,'games':240,'arms':arms,
      'decision_rule':'No invalid VMs or audit failures. Fort qualification >=30/40 wins in all six cells. Score qualification own mean > opponent mean and >=1.10x in every cell. Report separately; no broad-field qualification.'}
    h.freeze(path,plan);return plan

def collect(c,arm,folder,ep):
    row=h.collect(c,arm,folder,ep)
    if 'score' in row:
        out=folder/'artifacts'/ep['id'];actual=h.read(out/'results.json')
        other=range((1-arm['side'])*5,(1-arm['side'])*5+5)
        row={**row,'opponent_score':sum(actual['scores'][s] for s in other)/5}
        h.write(out/'matched-result.json',row)
    return row

def run(plan):
    with h.research.lock(STUDY/'hosted.lock',blocking=False),h.client() as c:
        for arm in plan['arms']:
            folder=STUDY/plan['label']/arm['target']/str(arm['side'])
            if (folder/'result.json').exists():continue
            receipt=folder/'batch/created.json'
            ident=h.read(receipt)['id'] if receipt.exists() else reserve(c,h.read(folder/'request.json'),folder/'batch')
            print(json.dumps({'target':arm['target'],'side':arm['side'],'request':ident}),flush=True)
            while True:
                eps=h.episodes(c,ident);h.write(folder/'episodes.json',eps)
                done=[e for e in eps if e['status'] in ('completed','failed','cancelled','error')]
                with ThreadPoolExecutor(4) as pool:rows=list(pool.map(lambda e:collect(c,arm,folder,e),done))
                h.write(folder/'progress.json',{'audited':len(rows),'total':len(eps),'rows':rows})
                if len(rows)==40:break
                print(json.dumps({'target':arm['target'],'side':arm['side'],'audited':len(rows)}),flush=True)
                time.sleep(10)
            result={'arm':arm,'games':40,'invalid':sum(not r['valid'] for r in rows),'wins':sum(r.get('win',0) for r in rows),'losses':sum(r.get('loss',0) for r in rows),'draws':sum(r.get('draw',0) for r in rows),'own_score':sum(r.get('score',0) for r in rows)/40,'opponent_score':sum(r.get('opponent_score',0) for r in rows)/40,'rows':rows}
            result['fort_passed']=result['invalid']==0 and result['wins']>=30
            result['score_passed']=result['invalid']==0 and result['own_score']>result['opponent_score'] and result['own_score']>=1.1*result['opponent_score']
            h.write(folder/'result.json',result)
            print(json.dumps({k:v for k,v in result.items() if k not in ('arm','rows')}),flush=True)
        results=[h.read(STUDY/plan['label']/a['target']/str(a['side'])/'result.json') for a in plan['arms']]
        h.write(STUDY/plan['label']/'result.json',{'complete':True,'fort_passed':all(x['fort_passed'] for x in results),'score_passed':all(x['score_passed'] for x in results),'results':results})

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--label',default='baseline');parser.add_argument('--version',default=BASELINE);parser.add_argument('--source',default=str(h.ROOT/'examples/gods_of_the_arena/players/ir/forks/week20260921/policy.bas'));parser.add_argument('--prepare-only',action='store_true');args=parser.parse_args()
    setup();plan=prepare(args.label,args.version,args.source)
    if not args.prepare_only:run(plan)
