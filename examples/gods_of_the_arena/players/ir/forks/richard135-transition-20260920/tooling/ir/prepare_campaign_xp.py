"""Freeze a hosted comparison after local qualification and inert upload.

This command makes only GET requests. Launch/harvest with hosted_batch.py.
"""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import shutil

from hosted_wave import client, get
from policy_ir import digest, read, write
from upload_qualified import PLAYER

LEAGUE = 'league_3c60897b-25cf-4b37-9d1a-8554c1198f28'
DIVISION = 'div_a4534073-c5d2-4193-a94a-93d9c5e2e443'
CONTROL = '6d0ff780-652f-47a8-82b3-336cb7a10a56'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('campaign', type=Path)
    parser.add_argument('--requested-xp', action='store_true')
    args = parser.parse_args()
    campaign = args.campaign.resolve()
    confirmation = read(campaign / 'confirmation-result.json')
    authorization = None
    if args.requested_xp:
        authorization = read(campaign / 'xp-authorization.json')
        if not authorization.get('explicit_user_requested_xp'):
            raise ValueError('Explicit XP request record missing')
    if not confirmation['passed'] and not args.requested_xp:
        raise ValueError('Local qualification required')
    local = read(campaign / 'plan.json')
    uploaded = read(campaign / 'upload/uploaded-version.json')
    output = campaign / 'hosted'
    if (output / 'plan.json').exists():
        print('Existing frozen hosted plan retained: ' + str(output))
        return
    with client() as c:
        league = get(c, '/v2/leagues/' + LEAGUE)
        coworld = get(c, '/v2/coworlds/' + league['game']['coworld_id'])
        champions = get(c, f'/v2/league-policy-memberships?league_id={LEAGUE}&champions_only=true&limit=100')
        leaderboard = get(c, f'/v2/divisions/{DIVISION}/leaderboard')
    if coworld['version'] != local['game_version']:
        raise ValueError('Published game changed since local confirmation')
    selected = {m['player']['id']: m['policy_version'] for m in champions}
    opponents = [selected[r['player_id']] for r in sorted(leaderboard, key=lambda r: r['rank'])
                 if r['player_id'] != PLAYER and r['player_id'] in selected][:9]
    if len(opponents) != 9 or len({v['id'] for v in opponents}) != 9:
        raise ValueError('Need nine distinct incumbent champions')
    if selected[PLAYER]['id'] != CONTROL:
        raise ValueError('Selected league control changed; review before creating comparison')
    output.mkdir(exist_ok=True)
    config = {k: v for k, v in read(campaign / 'config.json').items() if k not in {'seed', 'players', 'tokens'}}
    common = {'created_at': datetime.now(timezone.utc).isoformat(),
              'run_id': campaign.name, 'game_version': coworld['version'],
              'game_source': coworld['manifest']['game']['runnable']['source_url'],
              'target': {'coworld_id': coworld['id'], 'variant_id': 'competition'},
              'config': config, 'opponents': opponents,
              'notes': 'Preregistered 100-episode arm of an independent-cohort A/B. Identical pinned incumbent roster, rotated subject seats, platform-generated distinct seeds. Complete both arms and all replay audits before applying the frozen campaign win/survival gates.'}
    plan = {'local_confirmation_sha256': digest((campaign / 'confirmation-result.json').read_bytes()),
            'local_confirmation_passed': confirmation['passed'],
            'advancement_authorization': authorization,
            'candidate_version': uploaded['id'], 'control_version': CONTROL,
            'gates': {'minimum_win_gain': .10, 'maximum_win_p': .05,
                      'maximum_death_rate_ratio': 1.10, 'minimum_xp_ratio': .80},
            'episodes_per_arm': 100,
            'design': 'Fixed-size independent cohorts; not seed-matched. Drain each arm before launching the next. No interim decision or dropped episodes.',
            'field_guardrail': {'episodes': 40, 'minimum_wins': 12,
                                'maximum_death_rate_vs_ab_control': 1.25,
                                'maximum_timeout_fraction': .20,
                                'equipment_required_every_episode': True,
                                'design': 'After passing A/B, one new 40-episode request against nine sampled division champions, excluding Aaron. Broad regression screen only; superiority comes from the completed A/B. All replays and VMs must verify.'},
            **common}
    write(output / 'plan.json', plan)
    write(output / 'champions.json', champions)
    write(output / 'leaderboard.json', leaderboard)
    write(output / 'coworld.json', coworld)
    for arm, version in [('control', CONTROL), ('candidate', uploaded['id'])]:
        folder = output / arm
        folder.mkdir(exist_ok=True)
        write(folder / 'plan.json', common | {'policy_version': version})
        shutil.copy2(campaign / 'audit-field', folder / 'audit')
    print('Frozen hosted roster: ' + ', '.join(v['label'] for v in opponents))


if __name__ == '__main__':
    main()
