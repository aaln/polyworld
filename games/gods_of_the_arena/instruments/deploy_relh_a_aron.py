"""Deploy the user's chosen historical relh counter to the existing a-aron player."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import pprint
import sys
import time
import httpx

ROOT = Path(__file__).resolve().parents[3]
CLEAN = ROOT.parent / 'polyworld-gota-clean-20260916-r5/examples/gods_of_the_arena/players/ir'
sys.path.insert(0, str(CLEAN))
from hosted_wave import client, get
from release_deploy_pair import verify_owned, select
from win_hosted import live
from policy_ir import compile_policy, extract

OUT = ROOT / 'tmp/gota-ir/a-aron-relh-deploy-20260920'
SOURCE = ROOT.parent / 'gota-research-20260916/coached-lanes/r5-relh154/scoped-followup'
BUNDLE = ROOT / 'examples/gods_of_the_arena/players/ir/forks/relh154-a-aron'
LOG = ROOT / 'games/gods_of_the_arena/players/relh154-a-aron/VERSION_LOG.md'
LEAGUE = 'league_3c60897b-25cf-4b37-9d1a-8554c1198f28'
PLAYER = 'ply_cec02b42-a653-4253-be4b-602ba5acacc4'
ORIGINAL = '53f15b12-2198-41d1-bb99-df4bdb1ff7fd'
AUTHORIZATION = "i had a policy which beat relh almost every time, maybe just use that\nuse it on another player named a-aron"


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2)+'\n')


def champions(c):
    return get(c, f'/v2/league-policy-memberships?league_id={LEAGUE}&champions_only=true&mine=true&limit=100')


def main():
    game = live()
    policy = read(SOURCE / 'final-feedback/policy.ir.json')
    source = (SOURCE / 'final-feedback/policy.bas').read_bytes()
    evidence = read(SOURCE / 'final-result.json')
    sha = hashlib.sha256(source).hexdigest()
    assert evidence['promotion_ready'] and evidence['confirmed'] == 'legacy'
    assert sha == evidence['source_sha256'] == 'b2693715459d0de7283ba6f45440c0084ea5c7781c2305e163976a6572246ca9'
    assert evidence['relh154']['candidate_games'] == 120
    assert all(evidence['relh154'][k] == 40 for k in ('discovery_blue', 'fresh_red', 'fresh_blue'))
    assert compile_policy(policy).encode() == source and extract(source.decode(), policy) == policy
    for e in evidence['evidence']:
        assert hashlib.sha256(Path(e['artifact']).read_bytes()).hexdigest() == e['sha256']
    BUNDLE.mkdir(parents=True, exist_ok=True)
    (BUNDLE / 'policy.bas').write_bytes(source)
    write(BUNDLE / 'policy.ir.json', policy)
    (BUNDLE / 'policy.py').write_text('"""Previously validated relh154 counter in primary Python IR format."""\n\nPOLICY = '
        + pprint.pformat(policy, width=110, sort_dicts=False)+'\n')
    write(BUNDLE / 'evaluation.json', evidence)
    with client() as c:
        players = get(c, '/players')
        assert len([p for p in players if p['id'] == PLAYER and p['name'] == 'a-aron' and p['disabled_at'] is None]) == 1
        before_path = OUT / 'champions-before.json'
        if not before_path.exists():
            write(before_path, champions(c))
        before = read(before_path)
        prior = [r for r in before if r['player']['id'] == PLAYER]
        assert len(prior) <= 1
        metadata = {'name': 'a-aron-gota-ir-relh154-legacy-0920', 'content_hash': sha,
            'size_bytes': len(source), 'player_id': PLAYER, 'attributes': {},
            'tags': {'game': 'gods_of_the_arena', 'game_version': game['version'],
                'source_policy_version_id': ORIGINAL,
                'validation': 'Identical previously validated relh154-legacy executable:120/120 exact relh154 games, repeated fixed-lineup trajectories; no new independent evidence from this registration.',
                'authorization': AUTHORIZATION}}
        path = OUT / 'upload-request.json'
        if path.exists():
            assert read(path) == metadata
        write(path, metadata)
        receipt = OUT / 'uploaded-version.json'
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
                    uploaded = httpx.put(payload['upload_url'], content=source,
                        headers={'Content-Type': 'application/octet-stream'}, timeout=120)
                    uploaded.raise_for_status()
                    response = c.post('/stats/policies/files/complete', json=metadata)
                    response.raise_for_status()
                    version = response.json()
            write(receipt, version)
        version = read(receipt)
        LOG.parent.mkdir(parents=True, exist_ok=True)
        log = LOG.read_text() if LOG.exists() else '# a-aron relh154 counter\n'
        if version['id'] not in log:
            LOG.write_text(log + f"\n## {version['name']}:v{version['version']}\n\n"
                f"- Version `{version['id']}`, registered {datetime.now(timezone.utc).isoformat()}; player a-aron `{PLAYER}`.\n"
                f"- Byte-identical clone of `{ORIGINAL}`; BASIC SHA `{sha}`; native GOTA {game['version']}.\n"
                '- Validated historical executable:120/120 versus exact relh154,280/280 across original selected tests. Correlated fixed-lineup games; this registration adds no independent evidence.\n'
                f'- User instruction: {json.dumps(AUTHORIZATION)}. Initial state: registered, pending submission.\n')
        write(OUT / 'owned-readback.json', verify_owned(c, version, PLAYER))
        decision_path = OUT / 'decision.json'
        if not decision_path.exists():
            write(decision_path, {'recorded_at': datetime.now(timezone.utc).isoformat(),
                'authorization_verbatim': AUTHORIZATION, 'player_id': PLAYER, 'league_id': LEAGUE,
                'policy_version_id': version['id'], 'source_policy_version_id': ORIGINAL,
                'basic_sha256': sha, 'historical_validation': evidence['scope'],
                'prior_champion': prior[0] if prior else None,
                'rollback': (f"POST /v2/league-policy-memberships/{prior[0]['id']}/champion" if prior
                    else 'No previous GOTA champion. Retire the newly created membership using its /retire endpoint to undo league participation.')})
        print('REGISTERED', version['id'], version['name'], flush=True)
        current = [r for r in champions(c) if r['player']['id'] == PLAYER]
        if not current or current[0]['policy_version']['id'] != version['id']:
            if current and (not prior or current[0]['id'] != prior[0]['id']):
                raise ValueError('a-aron champion changed since preflight')
            select(c, PLAYER, version, OUT, 'User explicitly selected historical relh counter for a-aron. '
                + metadata['tags']['validation'] + ' BASIC SHA '+sha)
        for _ in range(120):
            rows = get(c, f'/v2/league-policy-memberships?league_id={LEAGUE}&mine=true&limit=100')
            write(OUT / 'memberships-readback.json', rows)
            selected = [r for r in rows if r['player']['id'] == PLAYER and r['policy_version']['id'] == version['id']]
            assert len(selected) == 1
            r = selected[0]
            print('STATE', r['status'], r.get('substatus'), r['is_champion'], flush=True)
            if r['status'] in ('disqualified', 'retired', 'rejected'):
                raise ValueError('Qualification failed: '+r['status'])
            if r['status'] == 'competing' and r.get('substatus') == 'active' and r['is_champion']:
                after = champions(c)
                assert any(x['id'] == r['id'] for x in after)
                other = lambda rows: {x['player']['id']:x['policy_version']['id'] for x in rows if x['player']['id'] != PLAYER}
                verification = {'verified_at': datetime.now(timezone.utc).isoformat(),
                    'state': 'competing_active_champion', 'membership_id': r['id'],
                    'player': r['player'], 'policy_version': r['policy_version'],
                    'basic_sha256': sha, 'other_players_unchanged': other(before) == other(after),
                    'champions_after': after}
                write(OUT / 'promotion-verified.json', verification)
                write(BUNDLE / 'promotion.json', {'decision': read(decision_path), 'verification': verification})
                LOG.write_text(LOG.read_text()+f"\n- Verified {verification['verified_at']}: active, competing champion, membership `{r['id']}`. Other player champions unchanged: {verification['other_players_unchanged']}. Receipt: `{BUNDLE / 'promotion.json'}`.\n")
                print('VERIFIED_A_ARON', r['policy_version']['label'], r['id'], flush=True)
                return
            time.sleep(5)
        raise ValueError('Placement pending; resume exact existing receipt')


if __name__ == '__main__':
    main()
