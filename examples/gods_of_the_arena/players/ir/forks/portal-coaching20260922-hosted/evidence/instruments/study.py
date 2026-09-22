"""Frozen portal A/B; --prepare never spends hosted games or changes champions."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
from pathlib import Path
import sys
import time
import httpx
import jsonschema

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
STUDY=ROOT.parent/'polyworld/tmp/gota-portals-20260922'
OLD=ROOT.parent/'polyworld/tmp/gota-balance-20260922'
sys.path.insert(0,str(HERE.parent/'balance20260922'))
from environment import h,panel
loader=importlib.util.spec_from_file_location('portal_audit',HERE.parent/'balance20260922/hosted.py')
audit=importlib.util.module_from_spec(loader)
loader.loader.exec_module(audit)
h.STUDY=panel.STUDY=audit.STUDY=STUDY
h.CYCLE='interactive-portals-coaching-20260922'
BASELINE='0dc85085-cb5b-4de6-8d50-e8fd043d0b5f'
SOURCE=STUDY/'candidate-r3/policy.bas'
HASH='db71abb37180a06a432ac71c3c5d6802be2ba2c1b2d782b151336beacd8b1520'


def prepare():
    assert h.sha(SOURCE.read_bytes())==HASH
    assert all(r['passed'] for r in h.read(STUDY/'candidate-r3-practice-v2.json')['rows'])
    assert h.read(STUDY/'candidate-r3-scenarios.json')['passed']
    assert h.read(STUDY/'native-result.json')['passed']
    with h.client() as c:
        game=h.live(c)
        h.freeze(STUDY/'canonical-game.json',game)
        schema=h.get(c,'/openapi.json')
        h.freeze(STUDY/'openapi.json',schema)
        source=SOURCE.read_bytes()
        meta={'name':'aaron-gota-portals0922-r3','content_hash':HASH,'size_bytes':len(source),'player_id':h.PLAYER,'attributes':{},'tags':{'game':'gods_of_the_arena','game_version':h.VERSION,'engine_commit':h.COMMIT,'validation':'72 portal fixtures +126 all-class host checks +8 full native matched control/candidate replays; competitive quality unvalidated. Inert research upload.'}}
        out=STUDY/'upload'
        h.freeze(out/'request.json',meta)
        jsonschema.validate(meta,schema['components']['schemas']['PlayerFilePolicyUploadRequest'])
        if not (out/'version.json').exists():
            r=c.post('/stats/policies/files/upload',json=meta)
            if r.status_code==409:
                r=c.post('/stats/policies/files/complete',json=meta);r.raise_for_status();version=r.json()
            else:
                r.raise_for_status();payload=r.json();version=payload.get('existing_policy_version')
                if version is None:
                    r=httpx.put(payload['upload_url'],content=source,headers={'Content-Type':'application/octet-stream'},timeout=120);r.raise_for_status()
                    r=c.post('/stats/policies/files/complete',json=meta);r.raise_for_status();version=r.json()
            h.write(out/'version.json',version)
        version=h.read(out/'version.json')
        assert h.get(c,'/stats/policy-versions/'+version['id'])['name']==meta['name']
        prior=h.read(OLD/'roster.json')
        # A fixed healthy background panel; refresh the owned Coach seat to its
        # current exact source for both arms. Rival UUIDs remain explicit.
        pool=[m['policy_version']['id'] if m['player']['id']!='ply_594ec24d-d7f3-4370-a000-468354ec41c9' else '35c85505-1977-4bad-b4ea-f1473aaa79dc' for m in prior]
        cfg={k:v for k,v in game['manifest']['variants'][0]['game_config'].items() if k not in ('seed','players','tokens')}
        arms=[]
        for name,ident,sha in [('baseline',BASELINE,'7631fa32fb7ef6725074ad6778f4f94fe1e18ac5018bece1eed40e32cbef9bb8'),('candidate',version['id'],HASH)]:
            for side in (0,1):
                slot=side*5;others=iter(pool);roster=[ident if i==slot else next(others) for i in range(10)]
                arm={'name':name,'side':side,'version':ident,'source_sha256':sha,'own_slots':[slot],'roster':roster,'games':40}
                body={'idempotency_key':'gota-portals0922-'+name+'-'+str(side)+'-'+HASH[:10],'target':{'coworld_id':h.GAME,'variant_id':'competition'},'game_config_overrides':cfg,'num_episodes':40,'roster':[{'slot':i,'player':{'policy_ref':v}} for i,v in enumerate(roster)],'notes':'Portal coaching session2026-09-22t16-43-56-076z862811: fixed-roster current-engine A/B, one subject, both colors. All source/VM/replay/XP/integer-score checks. No automatic champion selection. Fresh controls; frozen strict >=10% aggregate gain, >=95% each color and no invalid games.'}
                folder=STUDY/'hosted'/name/str(side)
                h.freeze(folder/'arm.json',arm);h.freeze(folder/'request.json',body)
                h.create(c,body,folder/'batch',dry_run=True)
                arms.append(arm)
        plan={'game_version':h.VERSION,'engine_commit':h.COMMIT,'source_sha256':HASH,'cycle':h.CYCLE,'games':160,'arms':arms,'rule':'No invalid games; strict aggregate gain >=10% and each color >=95% control; full hashes/source/XP/intscore. Fixed first-pick roster, fresh controls, unmatched random seeds.'}
        h.freeze(STUDY/'hosted/plan.json',plan)
        for name in ('episode-v2','command-hash'):
            p=STUDY/'bin'/name
            if not p.exists():p.symlink_to(OLD/'bin'/name)
        p=STUDY/'terminal-requests.json'
        if not p.exists():h.write(p,h.read(OLD/'terminal-requests.json'))
        print(json.dumps({'prepared':True,'version':version,'source_sha256':HASH,'games':160,'created_requests':0}))
        return plan


def run():
    plan=h.read(STUDY/'hosted/plan.json')
    assert plan['source_sha256']==h.sha(SOURCE.read_bytes())==HASH
    with h.research.lock(STUDY/'hosted.lock',blocking=False),h.client() as c:
        for arm in plan['arms']:
            folder=STUDY/'hosted'/arm['name']/str(arm['side'])
            if (folder/'result.json').exists():continue
            receipt=folder/'batch/created.json'
            ident=h.read(receipt)['id'] if receipt.exists() else panel.reserve(c,h.read(folder/'request.json'),folder/'batch')
            print(json.dumps({'name':arm['name'],'side':arm['side'],'request':ident}),flush=True)
            while True:
                eps=h.episodes(c,ident);h.write(folder/'episodes.json',eps)
                done=[e for e in eps if e['status'] in ('completed','failed','cancelled','error')]
                with ThreadPoolExecutor(8) as pool:rows=list(pool.map(lambda ep:audit.collect(c,arm,folder,ep),done))
                h.write(folder/'progress.json',{'audited':len(rows),'total':40,'rows':rows})
                if len(rows)==40:break
                print(arm['name'],arm['side'],'audited',len(rows),flush=True);time.sleep(10)
            cell={'name':arm['name'],'side':arm['side'],'games':len(rows),'invalid':sum(not r['valid'] for r in rows),'score':sum(r.get('score',0) for r in rows)/40,'xp':sum(r.get('xp',0) for r in rows)/40,'deaths':sum(r.get('deaths',0) for r in rows)/40,'picks':dict(Counter(r.get('class') for r in rows)),'distinct_streams':len({r.get('canonical_commands_sha1') for r in rows}),'rows':rows}
            h.write(folder/'result.json',cell);print(json.dumps({k:v for k,v in cell.items() if k!='rows'}),flush=True)
        cells=[h.read(STUDY/'hosted'/a['name']/str(a['side'])/'result.json') for a in plan['arms']]
        old,new=cells[:2],cells[2:];control=sum(c['score'] for c in old)/2;score=sum(c['score'] for c in new)/2
        passed=all(c['invalid']==0 for c in cells) and score>control and score>=1.1*control and all(c['score']>=.95*b['score'] for c,b in zip(new,old))
        result={'complete':True,'passed':passed,'score':score,'control_score':control,'cells':cells}
        h.write(STUDY/'hosted/result.json',result);print(json.dumps({k:v for k,v in result.items() if k!='cells'}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');a=p.parse_args()
    if a.prepare:prepare()
    else:run()
