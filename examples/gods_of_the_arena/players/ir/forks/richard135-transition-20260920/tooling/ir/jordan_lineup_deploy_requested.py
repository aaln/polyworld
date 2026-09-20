"""Explicit user-requested deployment before broad validation completes.

Preserve the failed/pending research gates. This is a deployment decision,
not a retrospective declaration that the candidate passed those gates.
"""
import argparse
from datetime import datetime, timezone
import time

from economy_feedback import record
from hosted_wave import client, get
from jordan_lineup import STUDY
from jordan_lineup_promote import PRIORS
from jordan_lineup_wide import ROOT as WIDE, WINNER
from policy_ir import HERE, compile_policy, digest, extract, read, write
from release_deploy import AARON, champions
from release_deploy_pair import check_champions, select, verify_owned
from release_hosted import OPTIMIZER
from release_workspace import verify
from win_hosted import live

OUT = STUDY / 'deployment-requested'
NOTE = ('User explicitly said "promote it" after being told the broad tests were pending and '
        'Richard69 scored57/80 versus deployed60/80, missing the earlier red guardrail by one win. '
        'Promote the exact named blue_repair:v1 and its byte-identical Aaron registration now. '
        'Jordan186 passed80/80 (40 per color), local60 full-gameplay parity and exact replay '
        'reconstruction passed. Broad evaluation continues; its original gates remain unchanged. '
        'This deployment is explicitly requested, not a claim of passing broad validation.')


