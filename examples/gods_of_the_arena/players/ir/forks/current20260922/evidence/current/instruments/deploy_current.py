"""Deploy exact validated current-game bytes to the two authorized players."""
import argparse
import json
import subprocess
import sys
import time
import httpx
import jsonschema
from panel import h

OUT = h.STUDY / 'deployment'
PAIR = h.ROOT / 'examples/gods_of_the_arena/players/ir/forks/current20260922'
LEAGUE = 'league_3c60897b-25cf-4b37-9d1a-8554c1198f28'
PLAYERS = {'aaron': h.PLAYER, 'coach': 'ply_594ec24d-d7f3-4370-a000-468354ec41c9'}
PRIOR = {'aaron': h.INCUMBENT, 'coach': '7dcba95c-6966-4a86-b033-7ffcafa8991f'}
SOURCE = 'b82c379953831b719776ba4faf3ab21a5ac2d1d383ed7f93c5f70df26fc81098'
AUTH = ['deploy the policy to latest on league',
        "deploy the policy to league that can beat richard's v135 even half the time to both players. it's important even while we work that we start beating him"]
LOG = h.ROOT / 'games/gods_of_the_arena/players/micro20260922/VERSION_LOG.md'
NOTE = ('Current-game practiced policy: ranged-first public drafting, explicit skill points, '
        'actual-tick attack recovery, last-hit/XP positioning, equipment and purposeful portals. '
        'Exact BASIC passed current-engine both-color mixed A/B against deployed compat and '
        'later-draft guardrail, all VMs/replay/XP/score audited. Original target panel and its '
        'limitations remain preserved. Fixed rosters/correlated trajectories; no universal '
        'opponent, class or rank guarantee. Prior user league/latest and two-player authorization '
        'continues; this is not a new user approval or old-v135 qualification claim.')


def log_once(marker, body):
    text = LOG.read_text()
    if marker not in text:
        LOG.write_text(text + '\n\n' + marker + '\n\n' + body + '\n')


def champions(c):
    rows = h.get(c, f'/v2/league-policy-memberships?league_id={LEAGUE}&mine=true&champions_only=true&limit=100')
    assert len(rows) == 2 and {r['player']['id'] for r in rows} == set(PLAYERS.values())
    assert all(r['status'] == 'competing' and r['substatus'] == 'active' and r['is_champion'] for r in rows)
    return {r['player']['id']: r for r in rows}


def owned(c, version, player):
    data = h.get(c, '/v2/policy-versions?mine=true&limit=100&q=' + version['name'])
    rows = data if isinstance(data, list) else data.get('entries', data.get('policy_versions', []))
    matches = [v for v in rows if v.get('policy_version_id', v.get('id')) == version['id']]
    assert len(matches) == 1 and matches[0].get('player_id') == player
    return matches[0]


def upload_coach(c, source, schema):
    metadata = {'name': 'aaron-gota-micro0922-coach', 'content_hash': SOURCE,
                'size_bytes': len(source), 'player_id': PLAYERS['coach'], 'attributes': {},
                'tags': {'game': 'gods_of_the_arena', 'game_version': h.VERSION,
                         'engine_commit': h.COMMIT, 'validation': NOTE}}
    folder = OUT / 'coach'
    h.freeze(folder / 'upload-request.json', metadata)
    jsonschema.validate(metadata, schema['components']['schemas']['PlayerFilePolicyUploadRequest'])
    receipt = folder / 'uploaded-version.json'
    if not receipt.exists():
        r = c.post('/stats/policies/files/upload', json=metadata)
        if r.status_code == 409:
            r = c.post('/stats/policies/files/complete', json=metadata)
            r.raise_for_status()
            version = r.json()
        else:
            r.raise_for_status()
            payload = r.json()
            version = payload.get('existing_policy_version')
            if version is None:
                r = httpx.put(payload['upload_url'], content=source,
                              headers={'Content-Type': 'application/octet-stream'}, timeout=120)
                r.raise_for_status()
                r = c.post('/stats/policies/files/complete', json=metadata)
                r.raise_for_status()
                version = r.json()
        h.write(receipt, version)
    version = h.read(receipt)
    log_once('## Coach practiced registration ' + version['id'],
             f"- {version['name']}:v{version['version']}; registered {h.research.now()}; BASIC `{SOURCE}`.\n"
             '- Runtime: BASIC file, no container or argv. Byte-identical to tested Aaron source; separate player binding, not independent evidence.\n'
             '- Validation: validated executable via completed 320-game current mixed A/B and guardrail; registration inert until selection.\n'
             '- ' + NOTE)
    h.write(folder / 'owned-readback.json', owned(c, version, PLAYERS['coach']))
    return version


