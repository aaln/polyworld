"""Promote the exact user-named repair only after its complete broad validation."""
import argparse
from datetime import datetime, timezone
import time

from hosted_wave import client, get
from jordan_lineup import STUDY
from jordan_lineup_wide import ROOT, WINNER, AUTHORIZATION, metric_checks
from policy_ir import HERE, compile_policy, digest, extract, read, write
from release_deploy import AARON, champions
from release_deploy_pair import check_champions, select, verify_owned
from release_hosted import OPTIMIZER
from release_workspace import verify
from win_hosted import live

PRIORS = {OPTIMIZER: 'fb8454da-1657-40fe-ad1b-bcf185d0bcaa',
          AARON: '3a1c17a7-6f8f-4aa0-a297-c3f2bf14b2d0'}


def validate_result(plan, result):
    if (not result['passed'] or not result['checks'] or not all(result['checks'].values()) or
            result['plan_sha256'] != digest(plan) or result['games_per_head_arm'] != 1040 or
            result['games_per_mixed_arm'] != 200 or len(result['heads']) != 13 or
            set(result['heads']) != {r['id'] for r in plan['rivals']}):
        raise ValueError('Complete passing current-field evidence is required')
    if any(h[a]['games'] != 80 for h in result['heads'].values() for a in ('candidate', 'control')):
        raise ValueError('Incomplete direct matchup')
    if any(result['arms'][a]['games'] != 200 for a in ('candidate', 'control')):
        raise ValueError('Incomplete mixed comparison')
    checks = metric_checks(plan, result['arms'], result['heads'],
                           result['checks']['prior_guardrails'], result['checks']['jordan'])
    if checks != result['checks'] or not all(checks.values()):
        raise ValueError('Recomputed promotion gates failed')


def readiness():
    verify()
    local = read(STUDY / 'local/comparison.json')
    if local['selected'] != 'blue_repair' or local['games'] != 60 or not local['all_gameplay_equal']:
        raise ValueError('Local full-gameplay parity validation is required')
    plan, result = read(ROOT / 'plan.json'), read(ROOT / 'result.json')
    # File hashing and semantic hashing differ: the verdict pins exact saved JSON.
    if result['plan_sha256'] != digest((ROOT / 'plan.json').read_bytes()):
        raise ValueError('Frozen plan file changed')
    semantic_result = result | {'plan_sha256': digest(plan)}
    validate_result(plan, semantic_result)
    for path, expected in result['evidence_sha256'].items():
        from pathlib import Path
        if digest(Path(path).read_bytes()) != expected:
            raise ValueError('Evidence file changed: ' + path)
    review = read(WINNER / 'replay-review/result.json')
    if not review['representatives'] or not all(r['summary']['all_state_hashes_equal'] and
            r['summary']['all_actions_consumed'] for r in review['representatives']):
        raise ValueError('Exact candidate replay reconstruction is required')
    source = (STUDY / 'candidate/policy.bas').read_bytes()
    feedback = ROOT / 'feedback'
    policy = read(feedback / 'policy.ir.json')
    if (digest(source) != plan['basic_sha256'] or (feedback / 'policy.bas').read_bytes() != source or
            compile_policy(policy).encode() != source or extract(source.decode(), policy) != policy):
        raise ValueError('Validated semantic IR and uploaded executable differ')
    versions = {}
    for player, folder in ((OPTIMIZER, WINNER), (AARON, WINNER / 'deployment-pair/aaron-upload')):
        version, metadata = read(folder / 'uploaded-version.json'), read(folder / 'upload-request.json')
        if metadata['player_id'] != player or metadata['content_hash'] != digest(source):
            raise ValueError('Candidate registration/source mismatch')
        versions[player] = version
    if [versions[p]['id'] for p in (OPTIMIZER, AARON)] != plan['candidate_versions']:
        raise ValueError('Validated pair differs from deployment pair')
    if versions[OPTIMIZER]['id'] != 'b61bfdfb-f82f-4c6b-a504-5c040ed82a68':
        raise ValueError('Not the exact user-named candidate')
    game = live()
    if (game['id'] != plan['target']['coworld_id'] or game['version'] != plan['game_version'] or
            game['manifest']['game']['runnable']['source_url'] != plan['game_source']):
        raise ValueError('Live game changed after testing')
    return plan, result, versions, source, policy, feedback


