"""Budgeted, resumable counterfactual creation; never invent a key after a timeout."""
from pathlib import Path
import jsonschema

TERMINAL = {'completed', 'failed', 'cancelled', 'error', 'skipped'}


def active_requests(c, h):
    journal = h.read(h.CAMPAIGN / 'xp-ledger.json')
    path = h.STUDY / 'terminal-requests.json'
    cache = h.read(path) if path.exists() else {}
    active = 0
    for entry in journal.values():
        out = Path(entry['output'])
        if entry.get('kind') == 'counterfactual_eval':
            receipt = out / 'evaluation.json'
            assert receipt.exists(), 'Resume unresolved counterfactual reservation first'
            row = h.get(c, '/v2/counterfactual-evals/' + h.read(receipt)['id'])
            h.write(out / 'evaluation-status.json', row)
            active += row['status'] not in TERMINAL
            continue
        if entry['episodes'] == 0 and entry.get('response_evidence'):
            error = h.read(Path(entry['response_evidence']))
            assert error['status'] == 422 and error['body']['type'] == 'validation_error'
            continue
        receipt = out / 'created.json'
        assert receipt.exists(), 'Unreconciled XP reservation: ' + str(out)
        ident = h.read(receipt)['id']
        if cache.get(ident, {}).get('games') == entry['episodes']:
            continue
        eps = h.episodes(c, ident)
        terminal = len(eps) == entry['episodes'] and all(e['status'] in TERMINAL for e in eps)
        if terminal:
            cache[ident] = {'games': len(eps), 'terminal': True, 'checked_at': h.research.now()}
        else:
            active += 1
    h.write(path, cache)
    return active


def create(c, h, body, out, schema, ready):
    """`ready` freezes an audited fresh-baseline pool; all comparisons reuse it."""
    n = body.get('n')
    cfg = h.research.config(h.CAMPAIGN)
    assert type(n) is int and 1 <= n <= min(100, cfg.get('max_counterfactual_pairs_per_request', 100))
    assert body['source'] == 'experience_request' and not body.get('league_id')
    assert ready['baseline_version'] == body['baseline_policy_version_id']
    assert ready['coworld_id'] == h.GAME and ready['complete']
    assert len(ready['episode_ids']) == len(set(ready['episode_ids'])) == n
    jsonschema.validate(body, schema['components']['schemas']['CreateCounterfactualEvalBody'],
                        resolver=jsonschema.RefResolver.from_schema(schema))
    h.freeze(out / 'request.json', body)
    pool_path = out / 'baseline-pool.json'
    if pool_path.exists():
        frozen = h.read(pool_path)
        assert {k:v for k,v in frozen.items() if k != 'episode_ids'} == {k:v for k,v in ready.items() if k != 'episode_ids'}
        assert len(frozen['episode_ids']) == n and set(frozen['episode_ids']) == set(ready['episode_ids'])
        ready = frozen  # Completion order can change on resume; the frozen cohort cannot.
    h.freeze(pool_path, ready)
    with h.research.lock(h.CAMPAIGN / 'xp-create.lock'):
        h.live(c)
        assert h.read(h.CAMPAIGN / 'service.json')['state'] == 'paused'
        key = body['idempotency_key']
        journal = h.read(h.CAMPAIGN / 'xp-ledger.json')
        # A prior reservation with this exact key may be between POST and receipt.
        # Retry the identical idempotent POST; do not require its own missing receipt.
        if key not in journal:
            assert active_requests(c, h) < cfg['max_parallel_xp']
        with h.research.lock(h.CAMPAIGN / 'budget.lock'):
            journal = h.read(h.CAMPAIGN / 'xp-ledger.json')
            if key in journal:
                assert journal[key]['body_sha256'] == h.research.fingerprint(body)
                assert journal[key]['output'] == str(out.resolve())
            else:
                day = h.research.now()[:10]
                assert sum(e['episodes'] for e in journal.values() if e['day'] == day) + n <= cfg['daily_episode_limit']
                assert sum(e['episodes'] for e in journal.values() if e['cycle'] == h.CYCLE) + n <= cfg['cycle_episode_limit']
                journal[key] = {'day': day, 'cycle': h.CYCLE, 'episodes': n,
                    'kind': 'counterfactual_eval', 'body_sha256': h.research.fingerprint(body),
                    'output': str(out.resolve()), 'reserved_at': h.research.now(),
                    'new_release': h.VERSION, 'engine': h.COMMIT}
                h.research.write(h.CAMPAIGN / 'xp-ledger.json', journal)
        receipt = out / 'evaluation.json'
        if receipt.exists():
            return h.read(receipt)
        response = c.post('/v2/counterfactual-evals', json=body)
        if response.status_code >= 400:
            h.write(out / 'create-error.json', {'status': response.status_code, 'body': response.text})
        response.raise_for_status()
        result = response.json()
        assert result['idempotency_key'] == key
        h.write(receipt, result)
        return result