def select(c, label, version, schema):
    player = PLAYERS[label]
    folder = OUT / label / 'league'
    folder.mkdir(parents=True, exist_ok=True)
    query = f'/v2/league-submissions?league_id={LEAGUE}&player_id={player}&policy_version_id={version["id"]}&limit=100'
    rows = h.get(c, query)
    matches = [r for r in rows if r['policy_version']['id'] == version['id'] and r['player']['id'] == player]
    if not matches:
        body = {'league_id': LEAGUE, 'policy_version_id': version['id'], 'player_id': player,
                'auto_champion': 'never', 'notes': NOTE}
        definition = schema['paths']['/v2/league-submissions']['post']['requestBody']['content']['application/json']['schema']
        jsonschema.validate(body, definition, resolver=jsonschema.RefResolver.from_schema(schema))
        h.freeze(folder / 'submission-request.json', body)
        r = c.post('/v2/league-submissions', json=body)
        r.raise_for_status()
        h.write(folder / 'submission-created.json', r.json())
    for _ in range(120):
        rows = h.get(c, query)
        h.write(folder / 'submissions-readback.json', rows)
        matches = [r for r in rows if r['policy_version']['id'] == version['id'] and r['player']['id'] == player]
        assert len(matches) == 1, 'Reconcile existing submission; do not resubmit'
        row = matches[0]
        assert row['status'] not in ('failed', 'rejected', 'cancelled')
        if row['status'] == 'placed' and row.get('league_policy_membership_id'):
            break
        time.sleep(5)
    else:
        raise RuntimeError('Placement pending; resume exact existing receipts')
    r = c.post('/v2/league-policy-memberships/' + row['league_policy_membership_id'] + '/champion', json={})
    r.raise_for_status()
    h.write(folder / 'champion-response.json', r.json())
    for _ in range(120):
        rows = h.get(c, f'/v2/league-policy-memberships?league_id={LEAGUE}&mine=true&limit=100')
        h.write(folder / 'qualification-readback.json', rows)
        matches = [r for r in rows if r['player']['id'] == player and r['policy_version']['id'] == version['id']]
        assert len(matches) == 1
        row = matches[0]
        assert row['status'] not in ('disqualified', 'retired', 'rejected'), 'Use saved rollback and reconcile exact state'
        if row['status'] == 'competing' and row['substatus'] == 'active' and row['is_champion']:
            return row
        time.sleep(5)
    raise RuntimeError('Qualification pending; resume exact existing membership')


