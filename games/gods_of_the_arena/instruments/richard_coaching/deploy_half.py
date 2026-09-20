"""Deploy the unchanged half-win specialist under the user's new explicit scope."""
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

import httpx
import jsonschema

ROOT = Path(__file__).resolve().parents[4]
CLEAN = ROOT.parent / 'polyworld-gota-clean-20260916-r5/examples/gods_of_the_arena/players/ir'
sys.path.insert(0, str(CLEAN))
from hosted_wave import client, get
from release_deploy_pair import select, verify_owned

CAMPAIGN = ROOT.parent / 'gota-autoresearch'
OUT = ROOT / 'tmp/gota-ir/richard-half-deployment-20260920'
ORIGINAL = ROOT / 'tmp/gota-ir/richard-coaching-20260920/candidates/formation3600'
BUNDLE = ROOT / 'examples/gods_of_the_arena/players/ir/forks/richard135-coaching-20260920'
PAIR = BUNDLE / 'evaluated/formation3600'
LEAGUE = 'league_3c60897b-25cf-4b37-9d1a-8554c1198f28'
PLAYERS = {'aaron': 'ply_630a768f-d623-44b2-80fa-36968d6fa75a',
           'coach': 'ply_594ec24d-d7f3-4370-a000-468354ec41c9'}
RICHARD = '7c370daf-3c5f-42f8-870b-54b79c495a44'
SOURCE_HASH = 'e9eac314c36c06be53af969b54be0eb42a9ee329b0c6d1874eebda489d645e4a'
AUTH = "deploy the policy to league that can beat richard's v135 even half the time to both players. it's important even while we work that we start beating him"
NOTE = ('Explicit user-authorized interim deployment to both Aaron and Coach: formation3600 '
        'won40/80 Richard v135 games, blue40W0L0D/red0W14L26D, all80 full replay/ten-VM audits. '
        'Repeated trajectories; no independent-trial significance or future50% guarantee. '
        'Original both-color Richard gate failed; Alex/Jordan/field unqualified. '
        'New user half-win scope supersedes prior conditional deployment scope, not research acceptance.')
LOG = ROOT / 'games/gods_of_the_arena/players/richard135-counter/VERSION_LOG.md'


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2) + '\n')
    temp.replace(path)


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def owned_champions(c):
    rows = get(c, f'/v2/league-policy-memberships?league_id={LEAGUE}&mine=true&champions_only=true&limit=100')
    assert len(rows) < 100
    result = {r['player']['id']: r for r in rows}
    assert set(result) == set(PLAYERS.values()), 'Unexpected owned champions'
    assert all(r['status'] == 'competing' and r['substatus'] == 'active' and r['is_champion'] for r in rows)
    return result


def upload(c, label, metadata, source, schema):
    dest = OUT / label
    path = dest / 'upload-request.json'
    if path.exists():
        assert read(path) == metadata
    write(path, metadata)
    jsonschema.validate(metadata, schema['components']['schemas']['PlayerFilePolicyUploadRequest'])
    receipt = dest / 'uploaded-version.json'
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
    write(dest / 'owned-readback.json', verify_owned(c, version, metadata['player_id']))
    return version


