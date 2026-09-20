"""Fresh pinned comparison, shared ledger, full streaming validation."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import importlib.util
import os
from pathlib import Path
from study import ROOT, STUDY, CAMPAIGN, NAMES, read, write, digest

# Import the established collector by path to avoid this module's own name.
spec=importlib.util.spec_from_file_location('coaching_hosted_shared',ROOT/'games/gods_of_the_arena/instruments/richard_coaching/hosted.py')
shared=importlib.util.module_from_spec(spec);spec.loader.exec_module(shared)
r=shared.r
CYCLE='interactive-richard-transition-20260920'
BASELINE='e25f30b8-0cc0-4ee4-a333-a7e1f66b7ba6'


def main():
    with r.lock(STUDY/'hosted-runner.lock',blocking=False):
        assert read(STUDY/'vm-proof.json')['passed'] and read(STUDY/'runtime-margin.json')['passed']
        local=read(STUDY/'local-results.json')
        assert local['complete'] and len(local['rows'])==36
        assert all(x['valid'] and x['gear_heroes']==5 and x['max_instructions']<=19000 for x in local['rows'])
        for path,sha in read(STUDY/'plan.json')['inputs_sha256'].items():assert digest(Path(path).read_bytes())==sha,path
        shared.live()
        spec=importlib.util.spec_from_file_location('transition_upload',ROOT/'games/gods_of_the_arena/instruments/richard_counter/campaign.py')
        uploader=importlib.util.module_from_spec(spec);spec.loader.exec_module(uploader);uploader.STUDY=STUDY
        versions={'coached_baseline':BASELINE}
        for name in NAMES[1:]:versions[name]=uploader.upload(name)
        c=r.config(CAMPAIGN);arms=[]
        for name in NAMES:
            for color in ('red','blue'):
                own=list(range(5)) if color=='red' else list(range(5,10));version=versions[name]
                roster=[version if i in own else shared.RIVAL for i in range(10)]
                d=STUDY/'hosted'/name/color;d.mkdir(parents=True,exist_ok=True)
                arm={'key':f'{name}/{color}','name':name,'kind':'team','policy_version':version,
                    'rival_version':shared.RIVAL,'color':color,'own_slots':own,'roster':roster,'games':40,'directory':str(d)}
                body={'idempotency_key':'richard-transition-'+digest(arm)[:24],
                    'target':c['target'],'game_config_overrides':c['game_config'],'num_episodes':40,
                    'roster':[{'slot':i,'player':{'policy_ref':v}} for i,v in enumerate(roster)],
                    'notes':'Session19:10coached defense release/scout/Ranger response; '+arm['key']+
                        '. ExactRichard135 and all10seats pinned. Fresh same-window comparison, generated seeds differ and trajectories may correlate. Full VM/replay/config audits. Combined changes, no isolated-edit gain requirement; no automatic promotion.'}
                uploader.freeze(d/'plan.json',arm);uploader.freeze(d/'request.json',body);arms.append(arm)
        if not (STUDY/'hosted-plan.json').exists():
            write(STUDY/'hosted-plan.json',{'created_at':datetime.now(timezone.utc).isoformat(),
                'cycle':CYCLE,'episodes':240,'arms':arms,'gate':read(STUDY/'plan.json')['gate'],
                'immutable_sources':{n:digest((STUDY/'candidates'/n/'policy.bas').read_bytes()) for n in NAMES}})
            write(STUDY/'hosted-plan.sha256.json',{'sha256':digest((STUDY/'hosted-plan.json').read_bytes())})
        assert digest((STUDY/'hosted-plan.json').read_bytes())==read(STUDY/'hosted-plan.sha256.json')['sha256']
        plan=read(STUDY/'hosted-plan.json');os.environ['GOTA_RESEARCH_CYCLE']=CYCLE
        write(STUDY/'hosted-owner.json',{'pid':os.getpid(),'cycle':CYCLE,'episodes':240,'started_at':r.now()})
        with ThreadPoolExecutor(2) as pool:results=list(pool.map(shared.collect,plan['arms']))
        cells=[{'key':a['key'],**{k:v for k,v in result.items() if k!='rows'}} for a,result in zip(plan['arms'],results)]
        write(STUDY/'hosted-result.json',{'complete':True,'games':240,'cells':cells,'promotion_eligible':False,'gate':plan['gate']})


if __name__=='__main__':main()
