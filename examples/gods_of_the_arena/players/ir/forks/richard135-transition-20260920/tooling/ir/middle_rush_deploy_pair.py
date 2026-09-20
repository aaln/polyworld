"""Apply the user's specific g002/black16 nonregression replacement decision.

The absolute relh/Jordan guard remains failed. This is a scoped replacement,
not a claim of broad-field qualification or a rewritten experimental verdict.
"""
import argparse
from datetime import datetime, timezone
import time

from economy_feedback import record
from hosted_wave import client, get
from macromackie_middle_rush import STUDY
from middle_rush_parallel_checks import branch_proof
from policy_ir import HERE, compile_policy, digest, extract, read, write
from ranger_guard_hosted import freeze
from release_deploy import AARON, champions
from release_deploy_pair import check_champions, clone_for_aaron, select, verify_owned
from release_hosted import OPTIMIZER
from release_workspace import verify
from win_hosted import live

OUT = STUDY/'deployment-pair'
PRIORS = {AARON:'b64f1ccb-02e1-4ad5-b75b-f374222e9e9a',
          OPTIMIZER:'9cedf3ff-c7ce-4cff-897f-d48b44e049ad'}
AUTHORIZATION = ('replace this new policy for both of our champions. First confirm it '
                 "doesn't regress against gota-g002:v1 AND black-kite:v16\n\n"
                 'you can merge the xp requests and run them in parallel')
NOTE = ('User-authorized replacement of both champions after the requested fixed-lineup '
        'g002v1/black-kitev16 nonregression comparisons. Candidate g002 RED21/40 BLUE40/40 '
        'versus Coach anchor RED8/40 and shared deployed BLUE40/40; black16 RED0/40 '
        'BLUE40/40 for candidate and deployed controls. Candidate RED is exactly Aaron '
        'blue_repair RED by lowered execution, also six full local replay parities. '
        'Macromackie4 candidate80/80 versus prior blue_repair48/80. Relh154 BLUE0/40 '
        'and Jordan228 RED0/40 also fail in fresh deployed controls: inherited weaknesses '
        'remain, absolute >=38/color guard FAILED and is preserved. No broad-field or '
        '10-player qualification claimed. Correlated fixed-lineup trajectories and '
        'different generated seeds: directional evidence, no independent-trial significance. '
        'Known portfolio tradeoff: replacing Coach anchor red with blue_repair red gives '
        'up its historical Richard78 advantage (anchor40/40 versus blue_repair11/40 red). '
        'Local deaths151 versus parent100 remains a risk. Original tested BASIC unchanged.')


def readiness():
    verify(); OUT.mkdir(exist_ok=True)
    comparison = read(STUDY/'parallel-nonregression/result.json')
    assert comparison['passed'] and all(all(v.values()) for v in comparison['checks'].values())
    for r in comparison['arms'].values():
        assert r['games']==40 and r['all_full_audits_passed']
    for rival in ('g002','black16'):
        arms = comparison['arms']
        assert arms[rival+'/candidate/blue']['wins'] >= arms[rival+'/blue_control/blue']['wins']
        assert arms[rival+'/candidate/red']['wins'] >= arms[rival+'/red_control/red']['wins']
    proof = branch_proof()
    guards = read(STUDY/'tournament-guards/result.json')
    assert not guards['passed']
    h_jordan = read(STUDY/'jordan-red-control/result.json')
    assert h_jordan['games']==40 and h_jordan['all_full_audits_passed']
    assert h_jordan['wins']==guards['results']['jordan228']['result']['colors']['red']['win']==0
    assert comparison['arms']['relh154/blue_control/blue']['wins']==guards['results']['relh154']['result']['colors']['blue']['win']==0
    macro = read(STUDY/'review-result.json')
    assert macro['targeted_pass'] and macro['candidate']['wins']==80
    candidate = read(STUDY/'hosted/blue_three/uploaded-version.json')
    metadata = read(STUDY/'hosted/blue_three/upload-request.json')
    assert candidate['id']=='d94c63e8-4aa5-4a71-8ec5-78549f3958c6'
    source = (STUDY/'local/candidates/blue_three/policy.bas').read_bytes()
    assert digest(source)==metadata['content_hash']==proof['source_hashes']['new']
    evidence = ['parallel-nonregression/result.json','tournament-guards/result.json',
                'jordan-red-control/result.json','review-result.json','guard-review/decisions.json']
    decision = {'authorization':AUTHORIZATION,'scope':NOTE,'source_sha256':digest(source),
                'candidate':candidate,'rollback_versions':PRIORS,'requested_nonregression_passed':True,
                'absolute_relh_jordan_guard_passed':False,'broad_field_passed':False,
                'branch_proof':proof,
                'evidence':{p:digest((STUDY/p).read_bytes()) for p in evidence},
                'rollback':'Re-select the retained prior memberships for each player; no source deletion.'}
    freeze(OUT/'decision.json',decision)
    parent = STUDY/'parallel-nonregression/evaluated-feedback'
    if not (OUT/'policy').exists():
        record(parent/'policy.ir.json',parent/'policy.bas',NOTE,OUT/'decision.json',OUT/'policy')
    policy = read(OUT/'policy/policy.ir.json')
    assert compile_policy(policy).encode()==source and extract(source.decode(),policy)==policy
    assert (OUT/'policy/policy.bas').read_bytes()==source
    plan = read(STUDY/'hosted/blue_three/macromackie-v4/plan.json')
    game = live()
    assert game['version']==plan['game_version'] and game['manifest']['game']['runnable']['source_url']==plan['game_source']
    return candidate,metadata,source,policy


