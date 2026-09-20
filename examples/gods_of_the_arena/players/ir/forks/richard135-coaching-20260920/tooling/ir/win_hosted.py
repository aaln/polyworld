"""Win-first hosted research against the currently deployed Lich policy."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import shutil
import httpx
from campaign_hosted_compare import cohort, fisher_greater
from economy_feedback import record
from hosted_queue import run
from hosted_wave import client,get
from policy_ir import HERE,read,write,digest,compile_policy,extract
from release_hosted import OPTIMIZER,summarize
from release_workspace import RUN,SOURCE,VERSION,verify
from win_screen import STUDY,RULE
CURRENT='3b5d11e5-cd80-4783-afae-0aa2ef1e4505'

def live():
    verify()
    with client() as c:
        league=get(c,'/v2/leagues/league_3c60897b-25cf-4b37-9d1a-8554c1198f28')
        game=get(c,'/v2/coworlds/'+league['game']['coworld_id'])
    if game['version']!=VERSION or f'/tree/{SOURCE}/' not in game['manifest']['game']['runnable']['source_url']:raise ValueError('Live game changed')
    return game

def upload(n,root):
    local=STUDY/'local'; source=(local/'candidates'/n/'policy.bas').read_bytes()
    policy=read(local/'screen-feedback'/n/'policy.ir.json')
    assert compile_policy(policy).encode()==source and extract(source.decode(),policy)==policy
    out=root/n;out.mkdir(exist_ok=True)
    meta={'name':'aaron-gota-ir-win-'+n.replace('_','-')+'-0916','content_hash':digest(source),'size_bytes':len(source),'player_id':OPTIMIZER,
          'attributes':{},'tags':{'game':'gods_of_the_arena','change':n,'semantic_ir_sha256':digest(policy),'game_version':VERSION,'validation':'win-first local qualifier; hosted unvalidated'}}
    if (out/'upload-request.json').exists() and read(out/'upload-request.json')!=meta:raise ValueError('Upload metadata changed')
    write(out/'upload-request.json',meta)
    with client() as c:
        if not (out/'uploaded-version.json').exists():
            r=c.post('/stats/policies/files/upload',json=meta)
            if r.status_code==409:
                r=c.post('/stats/policies/files/complete',json=meta);r.raise_for_status();version=r.json()
            else:
                r.raise_for_status();payload=r.json();version=payload.get('existing_policy_version')
                if version is None:
                    stored=httpx.put(payload['upload_url'],content=source,headers={'Content-Type':'application/octet-stream'},timeout=120);stored.raise_for_status()
                    r=c.post('/stats/policies/files/complete',json=meta);r.raise_for_status();version=r.json()
            write(out/'uploaded-version.json',version)
        version=read(out/'uploaded-version.json')
        log=HERE/'VERSION_LOG.md';text=log.read_text()
        if version['id'] not in text:
            text+=f'\n## {version["name"]}:v{version["version"]}\n\n- ID `{version["id"]}`; UTC {datetime.now(timezone.utc).isoformat()}; Optimizer-bound inertupload, **hosted unvalidated**.\n- {read(local/"plan.json")["variants"][n]}; original macro screen remainedfailed, separate freshwin-first study selected this policy.\n- BASIC `{meta["content_hash"]}`, IR `{meta["tags"]["semantic_ir_sha256"]}`. Local evidence `{local}`; currentbaseline `{CURRENT}`.\n'
            log.write_text(text)
        owned=get(c,'/v2/policy-versions?mine=true&limit=100&q='+meta['name']);write(out/'owned-readback.json',owned)
        matches=[v for v in owned if v.get('policy_version_id',v.get('id'))==version['id']]
        if len(matches)!=1 or matches[0].get('player_id')!=OPTIMIZER:raise ValueError('Wrong owner/player binding')
    return version['id']

def metrics(parts):
    a=summarize(parts);rr=a['rows'];a.update(deaths=sum(r['deaths'] for r in rr),mean_deaths=sum(r['deaths'] for r in rr)/len(rr),
      mean_minutes=sum(r['ticks'] for r in rr)/1440/len(rr),xp_per_minute=sum(r['xp'] for r in rr)*1440/sum(r['ticks'] for r in rr))
    return a

def prior_seeds():
    paths=[RUN/'hosted-discovery/result.json',RUN/'class-followup/hosted-discovery/result.json',RUN/'class-followup/hosted-confirmation/result.json',
           RUN/'lich-followup/hosted-discovery/result.json',RUN/'r3-study/hosted-confirmation/result.json']
    seeds={r['seed'] for p in paths for a in read(p)['arms'].values() for r in a['rows']}
    seeds.update(r['seed'] for r in read(RUN/'r3-study/field/result.json')['rows'])
    seeds.update(r['seed'] for a in read(RUN/'lich-followup/rival-matchups/result.json')['rivals'].values() for r in a['rows'])
    return seeds

def compare(confirmation=False):
    root=STUDY/('hosted-confirmation' if confirmation else 'hosted-discovery');plan=read(root/'plan.json')
    names=['current',plan['candidate']] if confirmation else ['current',*plan['candidates']]
    seen=prior_seeds()
    if confirmation:
        seen.update(r['seed'] for a in read(STUDY/'hosted-discovery/result.json')['arms'].values() for r in a['rows'])
        rival=STUDY/'rival-matchups/result.json'
        if rival.exists():seen.update(r['seed'] for a in read(rival)['rivals'].values() for r in a['rows'])
    arms={};checks={}
    for n in names:
        dirs=[root/n/f'part-{i}' for i in range(4)] if confirmation else [root/n]
        for d in dirs:
            arm=read(d/'plan.json')
            for k in ['target','game_version','game_source','config','opponents']:
                if arm[k]!=plan[k]:raise ValueError('Frozen arm changed')
        a=metrics([cohort(d,2) for d in dirs]);ss={r['seed'] for r in a['rows']}
        if ss&seen:raise ValueError('A previously observed seed was reused')
        seen|=ss;arms[n]=a
    b=arms['current'];qualified=[]
    for n in names[1:]:
        a=arms[n];gain=(a['wins']*b['games']-b['wins']*a['games'])/(a['games']*b['games']);p=fisher_greater(a['wins'],a['games'],b['wins'],b['games'])
        adverse=[cls for cls,g in a['class_wins'].items() if fisher_greater(b['class_wins'][cls]['wins'],b['class_wins'][cls]['games'],g['wins'],g['games'])<.005]
        criteria={'gain':gain>=.05,'mean_deaths':a['mean_deaths']<=1.1*b['mean_deaths'],'gear':a['equipment_games']==a['games'],
                  'significance':not confirmation or p<.025,'classes':not confirmation or not adverse}
        checks[n]={'gain':gain,'one_sided_p':p,'adverse_classes':adverse,'checks':criteria,'passed':all(criteria.values())}
        if all(criteria.values()):qualified.append(n)
    qualified.sort(key=lambda n:(-arms[n]['wins'],arms[n]['mean_deaths'],n))
    result={'stage':'confirmation' if confirmation else 'discovery','passed':bool(qualified),'selected':qualified[0] if qualified else None,
        'eligible':qualified,'comparisons':checks,'arms':arms,'rule':RULE,'meaning':'Held-out win-first verdict' if confirmation else 'Adaptive selection only; fresh confirmation required'}
    write(root/'result.json',result)
    for n in names[1:]:
        parent=STUDY/'hosted-discovery'/n/'feedback/policy.ir.json' if confirmation else STUDY/'local/screen-feedback'/n/'policy.ir.json'
        out=root/n/'feedback'
        if not out.exists():record(parent,STUDY/'local/candidates'/n/'policy.bas',f'Completed{result["stage"]}: {arms[n]["wins"]}/{arms[n]["games"]} vs current{b["wins"]}/{b["games"]}; {checks[n]}; mean deaths {arms[n]["mean_deaths"]} vs {b["mean_deaths"]}. Allgear/fullreplay/VMvalid. '+result['meaning'],root/'result.json',out)
    print({k:v for k,v in result.items() if k not in ['arms','rule']},flush=True)
    print({n:{k:v for k,v in a.items() if k not in ['rows','class_wins']} for n,a in arms.items()},flush=True)

def discovery():
    game=live();local=STUDY/'local';screen=read(local/'screen-result.json')
    if screen['verified_games']!=120 or not read(local/'vm-validity.json')['all_local_vm_logs_valid']:raise ValueError('Local screen incomplete')
    names=screen['selected']
    if not names:print('No freshlocalqualifier; no upload/XP.');return
    root=STUDY/'hosted-discovery';root.mkdir(exist_ok=True)
    for n in names:
        out=local/'screen-feedback'/n
        if not out.exists():record(local/'candidates'/n/'policy.ir.json',local/'candidates'/n/'policy.bas',f'Fresh win-first local screen, complete120games. {screen["metrics"][n]}. Original360-game macro screen remainsfailed; these120newgames support selection only.',local/'screen-result.json',out)
    prior=read(RUN/'r3-study/hosted-confirmation/plan.json');common={k:prior[k] for k in ['target','game_version','game_source','config','opponents']}
    plan=common|{'candidates':names,'rule':RULE,'episodes_per_arm':100,'current_version':CURRENT,'local_plan_sha256':digest((local/'plan.json').read_bytes()),'created_at':datetime.now(timezone.utc).isoformat()}
    if (root/'plan.json').exists():plan=read(root/'plan.json')
    else:write(root/'plan.json',plan)
    versions={'current':CURRENT}
    for n in names:versions[n]=upload(n,root)
    for n,v in versions.items():
        d=root/n;d.mkdir(exist_ok=True)
        arm=common|{'policy_version':v,'run_id':'gota-win-first-discovery-0916-'+n+'-'+digest(plan)[:10],
            'notes':'100episode fresh fixed-roster win-first discovery against currentlydeployedLich; no interim tuning/stopping, no league selection.'}
        if (d/'plan.json').exists() and read(d/'plan.json')!=arm:raise ValueError('Frozen arm changed')
        write(d/'plan.json',arm);shutil.copy2(RUN/'r3/audit',d/'audit')
    run([root/n for n in versions]);compare()

def confirmation():
    live();disc=STUDY/'hosted-discovery';result=read(disc/'result.json');n=result['selected']
    if n is None:raise ValueError('No discovery qualifier')
    old=read(disc/'plan.json');root=STUDY/'hosted-confirmation';root.mkdir(exist_ok=True)
    plan={k:old[k] for k in ['target','game_version','game_source','config','opponents']}
    plan.update(candidate=n,rule=RULE,sample_size=400,discovery_sha256=digest((disc/'result.json').read_bytes()),current_version=CURRENT,
        excluded_discovery_results=[str(RUN/p) for p in ['hosted-discovery/result.json','class-followup/hosted-discovery/result.json','class-followup/hosted-confirmation/result.json','lich-followup/hosted-discovery/result.json','r3-study/hosted-confirmation/result.json']],
        excluded_rival_results=[str(RUN/'lich-followup/rival-matchups/result.json')]+([str(STUDY/'rival-matchups/result.json')] if (STUDY/'rival-matchups/result.json').exists() else []),
        excluded_field_results=[str(RUN/'r3-study/field/result.json')])
    if (root/'plan.json').exists() and read(root/'plan.json')!=plan:raise ValueError('Frozen confirmation changed')
    write(root/'plan.json',plan)
    jobs=[]
    for i in range(4):
        for arm in ['current',n]:
            d=root/arm/f'part-{i}';d.mkdir(parents=True,exist_ok=True)
            p=read(disc/arm/'plan.json')|{'run_id':f'gota-win-first-confirm-0916-{digest(plan)[:10]}-{arm}-{i}','notes':'Fresh400/arm win-first confirmation; eight100game serialrequests; allpreviousoutcomes excluded, allVM/fullreplay checks required.'}
            write(d/'plan.json',p);shutil.copy2(disc/arm/'audit',d/'audit');jobs.append(d)
    run(jobs);compare(True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['discovery','confirmation','compare','confirm']);a=p.parse_args()
    {'discovery':discovery,'confirmation':confirmation,'compare':compare,'confirm':lambda:compare(True)}[a.command]()
