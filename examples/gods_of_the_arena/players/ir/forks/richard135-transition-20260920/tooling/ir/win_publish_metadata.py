"""Publish final IR/evidence hashes on both selected, byte-identical versions."""
import argparse
from datetime import datetime, timezone

from hosted_wave import client,get
from policy_ir import read,write,digest
from release_deploy import champions
from release_deploy_pair import check_champions,verify_owned
from win_deploy import readiness,PRIORS
from win_hosted import live
from win_screen import STUDY


def main(apply=False):
    live()
    plan,candidate,metadata=readiness(STUDY)
    receipt=read(STUDY/'deployment-pair/deployment-verified.json')
    versions=receipt['versions']
    if receipt['owned_active_ladder_players']!=2 or receipt['source_sha256']!=metadata['content_hash']:
        raise ValueError('Validated deployment receipt missing')
    result=read(STUDY/'hosted-confirmation/result.json');field=read(STUDY/'field/result.json')
    policy=read(STUDY/'reconciled'/plan['candidate']/'policy.ir.json')
    tags={'semantic_ir_sha256':digest(policy),'symbolic_policy_sha256':metadata['content_hash'],
        'ir_revision':str(policy['update']['revision']), 'feedback_parity':'Exact compile and reverse extraction of the evaluated BASIC',
        'validation':f'Passed fresh confirmation {result["arms"][plan["candidate"]]["wins"]}/400 vs deployed {result["arms"]["current"]["wins"]}/400; sampled-current-field {field["wins"]}/100; complete replay/VM/item checks.',
        'validation_scope':'Ten pinned role rotations plus separate sampled-current-field check. Fixed named-rival lineups are separate; no rank #1 claim.',
        'confirmation_sha256':digest((STUDY/'hosted-confirmation/result.json').read_bytes()),
        'field_sha256':digest((STUDY/'field/result.json').read_bytes())}
    out=STUDY/'deployment-pair/final-metadata';out.mkdir(exist_ok=True)
    write(out/'requested-tags.json',tags)
    verified=[]
    with client() as c:
        selected=check_champions(champions(c),versions,PRIORS)
        if any(selected[p]['policy_version']['id']!=v for p,v in versions.items()):
            raise ValueError('Both validated versions must be selected before publishing final metadata')
        for player,version_id in versions.items():
            row=selected[player]['policy_version']
            version={'id':version_id,'name':row['policy']['name']}
            verify_owned(c,version,player)
            pv=get(c,'/stats/policy-versions/'+version_id)
            upload=(STUDY/'hosted-discovery'/plan['candidate'] if version_id==candidate['id'] else STUDY/'deployment-pair/aaron-upload')
            request,completion=read(upload/'upload-request.json'),read(upload/'uploaded-version.json')
            if (completion['id']!=version_id or request['player_id']!=player or request['name']!=pv['name'] or
                    request['content_hash']!=metadata['content_hash'] or request['size_bytes']!=metadata['size_bytes']):
                raise ValueError('Validated upload receipt or player binding differs')
            # The current server exposes these legacy fields as null for BASIC
            # versions. The successful files/complete receipt validates staged
            # bytes and binds their hash to the returned immutable version ID.
            remote_hash=pv.get('player_file_content_hash')
            if remote_hash is not None and remote_hash!=metadata['content_hash']:
                raise ValueError('Remote executable differs from the tested policy')
            remote_size=pv.get('player_file_size_bytes')
            if remote_size is not None and remote_size!=metadata['size_bytes']:
                raise ValueError('Remote executable size differs')
            source_proof={'validated_upload_request':str(upload/'upload-request.json'),
                'validated_upload_completion':str(upload/'uploaded-version.json'),
                'request_sha256':digest((upload/'upload-request.json').read_bytes()),
                'completion_sha256':digest((upload/'uploaded-version.json').read_bytes()),
                'legacy_remote_hash':remote_hash,'legacy_remote_size':remote_size,
                'meaning':'Server-validated upload completion plus exact local evaluated bytes; null legacy hash fields do not provide an additional independent hash readback.'}
            before=out/(version_id+'-before.json')
            if not before.exists():write(before,{'version':version_id,'tags':pv['tags']})
            if apply:
                if any(pv['tags'].get(k)!=v for k,v in tags.items()):
                    response=c.put('/stats/policy-versions/'+version_id+'/tags',json=tags)
                    response.raise_for_status()
                after=get(c,'/stats/policy-versions/'+version_id)
                if any(after['tags'].get(k)!=v for k,v in tags.items()):
                    raise ValueError('Final metadata failed readback')
                verified.append({'player':player,'version':version_id,'tags':after['tags'],'source_sha256':metadata['content_hash'],'source_verification':source_proof})
            print(('Verified' if apply else 'Ready')+' final IR/evidence metadata for '+selected[player]['player']['name'],flush=True)
    if apply:write(out/'verified.json',{'verified_at':datetime.now(timezone.utc).isoformat(),'players':verified,'ir_sha256':digest(policy),'source_sha256':metadata['content_hash']})


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true')
    main(parser.parse_args().apply)
