"""Journaled 400-game exact-target discovery; no league writes."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import httpx
from build import ROOT, STUDY, read, write, digest

sys.path.insert(0,str(ROOT/'tools/gota_autoresearch'))
import researcher as r
from hosted_wave import client,get
from win_hosted import live
from release_deploy_pair import verify_owned

CAMPAIGN=ROOT.parent/'gota-autoresearch'
CYCLE='interactive-formation-adaptive-20260920'
CONTROL='2c025f1e-a6f9-46ca-bab1-32dfaef6e9de'
RIVALS={'alex':'a30542cb-54de-4109-92e6-bcabca7db4d8',
        'jordan':'207ffaf9-0d1e-4d92-a15d-4352f1bddec2',
        'richard':'7c370daf-3c5f-42f8-870b-54b79c495a44'}
COLLECTOR=ROOT.parent/'optimizer-seed/games/gods-of-the-arena/instruments/autoresearch_collect.py'


def freeze(p,v):
    if p.exists():assert read(p)==v,p
    else:write(p,v)


def prepare():
    admission=read(STUDY/'hosted-admission.json');assert admission['passed']
    name=admission['candidate'];folder=STUDY/'candidates'/name
    source=(folder/'policy.bas').read_bytes();assert digest(source)==admission['source_sha256']
    game=live()
    with client() as c:
        current=get(c,'/v2/league-policy-memberships?league_id=league_3c60897b-25cf-4b37-9d1a-8554c1198f28&champions_only=true&limit=100')
        assert all(v in {x['policy_version']['id'] for x in current} for v in [CONTROL,*RIVALS.values()])
        write(STUDY/'champions-at-discovery.json',current)
        meta={'name':'aaron-gota-ir-formation-'+name.replace('_','-')+'-0920',
              'content_hash':digest(source),'size_bytes':len(source),'player_id':'ply_630a768f-d623-44b2-80fa-36968d6fa75a',
              'attributes':{},'tags':{'game':'gods_of_the_arena','game_version':game['version'],
              'semantic_ir_sha256':digest((folder/'policy.ir.json').read_bytes()),
              'validation':'Native-admitted adaptive fork; hosted unvalidated; inert upload only'}}
        freeze(folder/'upload-request.json',meta)
        receipt=folder/'uploaded-version.json'
        if not receipt.exists():
            response=c.post('/stats/policies/files/upload',json=meta)
            if response.status_code==409:
                response=c.post('/stats/policies/files/complete',json=meta);response.raise_for_status();version=response.json()
            else:
                response.raise_for_status();payload=response.json();version=payload.get('existing_policy_version')
                if version is None:
                    response=httpx.put(payload['upload_url'],content=source,headers={'Content-Type':'application/octet-stream'},timeout=120);response.raise_for_status()
                    response=c.post('/stats/policies/files/complete',json=meta);response.raise_for_status();version=response.json()
            write(receipt,version)
        version=read(receipt);write(folder/'owned-readback.json',verify_owned(c,version,meta['player_id']))
    cfg=r.config(CAMPAIGN);arms=[]
    for rival,rival_version in RIVALS.items():
        for label,vid in [('candidate',version['id'])]+([] if rival=='richard' else [('formation',CONTROL)]):
            for side,color in enumerate(('red','blue')):
                own=list(range(side*5,side*5+5));roster=[vid if i in own else rival_version for i in range(10)]
                d=STUDY/'hosted'/rival/label/color;d.mkdir(parents=True,exist_ok=True)
                arm={'key':f'{rival}/{label}/{color}','name':label,'kind':'team','policy_version':vid,
                     'rival_version':rival_version,'color':color,'own_slots':own,'roster':roster,'games':40,'directory':str(d)}
                body={'idempotency_key':'formation-adaptive-'+digest(arm)[:24],'target':cfg['target'],
                      'game_config_overrides':cfg['game_config'],'num_episodes':40,
                      'roster':[{'slot':i,'player':{'policy_ref':v}} for i,v in enumerate(roster)],
                      'notes':'Formation3600 observed equipment profile strategy fork; '+arm['key']+'. All40 fixed-roster games fully audited. Generated seeds unpaired; duplicates correlated. No identity oracle, no proxy result, no automatic promotion.'}
                freeze(d/'plan.json',arm);freeze(d/'request.json',body);arms.append(arm)
    p=STUDY/'hosted-plan.json'
    if not p.exists():write(p,{'at':datetime.now(timezone.utc).isoformat(),'cycle':CYCLE,'episodes':400,
       'candidate':name,'version':version,'source_sha256':digest(source),'arms':arms,
       'decision_rule':'>=30/40 each Alex/Jordan color, >=8aggregate gain over fresh formation; Richard blue>=38/40 and >=40total wins; all full audits. No field or promotion claim.'})
    assert read(p)['source_sha256']==digest(source) and read(p)['arms']==arms
    return read(p)


def collect(arm):
    d=Path(arm['directory'])
    if (d/'arm-result.json').exists():return read(d/'arm-result.json')
    while not (d/'batch/created.json').exists():
        try:r.xp_create(CAMPAIGN,d/'request.json',d/'batch')
        except ValueError as exc:
            if 'Three XP batches already active' not in str(exc):raise
            time.sleep(20)
    ident=read(d/'batch/created.json')['id'];print(json.dumps({'arm':arm['key'],'request':ident}),flush=True)
    with (d/'harvest.log').open('a') as log:
        subprocess.run([sys.executable,str(COLLECTOR),str(d)],stdout=log,stderr=subprocess.STDOUT,check=True)
    result=read(d/'arm-result.json');print(json.dumps({'arm':arm['key'],**{k:v for k,v in result.items() if k!='rows'}}),flush=True)
    return result


def main():
    with r.lock(STUDY/'hosted-runner.lock',blocking=False):
        plan=prepare();os.environ['GOTA_RESEARCH_CYCLE']=CYCLE
        write(STUDY/'hosted-owner.json',{'pid':os.getpid(),'cycle':CYCLE,'episodes':400})
        with ThreadPoolExecutor(2) as pool:results=list(pool.map(collect,plan['arms']))
        cells={a['key']:v for a,v in zip(plan['arms'],results)}
        wins=lambda key:cells[key]['wins']
        gate={'all_audits':all(v['all_full_audits_passed'] and v['games']==40 for v in results),
            'alex_jordan_each':all(wins(f'{rival}/candidate/{color}')>=30 for rival in ('alex','jordan') for color in ('red','blue')),
            'alex_jordan_gain':sum(wins(f'{rival}/candidate/{color}')-wins(f'{rival}/formation/{color}') for rival in ('alex','jordan') for color in ('red','blue'))>=8,
            'richard_blue':wins('richard/candidate/blue')>=38,
            'richard_total':wins('richard/candidate/blue')+wins('richard/candidate/red')>=40}
        write(STUDY/'hosted-result.json',{'complete':True,'games':400,'passed':all(gate.values()),'gate':gate,'cells':cells,'promotion_eligible':False})
        print('FINAL',gate,flush=True)


if __name__=='__main__':main()
