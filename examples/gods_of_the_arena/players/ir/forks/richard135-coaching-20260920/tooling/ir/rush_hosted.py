"""Exact Jordan team probes for the locally screened shared-rush hypotheses."""
from datetime import datetime, timezone
import shutil
import httpx

from command_diversity import inventory
from economy_feedback import record
from direct_matchup import run_prepared
from hosted_wave import client, create
from policy_ir import HERE, compile_policy, digest, extract, read, write
from release_deploy_pair import verify_owned
from release_hosted import OPTIMIZER
from release_workspace import RUN,VERSION
from rush_local import STUDY
from win_hosted import live


def upload(name, study=STUDY, prefix='aaron-gota-ir-rush', change='shared lane then fort', feedback_override=None, candidate_override=None,
           validation_note='Local team screen passed; hosted unvalidated', evidence_path=None):
    folder=study/'hosted'/name;folder.mkdir(parents=True,exist_ok=True)
    candidate=candidate_override or study/'local/candidates'/name
    feedback=feedback_override or study/'local/feedback'/name
    if not feedback.exists():
        metrics=read(study/'local/result.json')['metrics'][name]
        record(candidate/'policy.ir.json',candidate/'policy.bas',
               f'Complete local team discovery: {metrics}. Selected for hosted testing only; fixed-lineup repetitions are not broad competitive proof.',
               study/'local/result.json',feedback)
    p=read(feedback/'policy.ir.json')
    source=(candidate/'policy.bas').read_bytes()
    if compile_policy(p).encode()!=source or extract(source.decode(),p)!=p:raise ValueError('IR parity mismatch')
    metadata={'name':prefix+'-'+name+'-0916','content_hash':digest(source),'size_bytes':len(source),
              'player_id':OPTIMIZER,'attributes':{},'tags':{'game':'gods_of_the_arena','change':change,
              'semantic_ir_sha256':digest(p),'game_version':VERSION,'validation':validation_note}}
    if (folder/'upload-request.json').exists() and read(folder/'upload-request.json')!=metadata:raise ValueError('Upload changed')
    write(folder/'upload-request.json',metadata)
    with client() as c:
        if not (folder/'uploaded-version.json').exists():
            r=c.post('/stats/policies/files/upload',json=metadata)
            if r.status_code==409:
                r=c.post('/stats/policies/files/complete',json=metadata);r.raise_for_status();v=r.json()
            else:
                r.raise_for_status();data=r.json();v=data.get('existing_policy_version')
                if v is None:
                    r=httpx.put(data['upload_url'],content=source,headers={'Content-Type':'application/octet-stream'},timeout=120);r.raise_for_status()
                    r=c.post('/stats/policies/files/complete',json=metadata);r.raise_for_status();v=r.json()
            write(folder/'uploaded-version.json',v)
        v=read(folder/'uploaded-version.json')
        log=HERE/'VERSION_LOG.md';text=log.read_text()
        if v['id'] not in text:
            evidence = evidence_path if evidence_path is not None else study/'local'
            text+=f'\n## {v["name"]}:v{v["version"]}\n\n- ID `{v["id"]}`; Optimizer; UTC {datetime.now(timezone.utc).isoformat()}.\n- Candidate {name}: {change}. Exact behaviors in referenced IR. BASIC `{digest(source)}`; IR `{digest(p)}`.\n- {validation_note}; inert upload. Evidence `{evidence}`.\n'
            log.write_text(text)
        write(folder/'owned-readback.json',verify_owned(c,v,OPTIMIZER))
    return folder,v


def prepare(name, study=STUDY, prefix='aaron-gota-ir-rush'):
    game=live();root,v=upload(name,study,prefix)
    prior=read(RUN/'jordan-v148-probe/plan.json')
    plan={k:prior[k] for k in ['target','game_version','game_source','config','rival','rival_version','episodes_per_color','interpretation']}
    meta=read(root/'upload-request.json')
    plan.update(policy_version=v['id'],policy_label=f'{v["name"]}:v{v["version"]}',basic_sha256=meta['content_hash'],
        ir_sha256=meta['tags']['semantic_ir_sha256'],design='Fivecopies of locallyscreened rush vs fivecopies exactJordanv148;40seeded games/color. Finish80andfullaudits. Measurecommanddiversity. Nointerimtuning.')
    if (root/'plan.json').exists() and read(root/'plan.json')!=plan:raise ValueError('Probe plan changed')
    write(root/'plan.json',plan)
    for color in ['red','blue']:
        folder=root/'jordan'/color;folder.mkdir(parents=True,exist_ok=True)
        slots=list(range(5)) if color=='red' else list(range(5,10))
        roster=[v['id'] if s in slots else plan['rival_version'] for s in range(10)]
        arm=plan|{'own_slots':slots,'roster':roster,'color':color}
        if (folder/'plan.json').exists() and read(folder/'plan.json')!=arm:raise ValueError('Arm changed')
        write(folder/'plan.json',arm);shutil.copy2(RUN/'r3/audit',folder/'audit')
        body={'idempotency_key':f'gota-rush-0916-{digest(plan)[:16]}-{color}','target':plan['target'],
              'game_config_overrides':plan['config'],'num_episodes':40,
              'roster':[{'slot':s,'player':{'policy_ref':p}} for s,p in enumerate(roster)],
              'notes':f'Shared-{name}-lane rush vs exactJordanv148. Forty seeded fixedlineup games on{color}; counterpart40othercolor. No league selection or interim tuning.'}
        with client() as c:create(c,body,folder/'batch',dry_run=True)
    return root


def main(study=STUDY, expected_local=160, prefix='aaron-gota-ir-rush'):
    screen=read(study/'local/result.json')
    if screen['verified_games']!=expected_local:raise ValueError('Local study incomplete')
    selected=screen['selected'][:2]
    if not selected:raise ValueError('No local qualifier')
    root=study/'hosted';root.mkdir(exist_ok=True)
    plan={'candidates':selected,'local_result_sha256':digest((study/'local/result.json').read_bytes()),
          'rule':'Complete80/candidate vsJordan. Qualify only if >20/40wins on BOTHcolors; rank totalwins, then averagewinningticks. Fixed-lineup tactical conclusion only. Beforepromotion: fresh100/arm fixedmixedroster againstdeployedbounded and100sampledfield guardrail; no morethan5pp mixedrosterwinregression, field>=50wins, allgear/fullVM/replaychecks. Preservefailed variants.'}
    if (root/'plan.json').exists() and read(root/'plan.json')!=plan:raise ValueError('Study changed')
    write(root/'plan.json',plan)
    results={}
    for name in selected:
        folder=prepare(name,study,prefix);run_prepared(folder);inventory(folder)
        r=read(folder/'result.json')['rivals']['jordan'];results[name]=r
    qualified=[n for n,r in results.items() if all(c['win']>20 for c in r['colors'].values())]
    qualified.sort(key=lambda n:(-results[n]['wins'],sum(r['ticks'] for r in results[n]['rows'] if r['win'])/max(1,results[n]['wins'])))
    write(root/'result.json',{'candidates':results,'qualified':qualified,'selected':qualified[0] if qualified else None})
    print('Qualified:',qualified,flush=True)


if __name__=='__main__':main()
