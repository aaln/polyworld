"""User-selected two-policy tournament portfolio; preserve rejected full-suite result."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import time
from hosted_wave import client,get
from policy_ir import HERE,read,write,digest,compile_policy,extract,refresh_grounding,bundle
from release_workspace import RUN,verify
from red_pressure_hosted import result
from release_deploy import champions,AARON
from release_hosted import OPTIMIZER
from release_deploy_pair import verify_owned,check_champions,select
from win_hosted import live

ROOT=RUN/'coached-lanes/r5-anchored-support/hosted/anchor'
OUT=ROOT/'tournament-portfolio'
PRIORS={OPTIMIZER:'b61bfdfb-f82f-4c6b-a504-5c040ed82a68',AARON:'b64f1ccb-02e1-4ad5-b75b-f374222e9e9a'}
NOTE=('User explicitly chose "Use the diverse pair" for the upcoming2000game tournament: '
      'Aaron retains blue_repair; Aarons Co-play Coach selects coordinated-support-anchor. '
      'Anchor Richard78 80/80 vs deployed51/80; Jordan186 both80/80; g002 anchor44/80 (red4blue40) '
      'vs deployed64/80 (red24blue40). All audited. These are repeated fixedlineup trajectories, '
      'not independent-trial significance. This is a deliberately diverse portfolio with known '
      'g002 regression, NOT a passed full-suite replacement. Current Jordan209, g003v2 and '
      'mixed10player field unvalidated. Original rejection remains preserved.')

def main(apply=False):
    verify();OUT.mkdir(exist_ok=True)
    v=read(ROOT/'uploaded-version.json');meta=read(ROOT/'upload-request.json')
    source=(ROOT/'final-feedback/policy.bas').read_bytes();parent=read(ROOT/'final-feedback/policy.ir.json')
    assert v['id']=='9cedf3ff-c7ce-4cff-897f-d48b44e049ad'
    assert digest(source)==meta['content_hash'] and compile_policy(parent).encode()==source and extract(source.decode(),parent)==parent
    heads={k:result(ROOT/k) for k in ('richard','jordan','g002')}
    assert [heads[k]['wins'] for k in ('richard','jordan','g002')]==[80,80,44]
    assert heads['g002']['colors']['red']['win']==4
    snapshot=read(RUN/'coached-lanes/r5-g002-retention/current-champions.json')
    decision={'authorization':'User: Use the diverse pair','scope':NOTE,'source_sha256':digest(source),
              'candidate':v,'unchanged_player':AARON,'changed_player':OPTIMIZER,'rollback_versions':PRIORS,
              'evidence':{k:{'games':r['games'],'wins':r['wins'],'colors':r['colors'],'all_full_audits_passed':r['all_full_audits_passed']} for k,r in heads.items()},
              'full_suite_passed':False,'current_field_snapshot':str(RUN/'coached-lanes/r5-g002-retention/current-champions.json')}
    if (OUT/'decision.json').exists():assert read(OUT/'decision.json')==decision
    write(OUT/'decision.json',decision)
    if not (OUT/'policy').exists():
        p=deepcopy(parent)
        p['belief']['claims']['B_tournament_portfolio']={'status':'requires_review','claim':NOTE,'evidence':[{'artifact':str(OUT/'decision.json'),'sha256':digest((OUT/'decision.json').read_bytes())}]}
        p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='User-selected tournament portfolio with known g002 regression and current-field uncertainty')
        refresh_grounding(p);assert compile_policy(p).encode()==source and extract(source.decode(),p)==p
        bundle(p,OUT/'policy');write(OUT/'policy/parent.ir.json',parent)
    p=read(OUT/'policy/policy.ir.json');assert compile_policy(p).encode()==source and extract(source.decode(),p)==p
    game=live();plan=read(ROOT/'g002/plan.json')
    assert game['version']==plan['game_version'] and game['manifest']['game']['runnable']['source_url']==plan['game_source']
    intended={OPTIMIZER:v['id'],AARON:PRIORS[AARON]}
    with client() as c:
        before=check_champions(champions(c),intended,PRIORS);verify_owned(c,v,OPTIMIZER)
        write(OUT/'preflight.json',{'ready':True,'players':list(before.values()),'scope':NOTE})
        if not apply:print('Portfolio preflight passed; no selections changed.');return
        path='/stats/policy-versions/'+v['id'];remote=get(c,path)
        assert remote.get('player_file_content_hash') in (None,digest(source))
        tags={'validation':NOTE,'semantic_ir_sha256':digest(p),'symbolic_policy_sha256':digest(source),'ir_revision':str(p['update']['revision'])}
        r=c.put(path+'/tags',json=(remote.get('tags') or {})|tags);r.raise_for_status()
        assert all(get(c,path)['tags'][k]==val for k,val in tags.items())
        if before[OPTIMIZER]['policy_version']['id']!=v['id']:select(c,OPTIMIZER,v,OUT/'coach',NOTE)
        for _ in range(12):
            after=check_champions(champions(c),intended,PRIORS)
            if after[OPTIMIZER]['policy_version']['id']==v['id']:break
            time.sleep(5)
        else:raise ValueError('Selectionnotvisible')
        assert after[AARON]['policy_version']['id']==PRIORS[AARON]
        write(OUT/'deployment-verified.json',{'verified_at':datetime.now(timezone.utc).isoformat(),'players':list(after.values()),'versions':intended,'owned_active_ladder_players':2,'source_sha256':digest(source),'semantic_ir_sha256':digest(p),'scope':NOTE})
        if not (OUT/'prior-active-policy.json').exists():write(OUT/'prior-active-policy.json',read(HERE/'active_policy.json'))
        active=read(OUT/'prior-active-policy.json')
        for row in active['players']:
            if row['player']==OPTIMIZER:row.update(version=v['id'],label=v['name']+':v'+str(v['version']),policy=str(OUT/'policy/policy.bas'),semantic_ir=str(OUT/'policy/policy.ir.json'))
            else:row.update(policy=active['policy'],semantic_ir=active['semantic_ir'])
        for k in ('policy','semantic_ir','latest_evaluation','monitoring_report','monitoring_feedback_sha256'):active.pop(k,None)
        active.update(deployment_receipt=str(OUT/'deployment-verified.json'),scope=NOTE)
        write(HERE/'active_policy.json',active)
        marker='## Tournament diverse pair '+v['id'];log=HERE/'VERSION_LOG.md'
        if marker not in log.read_text():
            with log.open('a') as f:f.write('\n'+marker+'\n\n'+NOTE+'\n\nExplicit authorization: Use the diverse pair. Receipt: '+str(OUT/'deployment-verified.json')+'\n')
    print('VERIFIED: Co-play Coach=anchor; Aaron=blue_repair. Exactly two active champions.',flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');a=ap.parse_args();main(a.apply)