def main(apply=False):
    verify()
    OUT.mkdir(exist_ok=True)
    plan = read(WIDE / 'plan.json')
    source = (STUDY / 'candidate/policy.bas').read_bytes()
    local, jordan = read(STUDY / 'local/comparison.json'), read(WINNER / 'jordan-result.json')
    if local['selected'] != 'blue_repair' or not local['all_gameplay_equal'] or jordan['wins'] != 80 or not jordan['passed']:
        raise ValueError('Existing evaluated candidate evidence changed')
    versions, metadata = {}, {}
    for player, folder in ((OPTIMIZER, WINNER), (AARON, WINNER / 'deployment-pair/aaron-upload')):
        versions[player] = read(folder / 'uploaded-version.json')
        metadata[player] = read(folder / 'upload-request.json')
        if metadata[player]['player_id'] != player or metadata[player]['content_hash'] != digest(source):
            raise ValueError('Exact executable or owner changed')
    ids = {p: v['id'] for p, v in versions.items()}
    if ids != {OPTIMIZER: 'b61bfdfb-f82f-4c6b-a504-5c040ed82a68', AARON: 'b64f1ccb-02e1-4ad5-b75b-f374222e9e9a'}:
        raise ValueError('Unexpected requested pair')
    if plan['candidate_versions'] != [ids[OPTIMIZER], ids[AARON]] or plan['basic_sha256'] != digest(source):
        raise ValueError('Requested pair differs from the frozen evaluation')
    game = live()
    if (game['id'] != plan['target']['coworld_id'] or game['version'] != plan['game_version'] or
            game['manifest']['game']['runnable']['source_url'] != plan['game_source']):
        raise ValueError('Live game differs from evaluated release')
    decision_path = OUT / 'decision.json'
    if not decision_path.exists():
        write(decision_path, {'authorization_verbatim': 'promote it', 'context': NOTE,
              'requested_at': datetime.now(timezone.utc).isoformat(), 'versions': ids,
              'rollback_versions': PRIORS, 'source_sha256': digest(source),
              'evaluation_status': 'broad_pending_historical_richard_guardrail_missed',
              'frozen_evaluation_plan': str(WIDE / 'plan.json'),
              'frozen_evaluation_plan_sha256': digest((WIDE / 'plan.json').read_bytes()),
              'jordan_result_sha256': digest((WINNER / 'jordan-result.json').read_bytes())})
    decision = read(decision_path)
    if decision['versions'] != ids or decision['source_sha256'] != digest(source):
        raise ValueError('Frozen deployment decision changed')
    feedback = OUT / 'policy'
    if not feedback.exists():
        parent = WINNER / 'jordan-feedback'
        record(parent / 'policy.ir.json', parent / 'policy.bas', NOTE, decision_path, feedback)
    policy = read(feedback / 'policy.ir.json')
    if ((feedback / 'policy.bas').read_bytes() != source or compile_policy(policy).encode() != source or
            extract(source.decode(), policy) != policy):
        raise ValueError('Semantic IR/executable parity failed')
    with client() as c:
        before = check_champions(champions(c), ids, PRIORS)
        for player, version in versions.items():
            verify_owned(c, version, player)
            remote = get(c, '/stats/policy-versions/' + version['id'])
            if remote.get('player_file_content_hash') not in (None, digest(source)):
                raise ValueError('Remote executable changed')
        write(OUT / 'preflight.json', {'checked_at': datetime.now(timezone.utc).isoformat(),
              'before': list(before.values()), 'versions': ids, 'decision': str(decision_path),
              'source_sha256': digest(source), 'semantic_ir_sha256': digest(policy),
              'game_version': game['version'], 'ready_for_requested_deployment': True,
              'broad_validation_passed': False})
        if not apply:
            print('Exact requested pair, source, live release, IR parity and two owned players verified.', flush=True)
            return
        log = HERE / 'VERSION_LOG.md'
        marker = '## Explicit blue_repair promotion before broad validation'
        if marker not in log.read_text():
            with log.open('a') as f:
                f.write('\n' + marker + '\n\nUser authorization: "promote it".\n\n' + NOTE +
                        '\n\nRollback: reselect prior long_three pair ' + str(PRIORS) +
                        '\n\nDecision record: ' + str(decision_path) + '\n')
        tags = {'semantic_ir_sha256': digest(policy), 'symbolic_policy_sha256': digest(source),
                'ir_revision': str(policy['update']['revision']), 'game_version': game['version'],
                'validation': NOTE, 'deployment_basis': 'explicit_user_request_before_broad_validation',
                'feedback_parity': 'Exact compile and reverse extraction; tested BASIC unchanged.'}
        for player, version in versions.items():
            remote = get(c, '/stats/policy-versions/' + version['id'])
            response = c.put('/stats/policy-versions/' + version['id'] + '/tags', json=(remote.get('tags') or {}) | tags)
            response.raise_for_status()
            saved = get(c, '/stats/policy-versions/' + version['id'])['tags']
            if any(saved.get(k) != v for k, v in tags.items()):
                raise ValueError('Deployment evidence tags did not persist')
            current = check_champions(champions(c), ids, PRIORS)
            if current[player]['policy_version']['id'] != version['id']:
                select(c, player, version, OUT / ('optimizer' if player == OPTIMIZER else 'aaron'), NOTE)
            for _ in range(12):
                current = check_champions(champions(c), ids, PRIORS)
                if current[player]['policy_version']['id'] == version['id']: break
                time.sleep(5)
            else: raise ValueError('Selection pending; resume existing submission')
            print('Active champion verified:', player, version['name'] + ':v' + str(version['version']), flush=True)
        after = check_champions(champions(c), ids, PRIORS)
        if any(after[p]['policy_version']['id'] != v for p, v in ids.items()):
            raise ValueError('Both selections have not verified')
        write(OUT / 'deployment-verified.json', {'verified_at': datetime.now(timezone.utc).isoformat(),
              'owned_active_ladder_players': 2, 'players': list(after.values()), 'versions': ids,
              'source_sha256': digest(source), 'semantic_ir_sha256': digest(policy),
              'ir_policy_pair': str(feedback), 'decision': str(decision_path), 'broad_validation_passed': False})
        write(HERE / 'active_policy.json', {'players': [{'player': p, 'version': v['id'],
              'label': f'{v["name"]}:v{v["version"]}'} for p, v in versions.items()],
              'policy': str(feedback / 'policy.bas'), 'semantic_ir': str(feedback / 'policy.ir.json'),
              'deployment_receipt': str(OUT / 'deployment-verified.json')})
        with log.open('a') as f:
            f.write('\nExplicit blue_repair promotion verified: submitted, both existing champions active. ' + str(OUT / 'deployment-verified.json') + '\n')
    print('Requested promotion complete; exactly two active owned ladder players verified.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    main(parser.parse_args().apply)
