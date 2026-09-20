"""Deploy the exact current candidate on the user's explicit deploy-now instruction.

This path preserves the unfinished research gates instead of declaring them passed.
"""
from copy import deepcopy
from datetime import datetime, timezone
import time

from hosted_wave import client, get
from policy_ir import HERE, bundle, compile_policy, digest, extract, read, refresh_grounding, write
from release_deploy import AARON, champions
from release_deploy_pair import check_champions, select, verify_owned
from release_hosted import OPTIMIZER
from release_workspace import RUN, verify
from rush_sentries import STUDY
from win_hosted import live

NAME='long_three'
PRIORS={OPTIMIZER:'810d3860-af35-4fed-9364-a4e4bd8b0c2b', AARON:'fa0cab2a-708f-40e0-b6b8-1e44ffeea124'}
AUTHORIZATION='deploy the latest policies to the league since i want to ensure our policy has time to make it to the top. keep going with the xp requests'
OUT=STUDY/'deployment-requested'


def main():
    verify();game=live();OUT.mkdir(exist_ok=True)
    locations={OPTIMIZER:STUDY/'hosted'/NAME, AARON:STUDY/'paired-guardrail/deployment-pair/aaron-upload'}
    versions={p:read(folder/'uploaded-version.json') for p,folder in locations.items()}
    ids={p:v['id'] for p,v in versions.items()}
    plan=read(STUDY/'hosted-plan.json')
    if (game['id']!=plan['target']['coworld_id'] or game['version']!=plan['game_version'] or
            game['manifest']['game']['runnable']['source_url']!=plan['game_source']):
        raise ValueError('Live game changed from the evaluated release')
    pair_plan=read(STUDY/'paired-guardrail/plan.json')
    if pair_plan['candidate_versions']!=[ids[OPTIMIZER],ids[AARON]]:
        raise ValueError('Deployment differs from the frozen XP pair')
    source=(STUDY/'local/candidates'/NAME/'policy.bas').read_bytes()
    parent=read(STUDY/'local/context-feedback'/NAME/'policy.ir.json')
    if compile_policy(parent).encode()!=source or extract(source.decode(),parent)!=parent:
        raise ValueError('IR and symbolic behavior differ')
    local=read(STUDY/'local/result.json')
    if NAME not in local['selected'] or local['metrics'][NAME]['games']!=60:
        raise ValueError('Expected complete local validation')
    for player,folder in locations.items():
        meta=read(folder/'upload-request.json')
        if meta['player_id']!=player or meta['content_hash']!=digest(source) or meta['size_bytes']!=len(source):
            raise ValueError('Owned uploads differ from the evaluated executable')
    decision_path=OUT/'decision.json'
    if not decision_path.exists():
        write(decision_path,{'requested_at':datetime.now(timezone.utc).isoformat(),
            'authorization_verbatim':AUTHORIZATION,'versions':ids,'previous_versions':PRIORS,
            'local_candidate':local['metrics'][NAME],'local_control':local['metrics']['current'],
            'research_status':'Full1120head-to-head plus200ten-player suite remains in progress. '
                              'User explicitly requested league deployment now. Pending hosted '
                              'criteria are not marked passed; no leaderboard superiority is asserted.',
            'symbolic_sha256':digest(source),'local_result_sha256':digest((STUDY/'local/result.json').read_bytes()),
            'rollback':'Reselect the previous existing membership as champion for each player; '
                       'previous versions and memberships are retained. No player is created or retired.'})
    decision=read(decision_path)
    if decision['versions']!=ids or decision['symbolic_sha256']!=digest(source):
        raise ValueError('Frozen deployment decision changed')
    policy=deepcopy(parent)
    policy['belief']['claims']['B_deploy_now']={'claim':decision['research_status'],
        'status':'requires_review','evidence':[{'artifact':str(decision_path),'sha256':digest(decision_path.read_bytes())}]}
    policy['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),
        change='Record explicit deploy-now instruction while full XP validation continues; executable unchanged.')
    policy['update']['needs_review'].append('belief/B_deploy_now');refresh_grounding(policy)
    if compile_policy(policy).encode()!=source or extract(source.decode(),policy)!=policy:
        raise ValueError('Deployment evidence changed the frozen policy')
    if not (OUT/'policy').exists():bundle(policy,OUT/'policy')
    elif read(OUT/'policy/policy.ir.json')!=policy:raise ValueError('Deployment IR changed')
    note=(f'User explicitly requested deploy now while XP continues. Local candidate '
          f'{local["metrics"][NAME]["wins"]}/60 versus deployed{local["metrics"]["current"]["wins"]}/60. '
          'The1120head-to-head+200ten-player suite is pending; no completed hosted superiority claim. '
          'Exact same tested executable under both existing players. Decision: '+str(decision_path))
    log=HERE/'VERSION_LOG.md'
    marker=str(decision_path)
    if marker not in log.read_text():
        with log.open('a') as stream:
            stream.write('\n## Submission decision records — requested sentry deployment\n\n'
                         +f'- Human authorization: "{AUTHORIZATION}"\n'
                         +f'- Versions: {ids}.\n- Evidence: {note}\n'
                         +f'- Rollback versions: {PRIORS}; reselect retained memberships.\n'
                         +'- Validation: local passed; full hosted suite pending. Submission state: requested.\n')
    with client() as c:
        before=check_champions(champions(c),ids,PRIORS)
        for player,version in versions.items():
            verify_owned(c,version,player)
            remote=get(c,'/stats/policy-versions/'+version['id'])
            if remote.get('player_file_content_hash') not in (None,digest(source)):
                raise ValueError('Remote policy content differs')
        write(OUT/'preflight.json',{'checked_at':datetime.now(timezone.utc).isoformat(),
            'players':list(before.values()),'versions':ids,'source_sha256':digest(source),
            'ir_sha256':digest(policy),'decision':str(decision_path),'ready_under_explicit_request':True})
        for player,version in versions.items():
            remote=get(c,'/stats/policy-versions/'+version['id'])
            tags=(remote.get('tags') or {})|{'validation':note,'deployment_authorization':AUTHORIZATION,
                  'semantic_ir_sha256':digest(policy),'symbolic_policy_sha256':digest(source),
                  'ir_revision':str(policy['update']['revision']),'hosted_validation':'in_progress'}
            response=c.put('/stats/policy-versions/'+version['id']+'/tags',json=tags);response.raise_for_status()
            saved=get(c,'/stats/policy-versions/'+version['id'])['tags']
            if any(saved.get(k)!=v for k,v in tags.items()):raise ValueError('Metadata readback failed')
            current=check_champions(champions(c),ids,PRIORS)
            if current[player]['policy_version']['id']!=version['id']:
                select(c,player,version,OUT/('optimizer' if player==OPTIMIZER else 'aaron'),note)
            for _ in range(24):
                current=check_champions(champions(c),ids,PRIORS)
                if current[player]['policy_version']['id']==version['id']:break
                time.sleep(5)
            else:raise ValueError('Selection pending; resume existing receipts')
            print('Verified selected:',version['name']+':v'+str(version['version']),flush=True)
        after=check_champions(champions(c),ids,PRIORS)
        if any(after[p]['policy_version']['id']!=v for p,v in ids.items()):raise ValueError('Selections differ')
        receipt={'verified_at':datetime.now(timezone.utc).isoformat(),'owned_active_ladder_players':2,
                 'players':list(after.values()),'versions':ids,'source_sha256':digest(source),
                 'semantic_ir_sha256':digest(policy),'decision':str(decision_path),
                 'ir_policy_pair':str(OUT/'policy'),'validation':'Local passed; full hosted suite continues.'}
        write(OUT/'deployment-verified.json',receipt)
    write(HERE/'active_policy.json',{'players':[{'player':p,'version':v['id'],
          'label':v['name']+':v'+str(v['version'])} for p,v in versions.items()],
          'policy':str(OUT/'policy/policy.bas'),'semantic_ir':str(OUT/'policy/policy.ir.json'),
          'deployment_receipt':str(OUT/'deployment-verified.json')})
    state=read(RUN/'active-state.json')
    state.update(players_changed=True,latest_deployment=str(OUT/'deployment-verified.json'),
                 warning='User requested deployment now: both exact long_three versions are active. Full1120+200XP suite continues with unchanged frozen rosters and source.')
    write(RUN/'active-state.json',state)
    with log.open('a') as stream:
        stream.write(f'\n- Submitted and selected for both existing players; active champion readback verified. Receipt `{OUT}/deployment-verified.json`. Hosted validation remains in progress.\n')
    print('Both existing players active on latest policies; XP suite continues unchanged.',flush=True)


if __name__=='__main__':main()
