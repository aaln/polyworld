"""Deploy one validated executable under both existing owned league players."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import time

import httpx

from hosted_wave import client, get
from policy_ir import HERE, digest, read, write
from prepare_campaign_xp import CONTROL, DIVISION, LEAGUE
from release_deploy import AARON, PRIOR_OPTIMIZER, champions, readiness
from release_hosted import OPTIMIZER
from release_workspace import verify


def check_champions(rows, versions, prior_versions=None):
    by_player = {r['player']['id']: r for r in rows}
    if len(rows) != 2 or set(by_player) != {AARON, OPTIMIZER}:
        raise ValueError('Expected exactly the two existing owned players')
    priors = prior_versions if prior_versions is not None else {AARON: CONTROL, OPTIMIZER: PRIOR_OPTIMIZER}
    if set(priors) != {AARON, OPTIMIZER}:
        raise ValueError('Prior versions must cover both existing players')
    for player, prior in priors.items():
        row = by_player[player]
        if (row['division']['id'] != DIVISION or row['status'] != 'competing' or
                row['substatus'] != 'active' or not row['is_champion'] or
                row['policy_version']['id'] not in {prior, versions.get(player)}):
            raise ValueError('Unexpected champion state; reconcile before selecting policies')
    return by_player


def verify_owned(c, version, player):
    data = get(c, '/v2/policy-versions?mine=true&limit=100&q=' + version['name'])
    rows = data if isinstance(data, list) else data.get('entries', data.get('policy_versions', []))
    matches = [v for v in rows if v.get('policy_version_id', v.get('id')) == version['id']]
    if len(matches) != 1 or matches[0].get('player_id') != player:
        raise ValueError('Version ownership/player binding did not verify')
    return matches[0]


def clone_for_aaron(c, directory, original_metadata, source, validation_note=None):
    out = directory / 'deployment-pair/aaron-upload'
    out.mkdir(parents=True, exist_ok=True)
    metadata = original_metadata | {'name': original_metadata['name'] + '-aaron', 'player_id': AARON,
        'tags': original_metadata['tags'] | {'validation': validation_note or 'Byte-identical clone of independently confirmed and field-validated Optimizer policy',
            'authorization': 'User: update the policies from my players on the league'}}
    if digest(source) != metadata['content_hash']:
        raise ValueError('Clone differs from evaluated BASIC')
    request, receipt = out / 'upload-request.json', out / 'uploaded-version.json'
    if request.exists() and read(request) != metadata:
        raise ValueError('Frozen clone metadata changed')
    write(request, metadata)
    if not receipt.exists():
        response = c.post('/stats/policies/files/upload', json=metadata)
        if response.status_code == 409:
            response = c.post('/stats/policies/files/complete', json=metadata)
            response.raise_for_status()
            version = response.json()
        else:
            response.raise_for_status()
            payload = response.json()
            version = payload.get('existing_policy_version')
            if version is None:
                result = httpx.put(payload['upload_url'], content=source,
                    headers={'Content-Type': 'application/octet-stream'}, timeout=120)
                result.raise_for_status()
                response = c.post('/stats/policies/files/complete', json=metadata)
                response.raise_for_status()
                version = response.json()
        write(receipt, version)
    version = read(receipt)
    log = HERE / 'VERSION_LOG.md'
    text = log.read_text()
    if version['id'] not in text:
        text += (f"\n## {version['name']}:v{version['version']}\n\n"
            f"- ID `{version['id']}`; player Aaron; UTC {datetime.now(timezone.utc).isoformat()}.\n"
            f"- Identical evaluated BASIC SHA `{metadata['content_hash']}`; only player registration differs.\n"
            f'- {validation_note or "Validated by the original executable’s fresh 400-game-per-arm confirmation and 100-game field check."} No claim of independent evidence from this duplicate registration.\n'
            f"- Evidence: `{directory}`. Upload is inert until explicit champion selection.\n")
        log.write_text(text)
    write(out / 'owned-readback.json', verify_owned(c, version, AARON))
    return version


def select(c, player, version, out, validation_note=None):
    out.mkdir(exist_ok=True)
    path = f'/v2/league-submissions?league_id={LEAGUE}&player_id={player}&policy_version_id={version["id"]}&limit=100'
    rows = get(c, path)
    matches = [r for r in rows if r['policy_version']['id'] == version['id'] and r['player']['id'] == player]
    if not matches:
        body = {'league_id': LEAGUE, 'policy_version_id': version['id'], 'player_id': player,
            'auto_champion': 'never', 'notes': validation_note or 'User explicitly requested updates to both existing players. Exact executable passed fresh400games/arm against the frozen deployed baseline policy or policies and100current-field games; full replay/VM and IR parity verified. See the campaign confirmation and deployment receipts for exact versions.'}
        write(out / 'submission-request.json', body)
        response = c.post('/v2/league-submissions', json=body)
        response.raise_for_status()
        write(out / 'submission-created.json', response.json())
    for _ in range(60):
        rows = get(c, path)
        write(out / 'submissions-readback.json', rows)
        matches = [r for r in rows if r['policy_version']['id'] == version['id'] and r['player']['id'] == player]
        if len(matches) != 1:
            raise ValueError('Expected one exact submission; resume the existing receipt')
        submission = matches[0]
        if submission['status'] in {'failed', 'rejected', 'cancelled'}:
            raise ValueError('Submission failed: ' + submission['status'])
        if submission['status'] == 'placed' and submission.get('league_policy_membership_id'):
            break
        time.sleep(5)
    else:
        raise ValueError('Placement pending; resume this exact submission')
    response = c.post('/v2/league-policy-memberships/' + submission['league_policy_membership_id'] + '/champion', json={})
    response.raise_for_status()
    write(out / 'champion-response.json', response.json())


def main(directory, apply=False, readiness_fn=readiness, prior_versions=None, validation_note=None):
    verify()
    plan, candidate, metadata = readiness_fn(directory)
    out = directory / 'deployment-pair'
    out.mkdir(exist_ok=True)
    clone_path = out / 'aaron-upload/uploaded-version.json'
    clone = read(clone_path) if clone_path.exists() else None
    versions = {OPTIMIZER: candidate['id']}
    if clone:
        versions[AARON] = clone['id']
    source = (directory / 'local/candidates' / plan['candidate'] / 'policy.bas').read_bytes()
    with client() as c:
        league = get(c, '/v2/leagues/' + LEAGUE)
        game = get(c, '/v2/coworlds/' + league['game']['coworld_id'])
        if (game['id'] != plan['target']['coworld_id'] or game['version'] != plan['game_version'] or
                game['manifest']['game']['runnable']['source_url'] != plan['game_source']):
            raise ValueError('Live game changed since evaluation')
        before = check_champions(champions(c), versions, prior_versions)
        verify_owned(c, candidate, OPTIMIZER)
        if clone:
            verify_owned(c, clone, AARON)
        write(out / 'preflight.json', {'checked_at': datetime.now(timezone.utc).isoformat(),
            'authorization': 'update the policies from my players on the league',
            'players': [AARON, OPTIMIZER], 'prior_champions': list(before.values()),
            'candidate': candidate, 'source_sha256': digest(source),
            'confirmation_sha256': digest((directory / 'hosted-confirmation/result.json').read_bytes()),
            'field_sha256': digest((directory / 'field/result.json').read_bytes()), 'ready': True})
        if not apply:
            print('Validated for both existing players. Read-only preflight; Aaron clone registered only on apply.')
            return
        clone = clone_for_aaron(c, directory, metadata, source, validation_note)
        versions[AARON] = clone['id']
        for player, version, label in [(OPTIMIZER, candidate, 'optimizer'), (AARON, clone, 'aaron')]:
            current = check_champions(champions(c), versions, prior_versions)
            if current[player]['policy_version']['id'] != version['id']:
                select(c, player, version, out / label, validation_note)
            for _ in range(12):
                current = check_champions(champions(c), versions, prior_versions)
                if current[player]['policy_version']['id'] == version['id']:
                    break
                time.sleep(5)
            else:
                raise ValueError('Selection not visible; reconcile existing receipts')
            print(f"Verified {label}: {version['name']}:v{version['version']}", flush=True)
        after = check_champions(champions(c), versions, prior_versions)
        assert all(after[p]['policy_version']['id'] == v for p, v in versions.items())
        write(out / 'deployment-verified.json', {'verified_at': datetime.now(timezone.utc).isoformat(),
            'owned_active_ladder_players': 2, 'players': list(after.values()), 'source_sha256': digest(source),
            'versions': versions, 'decision': 'Both existing players updated as explicitly requested; identical validated executable, separate owned registrations.'})
        print('Both policies selected; exactly two active owned ladder champions verified.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    main(args.directory.resolve(), args.apply)
