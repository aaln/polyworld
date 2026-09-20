"""Register the validated Jordan268 executable for Aaron and select his champion."""
import hashlib
import json
from pathlib import Path
import time

import httpx

from promote import BUNDLE, LEAGUE, STUDY, champions, client, get, live, now, read, verify_owned
from release_deploy_pair import select

PLAYER = 'ply_630a768f-d623-44b2-80fa-36968d6fa75a'
PRIOR_VERSION = 'eae99cdd-b2a9-4426-aa20-289d8637fa54'
ORIGINAL_VERSION = '00cd9483-0309-4613-bf61-89f3f4a33d01'
OUT = STUDY / 'promotion-aaron'
LOG = Path(__file__).resolve().parents[2] / 'players/jordan268-counter/VERSION_LOG.md'
AUTHORIZATION = 'upgrade this playre\nAaron aaron-gota-ir-relh154-legacy-0916-aaron:v1'
VALIDATION = ('Byte-identical registration of the Jordan268 counter just promoted for Aaron’s Co-play Coach. '
              'Original executable confirmed 40/40 red and 40/40 blue with full replay/VM/roster/score/XP '
              'audits. Fixed lineups and repeated trajectories; broad-field superiority untested. '
              'This duplicate registration adds no independent evaluation evidence.')


def save(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')


def own(rows):
    matches = [r for r in rows if r['player']['id'] == PLAYER and r['is_champion']]
    if len(matches) != 1:
        raise ValueError('Expected one Aaron champion')
    return matches[0]


def main():
    manifest = read(BUNDLE / 'manifest.json')
    source = (BUNDLE / 'policy.bas').read_bytes()
    sha = hashlib.sha256(source).hexdigest()
    assert sha == manifest['basic_sha256']
    assert manifest['uploaded_version'] == ORIGINAL_VERSION and manifest['both_color_criterion_passed']
    for color in ('red', 'blue'):
        result = read(STUDY / 'hosted/confirmation/redrace' / color / 'result.json')
        assert result['n'] == result['wins'] == 40 and result['all_replay_vm_roster_checks']
    game = live()
    assert game['version'] == manifest['game_version']
    with client() as c:
        before_path = OUT / 'champions-before.json'
        if not before_path.exists():
            save('champions-before.json', champions(c))
        before = read(before_path)
        prior = own(before)
        assert prior['policy_version']['id'] == PRIOR_VERSION
        receipt_path = OUT / 'uploaded-version.json'
        version = read(receipt_path) if receipt_path.exists() else None
        allowed = {PRIOR_VERSION} | ({version['id']} if version else set())
        if own(champions(c))['policy_version']['id'] not in allowed:
            raise ValueError('Aaron champion changed; reconcile existing receipts')
        metadata = {
            'name': 'aaron-gota-ir-j268-redrace-0920-aaron',
            'content_hash': sha, 'size_bytes': len(source), 'player_id': PLAYER, 'attributes': {},
            'tags': {'game': 'gods_of_the_arena', 'game_version': game['version'],
                     'source_policy_version_id': ORIGINAL_VERSION,
                     'change': 'Identical validated Jordan268 counter, registered for Aaron',
                     'validation': VALIDATION, 'authorization': AUTHORIZATION}}
        metadata_path = OUT / 'upload-request.json'
        if metadata_path.exists() and read(metadata_path) != metadata:
            raise ValueError('Frozen upload metadata changed')
        save('upload-request.json', metadata)
        if version is None:
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
                    uploaded = httpx.put(payload['upload_url'], content=source,
                        headers={'Content-Type': 'application/octet-stream'}, timeout=120)
                    uploaded.raise_for_status()
                    response = c.post('/stats/policies/files/complete', json=metadata)
                    response.raise_for_status()
                    version = response.json()
            save('uploaded-version.json', version)
        log = LOG.read_text()
        if version['id'] not in log:
            LOG.write_text(log + f"\n## {version['name']}:v{version['version']}\n\n"
                f"- Version `{version['id']}`; player Aaron `{PLAYER}`; UTC {now()}.\n"
                f"- BASIC SHA `{sha}`; byte-identical to evaluated version `{ORIGINAL_VERSION}`.\n"
                f"- {VALIDATION} Runtime: published GOTA BASIC host {game['version']}.\n"
                f"- Initial state: registered; inert until submission and champion selection. Receipts: `{OUT}`.\n")
        save('owned-readback.json', verify_owned(c, version, PLAYER))
        print('REGISTERED_AARON', version['id'], f"{version['name']}:v{version['version']}", flush=True)
        decision = {
            'recorded_at': now(), 'authorization_verbatim': AUTHORIZATION,
            'league_id': LEAGUE, 'player_id': PLAYER, 'policy_version_id': version['id'],
            'source_policy_version_id': ORIGINAL_VERSION, 'basic_sha256': sha,
            'game_version': game['version'], 'validation': VALIDATION,
            'rollback': {'membership_id': prior['id'], 'policy_version_id': PRIOR_VERSION,
                         'policy_label': prior['policy_version'].get('label'),
                         'action': f"POST /v2/league-policy-memberships/{prior['id']}/champion",
                         'expected_time': 'One authenticated request and readback; no rebuild needed.'}}
        if not (OUT / 'decision.json').exists():
            save('decision.json', decision)
        decision = read(OUT / 'decision.json')
        assert decision['policy_version_id'] == version['id']
        if own(champions(c))['policy_version']['id'] != version['id']:
            print('SUBMITTING_AND_SELECTING', flush=True)
            select(c, PLAYER, version, OUT, AUTHORIZATION + '. ' + VALIDATION + ' BASIC SHA ' + sha)
        for _ in range(120):
            rows = get(c, f'/v2/league-policy-memberships?league_id={LEAGUE}&mine=true&limit=100')
            save('memberships-readback.json', rows)
            matches = [r for r in rows if r['player']['id'] == PLAYER
                       and r['policy_version']['id'] == version['id']]
            if len(matches) != 1:
                raise ValueError('Expected one exact Aaron membership; receipts preserved')
            selected = matches[0]
            state = {k: selected.get(k) for k in ('id', 'status', 'substatus', 'is_champion')}
            print('MEMBERSHIP', json.dumps(state), flush=True)
            if selected['status'] in {'disqualified', 'retired', 'rejected'}:
                raise ValueError('Qualification did not succeed: ' + selected['status'])
            if selected['status'] == 'competing' and selected.get('substatus') == 'active' and selected['is_champion']:
                after = champions(c)
                confirmed = own(after)
                assert confirmed['id'] == selected['id'] and confirmed['policy_version']['id'] == version['id']
                other_before = {r['player']['id']: r['policy_version']['id'] for r in before if r['player']['id'] != PLAYER}
                other_after = {r['player']['id']: r['policy_version']['id'] for r in after if r['player']['id'] != PLAYER}
                save('promotion-verified.json', {
                    'verified_at': now(), 'state': 'competing_active_champion', 'league_id': LEAGUE,
                    'player': confirmed['player'], 'policy_version': confirmed['policy_version'],
                    'membership_id': confirmed['id'], 'basic_sha256': sha,
                    'source_policy_version_id': ORIGINAL_VERSION, 'rollback': decision['rollback'],
                    'champions_after': after, 'other_players_unchanged': other_before == other_after})
                print('VERIFIED_AARON_UPGRADED', version['id'], confirmed['id'], flush=True)
                return
            time.sleep(5)
        raise ValueError('Qualification still pending; resume monitoring the existing membership')


if __name__ == '__main__':
    main()
