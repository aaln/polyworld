"""The final80games in the finite coaching400cycle, after native validation."""
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import os
from pathlib import Path
import time
from discovery import STUDY, INITIAL, NAME
from prepare import ROOT, CAMPAIGN, read, write, digest
from hosted import CYCLE, RIVAL, collect, r, live


def prepare():
    assert read(STUDY/'vm-proof.json')['passed']
    local=read(STUDY/'local-results.json')
    assert local['complete'] and len(local['rows'])==24
    assert all(x['valid'] and x['gear_heroes']==5 for x in local['rows'])
    for path,sha in read(STUDY/'plan.json')['inputs_sha256'].items():
        assert digest(Path(path).read_bytes())==sha,path
    live()
    spec=importlib.util.spec_from_file_location('discovery_upload',ROOT/'games/gods_of_the_arena/instruments/richard_counter/campaign.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.STUDY=STUDY
    version=module.upload(NAME)
    c=r.config(CAMPAIGN);arms=[]
    for color in ('red','blue'):
        own=list(range(5)) if color=='red' else list(range(5,10))
        roster=[version if i in own else RIVAL for i in range(10)]
        d=STUDY/'hosted'/NAME/color;d.mkdir(parents=True,exist_ok=True)
        arm={'key':f'{NAME}/{color}','name':NAME,'kind':'team','policy_version':version,
             'rival_version':RIVAL,'color':color,'own_slots':own,'roster':roster,'games':40,'directory':str(d)}
        body={'idempotency_key':'richard-coaching-0920-'+digest(arm)[:24],
              'target':c['target'],'game_config_overrides':c['game_config'],'num_episodes':40,
              'roster':[{'slot':i,'player':{'policy_ref':v}} for i,v in enumerate(roster)],
              'notes':'Visibility-complete coordinated coaching vs exactRichard135; '+arm['key']+'. Fresh40, full10VM/replay audits. Existing deployed40each control in same window. Discovery, not independent confirmation or field qualification.'}
        module.freeze(d/'plan.json',arm);module.freeze(d/'request.json',body);arms.append(arm)
    if not (STUDY/'hosted-plan.json').exists():
        write(STUDY/'hosted-plan.json',{'cycle':CYCLE,'episodes':80,'arms':arms,
            'source_sha256':digest((STUDY/'candidates'/NAME/'policy.bas').read_bytes()),
            'baseline':str(INITIAL/'hosted/deployed'),
            'decision_rule':read(STUDY/'plan.json')['gate'],
            'interpretation':'Adaptive discovery refinement, not held-out confirmation. '
                'Original V2 not submitted because its known objective-discovery defect persisted.'})
        write(STUDY/'hosted-plan.sha256.json',{'sha256':digest((STUDY/'hosted-plan.json').read_bytes())})


def main():
    with r.lock(STUDY/'hosted-runner.lock',blocking=False):
        prepare()
        assert digest((STUDY/'hosted-plan.json').read_bytes())==read(STUDY/'hosted-plan.sha256.json')['sha256']
        plan=read(STUDY/'hosted-plan.json');os.environ['GOTA_RESEARCH_CYCLE']=CYCLE
        write(STUDY/'hosted-owner.json',{'pid':os.getpid(),'cycle':CYCLE,'episodes':80,'started_at':r.now()})
        # Collector starts immediately; complete both purchased cells.
        with ThreadPoolExecutor(2) as pool:results=list(pool.map(collect,plan['arms']))
        cells=[{'key':a['key'],**{k:v for k,v in result.items() if k!='rows'}} for a,result in zip(plan['arms'],results)]
        write(STUDY/'hosted-result.json',{'complete':True,'games':80,'cells':cells,
            'promotion_eligible':False,'decision_rule':plan['decision_rule']})


if __name__=='__main__':main()
