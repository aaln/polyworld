"""Promote the frozen warning100 executable under the user's conditional approval."""
import argparse
from datetime import datetime, timezone

from hosted_wave import client, get
from jordan254_finalize import NOTE, finalize
from jordan254_followup import STUDY
from policy_ir import HERE, compile_policy, digest, extract, read, write
from ranger_guard_hosted import freeze
from release_deploy import AARON, champions
from release_deploy_pair import check_champions, clone_for_aaron, select, verify_owned
from release_hosted import OPTIMIZER
from release_workspace import verify
from win_hosted import live

OUT = STUDY/'deployment-pair'
PRIORS = {OPTIMIZER:'d94c63e8-4aa5-4a71-8ec5-78549f3958c6',
          AARON:'95e39723-64cc-45b5-b66a-4440e12fb4b3'}
AUTHORIZATION = 'keep checking the new policy againt g002, black-kite, and macromackie and relh. Promote if it performs better than previous.'
REMOTE_NOTE = (
    'Validated warning100: Jordan254 RED40/40 BLUE40/40 vs deployed0/40,40/40; '
    'actual recall894 vs1480. Fresh local58/60 matches deployed;30blue full-game parities. '
    'Preservation40/color: g00222/40red40/40blue vs21/40,40/40; black160/40red40/40blue '
    'unchanged; macro480/80 unchanged; relh15440/40red0/40blue unchanged. '
    'All400 candidate hosted games fully audited. Reused controls, correlated fixed lineups, '
    'no independent-trial significance or10player claim. Initial failed screen preserved; '
    'separate prospectively declared followup passed. Stale red rally bug remains unfixed. '
    'Full evidence and limitations: jordan254/warning-followup/final-result.json.'
)


def main(apply=False):
    verify(); finalize(); OUT.mkdir(exist_ok=True)
    result = read(STUDY/'final-result.json')
    assert result['confirmed'] == 'warning100'
    policy = read(STUDY/'final-feedback/policy.ir.json')
    source = (STUDY/'final-feedback/policy.bas').read_bytes()
    version = read(STUDY/'hosted/warning100/uploaded-version.json')
    metadata = read(STUDY/'hosted/warning100/upload-request.json')
    assert compile_policy(policy).encode() == source and extract(source.decode(),policy) == policy
    assert digest(source) == metadata['content_hash'] == result['candidate_source_sha256']
    assert version['id'] == '62c4d2c0-69ab-4698-82c1-4f65924d7847'
    plan = read(STUDY/'batches/jordan254/warning100/red/plan.json')
    game = live()
    assert game['version'] == plan['game_version']
    assert game['manifest']['game']['runnable']['source_url'] == plan['game_source']
    freeze(OUT/'decision.json',{'authorization':AUTHORIZATION,'scope':NOTE,
        'candidate_version':version['id'],'source_sha256':digest(source),
        'semantic_ir_sha256':digest(policy),'evidence':result['evidence'],
        'rollback_versions':PRIORS,'rollback':'Re-select the retained prior memberships for each player.',
        'stale_anchor_bug_fixed':False})
    marker = '## Jordan254 warning100 deployment '+version['id']
    log = HERE/'VERSION_LOG.md'
    if marker not in log.read_text():
        with log.open('a') as f:
            f.write('\n'+marker+'\n\nValidation: validated for the targeted improvement and requested preservation comparisons.\n\n'+NOTE+'\n\nAuthorization: '+AUTHORIZATION+'\n\nEvidence and rollback: '+str(OUT/'decision.json')+'\n')
    versions = {OPTIMIZER:version['id']}
    clone_path = OUT/'aaron-upload/uploaded-version.json'
    if clone_path.exists(): versions[AARON] = read(clone_path)['id']
    tags = {'validation':REMOTE_NOTE,'semantic_ir_sha256':digest(policy),
            'symbolic_policy_sha256':digest(source),'ir_revision':str(policy['update']['revision'])}
    with client() as c:
        before = check_champions(champions(c),versions,PRIORS)
        verify_owned(c,version,OPTIMIZER)
        write(OUT/'preflight.json',{'checked_at':datetime.now(timezone.utc).isoformat(),
            'ready':True,'players':list(before.values()),'scope':NOTE})
        if not apply:
            print('Read-only preflight passed.'); return
        if not (OUT/'prior-active-policy.json').exists():
            write(OUT/'prior-active-policy.json',read(HERE/'active_policy.json'))
        clone = clone_for_aaron(c,STUDY,metadata|{'tags':metadata['tags']|tags},source,REMOTE_NOTE)
        versions[AARON] = clone['id']
        for player,v,label in [(OPTIMIZER,version,'coach'),(AARON,clone,'aaron')]:
            verify_owned(c,v,player)
            remote = get(c,'/stats/policy-versions/'+v['id'])
            assert remote.get('player_file_content_hash') in (None,digest(source))
            response = c.put('/stats/policy-versions/'+v['id']+'/tags',json=(remote.get('tags') or {})|tags)
            response.raise_for_status()
            assert all(get(c,'/stats/policy-versions/'+v['id'])['tags'][k] == value for k,value in tags.items())
            current = check_champions(champions(c),versions,PRIORS)
            if current[player]['policy_version']['id'] != v['id']:
                select(c,player,v,OUT/label,NOTE)
            after = check_champions(champions(c),versions,PRIORS)
            assert after[player]['policy_version']['id'] == v['id']
            print('VERIFIED',after[player]['player']['name'],v['name']+':v'+str(v['version']),flush=True)
        after = check_champions(champions(c),versions,PRIORS)
        assert all(after[p]['policy_version']['id'] == v for p,v in versions.items())
        write(OUT/'deployment-verified.json',{'verified_at':datetime.now(timezone.utc).isoformat(),
            'players':list(after.values()),'versions':versions,'owned_active_ladder_players':2,
            'source_sha256':digest(source),'semantic_ir_sha256':digest(policy),'scope':NOTE})
        active = read(OUT/'prior-active-policy.json')
        for row in active['players']:
            v = version if row['player'] == OPTIMIZER else clone
            row.update(version=v['id'],label=v['name']+':v'+str(v['version']),
                       policy=str(STUDY/'final-feedback/policy.bas'),semantic_ir=str(STUDY/'final-feedback/policy.ir.json'))
        active.update(deployment_receipt=str(OUT/'deployment-verified.json'),scope=NOTE)
        write(HERE/'active_policy.json',active)
        receipt = 'Submitted and verified: '+str(OUT/'deployment-verified.json')
        if receipt not in log.read_text():
            with log.open('a') as f: f.write('\n'+receipt+'\n')
    print('Exactly two active competing champions selected; evaluated BASIC and IR parity verified.',flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true')
    main(parser.parse_args().apply)