def main(apply=False):
    candidate,metadata,source,policy = readiness()
    clone_path = OUT/'aaron-upload/uploaded-version.json'
    clone = read(clone_path) if clone_path.exists() else None
    versions = {OPTIMIZER:candidate['id']}
    if clone: versions[AARON]=clone['id']
    tags = {'validation':NOTE,'semantic_ir_sha256':digest(policy),
            'symbolic_policy_sha256':digest(source),'ir_revision':str(policy['update']['revision'])}
    with client() as c:
        before = check_champions(champions(c),versions,PRIORS)
        verify_owned(c,candidate,OPTIMIZER)
        if clone: verify_owned(c,clone,AARON)
        write(OUT/'preflight.json',{'checked_at':datetime.now(timezone.utc).isoformat(),
              'ready_for_user_scoped_replacement':True,'players':list(before.values()),
              'scope':NOTE,'source_sha256':digest(source)})
        if not apply:
            print('Scoped nonregression preflight passed; absolute guards remain FAILED; no league change.');return
        if not (OUT/'prior-active-policy.json').exists():
            write(OUT/'prior-active-policy.json',read(HERE/'active_policy.json'))
        clone = clone_for_aaron(c,STUDY,metadata|{'tags':metadata['tags']|tags},source,NOTE)
        versions[AARON]=clone['id']
        for player,version,label in [(OPTIMIZER,candidate,'coach'),(AARON,clone,'aaron')]:
            remote=get(c,'/stats/policy-versions/'+version['id'])
            assert remote.get('player_file_content_hash') in (None,digest(source))
            response=c.put('/stats/policy-versions/'+version['id']+'/tags',json=(remote.get('tags') or {})|tags)
            response.raise_for_status()
            assert all(get(c,'/stats/policy-versions/'+version['id'])['tags'][k]==v for k,v in tags.items())
            current=check_champions(champions(c),versions,PRIORS)
            if current[player]['policy_version']['id']!=version['id']:
                select(c,player,version,OUT/label,NOTE)
            for _ in range(12):
                after=check_champions(champions(c),versions,PRIORS)
                if after[player]['policy_version']['id']==version['id']:break
                time.sleep(5)
            else:raise ValueError('Champion selection not visible; retain receipts and reconcile')
            print('VERIFIED',after[player]['player']['name'],version['name']+':v'+str(version['version']),flush=True)
        after=check_champions(champions(c),versions,PRIORS)
        assert all(after[p]['policy_version']['id']==v for p,v in versions.items())
        write(OUT/'deployment-verified.json',{'verified_at':datetime.now(timezone.utc).isoformat(),
              'players':list(after.values()),'versions':versions,'owned_active_ladder_players':2,
              'source_sha256':digest(source),'semantic_ir_sha256':digest(policy),'scope':NOTE})
        active=read(OUT/'prior-active-policy.json')
        for row in active['players']:
            v=candidate if row['player']==OPTIMIZER else clone
            row.update(version=v['id'],label=v['name']+':v'+str(v['version']),
                       policy=str(OUT/'policy/policy.bas'),semantic_ir=str(OUT/'policy/policy.ir.json'))
        active.update(deployment_receipt=str(OUT/'deployment-verified.json'),scope=NOTE)
        write(HERE/'active_policy.json',active)
        marker='## Middle rush scoped two-champion deployment '+candidate['id']
        log=HERE/'VERSION_LOG.md'
        if marker not in log.read_text():
            with log.open('a') as f:
                f.write('\n'+marker+'\n\nValidation: submitted after user-specified nonregression checks; full-suite validation FAILED.\n\n'+NOTE+'\n\nAuthorization: '+AUTHORIZATION+'\n\nEvidence and rollback: '+str(OUT/'decision.json')+'\nVerified receipt: '+str(OUT/'deployment-verified.json')+'\n')
    print('Exactly two owned active ladder champions verified on byte-identical tested BASIC.',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true')
    main(parser.parse_args().apply)
