"""Promote the exact user-approved Jordan268 fork; preserve API receipts."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
CLEAN = ROOT.parent / 'polyworld-gota-clean-20260916-r5/examples/gods_of_the_arena/players/ir'
sys.path.insert(0, str(CLEAN))
from hosted_wave import client, get
from release_deploy_pair import verify_owned
from win_hosted import live

STUDY = ROOT / 'tmp/gota-ir/jordan268-counter-20260920'
OUT = STUDY / 'promotion'
BUNDLE = ROOT / 'examples/gods_of_the_arena/players/ir/forks/jordan268'
LEAGUE = 'league_3c60897b-25cf-4b37-9d1a-8554c1198f28'
PLAYER = 'ply_594ec24d-d7f3-4370-a000-468354ec41c9'
VERSION = '00cd9483-0309-4613-bf61-89f3f4a33d01'


def read(path):
    return json.loads(path.read_text())


def save(name, value):
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')


def now():
    return datetime.now(timezone.utc).isoformat()


def champions(c):
    return get(c, f'/v2/league-policy-memberships?league_id={LEAGUE}&champions_only=true&mine=true&limit=100')


def own_champion(rows):
    own = [r for r in rows if r['player']['id'] == PLAYER and r['is_champion']]
    if len(own) != 1:
        raise ValueError('Expected one current champion for the approved player')
    return own[0]


def main():
    manifest = read(BUNDLE / 'manifest.json')
    source = (BUNDLE / 'policy.bas').read_bytes()
    assert manifest['uploaded_version'] == VERSION and manifest['both_color_criterion_passed']
    assert hashlib.sha256(source).hexdigest() == manifest['basic_sha256']
    for color in ('red', 'blue'):
        result = read(STUDY / 'hosted/confirmation/redrace' / color / 'result.json')
        assert result['n'] == result['wins'] == 40 and result['all_replay_vm_roster_checks']
    game = live()
    version = read(STUDY / 'candidates/redrace/uploaded-version.json')
    before = read(OUT / 'champions-before.json')
    prior = own_champion(before)
    decision = {
        'recorded_at': now(), 'authorization_verbatim': "let's promote",
        'authorized_candidate_context': 'The immediately preceding 80/80 Jordan268 fork readout.',
        'league_id': LEAGUE, 'player_id': PLAYER, 'policy_version_id': VERSION,
        'game_version': game['version'], 'basic_sha256': manifest['basic_sha256'],
        'validation_state': 'validated for the exact Jordan268 fixed-lineup matchup',
        'evidence': {'experiment': '2026-09-19-jordan268-redrace', 'red': '40/40', 'blue': '40/40',
                     'rule': 'At least30/40 fresh wins each color; full replay/VM/roster/score/XP audits.',
                     'p_value': None, 'limitations': 'Repeated trajectories; no broad-field check or A/B '
                     'against the intervening current champion. User explicitly requested promotion '
                     'after the scope-qualified result. No broad-field superiority claim.'},
        'rollback': {'membership_id': prior['id'], 'policy_version_id': prior['policy_version']['id'],
                     'policy_label': prior['policy_version'].get('label'),
                     'action': f"POST /v2/league-policy-memberships/{prior['id']}/champion",
                     'expected_time': 'One authenticated request and readback; no rebuild needed.'},
        'scope': 'Only the existing owner of the approved version, Aaron’s Co-play Coach.',
    }
    if not (OUT / 'decision.json').exists():
        save('decision.json', decision)
    with client() as c:
        save('owned-at-promotion.json', verify_owned(c, version, PLAYER))
        current = own_champion(champions(c))
        if current['policy_version']['id'] not in {prior['policy_version']['id'], VERSION}:
            raise ValueError('Champion changed after preflight; reconcile before applying')
        path = f'/v2/league-submissions?league_id={LEAGUE}&player_id={PLAYER}&policy_version_id={VERSION}&limit=100'
        submissions = get(c, path)
        matches = [s for s in submissions if s['policy_version']['id'] == VERSION and s['player']['id'] == PLAYER]
        if not matches:
            body = {'league_id': LEAGUE, 'policy_version_id': VERSION, 'player_id': PLAYER,
                    'auto_champion': 'never',
                    'notes': "User explicitly approved promotion: let's promote. Exact Jordan268 "
                    'specialist confirmed40/40 red and40/40 blue, full replay/VM/roster/score/XP audits. '
                    'Fixed lineups and repeated trajectories; broad-field superiority untested. '
                    'BASIC SHA ' + manifest['basic_sha256']}
            save('submission-request.json', body)
            response = c.post('/v2/league-submissions', json=body)
            response.raise_for_status()
            save('submission-created.json', response.json())
            print('SUBMITTED', response.json().get('id'), flush=True)
        last_state = None
        for _ in range(120):
            rows = get(c, path)
            save('submissions-readback.json', rows)
            matches = [s for s in rows if s['policy_version']['id'] == VERSION and s['player']['id'] == PLAYER]
            if len(matches) != 1:
                raise ValueError('Expected one exact submission; receipts preserved')
            submission = matches[0]
            if submission['status'] != last_state:
                print('PLACEMENT', submission['status'], submission.get('league_policy_membership_id'), flush=True)
                last_state = submission['status']
            if submission['status'] in {'failed', 'rejected', 'cancelled'}:
                raise ValueError('Submission rejected: ' + submission['status'])
            if submission['status'] == 'placed' and submission.get('league_policy_membership_id'):
                break
            time.sleep(5)
        else:
            raise ValueError('Placement still pending; resume the existing receipt')
        membership_id = submission['league_policy_membership_id']
        if own_champion(champions(c))['policy_version']['id'] != VERSION:
            response = c.post(f'/v2/league-policy-memberships/{membership_id}/champion', json={})
            response.raise_for_status()
            save('champion-response.json', response.json())
            print('CHAMPION_SELECTED', membership_id, flush=True)
        last_state = None
        for _ in range(120):
            # No active-only filter: disappearing disqualified memberships are not success.
            memberships = get(c, f'/v2/league-policy-memberships?league_id={LEAGUE}&mine=true&limit=100')
            save('memberships-readback.json', memberships)
            matches = [r for r in memberships if r['id'] == membership_id]
            if len(matches) != 1:
                raise ValueError('Selected membership missing; receipts preserved')
            selected = matches[0]
            state = {k: selected.get(k) for k in ('id', 'status', 'substatus', 'is_champion')}
            if state != last_state:
                print('MEMBERSHIP', json.dumps(state), flush=True)
                last_state = state
            if selected['status'] in {'disqualified', 'retired', 'rejected'}:
                raise ValueError('Qualification did not succeed: ' + selected['status'])
            if selected['status'] == 'competing' and selected.get('substatus') == 'active' and selected['is_champion']:
                after = champions(c)
                confirmed = own_champion(after)
                assert confirmed['id'] == membership_id and confirmed['policy_version']['id'] == VERSION
                other_before = {r['player']['id']: r['policy_version']['id'] for r in before if r['player']['id'] != PLAYER}
                other_after = {r['player']['id']: r['policy_version']['id'] for r in after if r['player']['id'] != PLAYER}
                save('promotion-verified.json', {'verified_at': now(), 'state': 'competing_active_champion',
                     'league_id': LEAGUE, 'player': confirmed['player'], 'policy_version': confirmed['policy_version'],
                     'membership_id': membership_id, 'basic_sha256': manifest['basic_sha256'],
                     'rollback': decision['rollback'], 'champions_after': after,
                     'other_players_unchanged': other_before == other_after})
                print('VERIFIED_PROMOTED', VERSION, membership_id, flush=True)
                return
            time.sleep(5)
        raise ValueError('Qualification still pending; resume monitoring the existing membership')


if __name__ == '__main__':
    main()
