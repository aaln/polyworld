"""Reuse the full audited control cohort for eighty responsive lane counterfactuals."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OLD = ROOT.parent / 'polyworld/tmp/gota-control-tactics61-20260923'
RAW = ROOT.parent / 'polyworld/tmp/gota-lane-occupancy61-20260923'
spec = importlib.util.spec_from_file_location('control_tactics_hosted', HERE.parent / 'controltactics20260923/hosted.py')
cc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cc)
h, panel = cc.h, cc.panel
cc.RAW = h.STUDY = panel.STUDY = RAW
CANDIDATE = RAW / 'lane-occupancy/policy.bas'
BASELINE = 'f063e236-4f9b-4f52-a57c-e41b29d14caf'


def prepare():
    assert h.read(RAW / 'native-comparison.json')['passed']
    assert h.read(RAW / 'practice-comparison.json')['passed']
    prior = h.read(OLD / 'paired-results.json')
    assert prior['complete'] and len(prior['pairs']) == 80
    baseline = []
    for r in prior['pairs']:
        roster = list(r['baseline']['roster'])
        roster[r['candidate']['slot']] = BASELINE
        row = r['candidate'] | {'cell': r['baseline']['cell'], 'roster': roster}
        assert row['valid']
        baseline.append(row)
        link = RAW / 'artifacts' / row['episode']
        link.parent.mkdir(parents=True, exist_ok=True)
        if not link.exists(): link.symlink_to(OLD / 'artifacts' / row['episode'], target_is_directory=True)
    h.freeze(RAW / 'baseline-pool.json', baseline)
    with h.client() as c:
        h.freeze(RAW / 'canonical-game.json', h.live(c))
        schema = h.get(c, '/openapi.json')
        h.freeze(RAW / 'openapi-preparation.json', schema)
        h.freeze(RAW / 'memberships-preparation.json', h.get(c, '/v2/league-policy-memberships?league_id=league_3c60897b-25cf-4b37-9d1a-8554c1198f28&champions_only=true&active_only=true&limit=1000'))
        # Upload helper performs schema/content/owner readbacks. Its old log is
        # restored below; this distinct study has its own semantic description.
        log = ROOT / 'games/gods_of_the_arena/players/controltactics20260923/VERSION_LOG.md'
        before = log.read_bytes()
        try:
            version = cc.upload(c, 'candidate', CANDIDATE, 'sable-oriole-61d3', schema)
        finally:
            log.write_bytes(before)
        newlog = ROOT / 'games/gods_of_the_arena/players/lanefarm20260923/VERSION_LOG.md'
        newlog.parent.mkdir(parents=True, exist_ok=True)
        if not newlog.exists():
            newlog.write_text('# Lane occupancy research version\n\n- ' + datetime.now(timezone.utc).isoformat() + ': `sable-oriole-61d3:v1` (`' + version + '`), source `' + h.sha(CANDIDATE.read_bytes()) + '`. One opening choice toward fewer committed allied heroes, persistent route and coordinated blue-route/portal handling. Uploaded inertly after local validity; no league selection.\n')
        h.freeze(RAW / 'hosted-plan.json', {
            'game': h.VERSION, 'engine': h.COMMIT,
            'versions': {'baseline': BASELINE, 'candidate': version},
            'source_hashes': {'baseline': h.read(OLD/'hosted-plan.json')['source_hashes']['candidate'], 'candidate': h.sha(CANDIDATE.read_bytes())},
            'pairs': 80, 'new_games': 80, 'reused_games': 80,
            'baseline_ids': [r['episode'] for r in baseline],
            'selection': 'All80previous control-tactics counterfactual episodes, no outcome or hero exclusions. Four fixed color/seat cells. Rerun allnineother policies responsively with same seed/config/roster/slot. Reused cohort is discovery, not independent confirmation.',
            'rung': 'Directional pilot; no established game-specific paired-sample N floor. No deployment from this pilot alone.',
            'rule': 'All80pairs, alltenVMs, fullreplayhash/XP/scores/config/source validity required. Primary statistic mean paired individual score delta with within-context whole-pair bootstrap95%CI. Advance to fresh confirmation only if mean>0 and lowerCI>=0. All hero/color/seat, nonzero/death/win metrics are diagnostic only; no independent preservation gate. No posthoc exclusions.',
            'method': 'Score-only objective, fixed seed9236102 and10000bootstrap resamples as tools/gota_autoresearch/score_statistics.py. Analyze creep/hero/structure XP and time penalty as mechanisms.'})
        print(json.dumps({'prepared': True, 'pairs': 80, 'new_games': 80, 'version': version}), flush=True)


def run():
    plan = h.read(RAW / 'hosted-plan.json')
    assert plan['source_hashes']['candidate'] == h.sha(CANDIDATE.read_bytes())
    baseline = h.read(RAW / 'baseline-pool.json')
    ready = {'baseline_version': BASELINE, 'coworld_id': h.GAME, 'complete': True, 'episode_ids': plan['baseline_ids']}
    body = {'candidate_policy_version_id': plan['versions']['candidate'], 'baseline_policy_version_id': BASELINE,
            'source': 'experience_request', 'n': 80, 'idempotency_key': 'gota-lane61d3-cf-' + plan['source_hashes']['candidate'][:8]}
    with h.client() as c, ThreadPoolExecutor(4) as pool:
        evaluation = cc.counterfactual_journal.create(c, h, body, RAW / 'counterfactual', h.read(RAW/'openapi-preparation.json'), ready)
        print(json.dumps({'counterfactual_eval': evaluation['id']}), flush=True)
        indexed = {r['episode']: r for r in baseline}
        seen = {}
        while True:
            evaluation = h.get(c, '/v2/counterfactual-evals/' + evaluation['id'])
            h.write(RAW / 'counterfactual/status.json', evaluation)
            pairs = evaluation.get('pairs', [])
            # The asynchronous API first returns pending with no materialized pairs.
            selected = {p['baseline_episode_request_id'] for p in pairs}
            assert selected <= set(indexed) and len(selected) == len(pairs)
            pending = [p for p in pairs if p['candidate_episode_request_id'] and p['candidate_episode_request_id'] not in seen and p['candidate_score'] is not None]
            def collect(pair):
                base = indexed[pair['baseline_episode_request_id']]
                roster = list(base['roster']); roster[base['slot']] = plan['versions']['candidate']
                return cc.collect(c, pair['candidate_episode_request_id'], roster, base['slot'], plan['source_hashes']['candidate'])
            for pair, result in zip(pending, pool.map(collect, pending)):
                base = indexed[pair['baseline_episode_request_id']]
                assert pair['coworld_id'] == h.GAME and pair['seed'] == base['seed'] and pair['probe_slot'] == base['slot']
                assert pair['opponent_policy_version_ids'] == [v for i,v in enumerate(base['roster']) if i != base['slot']]
                assert all(x == y for i,(x,y) in enumerate(zip(base['content_hashes'], result['content_hashes'])) if i != base['slot'])
                assert pair['baseline_score'] == base['score'] and pair['candidate_score'] == result['score']
                seen[result['episode']] = {'pair': pair, 'baseline': base, 'candidate': result}
            h.write(RAW / 'paired-results.json', {'complete': len(seen) == 80, 'pairs': list(seen.values())})
            print(json.dumps({'paired_audited': len(seen), 'status': evaluation['status']}), flush=True)
            if evaluation['status'] in ('completed', 'failed', 'cancelled', 'skipped'):
                assert evaluation['status'] == 'completed' and len(seen) == 80 and selected == set(indexed)
                break
            time.sleep(10)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--prepare', action='store_true')
    if p.parse_args().prepare: prepare()
    else: run()