def main(apply=False):
    OUT.mkdir(exist_ok=True)
    with (CAMPAIGN / 'league-deployment.lock').open('a+') as held:
        fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
        source = (PAIR / 'policy.bas').read_bytes()
        assert digest(source) == SOURCE_HASH
        assert source == (ORIGINAL / 'policy.bas').read_bytes()
        proof = subprocess.run([sys.executable, str(BUNDLE / 'reproduce.py'), '--pair', str(PAIR)],
                               check=True, capture_output=True, text=True)
        write(OUT / 'conversion-proof.json', json.loads(proof.stdout))
        validation = read(PAIR / 'validation.json')
        for color, expected in [('red', (0, 14, 26)), ('blue', (40, 0, 0))]:
            saved = validation['Richard'][color]['evidence']
            raw = Path(saved['artifact']).read_bytes()
            assert digest(raw) == saved['sha256']
            arm = json.loads(raw)
            assert arm['games'] == 40 and arm['all_full_audits_passed'] and arm['structured_ten_vm_exits']
            assert tuple(arm[k] for k in ('wins', 'losses', 'draws')) == expected
        write(OUT / 'selection.json', {'authorization_verbatim': AUTH, 'selected': 'formation3600',
              'source_sha256': SOURCE_HASH, 'pair': str(PAIR), 'evidence': validation,
              'new_deployment_threshold_met': True, 'research_acceptance_advanced': False,
              'selection_rule': 'Among valid saved Richard80-game policies with40wins, choose fewest losses.',
              'scope': NOTE})
        with client() as c:
            game = get(c, '/v2/coworlds/cow_126f2fcb-80a0-4b6e-8166-eb6163576db5')
            assert game['version'] == '2026.9.16.5'
            assert '/tree/f2ab9598d8f8001b6beae3e66404e341770c803f/' in game['manifest']['game']['runnable']['source_url']
            rivals = get(c, f'/v2/league-policy-memberships?league_id={LEAGUE}&champions_only=true&limit=100')
            assert any(r['player']['id'] == 'ply_ded11f40-3e30-4921-b019-f7f6bc3e9c83' and r['policy_version']['id'] == RICHARD for r in rivals)
            schema = get(c, '/openapi.json')
            write(OUT / 'live-schema.json', schema)
            write(OUT / 'game-at-apply.json', game)
            current = owned_champions(c)
            before_path = OUT / 'champions-before.json'
            if not before_path.exists():
                write(before_path, current)
            before = read(before_path)
            write(OUT / 'rollback.json', {p: {'policy_version': r['policy_version'], 'membership': r['id'],
                  'action': f"POST /v2/league-policy-memberships/{r['id']}/champion", 'body': {},
                  'expected_time': 'One authenticated selection and readback; no rebuild.'} for p, r in before.items()})
            for label, player in PLAYERS.items():
                receipt = OUT / label / 'uploaded-version.json'
                allowed = {before[player]['policy_version']['id']}
                if receipt.exists():
                    allowed.add(read(receipt)['id'])
                assert current[player]['policy_version']['id'] in allowed, 'Concurrent champion change'
            write(OUT / 'preflight.json', {'checked_at': now(), 'ready': True, 'authorization': AUTH,
                  'source_sha256': SOURCE_HASH, 'prior_champions': before, 'scope': NOTE})
            if not apply:
                print('Read-only preflight passed for both players.', flush=True)
                return
            versions = {}
            for label, player in PLAYERS.items():
                metadata = read(ORIGINAL / 'upload-request.json')
                if label == 'coach':
                    metadata.update(name=metadata['name'] + '-coach', player_id=player,
                                    tags=metadata['tags'] | {'validation': NOTE, 'authorization': AUTH})
                version = upload(c, label, metadata, source, schema)
                if label == 'aaron':
                    assert version['id'] == read(ORIGINAL / 'uploaded-version.json')['id'], 'Original content identity changed'
                versions[player] = version
            decision = {'recorded_at': now(), 'authorization_verbatim': AUTH, 'league': LEAGUE,
                        'versions': versions, 'source_sha256': SOURCE_HASH, 'evidence': validation,
                        'scope': NOTE, 'rollback': read(OUT / 'rollback.json')}
            if not (OUT / 'decision.json').exists():
                write(OUT / 'decision.json', decision)
            marker = '## Half-win deployment decision 2026-09-20'
            if marker not in LOG.read_text():
                with LOG.open('a') as log:
                    log.write('\n\n' + marker + '\n\n- User: ' + AUTH + '\n- ' + NOTE +
                              '\n- Exact versions, evidence and rollback: `' + str(OUT / 'decision.json') +
                              '`. Validation: qualified only for new user-authorized interim threshold.\n')
            for label, player in PLAYERS.items():
                current = owned_champions(c)
                for p, r in current.items():
                    assert r['policy_version']['id'] in {before[p]['policy_version']['id'], versions[p]['id']}
                version = versions[player]
                if current[player]['policy_version']['id'] != version['id']:
                    print('SUBMITTING', label, version['id'], flush=True)
                    select(c, player, version, OUT / label / 'league', NOTE)
                for attempt in range(120):
                    rows = get(c, f'/v2/league-policy-memberships?league_id={LEAGUE}&mine=true&limit=100')
                    write(OUT / label / 'qualification-readback.json', rows)
                    matches = [r for r in rows if r['player']['id'] == player and r['policy_version']['id'] == version['id']]
                    assert len(matches) == 1, 'Expected exact selected membership'
                    r = matches[0]
                    if r['status'] in {'disqualified', 'retired', 'rejected'}:
                        raise ValueError('Qualification failed; reconcile saved receipts')
                    if r['status'] == 'competing' and r['substatus'] == 'active' and r['is_champion']:
                        print('VERIFIED', label, version['id'], r['id'], flush=True)
                        break
                    time.sleep(5)
                else:
                    raise ValueError('Qualification pending; resume existing receipts')
            final = owned_champions(c)
            assert all(final[p]['policy_version']['id'] == v['id'] for p, v in versions.items())
            write(OUT / 'deployment-verified.json', {'verified_at': now(), 'league': LEAGUE,
                  'players': final, 'versions': versions, 'source_sha256': SOURCE_HASH,
                  'state': 'both_competing_active_champions', 'scope': NOTE})
            with LOG.open('a') as log:
                log.write('\n- Deployment verified ' + now() + ': both active competing champions. Receipt `' + str(OUT / 'deployment-verified.json') + '`.\n')
            print('Both players deployed and verified.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    main(parser.parse_args().apply)
