"""Apply the user's conditional Coach promotion only after the recorded gate."""
import argparse
from datetime import datetime,timezone
from pathlib import Path
import time
import httpx
from fresh_hit import ROOT,STUDY,INITIAL,read,write,digest
from study import compile_policy,extract
from hosted_wave import client,get
from win_hosted import live
from release_deploy_pair import select,verify_owned

CHECK=INITIAL/'promotion-check'
COACH='ply_594ec24d-d7f3-4370-a000-468354ec41c9'
AARON='ply_630a768f-d623-44b2-80fa-36968d6fa75a'
LOG=ROOT/'games/gods_of_the_arena/players/richard135-counter/VERSION_LOG.md'


def main(apply=False):
    result=read(CHECK/'result.json');auth=read(CHECK/'authorization-and-gate.json')
    assert result['complete'] and result['games']==160 and result['user_conditional_promotion_gate_passed']
    assert all(c['wins']>=30 and c['games']==40 and c['all_full_audits_passed'] for c in result['cells'])
    assert auth['promotion_player']['id']==COACH
    selection=read(CHECK/'selection.json');folder=STUDY/'candidates'/selection['name']
    source=(folder/'policy.bas').read_bytes();policy=read(folder/'policy.ir.json')
    assert digest(source)==selection['source_sha256']
    assert compile_policy(policy).encode()==source and extract(source.decode(),policy)==policy
    live()
    out=CHECK/'deployment';out.mkdir(exist_ok=True)
    snapshot=read(CHECK/'champions-at-authorization.json')
    priors={r['player']['id']:r['policy_version']['id'] for r in snapshot if r['player']['id'] in (COACH,AARON)}
    league=auth['league']
    def champions(c):return get(c,f'/v2/league-policy-memberships?league_id={league}&champions_only=true&limit=100')
    with client() as c:
        current=champions(c);by_player={r['player']['id']:r for r in current}
        for target in auth['targets'].values():
            assert by_player[target['player_id']]['policy_version']['id']==target['policy_version'],'Opponent changed since validation'
        original=read(folder/'uploaded-version.json');verify_owned(c,original,AARON)
        receipt=out/'coach-uploaded-version.json';version=read(receipt) if receipt.exists() else None
        for player in (COACH,AARON):
            v=by_player[player]
            allowed={priors[player]}
            if player==COACH and version:allowed.add(version['id'])
            assert v['status']=='competing' and v['substatus']=='active' and v['is_champion'] and v['policy_version']['id'] in allowed
        before={p:by_player[p] for p in (COACH,AARON)}
        write(out/'preflight.json',{'checked_at':datetime.now(timezone.utc).isoformat(),'authorization':auth,
            'selection':selection,'prior_champions':before,'gate_sha256':digest((CHECK/'result.json').read_bytes()),'ready':True})
        if not apply:
            print('Ready for authorized Coach promotion; Aaron remains incumbent.',flush=True);return
        note='User-authorized conditional promotion: unchanged source passed40percolor against both currentAlexg002v1 andJordan268 with>=30wins each and all160 full VM/replay audits. Richard results are separately recorded; no both-color Richard or rank1 claim. Preserve Aaron incumbent.'
        metadata=read(folder/'upload-request.json')
        metadata.update(name=metadata['name']+'-coach',player_id=COACH,
            tags=metadata['tags']|{'validation':note,'authorization':auth['user_authorization']})
        if (out/'coach-upload-request.json').exists():assert read(out/'coach-upload-request.json')==metadata
        else:write(out/'coach-upload-request.json',metadata)
        if version is None:
            response=c.post('/stats/policies/files/upload',json=metadata)
            if response.status_code==409:
                response=c.post('/stats/policies/files/complete',json=metadata);response.raise_for_status();version=response.json()
            else:
                response.raise_for_status();payload=response.json();version=payload.get('existing_policy_version')
                if version is None:
                    response=httpx.put(payload['upload_url'],content=source,headers={'Content-Type':'application/octet-stream'},timeout=120);response.raise_for_status()
                    response=c.post('/stats/policies/files/complete',json=metadata);response.raise_for_status();version=response.json()
            write(receipt,version)
        text=LOG.read_text()
        if version['id'] not in text:
            LOG.write_text(text+f"\n## {version['name']}:v{version['version']}\n\n- Version `{version['id']}`. Exact byte-identical Coach clone of `{original['id']}`, sourceSHA `{digest(source)}`.\n- Validation: conditional Alex/Jordan gate passed, fully audited160games; Richard tradeoff remains explicit.\n- Evidence: `{CHECK}`. Uploaded inert before authorized submission.\n")
        write(out/'coach-owned-readback.json',verify_owned(c,version,COACH))
        decision={'authorization':auth['user_authorization'],'recorded_at':datetime.now(timezone.utc).isoformat(),
            'version':version,'source_sha256':digest(source),'gate':result,'Richard_result':str(STUDY/'hosted-result.json'),
            'rollback':{'player':COACH,'previous_version':priors[COACH],'previous_membership':before[COACH]['id'],
                'method':'Re-select previous membership champion if rollback is required; Aaron stays unchanged.'}}
        write(out/'decision.json',decision)
        if by_player[COACH]['policy_version']['id']!=version['id']:select(c,COACH,version,out/'coach',note)
        for attempt in range(60):
            current=champions(c);owned={x['player']['id']:x for x in current if x['player']['id'] in (COACH,AARON)}
            write(out/'qualification-readback.json',owned)
            assert owned[AARON]['policy_version']['id']==priors[AARON]
            v=owned[COACH]
            if v['policy_version']['id']==version['id'] and v['is_champion'] and v['status']=='competing' and v['substatus']=='active':break
            time.sleep(5)
        else:raise ValueError('Qualification pending; retain and resume existing receipts')
        write(out/'deployment-verified.json',{'verified_at':datetime.now(timezone.utc).isoformat(),'players':owned,
            'source_sha256':digest(source),'version':version,'league_changed':True,'Aaron_unchanged':True})
        marker='Submission decision '+version['id']
        text=LOG.read_text()
        if marker not in text:LOG.write_text(text+'\n\n## '+marker+'\n\n- State: submitted, active competing champion verified.\n- User: '+auth['user_authorization']+'\n- Decision, measured outcomes and rollback: `'+str(out/'decision.json')+'`.\n')
        print('Coach champion verified; Aaron incumbent preserved.',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true')
    main(parser.parse_args().apply)
