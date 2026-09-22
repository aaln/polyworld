"""New-release hosted comparison with the existing shared budget journal.

No league writes. Canonical game pin is verified independently of the old
research campaign, whose accepted engine/configuration is never overwritten.
"""
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import httpx
import jsonschema

ROOT=Path(__file__).resolve().parents[4]
STUDY=ROOT/'tmp/gota-week-20260921'
ENGINE=ROOT.parent/'polyworld-gota-week-20260921'
CAMPAIGN=ROOT.parent/'gota-autoresearch'
sys.path.insert(0,str(ROOT/'examples/gods_of_the_arena/players/ir'))
sys.path.insert(0,str(ROOT/'tools/gota_autoresearch'))
from hosted_wave import client,get,create,episodes
import researcher as research

GAME='cow_e5445477-d55e-432d-ac38-bd1eae66e6d3'
COMMIT='f776d5e55d439706a8d49878d17d7ba1f6a1f7ce'
VERSION='2026.9.21.5'
CYCLE='interactive-week20260921-01'
INCUMBENT='c2785cd4-433b-46d1-a454-dd29147383ec'
PLAYER='ply_630a768f-d623-44b2-80fa-36968d6fa75a'

def read(p):return json.loads(p.read_text())
def sha(data):return hashlib.sha256(data).hexdigest()
def write(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    q=p.with_name(p.name+'.tmp');q.write_text(json.dumps(obj,indent=2)+'\n');q.replace(p)
def freeze(p,obj):
    if p.exists():assert read(p)==obj,p
    else:write(p,obj)

def live(c):
    league=get(c,'/v2/leagues/league_3c60897b-25cf-4b37-9d1a-8554c1198f28')
    assert league['game']['coworld_id']==GAME
    game=get(c,'/v2/coworlds/'+GAME)
    assert game['version']==VERSION and '/tree/'+COMMIT+'/' in game['manifest']['game']['runnable']['source_url']
    return game

def upload(c,label,source):
    out=STUDY/'uploads'/label
    meta={'name':'aaron-gota-week0921-'+label,'content_hash':sha(source),'size_bytes':len(source),
      'player_id':PLAYER,'attributes':{},'tags':{'game':'gods_of_the_arena','game_version':VERSION,
      'engine_commit':COMMIT,'validation':'Native admitted; inert research upload, hosted quality unvalidated'}}
    freeze(out/'upload-request.json',meta)
    jsonschema.validate(meta,read(STUDY/'openapi.json')['components']['schemas']['PlayerFilePolicyUploadRequest'])
    path=out/'uploaded-version.json'
    if not path.exists():
        r=c.post('/stats/policies/files/upload',json=meta)
        if r.status_code==409:
            r=c.post('/stats/policies/files/complete',json=meta);r.raise_for_status();version=r.json()
        else:
            r.raise_for_status();payload=r.json();version=payload.get('existing_policy_version')
            if version is None:
                r=httpx.put(payload['upload_url'],content=source,headers={'Content-Type':'application/octet-stream'},timeout=120);r.raise_for_status()
                r=c.post('/stats/policies/files/complete',json=meta);r.raise_for_status();version=r.json()
        write(path,version)
    version=read(path)
    assert get(c,'/stats/policy-versions/'+version['id'])['name']==meta['name']
    log=ROOT/'games/gods_of_the_arena/players/week20260921/VERSION_LOG.md'
    text=log.read_text() if log.exists() else '# New-week policy versions\n'
    if version['id'] not in text:
        log.parent.mkdir(parents=True,exist_ok=True)
        text+='\n## '+meta['name']+':v'+str(version['version'])+'\n\n'
        text+='- Version `'+version['id']+'`, source SHA256 `'+meta['content_hash']+'`.\n'
        text+='- Registered '+datetime.now(timezone.utc).isoformat()+'. Engine '+VERSION+' / '+COMMIT+'.\n'
        text+='- '+('New coordinated draft/lane/skill/economy/recovery policy.' if label=='lane' else 'Byte-exact upstream baseline for a fixed opponent.')+' Native validation complete; hosted quality unvalidated. Inert upload; no champion selection.\n'
        log.write_text(text)
    return version

def prepare(c):
    game=live(c)
    source=(STUDY/'candidates/lane/policy.bas').read_bytes()
    assert sha(source)==read(STUDY/'candidates/lane/manifest.json')['source_sha256']
    assert read(STUDY/'scenarios.json')['passed']
    rows=read(STUDY/'lane-local-result.json')['rows']
    assert len(rows)==8 and all(r['valid'] and r['win']==1 and r['max_instructions']<19000 for r in rows)
    assert read(STUDY/'calibration-blue.json')['hash_mismatches']==0
    assert read(CAMPAIGN/'service.json')['state']=='paused','Existing writer must checkpoint before the new-release writer acts'
    candidate=upload(c,'lane',source)
    baseline=upload(c,'baseline',(ENGINE/'examples/gods_of_the_arena/players/base.bas').read_bytes())
    config={k:v for k,v in game['manifest']['variants'][0]['game_config'].items() if k not in ('seed','players','tokens')}
    arms=[]
    for name,version in [('candidate',candidate['id']),('incumbent',INCUMBENT)]:
        for side in (0,1):
            roster=[version if i//5==side else baseline['id'] for i in range(10)]
            arm={'name':name,'side':side,'version':version,'opponent':baseline['id'],'roster':roster,'games':40}
            body={'idempotency_key':'gota-week0921-'+name+'-'+str(side)+'-'+sha(source)[:12],
              'target':{'coworld_id':GAME,'variant_id':'competition'},'game_config_overrides':config,
              'num_episodes':40,'roster':[{'slot':i,'player':{'policy_ref':v}} for i,v in enumerate(roster)],
              'notes':'New-week score A/B. Fixed exact new baseline opponent; candidate versus live compatibility control, '+name+' side '+str(side)+'. Score=max(0,XP-200*ticks/1440), full replay audit; no league selection.'}
            folder=STUDY/'hosted'/name/str(side)
            freeze(folder/'arm.json',arm);freeze(folder/'request.json',body);arms.append(arm)
    plan={'game_version':VERSION,'engine':COMMIT,'source_sha256':sha(source),'cycle':CYCLE,'games':160,
      'arms':arms,'decision_rule':'Mean subject score >=1.10x incumbent on each color, >=1.20x overall; no subject VM failures; every replay/score audited. Repeated streams correlated; not mixed-team qualification.'}
    freeze(STUDY/'hosted-plan.json',plan)
    return plan

def reserve_create(c,body,out):
    # Hold the shared creation lock through the read, budget reservation and POST.
    with research.lock(CAMPAIGN/'xp-create.lock'):
        live(c)
        cfg=research.config(CAMPAIGN)
        ledger=read(CAMPAIGN/'xp-ledger.json')
        active=0
        for row in ledger.values():
            receipt=Path(row['output'])/'created.json'
            if receipt.exists():
                es=episodes(c,read(receipt)['id'])
                active+=any(e['status'] not in ('completed','failed','cancelled','error') for e in es)
        assert active<cfg['max_parallel_xp'] or (out/'created.json').exists()
        create(c,body,out,dry_run=True)
        with research.lock(CAMPAIGN/'budget.lock'):
            ledger=read(CAMPAIGN/'xp-ledger.json');key=body['idempotency_key']
            if key in ledger:
                assert ledger[key]['body_sha256']==research.fingerprint(body)
                assert ledger[key]['output']==str(out.resolve())
            else:
                day=research.now()[:10]
                assert sum(r['episodes'] for r in ledger.values() if r['day']==day)+body['num_episodes']<=cfg['daily_episode_limit']
                assert sum(r['episodes'] for r in ledger.values() if r['cycle']==CYCLE)+body['num_episodes']<=cfg['cycle_episode_limit']
                assert body['target']=={'coworld_id':GAME,'variant_id':'competition'}
                assert body['game_config_overrides']=={k:v for k,v in read(STUDY/'canonical-game.json')['manifest']['variants'][0]['game_config'].items() if k not in ('seed','players','tokens')}
                ledger[key]={'day':day,'cycle':CYCLE,'episodes':body['num_episodes'],'body_sha256':research.fingerprint(body),
                  'output':str(out.resolve()),'reserved_at':research.now(),'new_release':VERSION,'engine':COMMIT}
                research.write(CAMPAIGN/'xp-ledger.json',ledger)
        return create(c,body,out)

def collect(c,arm,folder,ep):
    out=folder/'artifacts'/ep['id'];result_path=out/'result.json'
    if result_path.exists():return read(result_path)
    out.mkdir(parents=True,exist_ok=True)
    full=get(c,'/v2/episode-requests/'+ep['id']);write(out/'episode.json',full)
    assert full['coworld_id']==GAME and full['coworld_version']==VERSION
    assert full['policy_version_ids']==arm['roster']
    if ep['status']!='completed':
        result={'episode':ep['id'],'valid':False,'status':ep['status']};write(result_path,result);return result
    for kind,name in [('results','results.json'),('logs','game.log'),('replay','replay.bin'),('player-status','player-status.json')]:
        path=out/name
        if path.exists():continue
        r=c.get('/v2/episode-requests/'+ep['id']+'/artifacts/'+kind);r.raise_for_status();data=r.content
        if kind=='replay' and data.startswith(b'\x1f\x8b'):data=gzip.decompress(data)
        path.write_bytes(data)
    audit_path=out/'audit.json'
    if not audit_path.exists():
        p=subprocess.run([str(STUDY/'bin/episode'),'--replay',str(out/'replay.bin')],capture_output=True,text=True,timeout=900)
        (out/'audit-stderr.log').write_text(p.stderr)
        assert p.returncode==0,p.stderr[-1000:]
        write(audit_path,json.loads(p.stdout.splitlines()[-1]))
    audit=read(audit_path);actual=read(out/'results.json');status=read(out/'player-status.json')
    assert audit['ticks']==actual['ticks'] and [h['xp'] for h in audit['heroes']]==actual['total_xp']
    for h,score in zip(audit['heroes'],actual['scores']):assert abs(max(0,h['xp']-200*audit['ticks']/1440)-score)<1e-7
    own=arm.get('own_slots',list(range(arm['side']*5,arm['side']*5+5)))
    failed=[p['slot'] for p in status['players'] if p.get('exit_code')!=0]
    result={'episode':ep['id'],'valid':not failed,'failed_slots':failed,
      'subject_valid':not set(failed)&set(own),'score':sum(actual['scores'][s] for s in own)/len(own),
      'win':int(audit['winner']==arm['side']),'loss':int(audit['winner']==1-arm['side']),
      'draw':int(audit['winner']==-1),'seed':actual['seed'],'ticks':actual['ticks'],
      'replay_sha256':sha((out/'replay.bin').read_bytes()),'all_hashes_equal':True}
    write(result_path,result);return result

def main():
    with research.lock(STUDY/'hosted.lock',blocking=False),client() as c:
        plan=prepare(c)
        for arm in plan['arms']:
            folder=STUDY/'hosted'/arm['name']/str(arm['side'])
            if (folder/'result.json').exists():continue
            xreq=reserve_create(c,read(folder/'request.json'),folder/'batch')
            print(json.dumps({'arm':arm['name'],'side':arm['side'],'request':xreq}),flush=True)
            while True:
                es=episodes(c,xreq);write(folder/'episodes.json',es)
                completed=[e for e in es if e['status'] in ('completed','failed','cancelled','error')]
                with ThreadPoolExecutor(4) as pool:
                    rows=list(pool.map(lambda e:collect(c,arm,folder,e),completed))
                write(folder/'progress.json',{'total':len(es),'audited':len(rows),'rows':rows})
                if len(rows)==arm['games']:break
                print(json.dumps({'arm':arm['name'],'side':arm['side'],'audited':len(rows),'total':len(es)}),flush=True)
                time.sleep(10)
            result={'arm':arm,'games':len(rows),'mean_score':sum(r.get('score',0) for r in rows)/len(rows),
              'invalid':sum(not r['valid'] for r in rows),'subject_invalid':sum(not r.get('subject_valid',False) for r in rows),
              'wins':sum(r.get('win',0) for r in rows),'losses':sum(r.get('loss',0) for r in rows),
              'draws':sum(r.get('draw',0) for r in rows),'rows':rows}
            write(folder/'result.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('rows','arm')}),flush=True)
        results=[read(STUDY/'hosted'/a['name']/str(a['side'])/'result.json') for a in plan['arms']]
        candidate=[r for r in results if r['arm']['name']=='candidate'];control=[r for r in results if r['arm']['name']=='incumbent']
        passed=all(r['invalid']==0 for r in results) and all(candidate[i]['mean_score']>=1.1*control[i]['mean_score'] for i in (0,1)) and sum(r['mean_score'] for r in candidate)>=1.2*sum(r['mean_score'] for r in control)
        write(STUDY/'hosted-result.json',{'complete':True,'passed':passed,'results':results,'promotion_qualified':False})

if __name__=='__main__':main()
