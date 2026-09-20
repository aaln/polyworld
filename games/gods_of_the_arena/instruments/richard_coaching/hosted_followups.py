"""Two finite coaching follow-ups sharing one240game cycle and fresh control."""
from concurrent.futures import ThreadPoolExecutor
import argparse
import importlib
import importlib.util
import os
from pathlib import Path
from prepare import ROOT, CAMPAIGN, read, write, digest
from hosted import RIVAL, CONTROL, collect, r, live

CYCLE='interactive-richard-coaching-followup-20260920'


def main(module_name):
    module=importlib.import_module(module_name);study=module.STUDY
    with r.lock(study/'hosted-runner.lock',blocking=False):
        assert read(study/'vm-proof.json')['passed']
        local=read(study/'local-results.json')
        assert local['complete'] and len(local['rows'])==24
        assert all(x['valid'] and x['gear_heroes']==5 for x in local['rows'])
        for path,sha in read(study/'plan.json')['inputs_sha256'].items():
            assert digest(Path(path).read_bytes())==sha,path
        live()
        spec=importlib.util.spec_from_file_location('followup_upload',ROOT/'games/gods_of_the_arena/instruments/richard_counter/campaign.py')
        uploader=importlib.util.module_from_spec(spec);spec.loader.exec_module(uploader);uploader.STUDY=study
        version=uploader.upload(module.NAME)
        versions={module.NAME:version}
        if module_name=='late_cohort':versions={'deployed':CONTROL,**versions}
        c=r.config(CAMPAIGN);arms=[]
        for name,version in versions.items():
            for color in ('red','blue'):
                own=list(range(5)) if color=='red' else list(range(5,10))
                roster=[version if i in own else RIVAL for i in range(10)]
                d=study/'hosted'/name/color;d.mkdir(parents=True,exist_ok=True)
                arm={'key':f'{name}/{color}','name':name,'kind':'team','policy_version':version,
                     'rival_version':RIVAL,'color':color,'own_slots':own,'roster':roster,'games':40,'directory':str(d)}
                body={'idempotency_key':'richard-coaching-followup-'+digest(arm)[:24],
                      'target':c['target'],'game_config_overrides':c['game_config'],'num_episodes':40,
                      'roster':[{'slot':i,'player':{'policy_ref':v}} for i,v in enumerate(roster)],
                      'notes':'Combined coached Richard135 follow-up; '+arm['key']+'. Fresh40percolor, full10VM and complete replay audits. Exactroster/release/config. Same-window baseline, not seed-matched or independent confirmation. No promotion.'}
                uploader.freeze(d/'plan.json',arm);uploader.freeze(d/'request.json',body);arms.append(arm)
        if not (study/'hosted-plan.json').exists():
            write(study/'hosted-plan.json',{'cycle':CYCLE,'episodes':40*len(arms),'arms':arms,
                'immutable_sources':{n:digest((study/'candidates'/n/'policy.bas').read_bytes()) for n in versions},
                'baseline':str(module.INITIAL/'late-cohort/hosted/deployed'),
                'runner_sha256':digest(Path(__file__).read_bytes()),
                'decision_rule':read(study/'plan.json')['gate']})
            write(study/'hosted-plan.sha256.json',{'sha256':digest((study/'hosted-plan.json').read_bytes())})
        assert digest((study/'hosted-plan.json').read_bytes())==read(study/'hosted-plan.sha256.json')['sha256']
        plan=read(study/'hosted-plan.json');os.environ['GOTA_RESEARCH_CYCLE']=CYCLE
        write(study/'hosted-owner.json',{'pid':os.getpid(),'cycle':CYCLE,'episodes':plan['episodes'],'started_at':r.now()})
        with ThreadPoolExecutor(2) as pool:results=list(pool.map(collect,plan['arms']))
        cells=[{'key':a['key'],**{k:v for k,v in result.items() if k!='rows'}} for a,result in zip(plan['arms'],results)]
        write(study/'hosted-result.json',{'complete':True,'games':plan['episodes'],'cells':cells,
            'promotion_eligible':False,'decision_rule':plan['decision_rule']})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('module',choices=['late_cohort','home_commit'])
    main(p.parse_args().module)
