"""Apply the user's deadline priority with explicit targeted-only evidence."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import time
from hosted_wave import client,get
from policy_ir import HERE,read,write,digest,compile_policy,extract,refresh_grounding,bundle
from red_pressure_hosted import result as head_result
from release_deploy import champions,AARON
from release_deploy_pair import clone_for_aaron,verify_owned,check_champions,select
from release_hosted import OPTIMIZER
from win_hosted import live

PRIORS={OPTIMIZER:'b61bfdfb-f82f-4c6b-a504-5c040ed82a68',AARON:'b64f1ccb-02e1-4ad5-b75b-f374222e9e9a'}


def main(report_path,apply=False):
    report=read(report_path);name=report['selected']
    if name is None:raise ValueError('No qualified replacement')
    case=report['results'][name];study=Path(case['study']);root=study/'hosted'/name
    if not case['eligible']:raise ValueError('Not eligible')
    a=head_result(Path(case['head']))
    if a['games']!=80 or a['colors']['red']['win']<32 or a['colors']['blue']['win']<38 or not a['all_full_audits_passed']:raise ValueError('Target gate failed')
    if any(sum(a['colors'][c].values())!=40 for c in ('red','blue')):raise ValueError('Incomplete color cohort')
    if name not in read(study/'local/comparison.json')['qualified'] or not read(study/'vm-stress.json')['passed']:raise ValueError('Local validation missing')
    proof=read(study/'activation-proof.json');source=(study/'local/candidates'/name/'policy.bas').read_bytes()
    if not proof['passed'] or case['source_sha256']!=digest(source):raise ValueError('Unproven source')
    if not any(r['name']==name and r['source_sha256']==digest(source) and r['proof']['all_state_hashes_equal'] and r['proof']['all_actions_consumed'] for r in proof['rows']):raise ValueError('Native proof differs')
    meta=read(root/'upload-request.json');version=read(root/'uploaded-version.json')
    if version['id']!=case['version']['id'] or meta['content_hash']!=digest(source):raise ValueError('Upload differs')
    out=root/'deadline-deployment';out.mkdir(exist_ok=True)
    note=(f'User deadline priority: exact gota-g002:v1 complete80games, red{a["colors"]["red"]["win"]}/40 and blue{a["colors"]["blue"]["win"]}/40; deployed prior24red40blue. '
          'Local qualification, native mechanism execution, full hosted runtime/replay/equipment checks and IR parity passed. '
          'Targeted deadline promotion under explicit20-minute priority. Wider opponents and mixed10-player field were NOT validated for this source; no full-suite or leaderboard guarantee. '
          'Same executable registered under both existing owned players; duplicate registration adds no independent evidence.')
    decision={'authorization':'User previously requests promotion of improved policy to both leagueplayers; latestinstruction gives20minutes and highestpriorityg002red.',
        'scope':note,'source_sha256':digest(source),'report':str(report_path),'report_sha256':digest(report_path.read_bytes()),'rollback_versions':PRIORS}
    if (out/'decision.json').exists() and read(out/'decision.json')!=decision:raise ValueError('Decisionchanged')
    write(out/'decision.json',decision)
    if not (out/'policy').exists():
        parent=read(root/'deadline-feedback/policy.ir.json');p=deepcopy(parent)
        if p['skill']['observe']['parameters'].get('redbranch_release_enabled')==0:
            p['goal']['G_defense']['preference'] += ' Selected rally-only variant: quiet release is disabled after its local failures. Retain parent defense duration; the validated change separates role destinations and refreshes active attacker rally geometry. Do not interpret the earlier counterpush goal as an enabled timeout.'
            p['goal']['G_wave']['preference'] += ' This selected variant resumes ordinary offense on the inherited expiration, not a new quiet timeout.'
        p['belief']['claims']['B_deadline_selection']={'status':'requires_review','claim':note,'evidence':[{'artifact':str(out/'decision.json'),'sha256':digest((out/'decision.json').read_bytes())}]}
        p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='User-deadline targetedscope and exact testedbehavior reflected intoIR')
        refresh_grounding(p)
        if compile_policy(p).encode()!=source or extract(source.decode(),p)!=p:raise ValueError('IR/sourceparity')
        bundle(p,out/'policy');write(out/'policy/parent.ir.json',parent)
    p=read(out/'policy/policy.ir.json')
    if compile_policy(p).encode()!=source or extract(source.decode(),p)!=p:raise ValueError('Finalparity')
    game=live();hp=read(Path(case['head'])/'plan.json')
    if game['version']!=hp['game_version'] or game['manifest']['game']['runnable']['source_url']!=hp['game_source']:raise ValueError('Gamechanged')
    with client() as c:
        intended={OPTIMIZER:version['id']}
        clone_receipt=root/'deployment-pair/aaron-upload/uploaded-version.json'
        if clone_receipt.exists():intended[AARON]=read(clone_receipt)['id']
        before=check_champions(champions(c),intended,PRIORS);verify_owned(c,version,OPTIMIZER)
        write(out/'preflight.json',{'ready':True,'note':note,'players':list(before.values()),'source_sha256':digest(source)})
        if not apply:print('Targeted deadline preflight passed; no champion changed.');return
        buddy=clone_for_aaron(c,root,meta,source,note);versions={OPTIMIZER:version,AARON:buddy};ids={k:v['id'] for k,v in versions.items()}
        for player,v in versions.items():
            verify_owned(c,v,player)
            path='/stats/policy-versions/'+v['id'];remote=get(c,path)
            if remote.get('player_file_content_hash') not in (None,digest(source)):raise ValueError('Remotehashdiffers')
            tags={'semantic_ir_sha256':digest(p),'symbolic_policy_sha256':digest(source),'ir_revision':str(p['update']['revision']),'validation':note}
            r=c.put(path+'/tags',json=(remote.get('tags') or {})|tags);r.raise_for_status()
            saved=get(c,path)['tags']
            if any(saved.get(k)!=val for k,val in tags.items()):raise ValueError('Tagsnotpersisted')
            current=check_champions(champions(c),ids,PRIORS)
            if current[player]['policy_version']['id']!=v['id']:select(c,player,v,out/('coach' if player==OPTIMIZER else 'aaron'),note)
            for _ in range(12):
                current=check_champions(champions(c),ids,PRIORS)
                if current[player]['policy_version']['id']==v['id']:break
                time.sleep(5)
            else:raise ValueError('Selectionnotvisible')
        after=check_champions(champions(c),ids,PRIORS)
        if any(after[player]['policy_version']['id']!=vid for player,vid in ids.items()):raise ValueError('Pairnotconfirmed')
        write(out/'deployment-verified.json',{'verified_at':datetime.now(timezone.utc).isoformat(),'versions':ids,'owned_active_ladder_players':2,'players':list(after.values()),'source_sha256':digest(source),'semantic_ir_sha256':digest(p),'scope':note})
        write(HERE/'active_policy.json',{'players':[{'player':k,'version':v['id'],'label':f'{v["name"]}:v{v["version"]}'} for k,v in versions.items()],'policy':str(out/'policy/policy.bas'),'semantic_ir':str(out/'policy/policy.ir.json'),'deployment_receipt':str(out/'deployment-verified.json')})
        marker='## Deadline g002 promotion '+version['id'];log=HERE/'VERSION_LOG.md'
        if marker not in log.read_text():
            with log.open('a') as f:f.write('\n'+marker+'\n\n'+note+'\n\nReceipt: '+str(out/'deployment-verified.json')+'\n')
    print('Both existing players selected and verified.',flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('report',type=Path);ap.add_argument('--apply',action='store_true');args=ap.parse_args();main(args.report,args.apply)
