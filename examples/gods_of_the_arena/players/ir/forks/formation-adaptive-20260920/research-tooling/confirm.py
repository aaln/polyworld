"""Fresh, prospective confirmation of the unchanged successful adaptive fork."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import os
from build import STUDY, read, write, digest
from hosted import CAMPAIGN, RIVALS, collect, freeze, r, live, client, get

CYCLE = 'interactive-formation-adaptive-confirm-20260920'


def main():
    with r.lock(STUDY/'confirmation-runner.lock', blocking=False):
        discovery = read(STUDY/'hosted-result.json')
        assert discovery['complete'] and discovery['passed']
        assert read(STUDY/'review-progress.json')['complete']
        original = read(STUDY/'hosted-plan.json')
        source = STUDY/'candidates'/original['candidate']/'policy.bas'
        assert digest(source.read_bytes()) == original['source_sha256']
        live()
        with client() as c:
            current = get(c, '/v2/league-policy-memberships?league_id=league_3c60897b-25cf-4b37-9d1a-8554c1198f28&champions_only=true&limit=100')
        assert set(RIVALS.values()).issubset({x['policy_version']['id'] for x in current})
        write(STUDY/'champions-at-confirmation.json', current)
        cfg = r.config(CAMPAIGN)
        arms = []
        for old in original['arms']:
            if old['name'] != 'candidate':
                continue
            arm = dict(old)
            d = STUDY/'confirmation'/old['key']
            d.mkdir(parents=True, exist_ok=True)
            arm['directory'] = str(d)
            body = {'idempotency_key': 'formation-adaptive-confirm-'+digest(arm)[:24],
                    'target': cfg['target'], 'game_config_overrides': cfg['game_config'],
                    'num_episodes': 40,
                    'roster': [{'slot': i, 'player': {'policy_ref': v}} for i, v in enumerate(arm['roster'])],
                    'notes': 'Frozen unchanged adaptive fork prospective confirmation; '+arm['key']+
                             '. All40 full audited. Generated seeds unpaired; repeats correlated. No automatic promotion.'}
            freeze(d/'plan.json', arm)
            freeze(d/'request.json', body)
            arms.append(arm)
        plan = {'cycle': CYCLE, 'episodes': 240, 'candidate': original['candidate'],
                'source_sha256': original['source_sha256'], 'version': original['version'],
                'arms': arms,
                'decision_rule': 'All six cells fully audited; >=30/40 each Alex/Jordan color; Richard blue>=38/40 and total>=40/80. Discovery controls remain separate; no field or promotion qualification.'}
        freeze(STUDY/'confirmation-plan.json', plan)
        os.environ['GOTA_RESEARCH_CYCLE'] = CYCLE
        write(STUDY/'confirmation-owner.json', {'pid': os.getpid(), 'cycle': CYCLE,
              'started_at': datetime.now(timezone.utc).isoformat()})
        with ThreadPoolExecutor(2) as pool:
            results = list(pool.map(collect, arms))
        cells = {a['key']: v for a, v in zip(arms, results)}
        wins = lambda key: cells[key]['wins']
        gates = {'all_audits': all(v['all_full_audits_passed'] and v['games']==40 for v in results),
                 'alex_jordan_each': all(wins(f'{rival}/candidate/{color}')>=30
                                        for rival in ('alex','jordan') for color in ('red','blue')),
                 'richard_blue': wins('richard/candidate/blue')>=38,
                 'richard_total': wins('richard/candidate/blue')+wins('richard/candidate/red')>=40}
        write(STUDY/'confirmation-result.json', {'complete': True, 'games': 240,
              'passed': all(gates.values()), 'gate': gates, 'cells': cells, 'promotion_eligible': False})
        print('CONFIRMATION', gates, flush=True)


if __name__ == '__main__':
    main()
