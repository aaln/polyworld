"""Prepare the concrete fresh-control comparison; run only within shared budget."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import sys
import time
import httpx
import jsonschema

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
STUDY=ROOT.parent/'polyworld/tmp/gota-score-20260922'
sys.path.insert(0,str(HERE.parent/'portals20260922'))
import study as previous
h,panel,audit=previous.h,previous.panel,previous.audit
h.STUDY=panel.STUDY=audit.STUDY=STUDY
h.GAME='cow_2cb5d47d-c064-44af-8b44-cef246667920'
h.VERSION=audit.VERSION='2026.9.22.3'
h.COMMIT='1b70894436b7ffdcd0d421b6b32c2415c9c8bfde'
h.CYCLE='interactive-score-opportunities-20260922'
SOURCE=STUDY/'candidate-r3/policy.bas'
BASELINE='b65ccf7b-d7a1-4681-b57f-a55f5ace43c7'
OUT=STUDY/'hosted'


def prepare():
    for n in ['practice-r3-v2','portals-r3']:
        assert all(r['passed'] for r in h.read(STUDY/(n+'.json'))['rows'])
    assert h.read(STUDY/'scenarios-r3.json')['passed']
    assert h.read(STUDY/'native-result.json')['passed']
    assert h.read(STUDY/'calibration58.json')['full_hashes_equal']
    assert h.read(STUDY/'preflight.json')['passed']
    source=SOURCE.read_bytes();digest=h.sha(source)
    assert digest==h.read(STUDY/'candidate-r3/manifest.json')['source_sha256']
    with h.research.lock(h.CAMPAIGN/'runner.lock',blocking=False),h.client() as c:
        assert h.read(h.CAMPAIGN/'service.json')['state']=='paused'
        game=h.live(c)
        meta={'name':'aaron-gota-score0922-r3','content_hash':digest,'size_bytes':len(source),'player_id':h.PLAYER,'attributes':{},'tags':{'game':'gods_of_the_arena','game_version':h.VERSION,'engine_commit':h.COMMIT,'validation':'180 opportunity +84 portal +126 all-class checks;8 full native games. Inert research upload, hosted competitive score unvalidated.'}}
        h.freeze(STUDY/'upload/request.json',meta)
        jsonschema.validate(meta,h.read(STUDY/'openapi.json')['components']['schemas']['PlayerFilePolicyUploadRequest'])
        path=STUDY/'upload/version.json'
        if not path.exists():
            r=c.post('/stats/policies/files/upload',json=meta)
            if r.status_code==409:
                r=c.post('/stats/policies/files/complete',json=meta);r.raise_for_status();version=r.json()
            else:
                r.raise_for_status();payload=r.json();version=payload.get('existing_policy_version')
                if version is None:
                    r=httpx.put(payload['upload_url'],content=source,headers={'Content-Type':'application/octet-stream'},timeout=120);r.raise_for_status()
                    r=c.post('/stats/policies/files/complete',json=meta);r.raise_for_status();version=r.json()
            h.write(path,version)
        version=h.read(path)
        assert h.get(c,'/stats/policy-versions/'+version['id'])['name']==meta['name']
        template=h.read(STUDY/'roster-template-v2.json')
        cfg={k:v for k,v in game['manifest']['variants'][0]['game_config'].items() if k not in ('seed','players','tokens')}
        arms=[]
        for label,ident,sha in [('baseline',BASELINE,'db71abb37180a06a432ac71c3c5d6802be2ba2c1b2d782b151336beacd8b1520'),('candidate',version['id'],digest)]:
            for side in (0,1):
                roster=list(template);roster[0]=ident
                if side:roster=roster[5:]+roster[:5]
                arm={'name':label,'side':side,'version':ident,'source_sha256':sha,'own_slots':[side*5],'rival_slot':(1-side)*5,'roster':roster,'games':40}
                body={'idempotency_key':f'gota-score0922-{label}-{side}-{digest[:10]}','target':{'coworld_id':h.GAME,'variant_id':'competition'},'game_config_overrides':cfg,'num_episodes':40,'roster':[{'slot':i,'player':{'policy_ref':v}} for i,v in enumerate(roster)],'notes':'Individual XP score A/B on2026.9.22.3 god500XP patch. Fresh portal controls,40per source/color, whole-team rotations, khors114/Jordan411/Richard167 opposing both. No automatic league selection. >=10% aggregate mean score gain and>=95% each color, zero invalid games; full VM/source/replay/XP/integer score audit. Native score diagnostic only.'}
                folder=OUT/label/str(side)
                h.freeze(folder/'arm.json',arm);h.freeze(folder/'request.json',body)
                h.create(c,body,folder/'batch',dry_run=True)
                arms.append(arm)
        plan={'source_sha256':digest,'game_version':h.VERSION,'engine_commit':h.COMMIT,'games':160,'cycle':h.CYCLE,'arms':arms,'rule':'Zero invalid games; at least10% aggregate mean integer-score gain and each color>=95% fresh control. Report bootstrap intervals, duplicates, hero/creep/building/god XP and elapsed time. No team-win requirement. Fixed first-pick roster; no universal rank claim.','budget_status':'Prepared only; September22 allowance1760/1760 exhausted. Require explicit extra160 or next UTC normal budget.'}
        h.freeze(OUT/'plan.json',plan)
        for name in ('episode-v2','command-hash'):
            path=STUDY/'bin'/name
            if not path.exists():path.symlink_to(STUDY/'bin58'/name)
        print(json.dumps({'prepared':True,'created_requests':0,'version':version['id'],'games':160,'source_sha256':digest}))


def run():
    plan=h.read(OUT/'plan.json')
    assert plan['source_sha256']==h.sha(SOURCE.read_bytes())
    with h.research.lock(h.CAMPAIGN/'runner.lock',blocking=False),h.client() as c:
        for arm in plan['arms']:
            folder=OUT/arm['name']/str(arm['side'])
            if (folder/'result.json').exists():continue
            receipt=folder/'batch/created.json'
            ident=h.read(receipt)['id'] if receipt.exists() else panel.reserve(c,h.read(folder/'request.json'),folder/'batch')
            print(json.dumps({'arm':arm['name'],'side':arm['side'],'request':ident}),flush=True)
            while True:
                episodes=h.episodes(c,ident)
                h.write(folder/'episodes.json',episodes)
                done=[e for e in episodes if e['status'] in ('completed','failed','cancelled','error')]
                with ThreadPoolExecutor(6) as pool:rows=list(pool.map(lambda e:audit.collect(c,arm,folder,e),done))
                h.write(folder/'progress.json',{'rows':rows,'audited':len(rows),'total':40})
                if len(rows)==40:break
                time.sleep(10)
            cell={'name':arm['name'],'side':arm['side'],'invalid':sum(not r['valid'] for r in rows),'score':sum(r.get('score',0) for r in rows)/40,'picks':dict(Counter(r.get('class') for r in rows)),'distinct_streams':len({r.get('canonical_commands_sha1') for r in rows}),'rows':rows}
            h.write(folder/'result.json',cell)
        cells=[h.read(OUT/a['name']/str(a['side'])/'result.json') for a in plan['arms']]
        baseline=sum(c['score'] for c in cells[:2])/2;candidate=sum(c['score'] for c in cells[2:])/2
        passed=all(c['invalid']==0 for c in cells) and candidate>baseline and candidate>=1.1*baseline and all(c['score']>=.95*b['score'] for c,b in zip(cells[2:],cells[:2]))
        h.write(OUT/'result.json',{'complete':True,'passed':passed,'control_score':baseline,'score':candidate,'cells':cells,'review_required':'Full economy decomposition and confidence intervals before deployment.'})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');args=p.parse_args()
    if args.prepare:prepare()
    else:run()