def main(apply):
    with h.research.lock(h.CAMPAIGN / 'league-deployment.lock', blocking=False), h.client() as c:
        assert h.read(h.CAMPAIGN / 'service.json')['state'] == 'paused'
        h.live(c)
        source = (PAIR / 'policy.bas').read_bytes()
        assert h.sha(source) == SOURCE
        proof = subprocess.run([sys.executable, str(PAIR / 'verify.py')], capture_output=True, text=True, check=True)
        h.write(OUT / 'conversion-proof.json', {'stdout': proof.stdout, 'returncode': proof.returncode})
        evidence = {}
        for stage in ('healthy-field', 'middle-field'):
            result = h.read(h.STUDY / stage / 'result.json')
            assert result['complete'] and result['research_improved']
            assert all(c['games'] == 40 and c['invalid'] == 0 and c['all_hashes_equal'] for c in result['cells'])
            evidence[stage] = {'sha256': h.sha((h.STUDY / stage / 'result.json').read_bytes()),
                               'cells': [{k: v for k, v in c.items() if k != 'rows'} for c in result['cells']]}
        schema = h.get(c, '/openapi.json')
        h.write(OUT / 'live-schema.json', schema)
        current = champions(c)
        before_path = OUT / 'champions-before.json'
        if not before_path.exists():
            assert all(current[player]['policy_version']['id'] == PRIOR[label] for label, player in PLAYERS.items())
            h.write(before_path, current)
        before = h.read(before_path)
        candidate = h.read(h.STUDY / 'uploads/practiced/uploaded-version.json')
        assert candidate['id'] == 'f3f8baab-d02a-4f7f-8fc9-e1f050f967a7'
        h.write(OUT / 'aaron/owned-readback.json', owned(c, candidate, PLAYERS['aaron']))
        h.write(OUT / 'rollback.json', {p: {'policy_version': r['policy_version'], 'membership': r['id'],
                    'action': f"POST /v2/league-policy-memberships/{r['id']}/champion", 'body': {},
                    'trigger': 'Confirmed runtime failure or qualification rejection; normal stochastic losses are not a trigger.'} for p, r in before.items()})
        preflight = {'at': h.research.now(), 'ready': True, 'authorization_verbatim_prior_turns': AUTH,
                     'authorization_scope': 'Continuing prior explicit latest-league and both-player deployment instructions; no new assent implied.',
                     'league': LEAGUE, 'source_sha256': SOURCE, 'evidence': evidence,
                     'scope': NOTE, 'historical_accepted_state_changed': False}
        h.write(OUT / 'preflight.json', preflight)
        if not apply:
            print('Concrete deployment preflight passed for Aaron and Coach.', flush=True)
            return
        versions = {PLAYERS['aaron']: candidate, PLAYERS['coach']: upload_coach(c, source, schema)}
        for label, player in PLAYERS.items():
            assert current[player]['policy_version']['id'] in {before[player]['policy_version']['id'], versions[player]['id']}
        h.freeze(OUT / 'decision.json', {k: v for k, v in preflight.items() if k != 'at'} | {'versions': versions, 'rollback': h.read(OUT / 'rollback.json')})
        log_once('## Current-release submission decision 2026-09-22',
                 '- Earlier user authorization: ' + '; '.join(AUTH) + '\n- ' + NOTE +
                 '\n- Decision, exact version IDs, evidence deltas and rollback: `tmp/gota-targets-20260922/deployment/decision.json`.\n'
                 '- Validation: validated on 320 mixed A/B and later-draft games; submitting. No independence/significance claim from correlated streams.')
        for label, player in PLAYERS.items():
            current = champions(c)
            assert all(current[p]['policy_version']['id'] in {before[p]['policy_version']['id'], versions[p]['id']} for p in PLAYERS.values())
            if current[player]['policy_version']['id'] != versions[player]['id']:
                print('SUBMITTING', label, versions[player]['id'], flush=True)
                selected = select(c, label, versions[player], schema)
                print('VERIFIED', label, selected['id'], flush=True)
        final = champions(c)
        assert all(final[p]['policy_version']['id'] == versions[p]['id'] for p in PLAYERS.values())
        h.write(OUT / 'deployment-verified.json', {'at': h.research.now(), 'league': LEAGUE,
                 'players': final, 'versions': versions, 'source_sha256': SOURCE,
                 'state': 'both_competing_active_champions', 'scope': NOTE})
        log_once('## Current-release deployment verified 2026-09-22',
                 '- Both Aaron and Coach active, competing and champion; exact source `' + SOURCE + '`.\n'
                 '- Receipt: `tmp/gota-targets-20260922/deployment/deployment-verified.json`. Validation: submitted.')
        print('Both current-release policies deployed and verified.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    main(parser.parse_args().apply)
