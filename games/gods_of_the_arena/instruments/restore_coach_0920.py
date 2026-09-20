"""Restore the exact Coach champion requested by the user, preserving Aaron."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT.parent / 'polyworld-gota-clean-20260916-r5/examples/gods_of_the_arena/players/ir'))
from hosted_wave import client, get

OUT = ROOT / 'tmp/gota-ir/restore-coach-20260920'
LEAGUE = 'league_3c60897b-25cf-4b37-9d1a-8554c1198f28'
COACH = 'ply_594ec24d-d7f3-4370-a000-468354ec41c9'
VERSION = '00cd9483-0309-4613-bf61-89f3f4a33d01'
AARON = 'ply_630a768f-d623-44b2-80fa-36968d6fa75a'
AARON_VERSION = '4cdbbf36-3d70-4ea3-8aed-c92ee0e024be'
OTHER = 'ply_cec02b42-a653-4253-be4b-602ba5acacc4'

def save(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')

def rows(c):
    return get(c, f'/v2/league-policy-memberships?league_id={LEAGUE}&mine=true&limit=100')

def main():
    with client() as c:
        before = rows(c)
        if not (OUT / 'before.json').exists():
            save('before.json', before)
            save('decision.json', {'at': datetime.now(timezone.utc).isoformat(),
                'authorization_verbatim': "reactive coach's membership instead of a-aron",
                'league_id': LEAGUE, 'coach_player': COACH, 'policy_version': VERSION,
                'action': 'Retire a-aron membership; resubmit the unchanged Coach version and select it as champion. Preserve Aaron.',
                'reason': 'The platform disqualified Coach when a-aron exceeded the two active player limit.'})
        assert any(r['player']['id'] == AARON and r['policy_version']['id'] == AARON_VERSION
                   and r['is_champion'] and r['status'] == 'competing' for r in before)
        for r in before:
            if r['player']['id'] == OTHER and r['status'] in ('competing', 'qualifying'):
                response = c.post(f"/v2/league-policy-memberships/{r['id']}/retire",
                    json={'reason': 'User requested Coach membership instead of a-aron.'})
                response.raise_for_status()
                save('retired-a-aron.json', response.json())
                print('RETIRED_A_ARON', r['id'], flush=True)
        current = [r for r in rows(c) if r['player']['id'] == COACH
                   and r['policy_version']['id'] == VERSION and r['status'] in ('competing', 'qualifying')]
        if not current:
            pending = get(c, f'/v2/league-submissions?league_id={LEAGUE}&policy_version_id={VERSION}&limit=100')
            pending = [r for r in pending if r['status'] in ('pending', 'processing')]
            if not pending:
                body = {'league_id': LEAGUE, 'policy_version_id': VERSION, 'player_id': COACH,
                    'auto_champion': 'never', 'notes': 'User: reactive coach\'s membership instead of a-aron. Restore exact unchanged Coach policy; a-aron retired first to preserve Aaron under the two-player limit.'}
                save('submission-request.json', body)
                response = c.post('/v2/league-submissions', json=body)
                response.raise_for_status()
                save('submission-created.json', response.json())
                print('RESUBMITTED_COACH', response.json()['id'], flush=True)
        for _ in range(240):
            current = rows(c)
            save('memberships-readback.json', current)
            selected = [r for r in current if r['player']['id'] == COACH
                        and r['policy_version']['id'] == VERSION and r['status'] in ('competing', 'qualifying')]
            if selected:
                assert len(selected) == 1
                r = selected[0]
                print('COACH', r['status'], r.get('substatus'), r['is_champion'], flush=True)
                if r['status'] == 'competing' and not r['is_champion']:
                    response = c.post(f"/v2/league-policy-memberships/{r['id']}/champion", json={})
                    response.raise_for_status()
                    save('champion-response.json', response.json())
                elif r['status'] == 'competing' and r['is_champion'] and r.get('substatus') == 'active':
                    champions = [x for x in current if x['is_champion'] and x['status'] == 'competing']
                    assert {x['player']['id']: x['policy_version']['id'] for x in champions} == {COACH: VERSION, AARON: AARON_VERSION}
                    assert not any(x['player']['id'] == OTHER and x['status'] in ('competing', 'qualifying') for x in current)
                    save('verified.json', {'at': datetime.now(timezone.utc).isoformat(), 'champions': champions,
                        'coach_restored': True, 'a_aron_retired': True, 'aaron_unchanged': True})
                    print('VERIFIED_AARON_AND_COACH', r['id'], flush=True)
                    return
            time.sleep(5)
        raise RuntimeError('Coach placement still pending; resume from existing receipts.')

if __name__ == '__main__':
    main()
