"""Promote the fully evaluated relh repair to the two authorized champions."""
import argparse
from datetime import datetime,timezone
from relh154_scoped import STUDY
from relh154_scoped_finalize import finalize
from hosted_wave import client,get
from policy_ir import HERE,read,write,digest,compile_policy,extract
from ranger_guard_hosted import freeze
from release_deploy import AARON,champions
from release_deploy_pair import check_champions,clone_for_aaron,select,verify_owned
from release_hosted import OPTIMIZER
from release_workspace import verify
from win_hosted import live
OUT=STUDY/'deployment-pair'
PRIORS={OPTIMIZER:'62c4d2c0-69ab-4698-82c1-4f65924d7847',AARON:'04091b8f-fea6-4526-ac39-9f7fe6a90c9e'}
AUTHORIZATION='User: replace this new policy for both champions after no regression vs g002 andblackkite; keepcheckingg002blackkitemacromackierelh, promoteifbetter; latestfocusbeatrelh154.'


def main(apply=False):
    verify();note=finalize();OUT.mkdir(exist_ok=True)
    result=read(STUDY/'final-result.json');assert result['promotion_ready']
    name=result['confirmed'];policy=read(STUDY/'final-feedback/policy.ir.json');source=(STUDY/'final-feedback/policy.bas').read_bytes()
    version=read(STUDY/'hosted'/name/'uploaded-version.json');metadata=read(STUDY/'hosted'/name/'upload-request.json')
    assert compile_policy(policy).encode()==source and extract(source.decode(),policy)==policy
    assert digest(source)==metadata['content_hash']==result['source_sha256']
    plan=read(STUDY/'confirmation/relh154'/name/'red/plan.json');game=live()
    assert game['version']==plan['game_version'] and game['manifest']['game']['runnable']['source_url']==plan['game_source']
    freeze(OUT/'decision.json',{'authorization':AUTHORIZATION,'scope':note,'candidate_version':version['id'],
       'source_sha256':digest(source),'semantic_ir_sha256':digest(policy),'evidence':result['evidence'],
       'rollback_versions':PRIORS,'rollback':'Reselect retained warning100 memberships for each existing player.'})
    remote_note=('Relh154: discovery40/40BLUE,fresh40/40RED40/40BLUE,120/120 vsdeployedRED40/40BLUE0/40. '
      'Preservation BLUE40/40eachg002v1black-kitev16macromackie4Jordan254;280/280selected-candidate games allfullyaudited. '
      'Earlier visible damaged-side-tower alarm; originalrelease timing retained. REDsourceunchanged,6fullgameparities; '
      'local12/12matchesdeployed. Firstbroadpackage had5Jordandraws andwasnotpromoted; narrowedfollowuppassed. '
      'IR/BASICreverseparityverified. Historicalcontrols/correlatedfixedlineups, nofutureguarantee or10playerclaim. '
      'Generalredstalerallyweakness remains. Evidence:r5-relh154/scoped-followup/final-result.json.')
    assert len(remote_note)<=1024
    versions={OPTIMIZER:version['id']};clone_path=OUT/'aaron-upload/uploaded-version.json'
    if clone_path.exists():versions[AARON]=read(clone_path)['id']
    tags={'validation':remote_note,'semantic_ir_sha256':digest(policy),'symbolic_policy_sha256':digest(source),'ir_revision':str(policy['update']['revision'])}
    log=HERE/'VERSION_LOG.md';marker='## Relh154 repair deployment '+version['id']
    if marker not in log.read_text():
        with log.open('a') as f:f.write('\n'+marker+'\n\n'+note+'\n\nAuthorization: '+AUTHORIZATION+'\n\nEvidence/rollback: '+str(OUT/'decision.json')+'\n')
    with client() as c:
        before=check_champions(champions(c),versions,PRIORS);verify_owned(c,version,OPTIMIZER)
        write(OUT/'preflight.json',{'checked_at':datetime.now(timezone.utc).isoformat(),'ready':True,'players':list(before.values()),'scope':note})
        if not apply:
            print('Read-only preflight passed.');return
        if not (OUT/'prior-active-policy.json').exists():write(OUT/'prior-active-policy.json',read(HERE/'active_policy.json'))
        clone=clone_for_aaron(c,STUDY,metadata|{'tags':metadata['tags']|tags},source,remote_note);versions[AARON]=clone['id']
        for player,v,label in ((OPTIMIZER,version,'coach'),(AARON,clone,'aaron')):
            verify_owned(c,v,player);remote=get(c,'/stats/policy-versions/'+v['id'])
            assert remote.get('player_file_content_hash') in (None,digest(source))
            response=c.put('/stats/policy-versions/'+v['id']+'/tags',json=(remote.get('tags') or {})|tags);response.raise_for_status()
            assert all(get(c,'/stats/policy-versions/'+v['id'])['tags'][k]==value for k,value in tags.items())
            current=check_champions(champions(c),versions,PRIORS)
            if current[player]['policy_version']['id']!=v['id']:select(c,player,v,OUT/label,note)
            after=check_champions(champions(c),versions,PRIORS);assert after[player]['policy_version']['id']==v['id']
            print('VERIFIED',after[player]['player']['name'],v['name']+':v'+str(v['version']),flush=True)
        after=check_champions(champions(c),versions,PRIORS);assert all(after[p]['policy_version']['id']==v for p,v in versions.items())
        write(OUT/'deployment-verified.json',{'verified_at':datetime.now(timezone.utc).isoformat(),'players':list(after.values()),'versions':versions,
              'owned_active_ladder_players':2,'source_sha256':digest(source),'semantic_ir_sha256':digest(policy),'scope':note})
        active=read(OUT/'prior-active-policy.json')
        for row in active['players']:
            v=version if row['player']==OPTIMIZER else clone
            row.update(version=v['id'],label=v['name']+':v'+str(v['version']),policy=str(STUDY/'final-feedback/policy.bas'),semantic_ir=str(STUDY/'final-feedback/policy.ir.json'))
        active.update(deployment_receipt=str(OUT/'deployment-verified.json'),scope=note);write(HERE/'active_policy.json',active)
        receipt='Submitted and verified: '+str(OUT/'deployment-verified.json')
        if receipt not in log.read_text():
            with log.open('a') as f:f.write('\n'+receipt+'\n')
    print('Exactly two active competing champions verified on evaluated relh repair.',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');main(p.parse_args().apply)
