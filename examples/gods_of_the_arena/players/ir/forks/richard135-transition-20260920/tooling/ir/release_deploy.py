"""Select a confirmed, field-checked candidate for the existing Optimizer player.

The default is read-only. --apply performs the user-authorized league update;
future uploads never become champions automatically.
"""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import time

from release_hosted import OPTIMIZER
from hosted_wave import client, get
from policy_ir import compile_policy, digest, extract, read, write
from prepare_campaign_xp import CONTROL, DIVISION, LEAGUE

AARON = 'ply_630a768f-d623-44b2-80fa-36968d6fa75a'
PRIOR_OPTIMIZER = 'c5711f9d-6248-4843-ae39-bc13a4911b79'


def readiness(directory):
    root = directory / 'hosted-confirmation'
    plan = read(root / 'plan.json')
    result = read(root / 'result.json')
    field_plan, field = [read(directory / 'field' / n) for n in ['plan.json', 'result.json']]
    name = plan['candidate']
    discovery = directory / 'hosted-discovery'
    version = read(discovery / name / 'uploaded-version.json')
    metadata = read(discovery / name / 'upload-request.json')
    policy = read(root / name / 'feedback/policy.ir.json')
    source = (directory / 'local/candidates' / name / 'policy.bas').read_text()
    if (not result['passed'] or result['selected'] != name or not field['passed'] or
            field['version'] != version['id'] or field['candidate'] != name):
        raise ValueError('Independent confirmation and broad-field check must both pass')
    if (plan['sample_size'] != 400 or
            any(result['arms'][arm]['games'] != 400 for arm in ['v2', 'cadence', name]) or
            field['games'] != 100 or field['wins'] < 50 or field['equipment_games'] != 100):
        raise ValueError('Incomplete or nonqualifying held-out evidence')
    if (field_plan['confirmation_sha256'] != digest((root / 'result.json').read_bytes()) or
            plan['discovery_sha256'] != digest((discovery / 'result.json').read_bytes()) or
            set(field_plan['excluded_players']) != {AARON, OPTIMIZER}):
        raise ValueError('Evidence provenance or owned-player exclusion changed')
    if (compile_policy(policy) != source or extract(source, policy) != policy or
            digest(source.encode()) != metadata['content_hash'] or metadata['player_id'] != OPTIMIZER):
        raise ValueError('Validated IR, executable or player binding changed')
    return plan, version, metadata


def champions(c):
    return get(c, f'/v2/league-policy-memberships?league_id={LEAGUE}&champions_only=true&mine=true&limit=100')


def owned_champions(rows, candidate):
    owned = [r for r in rows if r.get('player', {}).get('id') in {AARON, OPTIMIZER}]
    by_player = {r['player']['id']: r for r in owned}
    if len(rows) != 2 or len(owned) != 2 or set(by_player) != {AARON, OPTIMIZER}:
        raise ValueError('Expected exactly the two existing owned champions')
    for row in owned:
        if (row['division']['id'] != DIVISION or row['status'] != 'competing' or
                row['substatus'] != 'active' or not row['is_champion']):
            raise ValueError('Owned champion is not active in the intended ladder')
    if (by_player[AARON]['policy_version']['id'] != CONTROL or
            by_player[OPTIMIZER]['policy_version']['id'] not in {PRIOR_OPTIMIZER, candidate}):
        raise ValueError('A deployed policy changed outside this experiment')
    return by_player


def main(directory, apply=False):
    from release_workspace import verify
    verify()
    plan, version, metadata = readiness(directory)
    out = directory / 'deployment'
    out.mkdir(exist_ok=True)
    with client() as c:
        league = get(c, '/v2/leagues/' + LEAGUE)
        coworld = get(c, '/v2/coworlds/' + league['game']['coworld_id'])
        if (coworld['id'] != plan['target']['coworld_id'] or coworld['version'] != plan['game_version'] or
                coworld['manifest']['game']['runnable']['source_url'] != plan['game_source']):
            raise ValueError('Published game changed since evaluation')
        rows = champions(c)
        before = owned_champions(rows, version['id'])
        versions = get(c, '/v2/policy-versions?mine=true&limit=100&q=' + metadata['name'])
        entries = versions if isinstance(versions, list) else versions.get('entries', versions.get('policy_versions', []))
        matching = [v for v in entries if v.get('policy_version_id', v.get('id')) == version['id']]
        if len(matching) != 1 or matching[0].get('player_id') != OPTIMIZER:
            raise ValueError('Uploaded candidate is not owned by Optimizer')
        write(out / 'preflight.json', {'checked_at': datetime.now(timezone.utc).isoformat(),
              'game': coworld['version'], 'version': version, 'owned_champions': list(before.values()),
              'confirmation_sha256': digest((directory / 'hosted-confirmation/result.json').read_bytes()),
              'field_sha256': digest((directory / 'field/result.json').read_bytes()),
              'source_sha256': metadata['content_hash'], 'readiness_passed': True})
        if not apply:
            print('Ready: exact validated candidate, current game, correct player, two active champions. No league mutation.')
            return
        membership = before[OPTIMIZER]
        if membership['policy_version']['id'] != version['id']:
            path = f'/v2/league-submissions?league_id={LEAGUE}&player_id={OPTIMIZER}&policy_version_id={version["id"]}&limit=100'
            submissions = get(c, path)
            matches = [s for s in submissions if s['policy_version']['id'] == version['id'] and s['player']['id'] == OPTIMIZER]
            if not matches:
                body = {'league_id': LEAGUE, 'policy_version_id': version['id'], 'player_id': OPTIMIZER,
                        'auto_champion': 'never', 'notes': 'User-authorized autoresearch promotion: independent400games/arm versus both deployed controls and100game sampled-field guardrail passed; full replay audits and IR/executable parity verified.'}
                write(out / 'submission-request.json', body)
                response = c.post('/v2/league-submissions', json=body)
                response.raise_for_status()
                write(out / 'submission-created.json', response.json())
            for attempt in range(60):
                submissions = get(c, path)
                write(out / 'submissions-readback.json', submissions)
                matches = [s for s in submissions if s['policy_version']['id'] == version['id'] and s['player']['id'] == OPTIMIZER]
                if len(matches) != 1:
                    raise ValueError('Expected one exact candidate submission; retain receipts and reconcile')
                submission = matches[0]
                if submission['status'] in {'failed', 'rejected', 'cancelled'}:
                    raise ValueError('League rejected the submission: ' + submission['status'])
                if submission['status'] == 'placed' and submission.get('league_policy_membership_id'):
                    break
                time.sleep(5)
            else:
                raise ValueError('Placement pending; resume exact submission instead of creating another')
            response = c.post('/v2/league-policy-memberships/' + submission['league_policy_membership_id'] + '/champion', json={})
            response.raise_for_status()
            write(out / 'champion-response.json', response.json())
        for attempt in range(12):
            rows = champions(c)
            after = owned_champions(rows, version['id'])
            if after[OPTIMIZER]['policy_version']['id'] == version['id']:
                break
            time.sleep(5)
        else:
            raise ValueError('Champion selection has not verified; retain receipts and reconcile')
        write(out / 'deployment-verified.json', {'verified_at': datetime.now(timezone.utc).isoformat(),
              'owned_active_ladder_players': 2, 'players': list(after.values()),
              'source_sha256': metadata['content_hash'], 'version': version,
              'decision': 'Independent confirmation and current-field guardrail passed; user-authorized selection on Optimizer.'})
        print(f"Deployed {version['name']}:v{version['version']} on Aaron's Optimizer; exactly two active ladder champions verified.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    main(args.directory.resolve(), args.apply)
