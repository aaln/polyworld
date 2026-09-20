"""Final candidate admission; reuse the one already purchased baseline batch."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import importlib.util
import os
from pathlib import Path
from fresh_hit import ROOT,STUDY,INITIAL,NAMES,read,write,digest
from study import CAMPAIGN

spec=importlib.util.spec_from_file_location('transition_old_hosted_runner',ROOT/'games/gods_of_the_arena/instruments/richard_transition/hosted.py')
support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)
r=support.r;shared=support.shared
CYCLE=support.CYCLE


def main():
    with r.lock(STUDY/'hosted-runner.lock',blocking=False):
        for n in ('vm-proof','focus-proof','boundary-proof','runtime-margin'):assert read(STUDY/(n+'.json'))['passed']
        for color in ('red','blue'):
            assert read(INITIAL/'cadence/hosted/coached_baseline'/color/'arm-result.json')['all_full_audits_passed'], 'Let the existing baseline collectors finish before reuse; never run duplicate collectors'
        local=read(STUDY/'local-results.json');assert local['complete'] and len(local['rows'])==36
        assert all(x['valid'] and x['gear_heroes']==5 and x['max_instructions']<=19000 for x in local['rows'])
        for path,sha in read(STUDY/'plan.json')['inputs_sha256'].items():assert digest(Path(path).read_bytes())==sha,path
        shared.live()
        spec=importlib.util.spec_from_file_location('transition_final_upload',ROOT/'games/gods_of_the_arena/instruments/richard_counter/campaign.py')
        uploader=importlib.util.module_from_spec(spec);spec.loader.exec_module(uploader);uploader.STUDY=STUDY
        versions={'coached_baseline':support.BASELINE}
        for name in NAMES[1:]:versions[name]=uploader.upload(name)
        c=r.config(CAMPAIGN);arms=[]
        for name in NAMES:
            for color in ('red','blue'):
                if name=='coached_baseline':
                    d=INITIAL/'cadence/hosted'/name/color
                    arm=read(d/'plan.json');body=read(d/'request.json')
                    assert arm['policy_version']==support.BASELINE and arm['rival_version']==shared.RIVAL
                    assert body['game_config_overrides']==c['game_config'] and body['num_episodes']==40
                else:
                    own=list(range(5)) if color=='red' else list(range(5,10));version=versions[name]
                    roster=[version if i in own else shared.RIVAL for i in range(10)]
                    d=STUDY/'hosted'/name/color;d.mkdir(parents=True,exist_ok=True)
                    arm={'key':f'{name}/{color}','name':name,'kind':'team','policy_version':version,
                        'rival_version':shared.RIVAL,'color':color,'own_slots':own,'roster':roster,'games':40,'directory':str(d)}
                    body={'idempotency_key':'richard-transition-'+digest(arm)[:24],
                        'target':c['target'],'game_config_overrides':c['game_config'],'num_episodes':40,
                        'roster':[{'slot':i,'player':{'policy_ref':v}} for i,v in enumerate(roster)],
                        'notes':'Session19:10 complete coached transition plus consecutive-decision hit recovery; '+arm['key']+
                            '. Fresh40percolor exactRichard135/all10seats. Full audits. Reuse exact contemporaneous coached baseline; no duplicate purchases. Generated seeds differ, trajectories correlate. No automatic promotion.'}
                    uploader.freeze(d/'plan.json',arm);uploader.freeze(d/'request.json',body)
                arms.append(arm)
        if not (STUDY/'hosted-plan.json').exists():
            write(STUDY/'hosted-plan.json',{'created_at':datetime.now(timezone.utc).isoformat(),'cycle':CYCLE,
                'episodes':240,'arms':arms,'gate':read(STUDY/'plan.json')['gate'],
                'baseline_reuse':'Existing 80 baseline episodes already purchased and audited. Exact original bodies and receipts reused. No earlier candidate XP was issued. Sources remain disqualified/inert.',
                'immutable_sources':{n:digest((STUDY/'candidates'/n/'policy.bas').read_bytes()) for n in NAMES}})
            write(STUDY/'hosted-plan.sha256.json',{'sha256':digest((STUDY/'hosted-plan.json').read_bytes())})
        assert digest((STUDY/'hosted-plan.json').read_bytes())==read(STUDY/'hosted-plan.sha256.json')['sha256']
        plan=read(STUDY/'hosted-plan.json');os.environ['GOTA_RESEARCH_CYCLE']=CYCLE
        write(STUDY/'hosted-owner.json',{'pid':os.getpid(),'cycle':CYCLE,'episodes':240,'started_at':r.now()})
        with ThreadPoolExecutor(2) as pool:results=list(pool.map(shared.collect,plan['arms']))
        cells=[{'key':a['key'],**{k:v for k,v in result.items() if k!='rows'}} for a,result in zip(plan['arms'],results)]
        write(STUDY/'hosted-result.json',{'complete':True,'games':240,'cells':cells,'promotion_eligible':False,'gate':plan['gate']})


if __name__=='__main__':main()