def main(apply=False):
    plan, result, versions, source, policy, feedback = readiness()
    ids = {p: v['id'] for p, v in versions.items()}
    out = ROOT / 'deployment'; out.mkdir(exist_ok=True)
    mixed = result['arms']
    note = (f'User explicitly authorized this candidate for both existing league players if broad tests pass. '
            f'Jordan80/80; current13-rival wins {result["head_wins"]}/1040 each; '
            f'fresh mixed allied {mixed["candidate"]["allied_wins"]}/160 vs deployed{mixed["control"]["allied_wins"]}/160. '
            'All frozen gates passed; full replay/VM/source/ownership/equipment checks and exact IR roundtrip. '
            'Repeated fixed lineups limit independent-trial claims. Evidence: ' + str(ROOT))
    with client() as c:
        before = check_champions(champions(c), ids, PRIORS)
        for player, version in versions.items():
            verify_owned(c, version, player)
            remote = get(c, '/stats/policy-versions/' + version['id'])
            if remote.get('player_file_content_hash') not in (None, digest(source)):
                raise ValueError('Remote source hash differs')
        write(out / 'preflight.json', {'authorization': AUTHORIZATION, 'checked_at': datetime.now(timezone.utc).isoformat(),
              'before': list(before.values()), 'versions': ids, 'rollback_versions': PRIORS,
              'source_sha256': digest(source), 'semantic_ir_sha256': digest(policy),
              'result_sha256': digest((ROOT / 'result.json').read_bytes()), 'ready': True})
        if not apply:
            print('Passing broad evidence and exact pair verified; no selections changed.', flush=True)
            return
        log = HERE / 'VERSION_LOG.md'
        marker = '## Lineup repair current-field decision'
        if marker not in log.read_text():
            with log.open('a') as f:
                f.write('\n' + marker + '\n\nValidation: validated.\n\n' + note +
                        '\n\nUser authorization (verbatim): ' + AUTHORIZATION +
                        '\n\nRollback: reselect the two long_three versions ' + str(PRIORS) +
                        '; retain exact membership receipts. Rollback has not been executed.\n')
        tags = {'semantic_ir_sha256': digest(policy), 'symbolic_policy_sha256': digest(source),
                'ir_revision': str(policy['update']['revision']), 'game_version': plan['game_version'],
                'validation': note, 'feedback_parity': 'Exact compile/reverse extraction of unchanged tested BASIC.'}
        for player, version in versions.items():
            remote = get(c, '/stats/policy-versions/' + version['id'])
            response = c.put('/stats/policy-versions/' + version['id'] + '/tags', json=(remote.get('tags') or {}) | tags)
            response.raise_for_status()
            saved = get(c, '/stats/policy-versions/' + version['id'])['tags']
            if any(saved.get(k) != v for k, v in tags.items()):
                raise ValueError('Final IR evidence tags did not persist')
            current = check_champions(champions(c), ids, PRIORS)
            if current[player]['policy_version']['id'] != version['id']:
                select(c, player, version, out / ('optimizer' if player == OPTIMIZER else 'aaron'), note)
            for _ in range(12):
                current = check_champions(champions(c), ids, PRIORS)
                if current[player]['policy_version']['id'] == version['id']: break
                time.sleep(5)
            else:
                raise ValueError('Selection still pending; resume the existing submission')
            print('Active champion verified:', player, version['name'], flush=True)
        after = check_champions(champions(c), ids, PRIORS)
        if any(after[p]['policy_version']['id'] != v for p, v in ids.items()):
            raise ValueError('Both active champions did not verify')
        write(out / 'deployment-verified.json', {'verified_at': datetime.now(timezone.utc).isoformat(),
              'owned_active_ladder_players': 2, 'players': list(after.values()), 'versions': ids,
              'source_sha256': digest(source), 'semantic_ir_sha256': digest(policy), 'ir_policy_pair': str(feedback)})
        write(HERE / 'active_policy.json', {'players': [{'player': p, 'version': v['id'],
              'label': f'{v["name"]}:v{v["version"]}'} for p, v in versions.items()],
              'policy': str(feedback / 'policy.bas'), 'semantic_ir': str(feedback / 'policy.ir.json'),
              'deployment_receipt': str(out / 'deployment-verified.json')})
        receipt_marker = 'Lineup repair deployment verified:'
        if receipt_marker not in log.read_text():
            with log.open('a') as f:
                f.write('\n' + receipt_marker + ' submitted; exactly two active owned champions. ' + str(out / 'deployment-verified.json') + '\n')
    print('Both existing players promoted and verified active.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    main(parser.parse_args().apply)
