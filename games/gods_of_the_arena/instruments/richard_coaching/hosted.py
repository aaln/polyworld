"""Frozen, shared-budget Richard135 comparison of complete coached policies."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from prepare import ROOT, STUDY, CAMPAIGN, NAMES, read, write, digest

sys.path.insert(0,str(ROOT/'tools/gota_autoresearch'))
import researcher as r
from hosted_wave import client
from win_hosted import live

CYCLE='interactive-richard-coaching-20260920'
RIVAL='7c370daf-3c5f-42f8-870b-54b79c495a44'
CONTROL='00cd9483-0309-4613-bf61-89f3f4a33d01'
PYTHON='/Users/aaln/experiments/softmax/metta/.venv/bin/python'
COLLECTOR=ROOT.parent/'optimizer-seed/games/gods-of-the-arena/instruments/autoresearch_collect.py'


def prepare():
    assert read(STUDY/'vm-proof.json')['passed']
    local=read(STUDY/'local-results.json')
    assert local['complete'] and len(local['rows'])==48
    assert all(x['valid'] and x['gear_heroes']==5 for x in local['rows'])
    for path,sha in read(STUDY/'plan.json')['inputs_sha256'].items():
        assert digest(Path(path).read_bytes())==sha,path
    live()
    spec=importlib.util.spec_from_file_location('coaching_upload',ROOT/'games/gods_of_the_arena/instruments/richard_counter/campaign.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.STUDY=STUDY
    versions={'deployed':CONTROL}
    for name in NAMES[1:]:versions[name]=module.upload(name)
    c=r.config(CAMPAIGN);arms=[]
    for name in NAMES:
        for color in ('red','blue'):
            version=versions[name];own=list(range(5)) if color=='red' else list(range(5,10))
            roster=[version if i in own else RIVAL for i in range(10)]
            directory=STUDY/'hosted'/name/color;directory.mkdir(parents=True,exist_ok=True)
            arm={'key':f'{name}/{color}','name':name,'kind':'team','policy_version':version,
                 'rival_version':RIVAL,'color':color,'own_slots':own,'roster':roster,'games':40,'directory':str(directory)}
            body={'idempotency_key':'richard-coaching-0920-'+digest(arm)[:24],
                  'target':c['target'],'game_config_overrides':c['game_config'],'num_episodes':40,
                  'roster':[{'slot':i,'player':{'policy_ref':v}} for i,v in enumerate(roster)],
                  'notes':'Coached complete team behavior vs exactRichard135; '+arm['key']+'. Fresh40, full audits. Same config/roles, generated seeds not seed-matched. Compare combined package, preserve all failures, no automatic promotion.'}
            module.freeze(directory/'plan.json',arm);module.freeze(directory/'request.json',body)
            arms.append(arm)
    plan={'created_at':datetime.now(timezone.utc).isoformat(),'cycle':CYCLE,'episodes':320,
          'local':str(STUDY/'local-results.json'),'decision_rule':read(STUDY/'plan.json')['gate'],
          'arms':arms,'immutable_sources':{n:digest((STUDY/'candidates'/n/'policy.bas').read_bytes()) for n in NAMES}}
    if not (STUDY/'hosted-plan.json').exists():
        write(STUDY/'hosted-plan.json',plan)
        write(STUDY/'hosted-plan.sha256.json',{'sha256':digest((STUDY/'hosted-plan.json').read_bytes())})


def collect(arm):
    d=Path(arm['directory'])
    if (d/'arm-result.json').exists():return read(d/'arm-result.json')
    while not (d/'batch/created.json').exists():
        try:r.xp_create(CAMPAIGN,d/'request.json',d/'batch')
        except ValueError as exc:
            if 'Three XP batches already active' not in str(exc):raise
            time.sleep(20)
    ident=read(d/'batch/created.json')['id']
    print(json.dumps({'arm':arm['key'],'request':ident,'at':r.now()}),flush=True)
    with (d/'harvest.log').open('a') as log:
        subprocess.run([PYTHON,str(COLLECTOR),str(d)],stdout=log,stderr=subprocess.STDOUT,check=True)
    result=read(d/'arm-result.json')
    print(json.dumps({'arm':arm['key'],**{k:v for k,v in result.items() if k!='rows'}}),flush=True)
    return result


def main():
    with r.lock(STUDY/'hosted-runner.lock',blocking=False):
        prepare()
        assert digest((STUDY/'hosted-plan.json').read_bytes())==read(STUDY/'hosted-plan.sha256.json')['sha256']
        plan=read(STUDY/'hosted-plan.json');assert len(plan['arms'])==8
        os.environ['GOTA_RESEARCH_CYCLE']=CYCLE
        write(STUDY/'hosted-owner.json',{'pid':os.getpid(),'cycle':CYCLE,'episodes':320,'started_at':r.now()})
        with ThreadPoolExecutor(3) as pool:results=list(pool.map(collect,plan['arms']))
        cells=[{'key':a['key'],**{k:v for k,v in result.items() if k!='rows'}} for a,result in zip(plan['arms'],results)]
        write(STUDY/'hosted-result.json',{'complete':True,'games':320,'cells':cells,
              'promotion_eligible':False,'decision_rule':plan['decision_rule']})


if __name__=='__main__':main()
